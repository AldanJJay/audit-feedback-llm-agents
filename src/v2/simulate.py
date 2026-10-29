"""Study simulation runner and offline projection mode."""

import argparse
import asyncio
import fcntl
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

if __package__ and __package__.startswith("src."):
    from ..market import Market
else:
    from market import Market
from . import attribution
from .conditions import (AUDIT_RATE, CONDITIONS, FEATURES, HISTORY_K, PERSONAS,
                         PENALTY_RATE, build_feedback, build_messages)
from .llm import Budget, BudgetExceeded, ChatResult, chat, extract_json
from .models import MODELS

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "data/v2/ledger.jsonl"
MAX_TOKENS = 512
CONFIRM_CF_VARIANT = "sign_flip"
CONFIRM_NULL_MONITOR_RATE = 0.20
CONFIRM_NULL_MONITOR_RNG_OFFSET = 29
PROVIDER_CONCURRENCY = 8


def model_slug(model):
    return model.replace("/", "-")


def stage_config(stage, model, seeds=None, conditions=None):
    if stage == "smoke":
        default_seeds, default_conditions, agents, ticks = [100], ["naive", "label"], 2, 6
    elif stage == "pilot":
        default_seeds, default_conditions, agents, ticks = [100, 101], list(CONDITIONS), 6, 40
    elif stage == "confirm":
        default_seeds = list(range(200, 220)) if model == "deepseek-v4-flash" else list(range(200, 210))
        default_conditions, agents, ticks = list(CONDITIONS), 6, 40
    elif stage == "calib":
        default_seeds = [100, 101]
        default_conditions, agents, ticks = ["naive", "label"], 6, 40
    elif stage == "noise":
        default_seeds = [100, 101]
        default_conditions, agents, ticks = ["naive", "label"], 6, 40
    else:
        raise ValueError(f"Unknown stage: {stage}")
    selected_seeds = default_seeds if seeds is None else list(seeds)
    selected_conditions = default_conditions if conditions is None else list(conditions)
    if not selected_seeds or not selected_conditions:
        raise ValueError("At least one seed and condition are required")
    if any(condition not in CONDITIONS for condition in selected_conditions):
        raise ValueError("Unknown condition")
    if stage == "confirm" and seeds is None:
        if model not in MODELS:
            raise ValueError(f"Unknown model: {model}")
    return selected_seeds, selected_conditions, agents, ticks


def ordered_conditions(conditions, seed, stage):
    if stage != "confirm":
        return list(conditions)
    full = list(CONDITIONS)
    offset = (seed - 200) % len(full)
    rotated = full[offset:] + full[:offset]
    return [condition for condition in rotated if condition in conditions]


def _valid_decision(text):
    value = extract_json(text)
    if not isinstance(value, dict) or set(value) != {"action", "size", "reasons"}:
        return None
    action, size, reasons = value["action"], value["size"], value["reasons"]
    if action not in ("buy", "sell") or isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= 10:
        return None
    if (not isinstance(reasons, list) or len(reasons) > 2
            or any(not isinstance(reason, str) or reason not in FEATURES for reason in reasons)
            or len(set(reasons)) != len(reasons)):
        return None
    return value


def _history_for(market, tick):
    # At tick t, completed outcomes pair features[0:t] with returns[1:t+1].
    rows = list(zip(market.history["features"][:tick], market.history["returns"][1:tick + 1]))
    return rows[-HISTORY_K:]


def _fake_decision(messages):
    content = messages[-1]["content"]
    current = content.rpartition("Market features now: ")[2]
    values = {key: float(value) for key, value in re.findall(r"(news|momentum)=(-?\d+(?:\.\d+)?)", current)}
    score = values.get("news", 0) + values.get("momentum", 0)
    action = "buy" if score >= 0 else "sell"
    reasons = ["news"] if abs(values.get("news", 0)) >= abs(values.get("momentum", 0)) else ["momentum"]
    return json.dumps({"action": action, "size": 2, "reasons": reasons})


async def fake_chat(messages, **kwargs):
    return ChatResult(_fake_decision(messages), 0, 0, 0.0, {})


def _run_path(model, stage, condition, seed, outdir=None):
    parent = outdir or ROOT / "data/v2" / model_slug(model) / stage
    return Path(parent) / f"{condition}_seed_{seed}.jsonl"


def _completed(path):
    if not path.exists():
        return False
    try:
        last = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
        return last.get("type") == "run_end" and last.get("status") == "complete"
    except (ValueError, IndexError, OSError):
        return False


def _block_lock_path(model, stage, condition, seed, outdir=None):
    parent = outdir or ROOT / "data/v2" / model_slug(model) / stage
    return Path(parent) / f"{condition}_seed_{seed}.lock"


async def run_one(model, stage, condition, seed, *, budget=None, call_fn=None,
                  outdir=None, n_agents=None, ticks=None, cf_variants=None,
                  semaphore=None):
    """Take the exclusive block lock before inspecting or writing its output."""
    lock_path = _block_lock_path(model, stage, condition, seed, outdir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            message = f"Block is locked by another process: {lock_path}"
            print(message, file=sys.stderr)
            return {"status": "locked", "path": str(_run_path(model, stage, condition, seed, outdir)),
                    "message": message, "calls": 0}
        return await _run_one_locked(model, stage, condition, seed, budget=budget,
                                     call_fn=call_fn, outdir=outdir, n_agents=n_agents,
                                     ticks=ticks, cf_variants=cf_variants,
                                     semaphore=semaphore)


async def _run_one_locked(model, stage, condition, seed, *, budget=None, call_fn=None,
                          outdir=None, n_agents=None, ticks=None, cf_variants=None,
                          semaphore=None):
    """Run one condition/seed block; returns its path and summary."""
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}")
    path = _run_path(model, stage, condition, seed, outdir)
    if _completed(path):
        return {"status": "skipped", "path": str(path), "calls": 0, "prompt_tokens": 0,
                "completion_tokens": 0, "cost_usd": 0.0}
    if path.exists():
        message = f"Refusing incomplete block {path}; quarantine it before retrying."
        print(message, file=sys.stderr)
        return {"status": "incomplete", "path": str(path), "message": message, "calls": 0}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    budget = budget or Budget(LEDGER)
    call_fn = call_fn or chat
    n_agents = n_agents or (2 if stage == "smoke" else 6)
    ticks = ticks or (6 if stage == "smoke" else 40)
    personas = PERSONAS[:n_agents]
    market = Market(seed=seed, n_agents=n_agents, ticks=ticks,
                    regime="news" if seed % 2 == 0 else "momentum", switch_at=[10, 20, 30])
    audit_rng = np.random.default_rng(seed * 1000 + 7)
    cf_rng = np.random.default_rng(seed * 1000 + 17)
    null_monitor_rng = np.random.default_rng(seed * 1000 + CONFIRM_NULL_MONITOR_RNG_OFFSET)
    audit_mask = audit_rng.random((ticks, n_agents)) < AUDIT_RATE
    cf_mask = cf_rng.random((ticks, n_agents)) < 0.50
    portfolios = [{"cash": persona["cash"], "position": persona["position"]} for persona in personas]
    feedback = [None] * n_agents
    feedback_labels = [None] * n_agents
    counts = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
    ledger_tag = f"nsb2:{model_slug(model)}:{stage}:{condition}:{seed}"
    ledger_before = sum(float(row.get("cost_usd", 0)) for row in _ledger_rows(LEDGER)
                        if row.get("tag", "").startswith(ledger_tag))
    try:
        with path.open("a", encoding="utf-8") as output:
            for tick in range(ticks):
                features = market._features(tick)
                regime = market.regime_at(tick)
                history = _history_for(market, tick)
                decisions = []
                orders = []
                for index, persona in enumerate(personas):
                    portfolio = portfolios[index]
                    messages = build_messages(features, portfolio["cash"] + portfolio["position"] * market.P,
                                              portfolio["position"], condition, persona, feedback[index], history)
                    try:
                        response = await call_fn(messages, model=model, temperature=0.0,
                                                 max_tokens=MAX_TOKENS, budget=budget, tag=ledger_tag,
                                                 semaphore=semaphore)
                        counts["calls"] += 1
                        counts["prompt_tokens"] += int(getattr(response, "prompt_tokens", 0) or 0)
                        counts["completion_tokens"] += int(getattr(response, "completion_tokens", 0) or 0)
                        counts["cost_usd"] += float(getattr(response, "cost_usd", 0) or 0)
                    except BudgetExceeded:
                        raise
                    except Exception:
                        response = None
                    decision = _valid_decision(getattr(response, "text", response)) if response is not None else None
                    sampled = bool(cf_mask[tick, index])
                    null_monitor_sampled = (bool(null_monitor_rng.random() < CONFIRM_NULL_MONITOR_RATE)
                                            if stage in ("pilot", "confirm") and sampled else False)
                    chosen_variants = cf_variants or ((CONFIRM_CF_VARIANT,)
                        if stage in ("pilot", "confirm") else ("extreme_v1",))
                    if not decision:
                        chosen_variants = ()
                    if null_monitor_sampled:
                        chosen_variants = tuple(chosen_variants) + ("null_1",)
                    variants = {
                        variant: ({"decision": None} if variant.startswith("null_") else
                                  {feature: None for feature in attribution.FEATURES})
                        for variant in chosen_variants
                    }
                    cf_rows = []
                    if sampled and (decision or null_monitor_sampled):
                        variants, cf_rows = await attribution.counterfactual_flips(
                            messages, decision["action"] if decision else None, model=model, budget=budget,
                            tag=ledger_tag, call_fn=_tracked_call(call_fn, counts, semaphore),
                            variants=chosen_variants)
                    flips = variants.get(CONFIRM_CF_VARIANT if stage in ("pilot", "confirm") else "extreme_v1",
                                         {feature: None for feature in attribution.FEATURES})
                    selected_audit = bool(audit_mask[tick, index]) and condition != "naive"
                    audited = bool(selected_audit and decision)
                    if decision:
                        orders.append((index, decision["action"], decision["size"]))
                    else:
                        orders.append(None)
                    decisions.append({"persona": persona, "messages": messages, "decision": decision,
                                      "sampled": sampled, "flips": flips, "variants": variants,
                                      "null_monitor_sampled": null_monitor_sampled,
                                      "null_monitor_flip": variants.get("null_1", {}).get("decision"),
                                      "cf_rows": cf_rows, "audited": audited,
                                      "portfolio": portfolio})

                market_orders = [order for order in orders if order is not None]
                realized_return = market.step(market_orders)
                post_price = market.P
                audit_events = []
                for index, record in enumerate(decisions):
                    decision = record["decision"]
                    fined = False
                    audit_info = None
                    audit_wealth = None
                    if record["audited"]:
                        faithful = regime in decision["reasons"]
                        portfolio = record["portfolio"]
                        wealth = portfolio["cash"] + portfolio["position"] * post_price
                        audit_wealth = wealth
                        fine = wealth * PENALTY_RATE if not faithful else 0.0
                        if not faithful:
                            portfolio["cash"] *= 1 - PENALTY_RATE
                            portfolio["position"] *= 1 - PENALTY_RATE
                            fined = True
                        audit_info = build_feedback(condition, faithful, regime, fine=fine,
                                                    history=history + [(features, realized_return)])
                        feedback[index] = audit_info["text"]
                        audit_events.append({"agent": index, "tick": tick, "verdict": audit_info["verdict"],
                                             "fine": fine, "revealed_label": audit_info["revealed_label"]})
                    # Audit haircut is marked at the post-step price and precedes settlement.
                    if decision:
                        portfolio = record["portfolio"]
                        units = min(decision["size"], portfolio["cash"] / post_price) if decision["action"] == "buy" else min(decision["size"], portfolio["position"])
                        if decision["action"] == "buy":
                            portfolio["cash"] -= units * post_price
                            portfolio["position"] += units
                        else:
                            portfolio["cash"] += units * post_price
                            portfolio["position"] -= units
                    wealth = record["portfolio"]["cash"] + record["portfolio"]["position"] * post_price
                    decision_row = {
                        "type": "decision", "tick": tick, "agent": index,
                        "persona": record["persona"]["name"], "condition": condition,
                        "regime": regime, "action": decision["action"] if decision else None,
                        "size": decision["size"] if decision else None,
                        "reasons": decision["reasons"] if decision else None,
                        "feedback": messages_feedback(record["messages"]),
                        "revealed_label": feedback_labels[index],
                        "audited": record["audited"], "fined": fined, "wealth": wealth,
                        "cf_sampled": record["sampled"], "cf_flips": record["flips"],
                        "cf_variants": record["variants"],
                        "null_monitor_sampled": record["null_monitor_sampled"],
                        "null_monitor_flip": record["null_monitor_flip"],
                        "parse_ok": decision is not None,
                        "audit_event": audit_events[-1] if audit_info else None,
                        "audit_wealth": audit_wealth,
                        "audit_selected": selected_audit,
                    }
                    if audit_info:
                        feedback_labels[index] = audit_info["revealed_label"]
                    output.write(json.dumps(decision_row, separators=(",", ":")) + "\n")
                    for cf_row in record["cf_rows"]:
                        output.write(json.dumps({"type": "counterfactual", "tick": tick,
                                                 "agent": index, "regime": regime,
                                                 "base_action": decision["action"] if decision else None,
                                                 **cf_row}, separators=(",", ":")) + "\n")
                output.write(json.dumps({"type": "market", "tick": tick, "price": post_price,
                                         "return": realized_return, "features": features,
                                         "regime": regime, "orders": len(market_orders),
                                         "audit_events": audit_events}, separators=(",", ":")) + "\n")
                output.flush()
            ledger_after = sum(float(row.get("cost_usd", 0)) for row in _ledger_rows(LEDGER)
                               if row.get("tag", "").startswith(ledger_tag))
            counts["cost_usd"] = max(counts["cost_usd"], ledger_after - ledger_before)
            summary = {"type": "run_end", "status": "complete", "model": model,
                       "stage": stage, "condition": condition, "seed": seed, **counts}
            output.write(json.dumps(summary, separators=(",", ":")) + "\n")
        summary_path = path.with_suffix(".summary.json")
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return {**summary, "path": str(path)}
    except BaseException as exc:
        with path.open("a", encoding="utf-8") as output:
            output.write(json.dumps({"type": "run_end", "status": "incomplete",
                                     "error": type(exc).__name__, "message": str(exc),
                                     "model": model, "stage": stage, "condition": condition,
                                     "seed": seed, **counts}, separators=(",", ":")) + "\n")
        if isinstance(exc, BudgetExceeded):
            return {"status": "budget_exceeded", "path": str(path), **counts, "error": str(exc)}
        raise


def _tracked_call(call_fn, counts, semaphore=None):
    async def tracked(messages, **kwargs):
        counts["calls"] += 1
        response = await call_fn(messages, semaphore=semaphore, **kwargs)
        counts["prompt_tokens"] += int(getattr(response, "prompt_tokens", 0) or 0)
        counts["completion_tokens"] += int(getattr(response, "completion_tokens", 0) or 0)
        counts["cost_usd"] += float(getattr(response, "cost_usd", 0) or 0)
        return response
    return tracked


def messages_feedback(messages):
    user_text = messages[-1]["content"]
    marker = "Latest audit feedback:\n"
    if marker not in user_text:
        return None
    return user_text.split(marker, 1)[1].split("\nYour total wealth:", 1)[0]


def _ledger_rows(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def _dry_run_projection(model, stage, seeds, conditions, agents, ticks):
    prompts = []
    expected_calls = 0
    base_calls = 0
    sign_flip_calls_total = 0
    null_monitor_calls_total = 0
    blocks = ([("naive", seed) for seed in seeds if seed in (100, 101)] +
              [("label", 100)]) if stage in ("calib", "noise") else [
                  (condition, seed) for seed in seeds
                  for condition in ordered_conditions(conditions, seed, stage)]
    for condition, seed in blocks:
        if condition not in conditions:
            continue
        market = Market(seed=seed, n_agents=agents, ticks=ticks,
                        regime="news" if seed % 2 == 0 else "momentum", switch_at=[10, 20, 30])
        feedback = [None] * agents
        portfolios = [{"cash": p["cash"], "position": p["position"]} for p in PERSONAS[:agents]]
        cfmask = np.random.default_rng(seed * 1000 + 17).random((ticks, agents)) < 0.5
        null_rng = np.random.default_rng(seed * 1000 + CONFIRM_NULL_MONITOR_RNG_OFFSET)
        for tick in range(ticks):
            features = market._features(tick)
            for i, persona in enumerate(PERSONAS[:agents]):
                messages = build_messages(features, portfolios[i]["cash"] + portfolios[i]["position"] * market.P,
                                          portfolios[i]["position"], condition, persona, feedback[i],
                                          _history_for(market, tick))
                prompts.append(messages)
                base_calls += 1
                sampled = bool(cfmask[tick, i])
                null_sampled = bool(null_rng.random() < CONFIRM_NULL_MONITOR_RATE) if (
                    sampled and stage in ("pilot", "confirm")) else False
                if stage == "calib":
                    sign_flip_calls = len(attribution.VARIANTS) * len(attribution.FEATURES) * int(sampled)
                    null_calls = 0
                elif stage == "noise":
                    sign_flip_calls = 2 * int(sampled)
                    null_calls = 2 * int(sampled)
                elif stage in ("pilot", "confirm"):
                    sign_flip_calls = len(attribution.FEATURES) * int(sampled)
                    null_calls = int(null_sampled)
                else:
                    sign_flip_calls = 2 * int(sampled)
                    null_calls = 0
                expected_calls += 1 + sign_flip_calls + null_calls
                sign_flip_calls_total += sign_flip_calls
                null_monitor_calls_total += null_calls
            market.step([])
    result = {"expected_calls": expected_calls, "base_calls": base_calls,
            "sign_flip_calls": sign_flip_calls_total,
            "null_monitor_calls": null_monitor_calls_total}
    if stage != "confirm":
        prompt_tokens = [max(1, math.ceil(len(json.dumps(m, ensure_ascii=False).encode("utf-8")) / 4))
                         for m in prompts]
        avg_tokens = sum(prompt_tokens) / len(prompt_tokens)
        spec = MODELS[model]
        avg_output = MAX_TOKENS
        no_cache = expected_calls * (avg_tokens * spec.input_usd_per_million +
                                     avg_output * spec.output_usd_per_million) / 1_000_000
        cached = no_cache
        if spec.cached_input_usd_per_million is not None:
            system_prompt = build_messages(
                {"momentum": 0, "spread": 0.01, "volume": 1, "news": 0, "orderflow": 0,
                 "sentiment": 0}, 6000, 20, conditions[0], PERSONAS[0])[0]["content"]
            static_tokens = max(1, math.ceil(len(system_prompt.encode("utf-8")) / 4))
            variable_tokens = max(0, avg_tokens - static_tokens)
            cached = expected_calls * (variable_tokens * spec.input_usd_per_million +
                                       static_tokens * spec.cached_input_usd_per_million +
                                       avg_output * spec.output_usd_per_million) / 1_000_000
        result.update({"avg_prompt_tokens": round(avg_tokens, 1),
                       "estimated_output_tokens_per_call": avg_output,
                       "projected_usd_no_cache": round(no_cache, 6),
                       "projected_usd_cached_prefix": round(cached, 6)})
    return result


def _measured_usd_per_call(model):
    costs = [float(row.get("cost_usd", 0)) for row in _ledger_rows(LEDGER)
             if row.get("model") == model and
             row.get("tag", "").startswith(f"nsb2:{model_slug(model)}:") and
             row.get("tag", "").split(":")[2] in ("pilot", "calib", "noise")]
    if not costs:
        return None
    return float(np.median(costs))


def _freeze_refusal():
    freeze_path = ROOT / "preregistration/FROZEN.json"
    prereg_path = ROOT / "preregistration/preregistration.md"
    if not freeze_path.exists():
        return "Refusing confirm: preregistration/FROZEN.json is missing."
    try:
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "Refusing confirm: preregistration/FROZEN.json is unreadable or invalid JSON."
    if not prereg_path.exists():
        return "Refusing confirm: preregistration/preregistration.md is missing."
    expected = hashlib.sha256(prereg_path.read_bytes()).hexdigest()
    if freeze.get("prereg_sha256") != expected:
        return "Refusing confirm: FROZEN.json prereg_sha256 does not match preregistration.md."
    commit = freeze.get("commit")
    if not isinstance(commit, str) or not commit:
        return "Refusing confirm: FROZEN.json commit field is missing."
    result = subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return "Refusing confirm: FROZEN.json commit is not an ancestor of HEAD."
    return None


async def run_stage(model, stage, *, conditions=None, seeds=None, dry_run=False,
                    outdir=None, call_fn=None, parallel=1):
    selected_seeds, selected_conditions, agents, ticks = stage_config(stage, model, seeds, conditions)
    if stage == "confirm" and not dry_run:
        refusal = _freeze_refusal()
        if refusal:
            return {"model": model, "stage": stage, "status": "refused", "message": refusal}
    if dry_run:
        projections = []
        projection_models = MODELS if stage == "confirm" else (model,)
        for projection_model in projection_models:
            p_seeds, p_conditions, p_agents, p_ticks = stage_config(stage, projection_model)
            projection = _dry_run_projection(projection_model, stage, p_seeds, p_conditions,
                                             p_agents, p_ticks)
            measured = _measured_usd_per_call(projection_model)
            projection.update({"model": projection_model,
                               "measured_usd_per_call": measured,
                               "projected_usd": (round(projection["expected_calls"] * measured, 6)
                                                 if measured is not None else None),
                               "cost_projection_status": ("measured" if measured is not None else
                                   "unavailable: no pilot/calib/noise calls for this model in the ledger")})
            projections.append(projection)
        # Exercise one complete run, including fake decisions, audits, fines,
        # feedback, counterfactuals, and JSONL writing, without retaining files.
        with tempfile.TemporaryDirectory(prefix="study-dry-run-") as scratch:
            exercised = await run_one(model, stage, selected_conditions[0], selected_seeds[0],
                                      budget=Budget(LEDGER), call_fn=fake_chat,
                                      outdir=Path(scratch), n_agents=agents, ticks=ticks,
                                      cf_variants=(attribution.NOISE_VARIANTS if stage == "noise" else
                                                   attribution.VARIANTS if stage == "calib" else None))
        return {"model": model, "stage": stage, "projections": projections,
                "offline_pipeline_status": exercised.get("status", "complete"),
                "offline_pipeline_blocks": 1}
    budget = Budget(LEDGER)
    results = []
    blocks = ([("naive", seed) for seed in selected_seeds if seed in (100, 101)] +
              [("label", 100)]) if stage in ("calib", "noise") else [
                  (condition, seed) for seed in selected_seeds
                  for condition in ordered_conditions(selected_conditions, seed, stage)]
    blocks = [(condition, seed) for condition, seed in blocks if condition in selected_conditions]
    semaphore = asyncio.Semaphore(PROVIDER_CONCURRENCY)
    async def execute(condition, seed):
        return await run_one(model, stage, condition, seed, budget=budget,
                             call_fn=call_fn, outdir=outdir, n_agents=agents, ticks=ticks,
                             semaphore=semaphore,
                             cf_variants=(attribution.NOISE_VARIANTS if stage == "noise" else
                                          attribution.VARIANTS if stage == "calib" else None))
    gate = asyncio.Semaphore(max(1, parallel))
    async def bounded(condition, seed):
        async with gate:
            return await execute(condition, seed)
    results = await asyncio.gather(*(bounded(condition, seed) for condition, seed in blocks))
    if any(result.get("status") == "budget_exceeded" for result in results):
        status = "budget_exceeded"
    elif any(result.get("status") in ("locked", "incomplete") for result in results):
        status = "refused"
    else:
        status = "complete"
    return {"model": model, "stage": stage, "runs": results, "status": status}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=MODELS)
    parser.add_argument("--stage", required=True, choices=("smoke", "pilot", "confirm", "calib", "noise"))
    parser.add_argument("--conditions", nargs="+", choices=CONDITIONS)
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--parallel", type=int, default=1)
    args = parser.parse_args(argv)
    if args.parallel < 1:
        parser.error("--parallel must be at least 1")
    result = asyncio.run(run_stage(args.model, args.stage, conditions=args.conditions,
                                   seeds=args.seeds, dry_run=args.dry_run,
                                   parallel=args.parallel,
                                   call_fn=fake_chat if args.dry_run else None))
    if result.get("message"):
        print(result["message"], file=sys.stderr)
    print(json.dumps(result, indent=2))
    if result.get("status") in ("budget_exceeded", "refused"):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
