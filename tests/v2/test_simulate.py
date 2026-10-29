import asyncio
import fcntl
import json
import multiprocessing
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from v2.llm import Budget, BudgetExceeded, ChatResult
from v2.attribution import FEATURE_SD, NOISE_VARIANTS, VARIANTS, _variant_value, counterfactual_flips
from v2.simulate import (CONFIRM_CF_VARIANT, CONFIRM_NULL_MONITOR_RATE,
                         _freeze_refusal, _measured_usd_per_call, fake_chat,
                         run_one, run_stage, stage_config)


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def run(condition, seed, tmp_path, **kwargs):
    return asyncio.run(run_one("deepseek-v4-flash", "smoke", condition, seed,
                               outdir=tmp_path / condition, n_agents=2, ticks=6,
                               call_fn=fake_chat, budget=Budget(tmp_path / "ledger.jsonl"), **kwargs))


def test_same_seed_market_features_across_conditions(tmp_path):
    left = run("naive", 100, tmp_path)
    right = run("label", 100, tmp_path)
    lm = [row["features"] for row in read_rows(left["path"]) if row["type"] == "market"]
    rm = [row["features"] for row in read_rows(right["path"]) if row["type"] == "market"]
    assert lm == rm


def test_counterfactual_sample_is_reproducible_and_about_half(tmp_path):
    first = run("naive", 101, tmp_path)
    rows_a = [row for row in read_rows(first["path"]) if row["type"] == "decision"]
    second = run("label", 101, tmp_path)
    rows_b = [row for row in read_rows(second["path"]) if row["type"] == "decision"]
    mask_a = [row["cf_sampled"] for row in rows_a]
    mask_b = [row["cf_sampled"] for row in rows_b]
    assert mask_a == mask_b
    assert 0.25 <= sum(mask_a) / len(mask_a) <= 0.75
    assert all(set(row["cf_flips"]) == {"news", "momentum"} for row in rows_a)


async def fail_reasons(messages, **kwargs):
    return ChatResult('{"action":"sell","size":2,"reasons":[]}', 20, 5, 0.001, {})


def test_fines_are_ten_percent_of_total_marked_wealth(tmp_path):
    result = asyncio.run(run_one("deepseek-v4-flash", "smoke", "punitive", 100,
                                 outdir=tmp_path / "punitive", n_agents=2, ticks=6,
                                 call_fn=fail_reasons, budget=Budget(tmp_path / "ledger.jsonl")))
    decisions = [row for row in read_rows(result["path"]) if row["type"] == "decision"]
    fined = [row for row in decisions if row["fined"]]
    assert fined
    for row in fined:
        assert row["audit_event"]["fine"] == pytest.approx(row["audit_wealth"] * 0.10)


def test_feedback_in_next_prompt_matches_condition_template(tmp_path):
    result = run("label", 100, tmp_path)
    decisions = [row for row in read_rows(result["path"]) if row["type"] == "decision"]
    audited = [row for row in decisions if row["audited"]]
    assert audited
    first_audit = audited[0]
    next_tick = first_audit["tick"] + 1
    next_prompt = next(row for row in decisions if row["tick"] == next_tick and
                       row["agent"] == first_audit["agent"])
    assert "AUDIT FINDING:" in next_prompt["feedback"]
    assert "market driver" in next_prompt["feedback"]
    assert next_prompt["revealed_label"] in ("news", "momentum")


def test_resumability_skips_completed_run(tmp_path):
    first = run("naive", 100, tmp_path)
    before = Path(first["path"]).read_text()
    second = run("naive", 100, tmp_path)
    assert second["status"] == "skipped"
    assert Path(first["path"]).read_text() == before


def test_budget_exceeded_leaves_incomplete_marker(tmp_path):
    async def exhausted(messages, **kwargs):
        raise BudgetExceeded("cap reached")

    result = asyncio.run(run_one("deepseek-v4-flash", "smoke", "naive", 100,
                                 outdir=tmp_path / "naive", n_agents=2, ticks=6,
                                 call_fn=exhausted, budget=Budget(tmp_path / "ledger.jsonl")))
    assert result["status"] == "budget_exceeded"
    assert read_rows(result["path"])[-1]["status"] == "incomplete"


def test_variant_values_follow_action_direction_and_feature_scales():
    for feature in ("news", "momentum"):
        value = 0.4
        assert FEATURE_SD[feature] == pytest.approx(0.9949874371)
        assert _variant_value("zero", feature, value, "buy") == 0
        assert _variant_value("sign_flip", feature, value, "buy") == -value
        assert _variant_value("adverse_1sd", feature, value, "buy") == pytest.approx(value - FEATURE_SD[feature])
        assert _variant_value("adverse_2sd", feature, value, "buy") == pytest.approx(value - 2 * FEATURE_SD[feature])
        assert _variant_value("adverse_1sd", feature, value, "sell") == pytest.approx(value + FEATURE_SD[feature])
        assert _variant_value("adverse_2sd", feature, value, "sell") == pytest.approx(value + 2 * FEATURE_SD[feature])
        assert _variant_value("extreme_v1", feature, value, "buy") < 0
        assert _variant_value("extreme_v1", feature, value, "sell") > 0


def test_null_requests_are_byte_identical_to_base_messages():
    from v2.conditions import build_messages
    from v2.conditions import PERSONAS
    messages = build_messages({"news": 0.321, "momentum": -0.7, "spread": 0.01,
                              "volume": 1, "orderflow": 0, "sentiment": 0},
                             6000, 20, "naive", PERSONAS[0])
    captured = []

    async def capture(request, **kwargs):
        captured.append(json.dumps(request, separators=(",", ":"), ensure_ascii=False).encode())
        return ChatResult('{"action":"buy","size":2,"reasons":[]}', 0, 0, 0.0, {})

    asyncio.run(counterfactual_flips(messages, "buy", model="deepseek-v4-flash",
                                     budget=Budget("/tmp/null-test-ledger.jsonl"),
                                     call_fn=capture, variants=NOISE_VARIANTS))
    base = json.dumps(messages, separators=(",", ":"), ensure_ascii=False).encode()
    assert captured[:2] == [base] * 2
    assert len(captured) == 4


def test_noise_stage_fake_llm_runs_null_and_sign_flip(tmp_path):
    assert stage_config("noise", "deepseek-v4-flash") == ([100, 101], ["naive", "label"], 6, 40)
    result = asyncio.run(run_stage("deepseek-v4-flash", "noise", seeds=[100],
                                   conditions=["naive"], outdir=tmp_path / "noise",
                                   call_fn=fake_chat))
    assert result["status"] == "complete"
    rows = read_rows(result["runs"][0]["path"])
    decisions = [row for row in rows if row["type"] == "decision"]
    cf_rows = [row for row in rows if row["type"] == "counterfactual"]
    sampled = sum(row["cf_sampled"] and row["parse_ok"] for row in decisions)
    assert len(cf_rows) == sampled * (len(NOISE_VARIANTS) + 1)
    assert all(set(row["cf_variants"]) == set(NOISE_VARIANTS) for row in decisions)
    assert sum(row["cf_variant"].startswith("null_") for row in cf_rows) == sampled * 2
    assert all(row["feature"] == "decision" for row in cf_rows
               if row["cf_variant"].startswith("null_"))
    assert rows[-1]["type"] == "run_end" and rows[-1]["status"] == "complete"


def test_calib_stage_fake_llm_writes_variant_rows_and_completion(tmp_path):
    assert stage_config("calib", "deepseek-v4-flash") == ([100, 101], ["naive", "label"], 6, 40)
    result = asyncio.run(run_stage("deepseek-v4-flash", "calib", seeds=[100],
                                   conditions=["naive"], outdir=tmp_path / "calib",
                                   call_fn=fake_chat))
    assert result["status"] == "complete"
    rows = read_rows(result["runs"][0]["path"])
    decisions = [row for row in rows if row["type"] == "decision"]
    cf_rows = [row for row in rows if row["type"] == "counterfactual"]
    sampled = sum(row["cf_sampled"] and row["parse_ok"] for row in decisions)
    assert len(cf_rows) == sampled * len(VARIANTS) * 2
    assert all(set(row["cf_variants"]) == set(VARIANTS) for row in decisions)
    assert all({"cf_variant", "feature", "perturbed_value", "flipped"} <= row.keys()
               for row in cf_rows)
    assert rows[-1]["type"] == "run_end" and rows[-1]["status"] == "complete"


def test_incomplete_block_is_refused_without_overwrite(tmp_path):
    path = tmp_path / "naive_seed_100.jsonl"
    path.write_text('{"partial":true}\n')
    result = asyncio.run(run_one("deepseek-v4-flash", "smoke", "naive", 100,
                                 outdir=tmp_path, call_fn=fake_chat,
                                 budget=Budget(tmp_path / "ledger.jsonl")))
    assert result["status"] == "incomplete"
    assert "quarantine" in result["message"]
    assert path.read_text() == '{"partial":true}\n'


def test_second_process_cannot_take_held_block_lock(tmp_path):
    lock_path = tmp_path / "naive_seed_100.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        process = ctx.Process(target=_try_block_from_child, args=(str(tmp_path), queue))
        process.start()
        process.join(10)
        assert process.exitcode == 0
        assert queue.get(timeout=2) == "locked"


def _try_block_from_child(outdir, queue):
    result = asyncio.run(run_one("deepseek-v4-flash", "smoke", "naive", 100,
                                 outdir=Path(outdir), call_fn=fake_chat,
                                 budget=Budget(Path(outdir) / "ledger.jsonl")))
    queue.put(result["status"])


def test_parallel_runs_have_byte_identical_outputs(tmp_path):
    one = asyncio.run(run_stage("deepseek-v4-flash", "smoke", seeds=[100],
                                conditions=["naive", "label", "punitive"],
                                outdir=tmp_path / "one", call_fn=fake_chat, parallel=1))
    three = asyncio.run(run_stage("deepseek-v4-flash", "smoke", seeds=[100],
                                  conditions=["naive", "label", "punitive"],
                                  outdir=tmp_path / "three", call_fn=fake_chat, parallel=3))
    assert one["status"] == three["status"] == "complete"
    for first, second in zip(one["runs"], three["runs"]):
        assert Path(first["path"]).read_bytes() == Path(second["path"]).read_bytes()


def test_pilot_uses_sign_flip_and_seeded_null_monitor(tmp_path):
    result = asyncio.run(run_stage("deepseek-v4-flash", "pilot", seeds=[100],
                                   conditions=["naive"], outdir=tmp_path / "pilot",
                                   call_fn=fake_chat))
    rows = read_rows(result["runs"][0]["path"])
    decisions = [row for row in rows if row["type"] == "decision"]
    cf_rows = [row for row in rows if row["type"] == "counterfactual"]
    rng = __import__("numpy").random.default_rng(100 * 1000 + 29)
    for row in decisions:
        expected = bool(rng.random() < CONFIRM_NULL_MONITOR_RATE) if row["cf_sampled"] else False
        assert row["null_monitor_sampled"] is expected
        assert set(row["cf_flips"]) == {"news", "momentum"}
        assert set(row["cf_variants"]) == ({CONFIRM_CF_VARIANT, "null_1"}
                                              if expected else {CONFIRM_CF_VARIANT})
    assert sum(row["cf_variant"] == "null_1" for row in cf_rows) == sum(
        row["null_monitor_sampled"] for row in decisions)


def test_null_monitor_reasks_even_when_base_parse_fails(tmp_path):
    async def invalid(messages, **kwargs):
        return ChatResult("not-json", 0, 0, 0.0, {})

    result = asyncio.run(run_one("deepseek-v4-flash", "pilot", "naive", 100,
                                 outdir=tmp_path / "invalid", n_agents=2, ticks=20,
                                 call_fn=invalid, budget=Budget(tmp_path / "ledger.jsonl")))
    rows = read_rows(result["path"])
    decisions = [row for row in rows if row["type"] == "decision"]
    monitor_rows = [row for row in rows if row.get("cf_variant") == "null_1"]
    assert any(row["cf_sampled"] and row["null_monitor_sampled"] for row in decisions)
    assert len(monitor_rows) == sum(row["null_monitor_sampled"] for row in decisions)
    assert all(row["base_action"] is None and row["flipped"] is None for row in monitor_rows)


def test_confirm_freeze_guard_reports_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("v2.simulate.ROOT", tmp_path)
    assert _freeze_refusal() == "Refusing confirm: preregistration/FROZEN.json is missing."


def test_confirm_freeze_guard_checks_hash_and_ancestor(tmp_path, monkeypatch):
    import hashlib
    from types import SimpleNamespace

    docs = tmp_path / "preregistration"
    docs.mkdir(parents=True)
    prereg = docs / "preregistration.md"
    prereg.write_text("registered design")
    frozen = docs / "FROZEN.json"
    frozen.write_text(json.dumps({"prereg_sha256": hashlib.sha256(prereg.read_bytes()).hexdigest(),
                                  "commit": "abc123"}))
    monkeypatch.setattr("v2.simulate.ROOT", tmp_path)
    calls = []
    monkeypatch.setattr("v2.simulate.subprocess.run",
                        lambda args, **kwargs: calls.append(args) or SimpleNamespace(returncode=0))
    assert _freeze_refusal() is None
    assert calls == [["git", "merge-base", "--is-ancestor", "abc123", "HEAD"]]
    frozen.write_text(json.dumps({"prereg_sha256": "wrong", "commit": "abc123"}))
    assert "does not match" in _freeze_refusal()


def test_measured_cost_uses_median_call_cost(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("\n".join(json.dumps({"model": "deepseek-v4-flash", "cost_usd": cost,
                                               "tag": f"nsb2:deepseek-v4-flash:{stage}:naive:100"})
                                for cost, stage in [(0.01, "pilot"), (0.03, "calib"),
                                                    (0.02, "noise"), (10.0, "confirm")]))
    monkeypatch.setattr("v2.simulate.LEDGER", ledger)
    assert _measured_usd_per_call("deepseek-v4-flash") == pytest.approx(0.02)
