"""Offline tests of post hoc computations and frozen-data invariants."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.v2.analyze import DATA_ROOT, PRIMARY, REQUIRED_MODELS, _prepare, load_runs
from src.v2.posthoc_analyses import (
    PKEYS, actual_label_values, citation_analyses, describe, diagnostics,
    dgp_analyses, evidence_analyses, label_analyses, minimum_detectable_effect,
    opposite, paired_custom, paired_t_power, pairs_component, planned_labels,
    power_analyses, perturbation_analyses, perturbation_cell, regime_analyses,
    required_n, return_components, specificity_value, summarize_tables,
    table_correlations, tercile_cutpoints, variance_decomposition,
    verify_exogenous,
)
from src.v2.exploratory_analyses import reproduce_primary

MODEL = REQUIRED_MODELS[0]


def row(tick=20, agent=0, regime="news", reasons=("news",), flips=None, **kw):
    raw = dict(tick=tick, agent=agent, regime=regime, action="buy", size=2,
               parse_ok=True, reasons=list(reasons), cf_sampled=True,
               cf_flips={"news": True, "momentum": False} if flips is None else flips,
               revealed_label=None, feedback=None, audited=False, audit_selected=False,
               audit_event=None)
    raw.update(kw)
    return _prepare(raw)


def run(rows, condition="naive", seed=200, markets=None):
    return {"source": {"model": MODEL, "condition": condition, "seed": seed},
            "rows": rows, "coordinates": {(r["tick"], r["agent"]): r for r in rows},
            "markets": {} if markets is None else markets}


def test_describe_weights_seeds_not_rows_and_preserves_undefined():
    z = describe({200: [0., 0., None], 201: [1.], 202: []}, lambda x: x)
    assert z["mean"] == .5
    assert z["pooled"] == {"mean": 1 / 3, "sum": 1., "n": 3}
    assert z["n_by_seed"] == {"200": 2, "201": 1, "202": 0}


def test_pairing_matches_coordinates_and_undefined_then_weights_seeds():
    a = {200: [row(), row(agent=1)], 201: [row(reasons=())], 202: [row()]}
    b = {200: [row(reasons=()), row(agent=1, reasons=())], 201: [row()], 202: [row(parse_ok=False)]}
    z = paired_custom(a, b, lambda x, y: (x["_values"].get("citation_true"), y["_values"].get("citation_true")))
    assert z["mean_delta"] == 0  # seed differences +1 and -1
    assert z["n_common_decisions"] == 3
    assert z["n_seed_pairs"] == 2
    assert z["excluded_seeds"] == [202]
    selected = paired_custom(a, b, lambda x, y: (1., 0.), lambda x, y, s: s == 201)
    assert selected["n_common_decisions"] == 1
    assert selected["seed_pairs"][0]["coordinates"] == ["20:0"]


@pytest.mark.parametrize("mode,expected", [("ordinary", .5), ("exclusive", 0.), ("at_most_one", None)])
def test_exclusive_precision_distinguishes_zero_credit_from_exclusion(mode, expected):
    r = row(reasons=("news", "momentum"))
    assert specificity_value(r, "precision", mode) == expected
    if expected is not None:
        components = [specificity_value(r, f"precision_{f}_component", mode) for f in ("true", "false")]
        assert sum(components) == expected


def test_exclusive_citation_csd_preserves_sensitivity_and_empty_precision():
    dual = row(reasons=("news", "momentum"))
    assert specificity_value(dual, "gap_true", "exclusive") == -1
    assert specificity_value(dual, "citation_false", "exclusive") == 0
    assert specificity_value(row(reasons=()), "precision", "exclusive") is None
    assert specificity_value(row(reasons=("news", "volume")), "precision", "at_most_one") == 1
    assert specificity_value(row(parse_ok=False), "gap_true", "exclusive") is None
    with pytest.raises(ValueError):
        specificity_value(row(), "unknown", "ordinary")


def test_planned_label_is_preaction_and_uses_previous_draw_not_current_draw():
    seed = 200
    labels = planned_labels(seed)
    mask = np.random.default_rng(seed * 1000 + 7).random((40, 6)) < .3
    for a in range(6):
        previous = None
        for t in range(40):
            p = labels[t, a]
            expected_regime = "news" if (t // 10) % 2 == 0 else "momentum"
            assert p["regime"] == expected_regime
            assert p["label"] == previous
            assert p["placebo"] == (opposite(previous) if previous else None)
            if mask[t, a]:
                previous = expected_regime


def test_exogeneity_verifier_reconstructs_draw_and_flags_logging_bug():
    labels = planned_labels(200)
    rows = [row(tick=t, agent=a, regime=p["regime"], revealed_label=p["label"],
                audited=p["draw"], audit_selected=not p["draw"])
            for (t, a), p in labels.items()]
    loaded = {"x": run(rows, "label")}
    _, verified = verify_exogenous(loaded)
    assert verified["verified_label_exposures_all_ticks"] == 240
    assert verified["audit_selected_logging_mismatches_by_model"][MODEL] == 240
    rows[-1]["revealed_label"] = opposite(rows[-1]["revealed_label"])
    with pytest.raises(AssertionError):
        verify_exogenous(loaded)


def test_actual_label_csd_uses_stale_label_for_both_packages():
    a = row(revealed_label="momentum", reasons=("momentum",), flips={"news": True, "momentum": False})
    b = row(reasons=("news",), flips={"news": False, "momentum": True})
    assert actual_label_values(a, b) == (1., -1.)
    assert actual_label_values(row(), b) == (None, None)


def test_component_summary_uses_identical_seed_weights_and_support():
    z = pairs_component([{"seed": 200, "citation_delta": .2, "n_common_coordinates": 1},
                         {"seed": 201, "citation_delta": -.1, "n_common_coordinates": 100}], "citation_delta")
    assert z["mean_delta"] == pytest.approx(.05)
    assert z["n_common_decisions"] == 101


def test_return_components_use_requested_orders_and_ignore_invalid_bases():
    rows = [row(), row(agent=1, action="sell", size=1), row(agent=2, parse_ok=False, size=10)]
    market = {20: {"features": {"news": 2.}, "regime": "news", "return": .047}}
    c = return_components(run(rows, markets=market))[20]
    assert c["fundamental"] == .04
    assert c["impact"] == pytest.approx(.001)
    assert c["eta"] == pytest.approx(.006)
    assert c["without_impact"] == pytest.approx(.046)


def test_table_correlations_recompute_each_target_and_mark_undefined():
    markets, components = {}, {}
    for t, x in enumerate([-2., -1., 0., 1., 2.]):
        feats = dict(news=x, momentum=-x, spread=1., volume=1., sentiment=x / 2, orderflow=-x / 2)
        markets[t] = {"features": feats}
        components[t] = {"fundamental": .02 * x, "without_impact": -.02 * x}
    z = table_correlations(markets, components, list(range(5)), "fundamental", "news")
    assert z["true_abs_r"] == pytest.approx(1.)
    assert z["opposite_abs_r"] == pytest.approx(1.)
    assert z["true_largest_abs_r_all_six"] is True  # ties accepted
    assert z["true_positive_sign"] is True
    assert z["correlations"]["volume"] is None
    z = table_correlations(markets, components, list(range(5)), "without_impact", "news")
    assert z["true_positive_sign"] is False
    z = table_correlations(markets, components, [0], "fundamental", "news")
    assert z["true_abs_r"] is None
    assert z["true_largest_abs_r_all_six"] is None


def test_table_summaries_weight_seed_means_and_drop_unavailable_correlations():
    def entry(seed, v):
        return dict(seed=seed, true_abs_r=v, opposite_abs_r=v,
                    true_largest_abs_r_all_six=v, true_largest_abs_r_two_probes=v,
                    true_positive_sign=v, mixed_regimes=False)
    z = summarize_tables([entry(200, 0.), entry(200, None), entry(201, 1.)])
    assert z["n_tables"] == 3
    assert z["metrics"]["true_abs_r"]["mean"] == .5
    assert z["metrics"]["true_abs_r"]["pooled"]["n"] == 2
    assert z["metrics"]["mixed_regimes"]["pooled"]["n"] == 3


def test_terciles_boundary_ties_proxy_reversal_and_zeros():
    assert tercile_cutpoints([0., 1., 2., 3.]) == pytest.approx([1., 2.])
    assert perturbation_cell(1., 2., [1., 2.]) == ("low", "agree", "disagree")
    assert perturbation_cell(-2., 2., [1., 2.]) == ("middle", "disagree", "agree")
    assert perturbation_cell(3., 0., [1., 2.]) == ("high", "zero", "zero")
    assert perturbation_cell(0., 2., [1., 2.]) == ("low", "zero", "zero")


@pytest.mark.parametrize("n,alpha,expected", [(20, .05, .6604), (10, .05, .9960),
                                               (20, .0125, .8146), (10, .0125, 1.2843)])
def test_mde_reproduces_registered_noncentral_t_benchmarks(n, alpha, expected):
    d = minimum_detectable_effect(.1, n, alpha)
    assert d["standardized"] == pytest.approx(expected, abs=.00006)
    assert d["raw"] == pytest.approx(d["standardized"] * .1)
    assert paired_t_power(d["standardized"], n, alpha) == pytest.approx(.8)


def test_required_n_is_minimal_integer_and_uses_effect_magnitude():
    for alpha in (.05, .0125):
        n = required_n(-.05, .1, alpha)
        assert n == required_n(.05, .1, alpha)
        assert paired_t_power(.5, n, alpha) >= .8
        assert paired_t_power(.5, n - 1, alpha) < .8
    assert required_n(0., .1, .05) is None
    assert minimum_detectable_effect(0., 10, .05)["raw"] is None
    with pytest.raises(ValueError):
        paired_t_power(1., 1, .05)


def test_power_table_uses_actual_sd_and_reference_effect_not_local_effect():
    z = power_analyses({"P": {"paired_sd": .1, "n_seed_pairs": 10, "mean_delta": .8}},
                      {"P": {"mean_delta": -.05}})["P"]
    assert z["target_DeepSeek_effect"] == -.05
    assert z["by_alpha"]["0.05"]["n_for_DeepSeek_effect"] == required_n(.05, .1, .05)


def test_variance_ratios_and_covariance_shares_handle_correlated_components():
    rows = [dict(fundamental=x, impact=x, eta=0., realized=2 * x) for x in (-1., 0., 1.)]
    z = variance_decomposition(rows)
    assert z["components"]["fundamental"]["variance_ratio"] == pytest.approx(.25)
    assert z["components"]["impact"]["covariance_allocated_share"] == pytest.approx(.5)
    assert z["cross_covariance_share"] == pytest.approx(.5)
    assert sum(v["covariance_allocated_share"] for v in z["components"].values()) == pytest.approx(1.)
    rows[0]["realized"] += .1
    with pytest.raises(AssertionError):
        variance_decomposition(rows)


@pytest.fixture(scope="module")
def existing():
    manifest, loaded = load_runs(DATA_ROOT, "confirm", REQUIRED_MODELS)
    assert len(loaded) == 200 and all(m["status"] == "included" for m in manifest)
    frozen = json.loads((DATA_ROOT / "analysis/confirm/results.json").read_text())
    return loaded, frozen


def test_all_frozen_primaries_and_regime_holm_reproduce(existing):
    loaded, frozen = existing
    for model in REQUIRED_MODELS:
        primary = reproduce_primary(loaded, frozen, model)
        z = regime_analyses(loaded, model, primary)
        for regime in ("news", "momentum"):
            assert len(z["by_regime"][regime]) == 4
            for p in z["by_regime"][regime].values():
                assert p["holm_p"] >= p["paired_t_p"]
                assert p["n_seed_pairs"] == (20 if model == MODEL else 10)


def test_disk_label_subgroup_and_shared_adoption_coordinates(existing):
    loaded, _ = existing
    planned, verified = verify_exogenous(loaded)
    assert verified["verified_label_exposures_all_ticks"] == 19200
    assert len(verified["skipped_scheduled_audits"]) == 1
    for model in REQUIRED_MODELS:
        z = label_analyses(loaded, model, planned)
        for c in ("label", "placebo"):
            adoption = z[c]["matched_label_adoption"]
            assert len({v["pooled"]["n"] for v in adoption.values()}) == 1
            assert len({json.dumps(v["n_by_seed"], sort_keys=True) for v in adoption.values()}) == 1
            assert sum(z[c]["assigned_subgroup_counts_by_seed"]["unexposed"].values()) == 0
        true_label = sum(z["label"]["assigned_subgroup_counts_by_seed"]["true"].values())
        stale_false = sum(z["placebo"]["assigned_subgroup_counts_by_seed"]["stale"].values())
        assert true_label == stale_false


def test_disk_specificity_ordinary_scores_equal_primary_and_components_sum(existing):
    loaded, frozen = existing
    z = citation_analyses(loaded, MODEL)
    for name, primary_name in (("P1", PKEYS["P1"]), ("P3_CSD", PKEYS["P3"]), ("P4_CSD", PKEYS["P4"])):
        for field in ("mean_delta", "bootstrap_ci_95", "paired_t_p"):
            assert z["contrasts"]["ordinary"][name][field] == frozen["models"][MODEL]["primary_contrasts"][primary_name][field]
    for mode in ("ordinary", "exclusive", "at_most_one"):
        contrasts = z["contrasts"][mode]
        total = contrasts["P1"]["mean_delta"]
        assert total == pytest.approx(contrasts["P1_true_component"]["mean_delta"] + contrasts["P1_false_component"]["mean_delta"])
        assert contrasts["P1"]["n_common_decisions"] == contrasts["P1_true_component"]["n_common_decisions"]


def test_disk_perturbation_strata_partition_reasks_and_fixed_exogenous_cutpoints(existing):
    loaded, _ = existing
    z = perturbation_analyses(loaded, MODEL)
    cells = z["cells"]
    counts = sum(c["pooled"]["n"] for c in cells if c["proxy_agreement_after"] == "all")
    assert counts == z["verified_feature_reasks"] == 12070
    assert all(d["n_naive_seed_ticks"] == 400 for d in z["cutpoints"].values())
    for c in cells:
        if c["tercile"] == "all":
            continue
        if c["proxy_agreement_after"] == "all":
            split = [v for v in cells if all(v[k] == c[k] for k in ("condition", "feature", "regime", "tercile"))
                     and v["proxy_agreement_after"] != "all"]
            assert sum(v["pooled"]["n"] for v in split) == c["pooled"]["n"]


def test_disk_dgp_variance_noise_and_false_label_component_support(existing):
    loaded, frozen = existing
    planned, _ = verify_exogenous(loaded)
    primary = reproduce_primary(loaded, frozen, MODEL)
    z = dgp_analyses(loaded, MODEL)
    c = z["primary"]["pooled_packages"]
    assert c["components"]["eta"]["population_sd"] == pytest.approx(.00494297960373873)
    assert z["unique_seed_tick_volume_all_ticks"]["n"] == 800
    assert z["unique_seed_tick_volume_all_ticks"]["sum"] == 0
    assert sum(v["covariance_allocated_share"] for v in c["components"].values()) == pytest.approx(1.)
    diag = diagnostics(loaded, MODEL, planned, primary)
    for regimes in diag["false_label_decomposition"].values():
        for state in regimes.values():
            assert state["gap_false"]["mean_delta"] == pytest.approx(state["citation_false"]["mean_delta"] - state["dependence_false"]["mean_delta"])
            assert len({s["n_common_decisions"] for s in state.values()}) == 1
    for csd in diag["CSD_headroom"].values():
        assert csd["maximum_citation_increase"]["mean"] + csd["naive_citation_on_CSD_support"]["mean"] == pytest.approx(1.)


def test_disk_evidence_distinguishes_generation_delivery_and_prompt_exposure(existing):
    loaded, _ = existing
    z = evidence_analyses(loaded)
    assert z["verified_persisted_feedback_instances"] == 8721
    d = z["models"][MODEL]["summaries"]["primary"]
    assert d["generated"]["realized"]["n_tables"] == 718
    assert d["exposed_prompts"]["realized"]["n_tables"] == 2400
    generated = z["models"][MODEL]["every_generated_table"]
    assert any(t["audit_tick"] == 39 for t in generated)
    assert all(t["n_observations"] == 5 for t in generated if t["audit_tick"] >= 20)
    assert d["generated"]["fundamental"]["metrics"]["mixed_regimes"]["pooled"]["sum"] == 294
    assert d["exposed_prompts"]["realized"]["metrics"]["mixed_regimes"]["pooled"]["sum"] == 996
    for target in ("realized", "without_impact", "fundamental"):
        assert d["delivered_unique"][target]["n_tables"] > 0
