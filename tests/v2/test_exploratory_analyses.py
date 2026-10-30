"""Offline checks of exploratory estimands and diagnostics; no model calls."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.v2.analyze import PRIMARY, _prepare, contrast, paired_bootstrap
from src.v2.conditions import build_evidence_feedback
from src.v2.exploratory_analyses import (
    decision_flow, hedging_description, hik_directionality, hik_evidence,
    hik_placebo_conflict, label_staleness, null_mask_audit, exploratory_contrast,
    reproduce_primary, seed_summary, support_counts,
)

MODEL = "deepseek-v4-flash"


def row(tick=20, agent=0, regime="news", reasons=("news",), flips=None, **updates):
    value = {"tick": tick, "agent": agent, "regime": regime, "action": "buy",
             "size": 2, "parse_ok": True, "reasons": list(reasons), "cf_sampled": True,
             "cf_flips": {"news": True, "momentum": False} if flips is None else flips,
             "revealed_label": None, "feedback": None, "null_monitor_sampled": False,
             "null_monitor_flip": None, "audited": False, "fined": False, "audit_event": None}
    value.update(updates)
    return _prepare(value)


def add(loaded, condition, seed, rows, **extra):
    loaded[f"{MODEL}|{condition}|{seed}"] = {
        "source": {"model": MODEL, "condition": condition, "seed": seed},
        "rows": rows, "coordinates": {(r["tick"], r["agent"]): r for r in rows}, **extra}


def test_seed_summary_uses_equal_seed_weights_and_leaves_empty_undefined():
    summary = seed_summary({200: 0., 201: 1., 202: None})
    assert summary["mean"] == .5
    assert summary["seed_sd"] == pytest.approx(np.sqrt(.5))
    assert summary["n_seeds"] == 2
    assert summary["bootstrap_ci_95"] == paired_bootstrap([0., 1.])
    assert seed_summary({200: None})["mean"] is None


def test_flow_separates_calls_decisions_empty_and_invalid_denominators():
    rows = [row(), row(agent=1, reasons=()),
            row(agent=2, flips={"news": False, "momentum": False}),
            row(agent=3, flips={"news": None, "momentum": False}),
            row(agent=4, parse_ok=False)]
    flow = decision_flow(rows)
    assert flow["assigned_decisions"] == 5
    assert flow["cf_mask_selected"] == 5
    assert flow["probed_decisions"] == 4
    assert flow["feature_reasks_attempted"] == 8
    assert flow["valid_feature_reasks"] == 7
    assert flow["invalid_or_failed_feature_reasks"] == 1
    assert flow["eligible_complete_decisions"] == 3
    assert flow["empty_C_valid_base"] == {"mean": .25, "sum": 1., "n": 4}
    assert flow["empty_C_complete_measured"]["n"] == 3
    assert flow["empty_D_complete_measured"]["sum"] == 1
    assert flow["analysed_all_available_precision"] == 2
    assert flow["analysed_all_available_recall"] == 2


def test_common_support_is_posttreatment_and_preserves_registered_estimand():
    loaded = {}
    for seed in range(200, 220):
        add(loaded, "evidence", seed, [row(reasons=()), row(agent=1)])
        add(loaded, "naive", seed, [row(), row(agent=1, flips={"news": False, "momentum": False})])
    specs = dict(list(PRIMARY.items())[:2])
    counts = support_counts(loaded, MODEL, specs)
    assert counts["H1_precision_evidence_minus_naive"]["common_analysed"] == 20
    assert counts["H1_dependence_evidence_minus_naive"]["common_analysed"] == 40
    current = exploratory_contrast(loaded, MODEL, PRIMARY["H1_precision_evidence_minus_naive"])
    registered = contrast(loaded, MODEL, "confirm", PRIMARY["H1_precision_evidence_minus_naive"])
    for field in ("mean_delta", "bootstrap_ci_95", "paired_t_p"):
        assert current[field] == registered[field]


def test_primary_reproduction_fails_closed_on_changed_frozen_number():
    loaded = {}
    for seed in range(200, 203):
        for c in ("evidence", "naive", "label", "placebo"):
            add(loaded, c, seed, [row()])
    from src.v2.analyze import holm
    frozen = {k: contrast(loaded, MODEL, "confirm", spec) for k, spec in PRIMARY.items()}
    for item, p in zip(frozen.values(), holm([i["paired_t_p"] for i in frozen.values()])):
        item["holm_p"] = p
    reference = {"models": {MODEL: {"primary_contrasts": frozen}}}
    assert all(r["matches_frozen_exactly"] for r in reproduce_primary(loaded, reference, MODEL).values())
    frozen["H4_sci_placebo"]["mean_delta"] = .1
    with pytest.raises(AssertionError, match="Frozen primary mismatch"):
        reproduce_primary(loaded, reference, MODEL)


def test_stale_placebo_keeps_current_opposite_selector_and_actual_label_separate():
    loaded = {}
    for seed in range(200, 220):
        add(loaded, "placebo", seed, [row(revealed_label="news", feedback="old placebo label")])
        add(loaded, "label", seed, [row(revealed_label="momentum", feedback="old true label")])
        add(loaded, "naive", seed, [row(reasons=(), flips={"news": False, "momentum": True})])
    result = label_staleness(loaded, MODEL)
    assert result["label"]["label_false"]["share_of_assigned"] == 1
    placebo = result["placebo"]
    assert placebo["placebo_accidentally_true"]["share_of_assigned"] == 1
    split = placebo["split"]["correct"]
    assert split["SCI_current_opposite_P4_selector"]["mean_delta"] == 1
    assert split["SCI_actual_persisted_label"]["mean_delta"] == 0
    assert split["metrics"]["label_adoption"]["mean"] == 1


def test_hedging_distinguishes_guaranteed_audit_pass_from_specificity():
    result = hedging_description({200: [row(reasons=("news", "momentum")), row()],
                                  201: [row(reasons=())]})
    assert result["both_news_and_momentum"]["mean"] == .25
    assert result["exclusive_true_within_probes"]["mean"] == .25
    assert result["true_share_of_probed_citations"]["mean"] == .75
    assert result["true_share_of_probed_citations"]["n_seeds"] == 1
    assert result["unconditional_true_minus_opposite_citation"]["mean"] == .25


def test_null_mask_audit_validates_conditional_draw_schedule():
    seed = 200
    cf = np.random.default_rng(seed * 1000 + 17).random((40, 6)) < .5
    rng = np.random.default_rng(seed * 1000 + 29)
    rows = [row(tick=t, agent=a, cf_sampled=bool(cf[t, a]),
                null_monitor_sampled=bool(rng.random() < .2) if cf[t, a] else False)
            for t in range(40) for a in range(6)]
    loaded = {}
    add(loaded, "naive", seed, rows)
    result = null_mask_audit(loaded, MODEL)
    assert result["runs_matching_implemented"] == 1
    assert result["runs_matching_registered"] == 0
    rows[0]["null_monitor_sampled"] = not rows[0]["null_monitor_sampled"]
    with pytest.raises(AssertionError):
        null_mask_audit(loaded, MODEL)


def test_direction_reconstructs_binary_action_and_excludes_zero_only_from_alignment(tmp_path):
    rows = [row(), row(tick=21, flips={"news": False, "momentum": True})]
    markets = {20: {"features": {"news": 1., "momentum": .5}},
               21: {"features": {"news": 0., "momentum": -.5}}}
    cfs = [{"type": "counterfactual", "cf_variant": "sign_flip", "tick": r["tick"], "agent": r["agent"],
            "feature": f, "perturbed_value": -markets[r["tick"]]["features"][f],
            "base_action": r["action"], "flipped": r["cf_flips"][f]} for r in rows for f in ("news", "momentum")]
    path = tmp_path / "run.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in cfs))
    loaded = {}
    add(loaded, "naive", 200, rows, markets=markets)
    loaded[f"{MODEL}|naive|200"]["source"]["path"] = str(path)
    h = hik_directionality(loaded)
    driver = next(x for x in h["cells"] if x["probe_role"] == "driver")
    assert h["verified_sign_flip_records"] == 4
    assert driver["n_zero_feature"] == 1
    assert driver["new_action_matches_flipped_sign"] == {"numerator": 1, "n": 1, "rate": 1.}


def test_false_label_citation_can_pass_by_citing_both_drivers():
    fail = {"verdict": "unfaithful", "revealed_label": "momentum", "fine": 10.}
    passed = {"verdict": "faithful", "revealed_label": "momentum", "fine": 0.}
    rows = [row(reasons=("momentum",), revealed_label="momentum", audited=True, fined=True, audit_event=fail),
            row(agent=1, reasons=("news", "momentum"), revealed_label="momentum", audited=True, audit_event=passed),
            row(agent=2, reasons=("momentum",), revealed_label="momentum")]
    loaded = {}
    add(loaded, "placebo", 200, rows)
    b = hik_placebo_conflict(loaded)["models"][MODEL]
    assert b["n_persisted_false_label_cited"] == 3
    assert b["n_such_citations_audited"] == 2
    assert b["n_such_citations_failed_and_fined"] == 1
    assert b["failed_and_fined_fraction_audited_false_label_citations"] == .5
    assert b["failed_and_fined_fraction_all_valid_decisions"] == pytest.approx(1 / 3)


def test_realized_evidence_window_is_five_and_exposure_follows_audit():
    markets, rows = {}, []
    previous = None
    for t in range(22):
        regime = "news" if (t // 10) % 2 == 0 else "momentum"
        feats = {"news": .2 + t * .1, "momentum": -.3 + (t % 3) * .2,
                 "spread": .01 + t * .0001, "volume": 1 + (t % 2) * .1,
                 "orderflow": t * .03, "sentiment": -t * .02}
        markets[t] = {"tick": t, "regime": regime, "features": feats, "return": .01 * np.sin(t) + t * .001}
        audited = t in (4, 19, 20)
        event = {"verdict": "faithful", "fine": 0.} if audited else None
        rows.append(row(tick=t, regime=regime, reasons=(regime,), audited=audited, audit_event=event, feedback=previous))
        if audited:
            pairs = [(markets[k]["features"], markets[k]["return"]) for k in range(max(0, t - 4), t + 1)]
            previous = build_evidence_feedback(True, pairs, 0.)["text"]
    loaded = {}
    add(loaded, "evidence", 200, rows, markets=markets)
    k = hik_evidence(loaded)
    b = k["models"][MODEL]["windows"]["primary"]
    assert b["actual_table_n_distribution"] == {5: 1}
    assert b["generated_actual_crossing"]["numerator"] == 1
    assert b["n_prompts_with_evidence"] == 2
    assert k["verified_persisted_feedback_instances"] == 17
    # Changing a persisted text is detected, not silently reconstructed away.
    rows[-1]["feedback"] += "incorrect"
    with pytest.raises(AssertionError):
        hik_evidence(loaded)
