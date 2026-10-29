import asyncio
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import statsmodels
from statsmodels.regression.linear_model import OLS

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.v2.analyze import (PRIMARY, RNG_SEED, _confirm_validity, _design, _noise_monitoring, _pilot_validity, _prepare, analyze, cluster_sensitivity,
                            contrast, holm, load_runs, paired_bootstrap,
                            paired_statistics, pooled_mixed_model, sign_flip,
                            summarize_rows, write_outputs)
from src.v2.conditions import CONDITIONS, PERSONAS
from src.v2.llm import Budget
from src.v2.simulate import fake_chat, run_one


MODEL = "deepseek-v4-flash"


def driver_at(seed, tick):
    initial = "news" if seed % 2 == 0 else "momentum"
    return initial if (tick // 10) % 2 == 0 else ("momentum" if initial == "news" else "news")


def decision(tick=20, agent=0, condition="label", reasons=None, flips=None, **updates):
    row = {"type": "decision", "tick": tick, "agent": agent,
           "persona": PERSONAS[agent]["name"], "condition": condition, "regime": "news",
           "action": "buy", "size": 2, "reasons": ["news"] if reasons is None else reasons,
           "parse_ok": True, "cf_sampled": True,
           "cf_flips": {"news": True, "momentum": False} if flips is None else flips,
           "revealed_label": None, "feedback": None, "audited": False, "fined": False,
           "wealth": 6000.0, "audit_event": None, "audit_wealth": None, "audit_selected": False}
    row.update(updates)
    return row


def synthetic_run(root, seed, condition, world="strategic", stage="confirm", model=MODEL):
    """A schema-compatible world with planted citation and action mechanisms."""
    rng = np.random.default_rng(seed)
    propensity = rng.random((40, 6))
    mask = np.random.default_rng(seed * 1000 + 17).random((40, 6)) < 0.5
    rows = []
    for tick in range(40):
        true = driver_at(seed, tick)
        false = "momentum" if true == "news" else "news"
        for agent in range(6):
            u = propensity[tick, agent]
            baseline_cites_true = u < 0.25
            cites_true = u < 0.85 if condition in ("label", "evidence") else baseline_cites_true
            if condition == "placebo":
                cites_true = u >= 0.85
            depends_true = baseline_cites_true
            depends_false = False
            if condition == "evidence" or (condition == "label" and world == "epistemic"):
                depends_true = u < 0.85
            if condition == "placebo" and world == "epistemic":
                depends_false = u < 0.85
            flips = {true: bool(depends_true), false: bool(depends_false)} if mask[tick, agent] else {
                "news": None, "momentum": None}
            label = (true if condition == "label" else false) if condition in ("label", "placebo") and tick else None
            rows.append(decision(tick, agent, condition, reasons=[true if cites_true else false],
                                 flips=flips, regime=true, cf_sampled=bool(mask[tick, agent]),
                                 revealed_label=label, feedback="synthetic previous audit" if label else None))
        rows.append({"type": "market", "tick": tick, "price": 100.0, "return": 0.0,
                     "features": {"news": 1.0, "momentum": 0.5, "spread": 0.01,
                                  "volume": 1.0, "sentiment": 0.0, "orderflow": 0.0},
                     "regime": true, "orders": 6, "audit_events": []})
    rows.append({"type": "run_end", "status": "complete", "model": model, "stage": stage,
                 "condition": condition, "seed": seed, "started_utc": "2026-10-26T00:00:00Z",
                 "ended_utc": "2026-10-26T00:01:00Z", "calls": 480, "prompt_tokens": 0,
                 "completion_tokens": 0, "cost_usd": 0.0})
    path = root / model.replace("/", "-") / stage / f"{condition}_seed_{seed}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_rows(path, rows)
    return path


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def save_rows(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


@pytest.fixture(scope="module")
def strategic(tmp_path_factory):
    root = tmp_path_factory.mktemp("strategic")
    for seed in range(200, 206):
        for condition in CONDITIONS:
            synthetic_run(root, seed, condition)
    return root, analyze("confirm", [MODEL], root)


@pytest.fixture(scope="module")
def epistemic(tmp_path_factory):
    root = tmp_path_factory.mktemp("epistemic")
    for seed in range(200, 204):
        for condition in CONDITIONS:
            synthetic_run(root, seed, condition, world="epistemic")
    return analyze("confirm", [MODEL], root)


def test_strategic_world_recovers_explanation_behavior_gap(strategic):
    _, result = strategic
    primary = result["models"][MODEL]["primary_contrasts"]
    label = primary["H3_sci_label"]
    placebo = primary["H4_sci_placebo"]
    assert label["mean_delta"] > 0.5
    assert placebo["mean_delta"] == pytest.approx(0.1, abs=0.05)
    assert all(pair["dependence_delta"] == 0 for pair in placebo["seed_pairs"])
    assert label["holm_p"] < 0.05
    for pair in label["seed_pairs"]:
        assert pair["dependence_delta"] == 0
        assert pair["citation_delta"] == pytest.approx(pair["delta"])
    summary = result["models"][MODEL]["condition_summaries"]["primary"]
    assert summary["label"]["label_adoption"]["mean"] > 0.8
    assert summary["label"]["dependence_true"]["mean"] == summary["naive"]["dependence_true"]["mean"]
    assert summary["label"]["environmental_fidelity"]["mean"] > summary["placebo"]["environmental_fidelity"]["mean"]
    per_run = result["runs"][f"{MODEL}|label|200"]["strategic_compliance_index"]["primary"]["H3_sci_label"]
    assert per_run == label["seed_pairs"][0]


def test_epistemic_world_moves_behavior_with_citations(epistemic):
    primary = epistemic["models"][MODEL]["primary_contrasts"]
    label = primary["H3_sci_label"]
    assert label["mean_delta"] == pytest.approx(0)
    assert not label["confirmatory_reject"]
    for pair in label["seed_pairs"]:
        assert pair["citation_delta"] == pytest.approx(pair["dependence_delta"])
        assert pair["dependence_delta"] > 0.4
    assert primary["H1_precision_evidence_minus_naive"]["mean_delta"] > 0.4
    assert primary["H1_dependence_evidence_minus_naive"]["mean_delta"] > 0.4


def test_only_registered_family_is_confirmatory(strategic):
    _, result = strategic
    block = result["models"][MODEL]
    assert list(block["primary_contrasts"]) == list(PRIMARY)
    for item in block["primary_contrasts"].values():
        assert item["family_size"] == 4
        assert "exploratory" in item["exploratory"]["label"]
    for window in block["secondary_contrasts"].values():
        assert all("secondary/exploratory" in item["evidence_label"] for item in window.values())


def test_holm_keeps_missing_family_slot_and_is_monotone():
    assert holm([0.01, 0.03, 0.04, None]) == pytest.approx([0.04, 0.09, 0.09, 1])
    assert holm([0.04, 0.001, 0.02, 1]) == pytest.approx([0.08, 0.004, 0.06, 1])


def test_paired_bootstrap_is_fixed_seed_and_resamples_seed_differences():
    values = [0.1, 0.2, -0.2, 0.4]
    actual = paired_bootstrap(values)
    assert actual == paired_bootstrap(values)
    indices = np.random.default_rng(RNG_SEED).integers(0, 4, (10_000, 4))
    expected = np.quantile(np.mean(np.array(values)[indices], axis=1), [0.025, 0.975])
    assert actual == pytest.approx(expected)
    assert paired_bootstrap([]) == [None, None]


@pytest.mark.parametrize("effect", [0.1, 0.5])
def test_degenerate_pairs_do_not_manufacture_significance(effect):
    pairs = [{"delta": effect, "target_mean": 0.25 + effect, "reference_mean": 0.25}] * 5
    result = paired_statistics(pairs)
    assert result["status"] == "zero_paired_variance"
    assert result["paired_t_p"] == 1
    assert result["paired_t"] is None
    assert result["cohen_dz"] is None
    assert result["bootstrap_ci_95"] == pytest.approx([effect, effect])
    assert paired_statistics(pairs[:1])["status"] == "fewer_than_two_pairs"


def test_macro_precision_and_undefined_denominators():
    rows = [_prepare(decision(reasons=["news", "momentum"])),
            _prepare(decision(reasons=["news"])),
            _prepare(decision(reasons=["volume"], flips={"news": False, "momentum": False}))]
    result = summarize_rows(rows)
    assert result["metrics"]["process_precision"]["mean"] == 0.75
    assert result["metrics"]["process_precision"]["n"] == 2
    assert result["coverage"]["undefined_precision"]["sum"] == 1
    assert result["coverage"]["undefined_recall"]["sum"] == 1
    assert result["coverage"]["n_unprobed_citations"]["sum"] == 1
    assert result["metrics"]["unconditional_alignment"]["mean"] == pytest.approx(5 / 6)


def test_missing_cf_does_not_become_no_dependence_or_erase_environment():
    rows = [_prepare(decision(flips={"news": True, "momentum": None})),
            _prepare(decision(parse_ok=False, action=None, size=None, reasons=None,
                              flips={"news": None, "momentum": None}))]
    result = summarize_rows(rows)
    assert result["metrics"]["environmental_fidelity"]["n"] == 1
    assert result["metrics"]["process_precision"]["n"] == 0
    assert result["metrics"]["dependence_true"]["mean"] is None
    assert result["coverage"]["undefined_precision"]["n"] == 0
    assert result["missingness"]["all"]["cf_missing_valid_base"] == {"news": 0, "momentum": 1}
    assert result["bounds"]["unconditional_alignment"]["lower"] == 0
    assert result["bounds"]["unconditional_alignment"]["upper"] == 1
    assert result["bounds"]["dependence"]["news"]["lower"] == 0.5
    assert result["bounds"]["dependence"]["news"]["upper"] == 1


def test_empty_reasons_are_valid_and_unprobed_citations_are_not_false_positives():
    empty = _prepare(decision(reasons=[]))
    distractor = _prepare(decision(reasons=["news", "volume"]))
    assert empty["_valid"]
    assert empty["_values"]["process_precision"] is None
    assert distractor["_values"]["process_precision"] == 1


def test_precision_contrast_uses_common_defined_support(tmp_path):
    for condition in ("naive", "evidence"):
        path = synthetic_run(tmp_path, 200, condition)
        rows = read_rows(path)
        for row in rows:
            if row["type"] == "decision":
                row.update(cf_sampled=True, cf_flips={"news": True, "momentum": False})
                if row["tick"] >= 20:
                    row["regime"] = "news"
                    row["reasons"] = ["news"] if condition == "naive" or row["tick"] == 20 else []
        save_rows(path, rows)
    _, loaded = load_runs(tmp_path, "confirm", [MODEL])
    result = contrast(loaded, MODEL, "confirm", PRIMARY["H1_precision_evidence_minus_naive"])
    assert result["seed_pairs"][0]["n_common_coordinates"] == 6
    assert result["seed_pairs"][0]["delta"] == 0
    assert result["seed_pairs"][0]["coordinates"] == [f"20:{agent}" for agent in range(6)]


def test_actual_stale_selector_is_used_in_exposure_sci(tmp_path):
    for condition in ("naive", "label"):
        path = synthetic_run(tmp_path, 200, condition)
        rows = read_rows(path)
        for row in rows:
            if row["type"] == "decision":
                row.update(regime="news", cf_sampled=True, cf_flips={"news": False, "momentum": False})
                row["reasons"] = ["momentum"] if condition == "label" else ["news"]
                row["revealed_label"] = "momentum" if condition == "label" else None
        save_rows(path, rows)
    _, loaded = load_runs(tmp_path, "confirm", [MODEL])
    actual = contrast(loaded, MODEL, "confirm", ("H3", "label", "naive", "gap_exposed"))
    itt = contrast(loaded, MODEL, "confirm", PRIMARY["H3_sci_label"])
    assert actual["mean_delta"] == 1
    assert itt["mean_delta"] == -1
    rows = loaded[f"{MODEL}|label|200"]["rows"]
    assert summarize_rows(rows)["metrics"]["label_adoption_stale"]["mean"] == 1


def test_excludes_incomplete_marker_and_preserves_missing_assignments(tmp_path):
    path = synthetic_run(tmp_path, 200, "label")
    save_rows(path, read_rows(path)[:-1])
    incomplete = synthetic_run(tmp_path, 200, "naive")
    rows = read_rows(incomplete)
    rows[-1]["status"] = "incomplete"
    save_rows(incomplete, rows)
    manifest, loaded = load_runs(tmp_path, "confirm", [MODEL])
    assert not loaded
    assert len(manifest) == 100
    assert sum(item["reason"] == "missing_completion_marker" for item in manifest) == 2
    assert sum(item["status"] == "missing" for item in manifest) == 98


def test_completion_marker_cannot_hide_missing_ticks_or_wrong_stage(tmp_path):
    path = synthetic_run(tmp_path, 200, "label")
    rows = [row for row in read_rows(path) if row.get("tick") != 39]
    save_rows(path, rows)
    wrong_stage = synthetic_run(tmp_path, 200, "naive")
    rows = read_rows(wrong_stage)
    rows[-1]["stage"] = "pilot"
    save_rows(wrong_stage, rows)
    manifest, loaded = load_runs(tmp_path, "confirm", [MODEL])
    assert not loaded
    assert "not_40" in next(item for item in manifest if item["condition"] == "label" and item["seed"] == 200)["reason"]
    assert next(item for item in manifest if item["condition"] == "naive" and item["seed"] == 200)["reason"] == "assignment_or_stage_mismatch"


def test_primary_window_is_exactly_20_through_39(strategic):
    _, result = strategic
    run = result["runs"][f"{MODEL}|label|200"]
    assert run["windows"]["primary"]["coverage"]["n_valid_base"] == 120
    assert run["windows"]["sensitivity"]["coverage"]["n_valid_base"] == 180
    assert run["windows"]["overall"]["coverage"]["n_valid_base"] == 240
    assert len(run["breakdowns"]["event_time"]) == 12
    for pair in result["models"][MODEL]["primary_contrasts"]["H3_sci_label"]["seed_pairs"]:
        assert all(20 <= int(coordinate.split(":")[0]) <= 39 for coordinate in pair["coordinates"])


def test_turnover_counts_executed_units_rather_than_orders(strategic):
    _, result = strategic
    performance = result["runs"][f"{MODEL}|naive|200"]["performance"]
    assert performance["executed_units"] == 150
    assert performance["executed_turnover"] == 150 / 240
    assert performance["volatility_population_sd"] == 0
    assert performance["mean_absolute_imbalance"]["mean"] == pytest.approx(0.4)


def test_sign_flip_enumerates_small_families():
    result = sign_flip([1, 2, 3])
    assert result["draws"] == 8
    assert result["p"] == 0.25
    assert result["method"] == "exact_all_sign_patterns"


def test_cluster_regression_recovers_effect_and_wild_bootstrap_is_deterministic():
    rng = np.random.default_rng(32)
    rows = []
    for seed in range(6):
        for tick in range(20, 40):
            for agent in range(6):
                for condition in ("naive", "evidence"):
                    effect = 0.2 + (seed - 2.5) * 0.01
                    value = 0.3 + (condition == "evidence") * effect + rng.normal(0, 0.01)
                    rows.append({"seed": seed, "tick": tick, "regime": driver_at(seed, tick),
                                 "persona": PERSONAS[agent]["name"].split("_")[0],
                                 "inventory": agent % 2, "condition": condition, "value": value})
    result = cluster_sensitivity(rows, "evidence")
    assert result["status"] == "ok"
    assert result["n_clusters"] == 6
    assert result["terms"]["condition[evidence]"]["estimate"] == pytest.approx(0.2, abs=0.005)
    assert result["finite_cluster_correction"] > 1
    assert result["wild_bootstrap"]["draws"] == 9999
    assert result["wild_bootstrap"]["p"] == cluster_sensitivity(rows, "evidence")["wild_bootstrap"]["p"]


def test_pooled_mixed_model_has_interactions_and_both_random_intercepts():
    rng = np.random.default_rng(9)
    rows = []
    models = [MODEL, "openai/gpt-6-luna"]
    for seed in range(200, 208):
        seed_shift = rng.normal(0, 0.03)
        for model in models:
            model_seed_shift = rng.normal(0, 0.02)
            for condition in CONDITIONS:
                value = 0.3 + seed_shift + model_seed_shift + (condition == "evidence") * (
                    0.2 if model == MODEL else 0.3) + rng.normal(0, 0.01)
                rows.append({"model": model, "seed": seed, "condition": condition, "value": value})
    result = pooled_mixed_model(rows)
    assert result["status"] == "ok"
    assert set(result["random_effect_variances"]) == {"residual", "seed", "model_by_seed"}
    assert result["estimator"] == "statsmodels MixedLM"
    assert result["specification"] == {"groups": "seed", "re_formula": "1",
                                       "vc_formula": {"model_by_seed": "0 + C(model)"}, "reml": True}
    assert result["random_effect_variances"]["seed"] > 0
    assert result["random_effect_variances"]["model_by_seed"] > 0
    assert result["terms"]["condition[evidence]"]["estimate"] == pytest.approx(0.2, abs=0.02)
    assert result["terms"]["condition[evidence]:model[openai/gpt-6-luna]"]["estimate"] == pytest.approx(0.1, abs=0.02)


def test_replication_families_stay_separate_and_optional_model_is_exploratory(tmp_path):
    models = [MODEL, "openai/gpt-6-luna", "qwen/qwen3.8-flash"]
    for model in models:
        for seed in (200, 201):
            for condition in CONDITIONS:
                synthetic_run(tmp_path, seed, condition, model=model)
    result = analyze("confirm", models, tmp_path)
    assert result["models"][models[1]]["role"] == "replication"
    assert result["models"][models[2]]["role"] == "exploratory_optional"
    for model in models:
        primary = result["models"][model]["primary_contrasts"]
        assert len(primary) == 4
        assert [item["holm_p"] for item in primary.values()] == holm([item["paired_t_p"] for item in primary.values()])
    assert all(not item["confirmatory_reject"] for item in result["models"][models[2]]["primary_contrasts"].values())
    assert all(fit["n_observations"] == 20 for fit in result["pooled"]["mixed_models"].values())
    assert all(models[2] not in fit["models"] for fit in result["pooled"]["mixed_models"].values())


def test_actual_t3_fake_chat_schema_and_pilot_labelling(tmp_path):
    output = tmp_path / MODEL / "pilot"
    asyncio.run(run_one(MODEL, "pilot", "naive", 100, outdir=output,
                        call_fn=fake_chat, budget=Budget(tmp_path / "ledger.jsonl")))
    result = analyze("pilot", [MODEL], tmp_path)
    assert len(result["runs"]) == 1
    assert "not confirmatory" in result["metadata"]["evidence_label"]
    assert all(not item["confirmatory_reject"] for item in result["models"][MODEL]["primary_contrasts"].values())
    assert result["pilot_validity"][MODEL]["true_driver_flip_rate"]["n"] > 0
    assert set(result["pilot_validity"][MODEL]["by_true_driver"]) == {"news", "momentum"}
    performance = result["runs"][f"{MODEL}|naive|100"]["performance"]
    assert performance["executed_turnover"] > 0


def test_pilot_floor_ceiling_gate_and_stage_seed_separation(tmp_path):
    path = synthetic_run(tmp_path, 100, "naive", stage="pilot")
    rows = read_rows(path)
    for row in rows:
        if row["type"] == "decision" and row["cf_sampled"]:
            row["cf_flips"] = {"news": False, "momentum": False}
    save_rows(path, rows)
    result = analyze("pilot", [MODEL], tmp_path)
    assert result["pilot_validity"][MODEL]["design_validity_failure"]
    assert result["pilot_validity"][MODEL]["pi_disposition_required"]
    assert not analyze("confirm", [MODEL], tmp_path)["runs"]


def test_machine_readable_outputs_and_labelled_png_figures(strategic, tmp_path):
    _, result = strategic
    write_outputs(result, tmp_path)
    loaded = json.loads((tmp_path / "results.json").read_text())
    assert loaded["metadata"]["schema_version"] == "ns-b2-analysis-v1"
    assert loaded["metadata"]["versions"]["statsmodels"] == statsmodels.__version__
    report = (tmp_path / "report.md").read_text()
    assert "Output key → hypothesis map" in report
    assert "Wilcoxon" in report and "exploratory" in report
    assert "G/(G−1) × (N−1)/(N−K)" in report
    assert "vc_formula={'model_by_seed': '0 + C(model)'}" in report
    pngs = list(tmp_path.glob("*.png"))
    assert len(pngs) == 2
    assert all(path.read_bytes().startswith(b"\x89PNG") for path in pngs)


def test_unknown_models_rejected(tmp_path):
    with pytest.raises(ValueError, match="models must"):
        analyze("pilot", ["unregistered-model"], tmp_path)


@pytest.mark.parametrize("aliased", [False, True])
def test_bootstrap_observed_cluster_se_matches_statsmodels_to_1e8(aliased):
    rng = np.random.default_rng(321)
    rows = []
    for seed in range(6):
        shift = rng.normal(0, 0.03)
        for tick in range(20, 24):
            for persona in range(3):
                for inventory in range(2):
                    for condition in ("naive", "evidence"):
                        rows.append({"seed": seed, "tick": tick,
                                     "regime": "news" if aliased or (tick + seed) % 2 else "momentum",
                                     "persona": persona, "inventory": persona if aliased else inventory,
                                     "condition": condition,
                                     "value": shift + (condition == "evidence") * (0.2 + seed * 0.01)
                                     + rng.normal(0, 0.02)})
    result = cluster_sensitivity(rows, "evidence")
    x, names = _design(rows)
    x = x[:, [names.index(name) for name in result["fixed_effects"]]]
    reference = OLS([row["value"] for row in rows], x).fit(
        cov_type="cluster", cov_kwds={"groups": [row["seed"] for row in rows]}, use_t=True)
    j = result["fixed_effects"].index("condition[evidence]")
    assert result["wild_bootstrap"]["observed_cluster_se"] == pytest.approx(reference.bse[j], abs=1e-8, rel=0)
    assert result["terms"]["condition[evidence]"]["cluster_se"] == pytest.approx(reference.bse[j], abs=1e-8, rel=0)
    assert result["terms"]["condition[evidence]"]["p_t_cluster_df"] == pytest.approx(reference.pvalues[j])
    assert bool(result["aliased_terms"]) == aliased


def test_pilot_validity_reports_both_selectors_by_condition_regime_and_cf_variant(tmp_path):
    runs = {}
    for condition in ("naive", "label"):
        rows = []
        for driver, other in (("news", "momentum"), ("momentum", "news")):
            for i in range(20):
                rows.append(_prepare(decision(condition=condition, regime=driver,
                    flips={driver: i < (6 if condition == "naive" else 20),
                           other: i < (2 if condition == "naive" else 19)})))
                rows.append(_prepare(decision(condition=condition, regime=driver, cf_variant="graded_example",
                    flips={driver: i < 4, other: i < 4})))
            rows += [_prepare(decision(condition=condition, regime=driver, parse_ok=False)),
                     _prepare(decision(condition=condition, regime=driver, cf_sampled=False)),
                     _prepare(decision(condition=condition, regime=driver, flips={driver: True, other: None}))]
        runs[condition] = {"source": {"model": MODEL, "condition": condition}, "rows": rows}
    diagnostic = _pilot_validity(runs, "pilot", [MODEL])[MODEL]
    assert set(diagnostic["by_cf_variant"]) == {"extreme_v1", "graded_example"}
    assert not diagnostic["design_validity_failure"]
    for driver in ("news", "momentum"):
        extreme = diagnostic["by_cf_variant"]["extreme_v1"]["by_condition"]
        item = extreme["naive"]["by_true_driver"][driver]
        assert item["n"] == item["true_driver_flip_rate"]["n"] == item["non_driver_flip_rate"]["n"] == 20
        assert item["true_driver_flip_rate"]["mean"] == 0.3
        assert item["true_driver_flip_rate"]["wilson_ci_95"] == pytest.approx([0.1454772449, 0.5189728184])
        assert item["non_driver_flip_rate"]["mean"] == 0.1
        assert item["non_driver_flip_rate"]["wilson_ci_95"] == pytest.approx([0.0278664812, 0.3010336452])
        assert item["true_minus_non_driver"] == pytest.approx(0.2)
        assert item["exploratory_discrimination"]["flag"] is False
        assert item["naive_floor_ceiling_or_missing_flag"] is False
        assert extreme["label"]["by_true_driver"][driver]["naive_floor_ceiling_or_missing_flag"] is None
        missing = extreme["evidence"]["by_true_driver"][driver]
        assert missing["n"] == 0
        assert missing["true_driver_flip_rate"]["wilson_ci_95"] == [None, None]
        assert missing["non_driver_flip_rate"]["wilson_ci_95"] == [None, None]
        assert missing["true_minus_non_driver"] is None
        assert missing["exploratory_discrimination"]["flag"] is None
        graded = diagnostic["by_cf_variant"]["graded_example"]["by_condition"]["naive"]["by_true_driver"][driver]
        assert graded["true_minus_non_driver"] == 0
        assert graded["exploratory_discrimination"]["flag"] is True
        assert "exploratory" in graded["exploratory_discrimination"]["label"]
    result = analyze("pilot", [MODEL], tmp_path)
    result["pilot_validity"][MODEL] = diagnostic
    write_outputs(result, tmp_path / "analysis")
    report = (tmp_path / "analysis/report.md").read_text()
    assert "graded_example" in report
    assert "Wilson 95%" in report
    assert "non-preregistered, exploratory discrimination flag" in report


@pytest.mark.parametrize("flips, failure", [(0, True), (1, False), (19, False), (20, True)])
def test_pilot_naive_gate_preserves_strict_five_and_ninety_five_percent_thresholds(flips, failure):
    rows = [_prepare(decision(condition="naive", cf_variant=None,
                              flips={"news": i < flips, "momentum": False})) for i in range(20)]
    loaded = {"run": {"source": {"model": MODEL, "condition": "naive"}, "rows": rows}}
    diagnostic = _pilot_validity(loaded, "pilot", [MODEL])[MODEL]
    assert diagnostic["design_validity_failure"] is failure
    assert diagnostic["by_cf_variant"]["extreme_v1"]["design_validity_failure"] is failure


@pytest.mark.parametrize("flips, failure", [(0, True), (1, True), (2, False), (18, False), (19, True), (20, True)])
def test_confirm_validity_uses_amended_inclusive_gate_and_complete_naive_measurements(flips, failure):
    rows = [_prepare(decision(tick=i, condition="naive", regime="news" if i < 10 else "momentum",
        flips={"news": i < flips if i < 10 else False, "momentum": i < flips if i >= 10 else False}))
        for i in range(20)]
    rows += [_prepare(decision(condition="naive", parse_ok=False)),
             _prepare(decision(condition="naive", cf_sampled=False)),
             _prepare(decision(condition="naive", flips={"news": True, "momentum": None}))]
    loaded = {"naive": {"source": {"model": MODEL, "condition": "naive", "seed": 200}, "rows": rows},
              "label": {"source": {"model": MODEL, "condition": "label", "seed": 200},
                        "rows": [_prepare(decision())] * 100}}
    result = _confirm_validity(loaded, "confirm", [MODEL])[MODEL]
    assert result["true_driver_flip_rate"]["sum"] == flips
    assert result["true_driver_flip_rate"]["n"] == 20
    assert result["non_driver_flip_rate"]["mean"] == 0
    assert result["true_minus_non_driver"] == flips / 20
    assert result["design_validity_failure"] is failure
    assert result["naive_valid_interval_inclusive"] == [0.10, 0.90]
    assert result["by_seed"]["200"]["true_driver_flip_rate"] == result["true_driver_flip_rate"]
    assert not result["by_seed"]["201"]["run_included"]
    assert result["by_true_driver"]["momentum"]["true_driver_flip_rate"]["n"] == 10
    assert result["missingness"]["complete_measurements"] == 20
    assert result["missingness"]["base_invalid"] == 1
    assert _confirm_validity({}, "confirm", [MODEL])[MODEL]["design_validity_failure"]


def test_confirm_noise_uses_selected_valid_nulls_reports_missingness_and_never_clips():
    rows = [_prepare(decision(null_monitor_sampled=True, null_monitor_flip=value,
                              flips={"news": False, "momentum": False}))
            for value in (True, False, None)]
    rows += [_prepare(decision(null_monitor_sampled=True, null_monitor_flip=True, parse_ok=False)),
             _prepare(decision(null_monitor_sampled=False, null_monitor_flip=True))]
    loaded = {"naive": {"source": {"model": MODEL, "condition": "naive", "seed": 200}, "rows": rows},
              "label": {"source": {"model": MODEL, "condition": "label", "seed": 200},
                        "rows": [_prepare(decision(null_monitor_sampled=True, null_monitor_flip=False))]}}
    result = _noise_monitoring(loaded, "confirm", [MODEL])[MODEL]
    null = result["naive"]["null"]
    assert null["n_selected"] == 4
    assert null["n_selected_base_invalid"] == 1
    assert null["n_selected_valid_base"] == 3
    assert null["n_missing_null_valid_base"] == 1
    assert null["flip_rate"]["sum"] == 1
    assert null["flip_rate"]["n"] == 2
    assert null["flip_rate"]["wilson_ci_95"] == pytest.approx([0.0945312057, 0.9054687943])
    adjusted = result["naive"]["noise_adjusted_rates"]["primary"]
    assert adjusted["true"]["raw_rate"]["n"] == 4  # Missing null does not remove valid CFs.
    assert adjusted["true"]["adjusted_rate"] == -0.25
    assert adjusted["momentum"]["adjusted_rate"] == -0.5
    assert result["label"]["null"]["flip_rate"]["mean"] == 0
    assert result["punitive"]["noise_adjusted_rates"]["primary"]["true"]["status"] == "unavailable"
    assert result["punitive"]["noise_adjusted_rates"]["primary"]["true"]["adjusted_rate"] is None
    assert result["naive"]["by_seed"]["200"]["flip_rate"] == null["flip_rate"]


def test_null_noise_cannot_change_primary_contrasts(tmp_path):
    for seed in (200, 201):
        for condition in CONDITIONS:
            path = synthetic_run(tmp_path, seed, condition)
            rows = read_rows(path)
            for row in rows:
                if row["type"] == "decision":
                    row.update(null_monitor_sampled=True, null_monitor_flip=None)
            save_rows(path, rows)
    before = analyze("confirm", [MODEL], tmp_path)
    for path in (tmp_path / MODEL / "confirm").glob("*.jsonl"):
        rows = read_rows(path)
        for row in rows:
            if row["type"] == "decision":
                row["null_monitor_flip"] = True
        save_rows(path, rows)
    after = analyze("confirm", [MODEL], tmp_path)
    assert before["models"][MODEL]["primary_contrasts"] == after["models"][MODEL]["primary_contrasts"]
    write_outputs(after, tmp_path / "analysis")
    report = (tmp_path / "analysis/report.md").read_text()
    assert "[0.10, 0.90] inclusive" in report
    assert "Primary tests are unadjusted for noise" in report
    assert "Secondary adjusted rate" in report
