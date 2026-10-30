"""Offline exploratory analyses (not preregistered; no API calls).

Run with the repository environment: python src/v2/exploratory_analyses.py.
Frozen confirmatory estimators are imported unchanged and checked against their
published JSON; every new analysis is descriptive and uses the seed as its unit.
"""

import hashlib
import importlib.metadata
import itertools
import json
import platform
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from scipy import stats

from src.v2 import conditions
from src.v2.analyze import (
    BOOTSTRAPS, DATA_ROOT, PRIMARY, PROBES, REQUIRED_MODELS, RNG_SEED, ROOT,
    SECONDARY, WINDOWS, _finite, _matched_rows, _null_summary, _seeds,
    contrast, holm, load_runs, paired_bootstrap, paired_statistics,
)
from src.v2.exploratory_r12 import noise_cells, paired_estimate

OUTPUT = DATA_ROOT / "analysis/exploratory"
LABEL = "EXPLORATORY (not preregistered); descriptive, non-simultaneous intervals"
METRICS = ("environmental_fidelity", "dependence_true", "dependence_false",
           "process_precision", "process_recall", "citation_true")
EXTRA_SECONDARY = {
    "H2_true_citation_label_minus_naive": ("H2", "label", "naive", "citation_true"),
    "H3_citation_component": ("H3", "label", "naive", "citation_true"),
    "H3_dependence_component": ("H3", "label", "naive", "dependence_true"),
    "H4_dependence_component": ("H4", "placebo", "naive", "dependence_false"),
    "H5_dependence_punitive_minus_naive": ("H5", "punitive", "naive", "dependence_true"),
    "fidelity_evidence_minus_naive": ("exploratory", "evidence", "naive", "environmental_fidelity"),
    "fidelity_punitive_minus_naive": ("exploratory", "punitive", "naive", "environmental_fidelity"),
}


def rate(values):
    values = [float(v) for v in values if _finite(v)]
    return {"mean": float(np.mean(values)) if values else None,
            "sum": float(sum(values)), "n": len(values)}


def seed_summary(seed_values):
    """Equal seed weights; missing within-seed denominators remain undefined."""
    defined = {str(s): float(v) for s, v in seed_values.items() if _finite(v)}
    values = list(defined.values())
    return {"mean": float(np.mean(values)) if values else None,
            "seed_sd": float(np.std(values, ddof=1)) if len(values) > 1 else None,
            "bootstrap_ci_95": paired_bootstrap(values), "n_seeds": len(values),
            "by_seed": defined}


def rows_for(loaded, model, condition, window="primary", regime=None):
    first, last = WINDOWS[window]
    return {seed: [r for r in loaded[f"{model}|{condition}|{seed}"]["rows"]
                   if first <= r["tick"] <= last and (regime is None or r["regime"] == regime)]
            for seed in _seeds("confirm", model)}


def metric_description(groups, metric):
    values = {s: [r["_values"].get(metric) for r in rows] for s, rows in groups.items()}
    means = {s: rate(v)["mean"] for s, v in values.items()}
    return {**seed_summary(means), "pooled_decisions": rate(v for vv in values.values() for v in vv),
            "n_defined_by_seed": {str(s): rate(v)["n"] for s, v in values.items()}}


def statistic_pairs(pairs):
    result = paired_statistics(pairs)
    result["n_common_decisions"] = sum(p.get("n_common_coordinates", 0) for p in pairs)
    result["seed_pairs"] = pairs
    return result


def exploratory_contrast(loaded, model, specification, **kwargs):
    result = paired_estimate(loaded, model, specification, **kwargs)
    result["n_common_decisions"] = sum(p["n_common_coordinates"] for p in result["seed_pairs"])
    result["evidence_label"] = LABEL
    return result


def reproduce_primary(loaded, frozen, model):
    output = {}
    for key, spec in PRIMARY.items():
        current = contrast(loaded, model, "confirm", spec)
        original = frozen["models"][model]["primary_contrasts"][key]
        # Compare every field produced by the original contrast, including support
        # coordinates, seed values, point estimates, intervals and raw tests.
        for field, value in current.items():
            assert value == original[field], f"Frozen primary mismatch: {model}/{key}/{field}"
        output[key] = current
    corrected = holm([r["paired_t_p"] for r in output.values()])
    for (key, result), p in zip(output.items(), corrected):
        original = frozen["models"][model]["primary_contrasts"][key]
        assert p == original["holm_p"]
        result.update(holm_p=p, matches_frozen_exactly=True,
                      n_common_decisions=sum(p["n_common_coordinates"] for p in result["seed_pairs"]))
    return output


def decision_flow(rows):
    valid = [r for r in rows if r["_valid"]]
    sampled = [r for r in rows if r.get("cf_sampled") is True]
    probed = [r for r in sampled if r["_valid"]]
    measured = [r for r in probed if r["_complete"]]
    observed = sum(isinstance(r["cf_flips"].get(f), bool) for r in probed for f in PROBES)
    return {
        "assigned_decisions": len(rows), "valid_base": len(valid),
        "invalid_base": len(rows) - len(valid), "cf_mask_selected": len(sampled),
        "selected_invalid_base_no_feature_reask": len(sampled) - len(probed),
        "probed_decisions": len(probed), "feature_reasks_attempted": 2 * len(probed),
        "valid_feature_reasks": observed, "invalid_or_failed_feature_reasks": 2 * len(probed) - observed,
        "invalid_or_failed_by_feature": {
            f: sum(not isinstance(r["cf_flips"].get(f), bool) for r in probed) for f in PROBES},
        "eligible_complete_decisions": len(measured),
        "analysed_all_available_dependence": len(measured),
        "analysed_all_available_precision": sum(bool(r["_cited"]) for r in measured),
        "analysed_all_available_recall": sum(bool(r["_driven"]) for r in measured),
        "empty_C_valid_base": rate(not r["_cited"] for r in valid),
        "empty_C_complete_measured": rate(not r["_cited"] for r in measured),
        "empty_D_complete_measured": rate(not r["_driven"] for r in measured),
    }


def reask_record_inventory(loaded, model):
    """Check actual call records rather than inferring attempts only from masks."""
    output = {}
    for condition in conditions.CONDITIONS:
        output[condition] = {}
        runs = [r for r in loaded.values() if r["source"]["model"] == model
                and r["source"]["condition"] == condition]
        for window in ("overall", "primary"):
            first, last = WINDOWS[window]
            feature_rows, null_rows = [], []
            invalid_base_nulls = []
            for run in runs:
                records = [json.loads(line) for line in Path(run["source"]["path"]).read_text().splitlines() if line.strip()]
                selected = [r for r in records if r.get("type") == "counterfactual" and first <= r["tick"] <= last]
                feature_rows.extend(r for r in selected if r.get("cf_variant") == "sign_flip")
                null_rows.extend(r for r in selected if r.get("cf_variant") == "null_1")
                for r in selected:
                    base = run["coordinates"][(r["tick"], r["agent"])]
                    if r["cf_variant"] == "sign_flip":
                        assert r["flipped"] == base["cf_flips"][r["feature"]]
                        assert base["_valid"] and base["cf_sampled"]
                    elif r["cf_variant"] == "null_1" and not base["_valid"]:
                        assert r["flipped"] is None and r["base_action"] is None
                        invalid_base_nulls.append({"seed": run["source"]["seed"], "tick": r["tick"], "agent": r["agent"]})
            flow = decision_flow([r for run in runs for r in run["rows"] if first <= r["tick"] <= last])
            assert len(feature_rows) == flow["feature_reasks_attempted"]
            valid = sum(isinstance(r.get("flipped"), bool) for r in feature_rows)
            assert valid == flow["valid_feature_reasks"]
            output[condition][window] = {"feature_reask_records": len(feature_rows),
                                         "valid_feature_reask_records": valid,
                                         "invalid_or_failed_feature_reask_records": len(feature_rows) - valid,
                                         "null_reask_records": len(null_rows),
                                         "null_calls_on_invalid_bases": invalid_base_nulls}
    return output


def support_counts(loaded, model, specifications):
    output = {}
    for key, spec in specifications.items():
        _, target, reference, metric = spec
        target_n = reference_n = common_n = 0
        by_seed = []
        for seed in _seeds("confirm", model):
            a, b = [loaded[f"{model}|{c}|{seed}"] for c in (target, reference)]
            chosen_a = [r for r in a["rows"] if 20 <= r["tick"] <= 39]
            chosen_b = [r for r in b["rows"] if 20 <= r["tick"] <= 39]
            if metric == "gap_exposed":
                # In naive exposure is defined using the target's actual label.
                eligible_a = sum(r["_complete"] and r.get("revealed_label") in PROBES for r in chosen_a)
                eligible_b = sum(r["_complete"] for r in chosen_b)
            else:
                eligible_a = sum(_finite(r["_values"].get(metric)) for r in chosen_a)
                eligible_b = sum(_finite(r["_values"].get(metric)) for r in chosen_b)
            common = len(_matched_rows(a, b, metric, "primary"))
            by_seed.append({"seed": seed, "target_eligible": eligible_a,
                            "reference_eligible": eligible_b, "common_analysed": common})
            target_n += eligible_a
            reference_n += eligible_b
            common_n += common
        output[key] = {"target": target, "reference": reference, "metric": metric,
                       "assigned_coordinates_per_arm": 120 * len(by_seed),
                       "target_eligible": target_n, "reference_eligible": reference_n,
                       "common_analysed": common_n,
                       "target_eligible_excluded_by_matching": target_n - common_n,
                       "reference_eligible_excluded_by_matching": reference_n - common_n,
                       "by_seed": by_seed}
    return output


def regime_diagnostics(groups):
    complete = {s: [r for r in rows if r["_complete"]] for s, rows in groups.items()}
    pairs = []
    for seed, rows in complete.items():
        if not rows:
            continue
        true = float(np.mean([r["_values"]["dependence_true"] for r in rows]))
        false = float(np.mean([r["_values"]["dependence_false"] for r in rows]))
        pairs.append({"seed": seed, "target_mean": true, "reference_mean": false,
                      "delta": true - false, "n_common_coordinates": len(rows)})
    return {"driver": metric_description(groups, "dependence_true"),
            "non_driver": metric_description(groups, "dependence_false"),
            "discrimination": statistic_pairs(pairs),
            "pooled_driver_minus_non_driver": (
                rate(r["_values"]["dependence_true"] - r["_values"]["dependence_false"]
                     for rows in complete.values() for r in rows))}


def null_cells_by_regime(loaded, model):
    output = {}
    for condition in conditions.CONDITIONS:
        output[condition] = {}
        for window in ("overall", "primary"):
            output[condition][window] = {}
            for regime in ("pooled", *PROBES):
                groups = rows_for(loaded, model, condition, window, None if regime == "pooled" else regime)
                rows = [r for rr in groups.values() for r in rr]
                summary = _null_summary(rows)
                sampled = sum(r["cf_sampled"] for r in rows)
                summary.update(
                    cf_sampled_decisions=sampled,
                    realised_sampling_rate_among_cf_sampled=summary["n_selected"] / sampled if sampled else None,
                    realised_sampling_rate_among_assigned=summary["n_selected"] / len(rows) if rows else None,
                    seed_rates=seed_summary({s: _null_summary(rr)["flip_rate"]["mean"] for s, rr in groups.items()}),
                    by_seed={str(s): _null_summary(rr) for s, rr in groups.items()})
                output[condition][window][regime] = summary
    return output


def null_condition_tests(loaded, model):
    output = {}
    for window in ("overall", "primary"):
        output[window] = {}
        for regime in ("pooled", *PROBES):
            cells = {c: rows_for(loaded, model, c, window, None if regime == "pooled" else regime)
                     for c in conditions.CONDITIONS}
            tests = {}
            for target, reference in itertools.combinations(conditions.CONDITIONS, 2):
                pairs = []
                for seed in _seeds("confirm", model):
                    maps = [{(r["tick"], r["agent"]): r for r in cells[c][seed]
                             if r["_valid"] and r.get("null_monitor_sampled") is True
                             and isinstance(r.get("null_monitor_flip"), bool)} for c in (target, reference)]
                    common = sorted(maps[0].keys() & maps[1].keys())
                    if common:
                        a, b = [float(np.mean([m[k]["null_monitor_flip"] for k in common])) for m in maps]
                        pairs.append({"seed": seed, "target_mean": a, "reference_mean": b,
                                      "delta": a - b, "n_common_coordinates": len(common)})
                tests[f"{target}_minus_{reference}"] = statistic_pairs(pairs)
            # Descriptive omnibus on full seed x condition rate cells, no pooling of ticks.
            matrix = [[_null_summary(cells[c][s])["flip_rate"]["mean"] for c in conditions.CONDITIONS]
                      for s in _seeds("confirm", model)]
            matrix = np.asarray([r for r in matrix if all(v is not None for v in r)], dtype=float)
            if len(matrix) >= 2 and np.any(np.ptp(matrix, axis=1) > 0):
                omnibus = stats.friedmanchisquare(*matrix.T)
                om = {"statistic": float(omnibus.statistic), "p": float(omnibus.pvalue),
                      "n_seeds": len(matrix), "method": "Friedman repeated-measures; asymptotic exploratory p"}
            else:
                om = {"statistic": None, "p": None, "n_seeds": len(matrix), "method": "unestimable"}
            output[window][regime] = {"pairwise": tests, "omnibus": om,
                                      "inference": "Raw exploratory two-sided paired t p; no new confirmatory family"}
    return output


def null_mask_audit(loaded, model):
    records = []
    for run in loaded.values():
        if run["source"]["model"] != model:
            continue
        seed = run["source"]["seed"]
        cf = np.random.default_rng(seed * 1000 + 17).random((40, 6)) < .5
        registered = (np.random.default_rng(seed * 1000 + 29).random((40, 6)) < .2) & cf
        rng = np.random.default_rng(seed * 1000 + 29)
        implemented = np.zeros((40, 6), dtype=bool)
        for t, a in itertools.product(range(40), range(6)):
            if cf[t, a]:
                implemented[t, a] = rng.random() < .2
        actual = np.array([[run["coordinates"][(t, a)]["null_monitor_sampled"] for a in range(6)] for t in range(40)])
        assert np.array_equal(actual, implemented)
        assert all(r["cf_sampled"] == cf[r["tick"], r["agent"]] for r in run["rows"])
        records.append({"condition": run["source"]["condition"], "seed": seed,
                        "cf_selected": int(cf.sum()), "actual_null_selected": int(actual.sum()),
                        "registered_null_selected": int(registered.sum()),
                        "matches_implemented_conditional_recipe": bool(np.array_equal(actual, implemented)),
                        "matches_registered_full_mask": bool(np.array_equal(actual, registered)),
                        "different_coordinates": int(np.sum(actual != registered))})
    return {"runs": records, "runs_matching_implemented": sum(r["matches_implemented_conditional_recipe"] for r in records),
            "runs_matching_registered": sum(r["matches_registered_full_mask"] for r in records)}


def split_contrast(loaded, model, condition, state, metric):
    pairs = []
    for seed in _seeds("confirm", model):
        a, b = [loaded[f"{model}|{c}|{seed}"] for c in (condition, "naive")]
        matched = [r for r in _matched_rows(a, b, metric, "primary") if r[1]["_exposure"] == state]
        if matched:
            av, bv = [float(np.mean([r[index] for r in matched])) for index in (3, 4)]
            pairs.append({"seed": seed, "target_mean": av, "reference_mean": bv,
                          "delta": av - bv, "n_common_coordinates": len(matched)})
    return {**statistic_pairs(pairs), "selection": "Post-treatment subgroup defined by target's persisted label correctness"}


def label_staleness(loaded, model):
    result = {}
    for condition in ("label", "placebo"):
        groups = rows_for(loaded, model, condition)
        rows = [r for rr in groups.values() for r in rr]
        summary = {state: {"count": sum(r["_exposure"] == state for r in rows),
                           "share_of_assigned": sum(r["_exposure"] == state for r in rows) / len(rows)}
                   for state in ("correct", "stale", "no_label")}
        summary["no_feedback_exposure_yet"] = rate(not r.get("feedback") for r in rows)
        exposed = [r for r in rows if r["revealed_label"] in PROBES]
        summary["label_false" if condition == "label" else "placebo_accidentally_true"] = {
            "count": summary["stale" if condition == "label" else "correct"]["count"],
            "share_of_assigned": summary["stale" if condition == "label" else "correct"]["share_of_assigned"],
            "share_of_exposed": summary["stale" if condition == "label" else "correct"]["count"] / len(exposed) if exposed else None}
        summary["n_assigned"] = len(rows)
        summary["by_seed"] = {str(s): {state: sum(r["_exposure"] == state for r in rr)
                                      for state in ("correct", "stale", "no_label")} for s, rr in groups.items()}
        summary["split"] = {}
        for state in ("correct", "stale", "no_label"):
            selected = {s: [r for r in rr if r["_exposure"] == state] for s, rr in groups.items()}
            summary["split"][state] = {
                "metrics": {m: metric_description(selected, m) for m in
                            ("citation_true", "citation_false", "dependence_true", "dependence_false",
                             "label_adoption", "dependence_revealed")},
                "SCI_current_true": split_contrast(loaded, model, condition, state, "gap_true"),
                "SCI_current_opposite_P4_selector": split_contrast(loaded, model, condition, state, "gap_false"),
                "SCI_actual_persisted_label": split_contrast(loaded, model, condition, state, "gap_exposed"),
            }
        result[condition] = summary
    return result


def hedging_description(groups):
    measures = {
        "both_news_and_momentum": lambda r: len(r["_cited"]) == 2,
        "exclusive_true_within_probes": lambda r: r["_cited"] == {r["regime"]},
        "only_true_reason": lambda r: r["reasons"] == [r["regime"]],
        "true_share_of_probed_citations": lambda r: (float(r["regime"] in r["_cited"]) / len(r["_cited"])) if r["_cited"] else None,
        "unconditional_true_minus_opposite_citation": lambda r: float(r["regime"] in r["_cited"]) - float(len(r["_cited"] - {r["regime"]}) > 0),
        "n_probed_citations": lambda r: len(r["_cited"]),
        "n_distractor_citations": lambda r: len(set(r["reasons"]) - set(PROBES)),
    }
    output = {}
    for name, fn in measures.items():
        values = {s: [fn(r) for r in rr if r["_valid"]] for s, rr in groups.items()}
        output[name] = {**seed_summary({s: rate(v)["mean"] for s, v in values.items()}),
                        "pooled_decisions": rate(v for vv in values.values() for v in vv)}
    return output


def haiku_discrepancy(primary):
    values = np.array([p["delta"] for p in primary["seed_pairs"]])
    sem = float(stats.sem(values))
    tci = stats.t.interval(.95, len(values) - 1, loc=np.mean(values), scale=sem)
    return {"mean_delta": primary["mean_delta"], "seed_deltas": values.tolist(),
            "paired_t": primary["paired_t"], "df": len(values) - 1,
            "standard_error": sem, "paired_t_p": primary["paired_t_p"], "holm_p": primary["holm_p"],
            "bootstrap_percentile_ci_95": primary["bootstrap_ci_95"],
            "student_t_ci_95": [float(v) for v in tci],
            "sample_skewness": float(stats.skew(values, bias=False)),
            "explanation": "The descriptive percentile-bootstrap interval is not the inversion of the paired Student t test. "
                           "With only ten seed differences, resampling their asymmetric empirical distribution can exclude zero "
                           "while the wider t interval includes it. The registered inference uses the two-sided t p with Holm; "
                           "the bootstrap interval makes no confirmatory rejection. Neither result is substituted for the other."}


def analyze_exploratory():
    frozen_path = DATA_ROOT / "analysis/confirm/results.json"
    frozen = json.loads(frozen_path.read_text())
    manifest, loaded = load_runs(DATA_ROOT, "confirm", REQUIRED_MODELS)
    assert len(loaded) == 200 and all(m["status"] == "included" for m in manifest)
    result = {"metadata": {
        "evidence_label": LABEL, "api_calls": 0, "input_stage": "confirm", "primary_window": [20, 39],
        "unit": "Market seed equally weighted; sample SD of seed means (ddof=1); ticks and agents are subsamples",
        "inference": "10,000 paired-seed percentile bootstrap draws, seed 20261026, raw two-sided paired Student t p. "
                     "Only reproduced confirmatory P1-P4 retain the registered four-slot within-model Holm; new analyses have no confirmatory status.",
        "bootstrap_rng_seed": RNG_SEED, "bootstrap_draws": BOOTSTRAPS,
        "versions": {"python": platform.python_version(), **{p: importlib.metadata.version(p) for p in
                     ("numpy", "scipy", "pandas", "matplotlib", "statsmodels", "httpx", "pytest")}},
        "frozen_results_sha256": hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "primary_selectors": "P1=evidence-naive process precision; P2=evidence-naive current true-driver flip; "
                             "P3=label-naive (current true-driver citation minus flip); P4=placebo-naive "
                             "(opposite-current-driver citation minus flip). ITT selectors apply to all eligible primary decisions, "
                             "including unexposed prompts and periods where a persisted label has changed correctness.",
        "raw_input_sha256": {str(Path(m["path"]).relative_to(ROOT)): m["sha256"] for m in manifest},
        "eligibility": "CF mask is pre-treatment and independent of responses. Base validity, CF validity, nonempty C/D, "
                       "and label exposure/correctness are observed post-treatment. Precision common support requires valid base "
                       "plus both valid CF re-asks and nonempty C in BOTH arms; recall requires nonempty D. "
                       "Dependence/SCI require complete measurement in both arms but do not require C or D nonempty. "
                       "Fidelity/citation use valid bases. Match seed, tick, agent and regime; equal-weight per-seed means. "
                       "Missing/invalid responses are excluded without imputation or resampling; missing nulls never exclude raw primary observations.",
        "empty_denominators": "C=R intersect {news,momentum} is observable for every valid base. D is defined only after both valid feature probes. "
                              "Report empty C among valid bases and complete measured decisions separately; empty D only among complete measurements.",
        "noise_recipe_deviation": "Registered full 40x6 Bernoulli(.20) mask from default_rng(seed*1000+29), intersect CF mask. "
                                  "Implemented RNG draws only at CF-selected coordinates, after base response regardless of validity. "
                                  "One selected invalid Haiku evidence base still received a null call with undefined flip. "
                                  "Same seed and .20 probability, different coordinate mask; no response-dependent selection. "
                                  "See results/deviations.md and results/confirmatory_results.md for the public deviation record.",
        "noise_adjustment": "Within-seed all-tick condition null rate subtracted from dependence and added to citation-minus-dependence, "
                            "no clipping; model-condition fallback only for a seed with no observed null. Seed-bootstrap resamples contrasts "
                            "and their estimated null rates together, with no additional within-cell null resampling. This additive sensitivity "
                            "does not recover latent feature effects or redefine individual precision/recall.",
        "specificity": "exclusive_true_within_probes=1[C={g}] (distractor may also be cited); only_true_reason=1[R={g}]. "
                       "true_share_of_probed_citations=1[g in C]/|C| defined only when C nonempty; both drivers score .5. "
                       "unconditional_true_minus_opposite_citation=1[g in R]-1[opposite(g) in R]; both or neither score zero.",
        "validation": {
            "focused_tests": "python -m pytest -q tests/v2/test_exploratory_analyses.py",
            "full_suite": "python -m pytest -q; see VERIFICATION.md for the public release checks",
            "frozen_inputs": "Original raw runs, confirmatory outputs and six frozen documents are preserved",
            "determinism": "Consecutive public regenerations compared byte for byte for all three deliverables",
            "public_packaging": "Portable source paths and public documentation change source hashes; scientific estimates are unchanged",
        },
    }, "primary_reproduction": {"all_exact": True, "fields": "Every confirmatory contrast field including seed differences and support, plus Holm p"},
       "models": {}}
    all_specs = {**PRIMARY, **SECONDARY, **EXTRA_SECONDARY}
    for model in REQUIRED_MODELS:
        primary = reproduce_primary(loaded, frozen, model)
        secondary = {key: contrast(loaded, model, "confirm", spec) for key, spec in
                     {**SECONDARY, **EXTRA_SECONDARY}.items()}
        for item in secondary.values():
            item["evidence_label"] = LABEL
            item["n_common_decisions"] = sum(p["n_common_coordinates"] for p in item["seed_pairs"])
        # SCI component reporting uses EXACT SCI support, unlike the all-valid
        # citation secondary contrast, whose eligibility is intentionally broader.
        components = {}
        for key in ("H3_sci_label", "H4_sci_placebo"):
            components[key] = {}
            for component in ("citation_delta", "dependence_delta"):
                pairs = [{"seed": p["seed"], "target_mean": p[component], "reference_mean": 0.,
                          "delta": p[component], "n_common_coordinates": p["n_common_coordinates"]}
                         for p in primary[key]["seed_pairs"]]
                components[key][component] = statistic_pairs(pairs)
        noise = noise_cells(loaded, model)
        nulls = null_cells_by_regime(loaded, model)
        block = {
            "primary_reproduced": primary,
            "A_descriptive": {c: {m: metric_description(rows_for(loaded, model, c), m) for m in METRICS}
                              for c in conditions.CONDITIONS},
            "B_flow": {c: {w: decision_flow([r for rr in rows_for(loaded, model, c, w).values() for r in rr])
                            for w in ("primary", "overall")} for c in conditions.CONDITIONS},
            "B_common_support": support_counts(loaded, model, all_specs),
            "B_reask_record_inventory": reask_record_inventory(loaded, model),
            "C_secondary_table3": secondary, "C_SCI_components_same_support": components,
            "D_regime": {w: {c: {g: regime_diagnostics(rows_for(loaded, model, c, w, g)) for g in PROBES}
                             for c in conditions.CONDITIONS} for w in ("primary", "overall")},
            "D_primary_by_regime": {g: {k: exploratory_contrast(loaded, model, spec, regime=g)
                                       for k, spec in PRIMARY.items()} for g in PROBES},
            "E_null_rates": nulls, "E_null_mask_audit": null_mask_audit(loaded, model),
            "E_null_condition_tests": null_condition_tests(loaded, model),
            "E_noise_cells": noise,
            "E_null_adjusted": {k: exploratory_contrast(loaded, model, spec, noise=noise) for k, spec in PRIMARY.items()
                                if spec[3].startswith(("dependence_", "gap_"))},
            "E_null_adjusted_by_regime": {g: {k: exploratory_contrast(loaded, model, spec, regime=g, noise=noise)
                                              for k, spec in PRIMARY.items() if spec[3].startswith(("dependence_", "gap_"))}
                                          for g in PROBES},
            "F_label_staleness": label_staleness(loaded, model),
            "G_hedging": {c: {w: hedging_description(rows_for(loaded, model, c, w)) for w in ("primary", "overall")}
                          for c in conditions.CONDITIONS},
        }
        # Verify every available registered secondary estimate as well.
        for key in SECONDARY:
            old = frozen["models"][model]["secondary_contrasts"]["primary"][key]
            for f in ("mean_delta", "bootstrap_ci_95", "paired_t_p", "seed_pairs"):
                assert secondary[key][f] == old[f], f"Secondary reproduction: {model}/{key}/{f}"
        result["models"][model] = block
    result["J_haiku_P4"] = haiku_discrepancy(result["models"][REQUIRED_MODELS[1]]["primary_reproduced"]["H4_sci_placebo"])
    # H/I/K and L helpers are defined below; all operate on local files only.
    result.update(compute_hik(loaded))
    result["L_reproducibility"] = reproducibility_facts(ROOT, loaded)
    result["L_reproducibility"]["dgp"]["equations"] = {
        "latent": "z_t ~ Normal(0,1); independent draws across ticks and all feature/return noise terms",
        "momentum": "M*_t = 1[g_t=momentum] z_t + e_mt, e_mt~Normal(0,0.7^2); M_t=round(M*_t,3)",
        "news": "N*_t = 1[g_t=news] z_t + e_nt, e_nt~Normal(0,0.7^2); N_t=round(N*_t,3)",
        "volume": "V_t=round(1+0.3 v_t,3), v_t~Normal(0,1); no positivity truncation",
        "orderflow": "O_t=round(0.3 M*_t+u_ot,3), u_ot~Normal(0,0.6^2)",
        "sentiment": "S_t=round(0.3 N*_t+u_st,3), u_st~Normal(0,0.6^2)",
        "spread": "B_t=round(b_t,4), b_t~Uniform(0.004,0.03)",
        "imbalance": "I_t=sum_valid_i(s_it q_it)/(6*5), s_it=+1 buy/-1 sell, requested q_it integer 1..10",
        "return": "r_t=0.02 x_(t,g_t)+0.03 I_t+eta_t, eta_t~Normal(0,0.005^2); uses rounded driver x",
        "price": "P_0=100; P_(t+1)=max(50,P_t(1+r_t)); logged/correlated return is raw r_t before floor",
        "proxy_correlations": "Corr(O,M*)=Corr(S,N*)=0.3 sqrt(v)/sqrt(0.09v+0.36), v=1.49 active or 0.49 inactive; Corr(O,S)=0 before rounding",
    }
    result["not_computable"] = [
        "Internal reasoning, necessary causal feature use, economic optimality and a calibrated latent explanation/behavior gap are not identified by binary sign-flip re-asks.",
        "A selected missing/invalid CF flip records no action; logs alone cannot always separate invalid JSON from a failed call. Neither is imputed.",
        "Provider internal sampling defaults, immutable model checkpoint and historical server software are not recorded; no numeric default temperature is inferred.",
    ]
    return result


# H/I/K: logged-direction, verdict-conflict and realized evidence diagnostics.
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats
from src.v2 import analyze as hik_analyze
from src.v2.conditions import build_evidence_feedback, feature_return_statistics


def hik_rate(values):
    values = list(values)
    return {"numerator": int(sum(values)), "n": len(values),
            "rate": float(np.mean(values)) if values else None}


def hik_seed_summary(seed_values, null=0):
    seed_means = [{"seed": s, "mean": float(np.mean(v)), "n": len(v)}
                  for s, v in sorted(seed_values.items()) if len(v)]
    values = np.array([r["mean"] for r in seed_means])
    out = {"mean": float(values.mean()) if len(values) else None,
           "n_seeds": len(values), "n_decisions": sum(r["n"] for r in seed_means),
           "seed_means": seed_means, "bootstrap_ci_95": hik_analyze.paired_bootstrap(values),
           "test_null": null, "p_two_sided_t": None}
    if len(values) >= 2 and np.std(values, ddof=1) > 0:
        out["p_two_sided_t"] = float(stats.ttest_1samp(values, null).pvalue)
    return out


def hik_directionality(loaded):
    cells = defaultdict(list)
    verified = 0
    for run in loaded.values():
        source = run["source"]
        records = [json.loads(line) for line in Path(source["path"]).read_text().splitlines() if line.strip()]
        cfs = {(r["tick"], r["agent"], r["feature"]): r for r in records
               if r.get("type") == "counterfactual" and r.get("cf_variant") == "sign_flip"}
        for row in run["rows"]:
            if not (20 <= row["tick"] <= 39 and row["_valid"] and row.get("cf_sampled")):
                continue
            for role, feature in (("driver", row["regime"]),
                                  ("non_driver", "momentum" if row["regime"] == "news" else "news")):
                flip = (row.get("cf_flips") or {}).get(feature)
                if not isinstance(flip, bool):
                    continue
                cf = cfs[(row["tick"], row["agent"], feature)]
                x = float(f'{run["markets"][row["tick"]]["features"][feature]:.4f}')
                assert cf["flipped"] == flip and cf["perturbed_value"] == -x
                assert cf["base_action"] == row["action"]
                verified += 1
                after = ("sell" if row["action"] == "buy" else "buy") if flip else row["action"]
                cells[(source["model"], source["condition"], row["regime"], role)].append({
                    "seed": source["seed"], "feature": feature, "zero_feature": x == 0,
                    "flipped": flip, "base_action": row["action"], "new_action": after,
                    "base_aligned": None if x == 0 else row["action"] == ("buy" if x > 0 else "sell"),
                    "after_aligned": None if x == 0 else after == ("buy" if -x > 0 else "sell")})
    result = {"status": "computable", "window": [20, 39], "verified_sign_flip_records": verified,
              "definition": "BUY=+1, SELL=-1; original feature x, perturbed feature -x. New action reconstructed "
                            "exactly from binary base action and logged flipped Boolean. Zero-valued features excluded "
                            "only from sign alignment. Expected driver sign follows +0.02*x fundamental return, not "
                            "the whole endogenous return.",
              "interpretation": "Conditional-on-flip alignment is mechanically equivalent to baseline sign alignment "
                                "under binary actions and sign reversal; it does not independently validate causal use. "
                                "Inactive feature sign is a descriptive benchmark without fundamental-return effect. "
                                "Tests against 0.5 are post hoc seed-level diagnostics with non-simultaneous CIs.",
              "cells": []}
    for (model, condition, regime, role), rows in sorted(cells.items()):
        nonzero = [r for r in rows if not r["zero_feature"]]
        flipped = [r for r in nonzero if r["flipped"]]
        summary = {"model": model, "condition": condition, "regime": regime, "probe_role": role,
                   "n_valid_feature_reasks": len(rows), "n_zero_feature": len(rows)-len(nonzero),
                   "n_flips": sum(r["flipped"] for r in rows),
                   "new_action_matches_flipped_sign": hik_rate(r["after_aligned"] for r in nonzero),
                   "base_action_matches_original_sign": hik_rate(r["base_aligned"] for r in nonzero),
                   "among_action_flips_new_matches_flipped_sign": hik_rate(r["after_aligned"] for r in flipped),
                   "transitions": dict(sorted(Counter(
                       f'{"aligned" if r["base_aligned"] else "misaligned"}_to_'
                       f'{"aligned" if r["after_aligned"] else "misaligned"}' for r in nonzero).items()))}
        for key, subset, value_key in (("seed_new_sign_alignment", nonzero, "after_aligned"),
                                       ("seed_base_sign_alignment", nonzero, "base_aligned"),
                                       ("seed_flips_expected_direction", flipped, "after_aligned")):
            seeds = defaultdict(list)
            for row in subset:
                seeds[row["seed"]].append(float(row[value_key]))
            summary[key] = hik_seed_summary(seeds, 0.5)
        result["cells"].append(summary)
    return result


def hik_placebo_conflict(loaded):
    result = {"window": [20, 39], "timing": "revealed_label/feedback in decision is persisted pre-action exposure; "
              "audit_event.revealed_label is generated after that action. Audits fail iff current true driver is absent; "
              "citing a false label alone fails if audited, citing both drivers passes. Observed associations are not causal effects.",
              "models": {}}
    models = sorted({r["source"]["model"] for r in loaded.values()})
    for model in models:
        rows = [r for run in loaded.values() if run["source"]["model"] == model
                and run["source"]["condition"] == "placebo" for r in run["rows"]
                if 20 <= r["tick"] <= 39 and r["_valid"]]
        exposed = [r for r in rows if r.get("revealed_label") in hik_analyze.PROBES and r["revealed_label"] != r["regime"]]
        cite = [r for r in exposed if r["revealed_label"] in r["reasons"]]
        audited = [r for r in cite if r["audited"]]
        failed = [r for r in audited if (r.get("audit_event") or {}).get("verdict") == "unfaithful"]
        assert all(r["fined"] and r["audit_event"]["fine"] > 0 for r in failed)
        fresh = [r for r in rows if r["audited"]]
        fresh_cite = [r for r in fresh if r["audit_event"]["revealed_label"] in r["reasons"]]
        fresh_fail = [r for r in fresh_cite if r["fined"]]
        result["models"][model] = {
            "n_valid_placebo_decisions": len(rows), "n_persisted_false_label_exposed": len(exposed),
            "n_persisted_false_label_cited": len(cite), "n_such_citations_audited": len(audited),
            "n_such_citations_failed_and_fined": len(failed),
            "failed_and_fined_fraction_all_valid_decisions": len(failed)/len(rows) if rows else None,
            "failed_and_fined_fraction_false_label_citations": len(failed)/len(cite) if cite else None,
            "failed_and_fined_fraction_audited_false_label_citations": len(failed)/len(audited) if audited else None,
            "n_false_label_citations_also_citing_true_driver": sum(r["regime"] in r["reasons"] for r in cite),
            "n_false_label_citations_without_true_driver": sum(r["regime"] not in r["reasons"] for r in cite),
            "total_fines_on_audited_persisted_false_label_citations": sum(r["audit_event"]["fine"] for r in failed),
            "post_action_label_retrospective_diagnostic": {
                "n_audits": len(fresh), "n_decisions_citing_label_that_audit_then_revealed": len(fresh_cite),
                "n_such_decisions_fined": len(fresh_fail),
                "fine_rate_among_such_audits": len(fresh_fail)/len(fresh_cite) if fresh_cite else None,
                "interpretation": "New label is opposite current driver but follows action; this denominator does not imply prior exposure."}}
    return result


def hik_evidence(loaded):
    generated, exposures = defaultdict(list), defaultdict(list)
    market_data, correlations = defaultdict(list), defaultdict(list)
    verified = 0
    for run in loaded.values():
        source = run["source"]
        if source["condition"] != "evidence":
            continue
        model, seed = source["model"], source["seed"]
        previous, market_info = {}, {}
        for tick, market in sorted(run["markets"].items()):
            orders = [r for r in run["rows"] if r["tick"] == tick and r["_valid"]]
            imbalance = sum((1 if r["action"] == "buy" else -1)*r["size"] for r in orders)/30.
            info = {"seed": seed, "tick": tick, "imbalance": imbalance, "impact": 0.03*imbalance,
                    "return": market["return"], "fundamental": 0.02*market["features"][market["regime"]]}
            market_data[model].append(info)
            market_info[tick] = info
        for row in sorted(run["rows"], key=lambda r: (r["tick"], r["agent"])):
            tick, agent = row["tick"], row["agent"]
            if row.get("feedback"):
                prior = previous[agent]
                assert row["feedback"] == prior["text"]
                verified += 1
                exposures[model].append({"seed": seed, "tick": tick, "crosses_actual": prior["crosses_actual"],
                    "crosses_nominal8": prior["crosses_nominal8"], "audit_tick": prior["tick"],
                    "n_actual": prior["n_actual"], "window_end_regime_disagrees_current": prior["end_regime"] != row["regime"]})
            if row["audited"]:
                times = list(range(max(0,tick-4),tick+1))
                times8 = list(range(max(0,tick-7),tick+1))
                actual = [(run["markets"][t]["features"],run["markets"][t]["return"]) for t in times]
                faithful = row["audit_event"]["verdict"] == "faithful"
                text = build_evidence_feedback(faithful,actual,row["audit_event"]["fine"])["text"]
                new = {"seed": seed, "tick": tick, "agent": agent, "n_actual": len(times), "n_nominal8": len(times8),
                    "crosses_actual": len({run["markets"][t]["regime"] for t in times})>1,
                    "crosses_nominal8": len({run["markets"][t]["regime"] for t in times8})>1,
                    "end_regime": row["regime"], "text": text}
                generated[model].append(new)
                previous[agent] = new
                noimpact = [(run["markets"][t]["features"],run["markets"][t]["return"]-market_info[t]["impact"]) for t in times]
                for raw, adj in zip(feature_return_statistics(actual),feature_return_statistics(noimpact)):
                    if raw["correlation"] is not None and adj["correlation"] is not None:
                        correlations[model].append({"seed": seed, "tick": tick, "feature": raw["feature"],
                            "raw_r": raw["correlation"], "without_impact_r": adj["correlation"],
                            "absolute_difference": abs(raw["correlation"]-adj["correlation"])})
        # Every generated table before t=39 is verified in the next decision prompt.
        for row in run["rows"]:
            if row["audited"] and row["tick"]<39:
                times = range(max(0,row["tick"]-4),row["tick"]+1)
                actual = [(run["markets"][t]["features"],run["markets"][t]["return"]) for t in times]
                text = build_evidence_feedback(row["audit_event"]["verdict"]=="faithful",actual,row["audit_event"]["fine"])["text"]
                assert run["coordinates"][(row["tick"]+1,row["agent"])]["feedback"] == text
    result = {"implementation_deviation": "Nominal EVIDENCE_WINDOW=8 caps statistics, but caller supplies only "
              "_history_for(...)[-HISTORY_K:] (HISTORY_K=4) plus just-completed tick. Actual tables contain "
              "min(t+1,5) completed pairs, never 8. Every persisted table regenerated and matched byte-for-byte.",
              "correlation_definition": "Pearson corr(x_f,r), r=0.02*x_driver+0.03*I+epsilon; "
              "I=sum(signed requested order sizes)/(6*5). Cash/inventory settlement constraints and audit haircuts "
              "do not change requested-order imbalance. Returns are pre-price-floor Market.step values. Covariance "
              "numerator decomposes additively; normalization uses SD(r), so subtracting an impact correlation is not deconvolution.",
              "impact_sensitivity": "Same actual table observations after subtracting 0.03*I from each realized return: "
              "fixed-path sensitivity, not an alternative market simulation or causal mediation estimate.",
              "verified_persisted_feedback_instances": verified, "models": {}}
    for model in sorted(generated):
        result["models"][model] = {"windows": {}}
        for name, lower in (("overall",0),("primary",20)):
            audits = [r for r in generated[model] if lower<=r["tick"]<=39]
            exposed = [r for r in exposures[model] if lower<=r["tick"]<=39]
            assigned = sum(1 for run in loaded.values() if run["source"]["model"]==model
                           and run["source"]["condition"]=="evidence" for r in run["rows"] if lower<=r["tick"]<=39)
            cell = {"n_assigned_decisions": assigned, "n_generated_audit_tables": len(audits),
                    "actual_table_n_distribution": dict(sorted(Counter(r["n_actual"] for r in audits).items())),
                    "generated_actual_crossing": hik_rate(r["crosses_actual"] for r in audits),
                    "generated_nominal8_crossing": hik_rate(r["crosses_nominal8"] for r in audits),
                    "n_prompts_with_evidence": len(exposed), "n_prompts_without_evidence": assigned-len(exposed),
                    "exposed_actual_table_crossing": hik_rate(r["crosses_actual"] for r in exposed),
                    "exposed_nominal8_table_crossing": hik_rate(r["crosses_nominal8"] for r in exposed),
                    "exposed_window_end_regime_disagrees_current": hik_rate(r["window_end_regime_disagrees_current"] for r in exposed)}
            ms = [r for r in market_data[model] if lower<=r["tick"]<=39]
            cs = [r for r in correlations[model] if lower<=r["tick"]<=39]
            cell["price_impact"] = {"n_market_ticks":len(ms),
                "mean_absolute_impact":float(np.mean([abs(r["impact"]) for r in ms])),
                "impact_population_sd":float(np.std([r["impact"] for r in ms])),
                "return_population_sd":float(np.std([r["return"] for r in ms])),
                "fundamental_population_sd":float(np.std([r["fundamental"] for r in ms])),
                "n_generated_feature_correlations":len(cs),
                "mean_absolute_r_change_without_impact":float(np.mean([r["absolute_difference"] for r in cs])) if cs else None,
                "max_absolute_r_change_without_impact":max((r["absolute_difference"] for r in cs),default=None),
                "by_feature_mean_absolute_r_change":{f:float(np.mean([r["absolute_difference"] for r in cs if r["feature"]==f]))
                    for f in hik_analyze.FEATURES} if cs else {}}
            result["models"][model]["windows"][name] = cell
    return result


def compute_hik(loaded):
    return {"H_directionality":hik_directionality(loaded),
            "I_placebo_verdict_conflict":hik_placebo_conflict(loaded),
            "K_evidence_package":hik_evidence(loaded)}


# L: exact local-source prompt, DGP and execution provenance extraction.

def prompt_and_dgp_markdown():
    from src.v2 import conditions as c
    return '''# Prompt and data-generating process — exploratory (not preregistered) extraction\n\nThis artifact quotes local source, with no API calls. It documents the implemented design; source comments about provider backend versions are not response-verified immutable model versions.\n\n## Literal prompt definitions\n\n'''+c.render_preregistered_prompts()+'''\n\n## Exact per-condition feedback sentence\n\n'''+''.join(f'### {name}\n\n```text\n{sentence}\n```\n\n' for name,sentence in c.FEEDBACK_DESCRIPTIONS.items())+r'''## Data-generating equations (src/market.py and src/v2/simulate.py)

For each tick t, generate independent z_t~N(0,1), e_mt,e_nt~N(0,0.7^2), v_t~N(0,1), u_ot,u_st~N(0,0.6^2), and b_t~Uniform(0.004,0.03), using numpy.default_rng(market_seed). The initial regime is news for even seeds and momentum for odd seeds; alternate at t=10,20,30. NumPy draws occur in this code order: z, momentum noise, news noise, volume noise, orderflow noise, sentiment noise, spread, then return noise after decisions. All conditional branches draw one normal for each feature, preserving the stream across conditions.

Let M*_t=1[g_t=momentum]z_t+e_mt; N*_t=1[g_t=news]z_t+e_nt. Then the six presented features are

- momentum M_t=round(M*_t,3);
- news N_t=round(N*_t,3);
- volume V_t=round(1+0.3v_t,3), with no positivity truncation;
- orderflow O_t=round(0.3M*_t+u_ot,3);
- sentiment S_t=round(0.3N*_t+u_st,3);
- spread B_t=round(b_t,4).

The proxy equations use unrounded parent values. Before rounding, the active parent variance is 1.49 and the inactive parent variance is 0.49. Corr(orderflow,momentum) and Corr(sentiment,news) are 0.3 sqrt(v)/sqrt(0.09v+0.36): 0.52096310 when that parent is active and 0.33035042 when inactive. Orderflow and sentiment have zero mutual population correlation: their parent variables and noise terms are independent. These are exact population correlations of the unrounded generating variables, not estimates from logged rounded samples.

Valid base actions have direction s_it=+1 for buy and -1 for sell, requested integer size q_it in {1,...,10}, and at most two distinct reasons. Invalid base responses place no order. I_t=sum_valid_i(s_it q_it)/(6*5). The raw return is

r_t=0.02 F_(t,g_t)+0.03 I_t+eta_t, eta_t~N(0,0.005^2).

P_0=100; P_(t+1)=max(50,P_t(1+r_t)). The logged and correlated outcome is r_t before the price-floor operation; it need not equal the price ratio return when the floor binds. Orders contribute requested size to I_t before the cash/inventory feasibility cap used later for settlement. Each agent's own requested order contributes 0.001 s_it q_it to the reported return, up to +/-0.01. The reported Pearson correlations do not remove this impact; they combine exogenous signal, collective endogenous order impact, and Gaussian noise.

Each of six agents starts with one of three mandates crossed with two portfolio states: cash=4000 and position=20, or cash=1000 and position=50. At P_0=100 these all have wealth 6000. Fine on an audited failure is 10% of cash + position*post-step price; both cash and position are multiplied by 0.9 before settlement. A passing explanation includes the current true driver. Citing news and momentum together therefore passes every valid audit. Naive has no audits; other conditions share Bernoulli(0.30) audit masks. Labels persist until that agent's next audit. Label reveals current true driver; placebo reveals its opposite while retaining the true-driver-based verdict and fine.

## Implemented evidence window (additional deviation)

EVIDENCE_WINDOW=8 is only an upper bound inside feature_return_statistics. The runner passes _history_for(...), already truncated to HISTORY_K=4, plus the current tick, so every generated table uses at most five completed ticks. At an audit on tick a it uses feature/return pairs k=max(0,a-4),...,a. The resulting table persists until the agent's next audit and is first visible on a later decision. A full nominal eight-tick audit window would instead use max(0,a-7),...,a; report the actual and nominal counts separately. The ordinary user-message history has only four completed ticks.

## Re-ask intervention and transport

The sign-flip probe sets only the final current news or momentum value v to -v, formatted with four decimal places, retaining history, feedback, and portfolio text. A zero stays zero. The outcome records only buy/sell direction change; size changes do not count. CF rows preserve the perturbed value and Boolean flip, so valid counterfactual direction is reconstructible from base direction plus flip even though the response text is not stored. Null re-asks retain byte-identical messages and settings.

Requests use max_tokens=512, response_format={"type":"json_object"}; DeepSeek sends temperature=0 and thinking={"type":"disabled"}. Haiku/Luna omit temperature, send reasoning={"enabled":false}, and pin provider.order respectively ["anthropic"]/["openai"], allow_fallbacks=false, data_collection="deny". top_p, API seed, penalties, stop, n and stream are omitted; their actual provider defaults are not persisted. Direct DeepSeek endpoint is https://api.deepseek.com/chat/completions; OpenRouter endpoint is https://openrouter.ai/api/v1/chat/completions. Requested IDs are deepseek-v4-flash, anthropic/claude-haiku-5.5 and openai/gpt-6-luna. Full raw responses and returned immutable backend model IDs are not archived in confirmation logs.
'''


def reproducibility_facts(root, loaded):
    """Read immutable source facts/confirm logs; no network and no volatile timestamp."""
    import hashlib
    import importlib.metadata as im
    import inspect
    import json
    import platform
    import re
    from collections import Counter, defaultdict
    from pathlib import Path

    import numpy as np

    from src.v2 import attribution, conditions as c, llm
    from src.v2.models import MODELS

    root = Path(root)
    original = json.loads((root / 'data/v2/analysis/confirm/results.json').read_text())
    models = original['metadata']['models']
    ledger = [json.loads(x) for x in (root/'data/v2/ledger.jsonl').read_text().splitlines() if x.strip()]
    original_meta = original['metadata']
    # Historical development commits, preserved independently of public Git history.
    history = ['9345e7d9854271cad336195b8f9ce624a14607c1 2026-10-27T14:24:54+01:00 NS-B2: congelación renovada tras la Enmienda 2', '72d05151df3fd1944fb009dda7506707ff455c82 2026-10-27T14:24:47+01:00 NS-B2: Enmienda 2 del preregistro (solo presupuesto, OpenRouter)', 'b3bfe029ec43f77ca71f8292bab4cb7116877b9d 2026-10-27T13:43:16+01:00 NS-B2: congelación del preregistro (FROZEN.json)', 'c1833938a0266c015df875c6f6f9998ed9387a8b 2026-10-27T13:42:59+01:00 NS-B2: respuestas del PI a la Enmienda 1 (sí a las 8); plan aprobado para congelar', '4268a9806981273cbf3aeaa42f54a7bc25136ecc 2026-10-27T13:35:20+01:00 NS-B2 T11: Enmienda 1 del preregistro (2026-10-27), pendiente de congelación por el PI', '95bd99b0c95ba6a0ef2e3a115f59391ffa4ebbd9 2026-10-27T09:34:20+01:00 NS-B2 T1: prerregistro v2 (DRAFT), contrato v2 y prompts canónicos']
    sources = ['src/v2/conditions.py', 'src/v2/models.py', 'src/v2/llm.py',
               'src/v2/simulate.py', 'src/v2/attribution.py', 'src/market.py',
               'preregistration/preregistration.md', 'preregistration/FROZEN.json',
               'results/confirm_run_log.md', 'data/v2/analysis/confirm/results.json']
    facts = {
        'label': 'EXPLORATORY (not preregistered); local extraction only',
        'sources_sha256': {path: hashlib.sha256((root/path).read_bytes()).hexdigest() for path in sources},
        'models': {},
        'sampling': {
            'max_tokens': 512, 'response_format': {'type': 'json_object'},
            'retries': inspect.signature(llm.chat).parameters['retries'].default,
            'backoff_seconds': inspect.signature(llm.chat).parameters['backoff'].default,
            'backoff_recipe': 'backoff * (2 ** attempt), before another of 3 maximum total attempts',
            'httpx_timeout_seconds': 180,
            'omitted_parameters': ['top_p', 'API seed', 'frequency_penalty', 'presence_penalty', 'stop', 'n', 'stream'],
            'provider_default_values': 'Not persisted; no numeric default sampling values can be verified from disk.',
            'reasks': 'Same model/settings/provider; sign-flip calls do not trade; no invalid-JSON retries.',
            'transport_retry_conditions': ['httpx.TransportError', 'HTTP >=500', 'HTTP 429'],
            'transport_no_retry': 'Other HTTP >=400 errors; invalid JSON; provider mismatch.',
            'provider_concurrency_limit': 8,
            'collection_parallel_blocks': {'deepseek-v4-flash': 4, 'anthropic/claude-haiku-5.5': 3, 'openai/gpt-6-luna': 3},
            'condition_order': 'Rotate CONDITIONS by (seed-200)%5; block parallelism can alter wall-clock completion order.',
        },
        'random_seeds': {
            'market': 'default_rng(seed), unchanged draw schedule',
            'audit': 'default_rng(seed*1000+7), full (40,6) mask <0.30',
            'cf': 'default_rng(seed*1000+17), full (40,6) mask <0.50',
            'null_registered': 'default_rng(seed*1000+29), full (40,6) mask <0.20 intersect cf',
            'null_implemented': 'default_rng(seed*1000+29), scalar draw ONLY at CF-sampled decisions (no full null mask); restarted per seed/condition/model',
            'bootstrap_seed': 20261026, 'bootstrap_draws': 10000, 'wild_bootstrap_draws': 9999,
        },
        'versions_confirmatory_analysis': original_meta['versions'],
        'versions_preregistered': {'python': '3.12.2', 'numpy': '2.5.4', 'scipy': '1.18.1', 'pandas': '3.1.0', 'matplotlib': '3.11.2', 'httpx': '0.28.1', 'pytest': '9.1.1'},
        'versions_exploratory_analysis': {'python': platform.python_version(), **{p: im.version(p) for p in ('numpy','scipy','pandas','matplotlib','statsmodels','httpx','pytest')}},
        'freeze': json.loads((root/'preregistration/FROZEN.json').read_text()),
        'preregistration_history': history,
        'dates': {'original_registration_document_date': '2026-10-26', 'original_registration_commit': '95bd99b0c95ba6a0ef2e3a115f59391ffa4ebbd9',
                  'original_registration_commit_date': '2026-10-27T09:34:20+01:00',
                  'amendment_1': '2026-10-27', 'amendment_1_commit': '4268a9806981273cbf3aeaa42f54a7bc25136ecc',
                  'amendment_1_approval_commit': 'c1833938a0266c015df875c6f6f9998ed9387a8b',
                  'amendment_2_budget_only': '2026-10-27', 'amendment_2_commit': '72d05151df3fd1944fb009dda7506707ff455c82',
                  'renewed_freeze_marker_commit': '9345e7d9854271cad336195b8f9ce624a14607c1'},
        'confirmatory_analysis': {k: original_meta[k] for k in ('code_revision', 'executed_utc', 'analysis_code_sha256', 'preregistration_sha256')},
        'dgp': {
            'agents': 6, 'ticks': 40,
            'seed_sets': {m: list(range(200, 220 if m=='deepseek-v4-flash' else 210)) for m in models},
            'initial_regime': 'news iff seed even, momentum iff odd', 'switch_ticks': [10,20,30],
            'initial_price': 100., 'price_floor': 50., 'lam': .03, 'fundamental_coefficient': .02,
            'return_noise_sd': .005, 'latent_driver_sd': 1., 'feature_noise_sd': .7,
            'volume_mean': 1., 'volume_noise_sd': .3, 'proxy_parent_coefficient': .3,
            'proxy_noise_sd': .6, 'spread_uniform': [.004,.03],
            'feature_rounding_decimal_places': {'momentum':3,'news':3,'volume':3,'orderflow':3,'sentiment':3,'spread':4},
            'proxy_parent_correlations_before_rounding': {'active': .3*np.sqrt(1.49)/np.sqrt(.09*1.49+.36), 'inactive': .3*np.sqrt(.49)/np.sqrt(.09*.49+.36)},
            'orderflow_sentiment_mutual_correlation_before_rounding': 0.,
            'orderflow_equation': 'round(0.3 * unrounded_momentum + Normal(0,0.6^2),3)',
            'sentiment_equation': 'round(0.3 * unrounded_news + Normal(0,0.6^2),3)',
        },
        'not_identifiable': [
            'Full raw API responses, raw output strings, returned immutable model IDs/versions and actual provider default sampling parameters are not persisted in confirm JSONL/ledger. Requested IDs and successful provider pins are available; numeric temperature/top_p for Haiku/Luna are not.',
            'Original collection environment versions beyond preregistered versions and original-analysis metadata are not independently archived.',
            'Source comment identifies the DeepSeek alias as V4.1 Flash, but ledger preserves requested alias only, not a response-verified backend version.',
            'Some Luna ledger entries have no served_by identity and usage missing; logs do not establish the backend/version for those requests.',
        ],
        'prompts': {'literal_text': c.render_preregistered_prompts(), 'feedback_descriptions': c.FEEDBACK_DESCRIPTIONS},
        'evidence': {},
    }
    for model in models:
        spec = MODELS[model]
        rows = [r for r in ledger if r.get('tag','').startswith('nsb2:'+model.replace('/','-')+':confirm:')]
        payload = {'model':spec.provider_model_id,'max_tokens':512,'response_format':{'type':'json_object'}}
        if spec.provider == 'deepseek':
            payload.update(temperature=0., thinking={'type':'disabled'})
        else:
            payload.update(provider={'order':spec.provider_order,'allow_fallbacks':False,'data_collection':'deny'},reasoning={'enabled':False})
        model_runs = [run for run in loaded.values() if run['source']['model']==model]
        facts['models'][model] = {
            'provider': spec.provider, 'endpoint': spec.endpoint,
            'requested_provider_model_id': spec.provider_model_id,
            'provider_pin': spec.provider_order, 'payload_without_messages':payload,
            'temperature_omitted': not spec.supports_temperature,
            'ledger_first_utc':min(r['timestamp'] for r in rows), 'ledger_last_utc':max(r['timestamp'] for r in rows),
            'ledger_entries':len(rows),
            'served_by_counts':dict(sorted(Counter(str(r.get('served_by','direct_deepseek' if spec.provider=='deepseek' else 'not_recorded')) for r in rows).items())),
            'http_status_counts':dict(sorted(Counter(str(r['status_code']) for r in rows if 'status_code' in r).items())),
            'usage_missing_entries':sum(bool(r.get('usage_missing')) for r in rows),
            'provider_mismatch_entries':sum(bool(r.get('provider_mismatch')) for r in rows),
            'base_parse_failures':sum(not r['parse_ok'] for run in model_runs for r in run['rows']),
        }
        totals = {w: Counter() for w in ('overall','primary')}
        n_seen, corr_deltas = Counter(), []
        evidence_runs = sorted((run for run in model_runs if run['source']['condition']=='evidence'), key=lambda run: run['source']['seed'])
        for run in evidence_runs:
            markets, decisions = run['markets'], sorted(run['rows'], key=lambda r:(r['tick'],r['agent']))
            by_tick = defaultdict(list)
            for d in decisions:
                by_tick[d['tick']].append(d)
            latest = {}
            for d in decisions:
                t, idx = d['tick'], d['agent']
                windows = ['overall'] + (['primary'] if 20<=t<=39 else [])
                for w in windows:
                    z=totals[w];z['assigned_decisions']+=1
                    if idx in latest:
                        a=latest[idx]; start=max(0,a-4)
                        regs={markets[k]['regime'] for k in range(start,a+1)}
                        z['feedback_exposed_decisions']+=1
                        z['exposed_mixed_regime_windows']+=len(regs)>1
                        z['exposed_older_regime_window_endpoint']+=markets[a]['regime']!=d['regime']
                        mt=re.search(r'Pearson correlations from the last (\d+) completed ticks',d['feedback'] or '')
                        assert mt and int(mt[1])==a-start+1, 'Evidence sample size inconsistent with implemented five-tick window'
                if d.get('audited'):
                    latest[idx]=t;start=max(0,t-4)
                    regs={markets[k]['regime'] for k in range(start,t+1)}
                    nominal_start=max(0,t-7)
                    n_seen[t-start+1]+=1
                    for w in windows:
                        z=totals[w];z['generated_feedback_events']+=1
                        z['generated_mixed_regime_windows']+=len(regs)>1
                        z['nominal_eight_tick_mixed_regime_windows']+=len({markets[k]['regime'] for k in range(nominal_start,t+1)})>1
                    if t-start>=1:
                        yy=np.array([markets[k]['return'] for k in range(start,t+1)])
                        impact=np.array([.03*sum((1 if x['action']=='buy' else -1)*x['size'] for x in by_tick[k] if x['parse_ok'])/30 for k in range(start,t+1)])
                        for f in c.FEATURES:
                            xx=np.array([markets[k]['features'][f] for k in range(start,t+1)])
                            if np.std(xx)>0 and np.std(yy)>0 and np.std(yy-impact)>0:
                                corr_deltas.append(float(abs(np.corrcoef(xx,yy)[0,1]-np.corrcoef(xx,yy-impact)[0,1])))
        for z in totals.values():
            for key,den in [('generated_mixed_regime_windows','generated_feedback_events'),('nominal_eight_tick_mixed_regime_windows','generated_feedback_events'),('exposed_mixed_regime_windows','feedback_exposed_decisions'),('exposed_older_regime_window_endpoint','feedback_exposed_decisions')]:
                z[key+'_fraction']=z[key]/z[den] if z[den] else None
        facts['evidence'][model] = {
            'counts':{w:dict(z) for w,z in totals.items()},
            'actual_n_distribution_generated_audits':dict(sorted(n_seen.items())),
            'median_abs_correlation_change_after_subtracting_impact':float(np.median(corr_deltas)),
            'n_feature_correlations_compared':len(corr_deltas),
            'impact_subtraction_limitation':'Descriptive arithmetic sensitivity only; subtracting realized impact does not undo feedback-induced changes in orders/history or identify a causal mechanism.',
        }
    facts['evidence']['recipe'] = {
        'nominal_window':8,'actual_maximum_window':5,
        'explanation':'_history_for returns last HISTORY_K=4 completed ticks; feedback receives that list plus current completed tick; feature_return_statistics then takes last 8 from input of length at most 5.',
        'correlation_outcome':'market.step raw return = 0.02*rounded_true_feature + 0.03*I_t + Gaussian noise; price-floor clipping does not change logged raw return or correlation input.',
        'impact':'I_t=sum_i s_it q_it/(6*5), requested sizes from valid base decisions; not capped by cash/holdings. Each agent contributes 0.001*s_it*q_it to r_t, up to magnitude .01.',
        'crossing_definition':'Window spans a regime change iff its constituent market rows contain both news and momentum regimes; exact audit-generation tick reconstructed, not inferred from current decision regime.',
        'nominal_comparison':'Counterfactual eight-tick windows evaluated at the SAME observed audit ticks; not windows actually shown.',
    }
    return facts


def fmt(value, digits=4):
    return f"{value:.{digits}f}" if _finite(value) else "NA"


def estimate_text(item):
    return f'{fmt(item["mean_delta"])} [{fmt(item["bootstrap_ci_95"][0])}, {fmt(item["bootstrap_ci_95"][1])}]'


def mean_sd(item):
    return f'{fmt(item["mean"])} ± {fmt(item["seed_sd"])}'


def fraction_text(numerator, denominator):
    return f'{numerator}/{denominator} ({100*numerator/denominator:.2f}%)' if denominator else f'{numerator}/0 (NA)'


def write_report(result):
    short = dict(zip(REQUIRED_MODELS, ("DeepSeek", "Haiku", "Luna")))
    lines = ["# Exploratory analyses of existing confirmatory data", "", LABEL, "",
             "These analyses are exploratory (not preregistered). Confirmatory results are reproduced exactly, "
             "including common support, per-seed differences, 95% intervals, raw p and four-slot within-model Holm p. "
             "No API calls, new responses, changed seeds or changed confirmatory files. "
             "Primary window: ticks 20–39. DeepSeek: 20 seeds; Haiku and Luna: 10 seeds each. "
             "Every estimate weights seeds equally unless explicitly marked pooled. SD denotes the sample SD of seed means. "
             "All new intervals are descriptive 95% percentile seed-bootstrap intervals (10,000 draws, RNG 20261026); "
             "new p values are raw two-sided paired t diagnostics, without confirmatory rejection rules.", "",
             result["metadata"]["primary_selectors"], "",
             "## Headline facts for the paper", "",
             "- **Implementation deviation: evidence tables contain at most five completed ticks, "
             "not the registered eight.** Every persisted evidence message is regenerated and matched byte-for-byte. "
             "The ordinary four-tick history was reused as the evidence-builder input, then augmented by the audited tick."]
    for model, block in result["models"].items():
        name = short[model]
        p = block["primary_reproduced"]
        lines.append(f'- {name} primary: ' + "; ".join(
            f'P{i} {estimate_text(p[k])}, raw p={p[k]["paired_t_p"]:.5g}, Holm p={p[k]["holm_p"]:.5g}'
            for i, k in enumerate(PRIMARY, 1)) + ".")
        naive = block["D_regime"]["overall"]["naive"]
        lines.append(f'- {name} naive all-tick discrimination (driver − non-driver flip rates): ' + "; ".join(
            f'{g} pooled {fmt(naive[g]["pooled_driver_minus_non_driver"]["mean"])}, '
            f'seed estimate {estimate_text(naive[g]["discrimination"])} (n={naive[g]["discrimination"]["n_common_decisions"]} decisions)'
            for g in PROBES) + ".")
        lines.append(f'- {name} regime contrasts: ' + "; ".join(
            f'{g}: P2 {estimate_text(block["D_primary_by_regime"][g]["H1_dependence_evidence_minus_naive"])}, '
            f'P4 {estimate_text(block["D_primary_by_regime"][g]["H4_sci_placebo"])}' for g in PROBES) + ".")
        st = block["F_label_staleness"]
        lines.append(f'- {name} persisted label false in ' + fraction_text(st["label"]["stale"]["count"], st["label"]["n_assigned"]) +
                     ' primary decisions; placebo label accidentally true in ' + fraction_text(st["placebo"]["correct"]["count"], st["placebo"]["n_assigned"]) +
                     f'; no label exposure yet: label {st["label"]["no_label"]["count"]}, placebo {st["placebo"]["no_label"]["count"]}.')
        lines.append(f'- {name} both-driver citation rates: ' + "; ".join(
            f'{c} {100*block["G_hedging"][c]["primary"]["both_news_and_momentum"]["mean"]:.2f}%'
            for c in conditions.CONDITIONS) + ".")
        lines.append(f'- {name} additive noise-adjusted: ' + "; ".join(
            f'P{i} {estimate_text(block["E_null_adjusted"][k])}, p={block["E_null_adjusted"][k]["paired_t_p"]:.5g}'
            for i, k in ((2, "H1_dependence_evidence_minus_naive"), (3, "H3_sci_label"), (4, "H4_sci_placebo"))) + ".")
        e = result["K_evidence_package"]["models"][model]["windows"]["primary"]
        n = e["generated_actual_crossing"]
        lines.append(f'- {name} actual mixed-regime audit tables: {fraction_text(n["numerator"], n["n"])}; '
                     f'mixed windows carried by {fraction_text(e["exposed_actual_table_crossing"]["numerator"], e["n_assigned_decisions"])} '
                     f'primary prompts. Removing realized price impact changes feature correlations by mean |Δr|={e["price_impact"]["mean_absolute_r_change_without_impact"]:.4f} (fixed-path arithmetic sensitivity).')
    lines += ["", "## Estimands, eligibility and missing responses (B)", "", result["metadata"]["eligibility"], "",
              "Formally, let V_cj denote valid base plus two valid probes. For precision, J_sc={j:20≤t≤39, "
              "same seed/tick/agent/regime in c and reference, V_cj=V_rj=1, |C_cj|>0, |C_rj|>0}. "
              "For dependence and ITT SCI, drop the C restrictions. For recall replace them with |D_cj|>0 and |D_rj|>0. "
              "For fidelity/citation require only valid bases in both arms. Actual-label SCI additionally requires a revealed label "
              "in the target and uses that same label to score both arms, including when stale. "
              "For any metric Y, Δ_s=mean_(j∈J_sc)Y_cj−mean_(j∈J_sc)Y_rj, then Δ=mean_s Δ_s. "
              "C and D eligibility and subgroup membership are post-treatment. Common support therefore defines a selected estimand. "
              "All-available descriptive seed means in A have no cross-condition matching.", "",
              result["metadata"]["empty_denominators"], "",
              "Primary-window flow (each arm assigns 120 decisions per seed). A probed decision has two attempted feature re-asks; "
              "valid re-asks below count calls, whereas eligible counts decisions with both valid re-asks. "
              "An invalid base receives no feature re-asks and no market order; invalid or failed re-asks produce undefined flips. "
              "A decision with only one valid probe is excluded from process metrics and all raw dependence/SCI comparisons. "
              "No failed/invalid response is fabricated or resampled. All-tick flows and failures by feature are in JSON `B_flow`.", "",
              "| Model | Condition | Assigned | Valid bases | CF selected | Probed | Valid re-asks / attempted | Failed/invalid re-asks | Complete eligible | Defined P | Defined Q |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for model, block in result["models"].items():
        for c, windows in block["B_flow"].items():
            b = windows["primary"]
            lines.append(f'| {short[model]} | {c} | {b["assigned_decisions"]} | {b["valid_base"]} | {b["cf_mask_selected"]} | '
                         f'{b["probed_decisions"]} | {b["valid_feature_reasks"]}/{b["feature_reasks_attempted"]} | '
                         f'{b["invalid_or_failed_feature_reasks"]} | {b["eligible_complete_decisions"]} | '
                         f'{b["analysed_all_available_precision"]} | {b["analysed_all_available_recall"]} |')
    lines += ["", "| Model | Condition | Empty C / valid bases | Empty C / complete measured | Empty D / complete measured |",
              "|---|---|---|---|---|"]
    for model, block in result["models"].items():
        for c, windows in block["B_flow"].items():
            b = windows["primary"]
            values = [b[k] for k in ("empty_C_valid_base", "empty_C_complete_measured", "empty_D_complete_measured")]
            lines.append(f'| {short[model]} | {c} | ' + ' | '.join(fraction_text(int(x["sum"]), x["n"]) for x in values) + ' |')
    lines += ["", "Common support for every contrast is recorded under `B_common_support` with per-arm eligible/excluded counts and per-seed counts. "
              "The primary contrasts are shown here; a seed remains included if at least one eligible matched decision exists.", "",
              "| Model | Contrast | Target eligible | Reference eligible | Common analysed coordinates | Seed pairs |", "|---|---|---:|---:|---:|---:|"]
    for model, block in result["models"].items():
        for i, key in enumerate(PRIMARY, 1):
            b = block["B_common_support"][key]
            lines.append(f'| {short[model]} | P{i} | {b["target_eligible"]} | {b["reference_eligible"]} | {b["common_analysed"]} | '
                         f'{block["primary_reproduced"][key]["n_seed_pairs"]} |')
    lines += ["", "## A. All-available condition means ± seed SD, ticks 20–39", "",
              "E and true-driver citation are identically defined (the driver is in the reasons), so their numeric columns coincide. "
              "Precision and recall use only decisions with defined denominators; JSON includes the exact decision and seed denominators.", "",
              "| Model | Condition | E | Driver flip | Opposite flip | P | Q | True citation |",
              "|---|---|---|---|---|---|---|---|"]
    for model, block in result["models"].items():
        for c, metrics in block["A_descriptive"].items():
            lines.append(f'| {short[model]} | {c} | ' + ' | '.join(mean_sd(metrics[m]) for m in METRICS) + ' |')
    lines += ["", "## C. Numeric support for Table 3", "",
              "Raw secondary p values and descriptive intervals do not create a confirmatory rejection rule. "
              "Effect sizes (paired SD, d_z), exact seed means and support counts for these and all registered secondary contrasts are in JSON. "
              "H2 fidelity and true-driver citation are the same outcome. Opposite/false citation always selects the opposite CURRENT driver, "
              "independently of the persisted label's present correctness. H1/H3/H4 primary rows are in the headline list above.", "",
              "| Model | Secondary contrast | Δ [95% CI] | Raw p | Seeds | Common n |", "|---|---|---|---:|---:|---:|"]
    core = ("H2_fidelity_label_minus_naive", "H2_precision_label_minus_naive", "H2_precision_evidence_minus_label",
            "H4_fidelity_placebo_minus_label", "H4_false_citation_placebo_minus_naive", "H5_precision_evidence_minus_punitive",
            "H5_precision_punitive_minus_naive", "H1_dependence_evidence_minus_punitive", "H5_dependence_punitive_minus_naive")
    for model, block in result["models"].items():
        for key in core:
            b = block["C_secondary_table3"][key]
            lines.append(f'| {short[model]} | {key} | {estimate_text(b)} | {b["paired_t_p"]:.5g} | {b["n_seed_pairs"]} | {b["n_common_decisions"]} |')
    lines += ["", "SCI components below use exactly the corresponding primary SCI support; citation-only secondary contrasts above can use more valid bases.", "",
              "| Model | SCI | Component change | Δ [95% CI] | Raw p |", "|---|---|---|---|---:|"]
    for model, block in result["models"].items():
        for key, components in block["C_SCI_components_same_support"].items():
            for component, b in components.items():
                lines.append(f'| {short[model]} | {key} | {component} | {estimate_text(b)} | {b["paired_t_p"]:.5g} |')
    lines += ["", "## D. Regime split", "",
              "Rates and discrimination estimates below weight seeds equally; n counts complete decisions. "
              "The JSON also reports pooled-decision rates and pooled discrimination. All-tick naive discrimination reproduces the published instrument diagnostic; "
              "the full primary-window table includes every condition and both regimes.", "",
              "| Model | Window | Condition | Regime | Driver rate | Non-driver rate | Discrimination [95% CI] | Seeds | Decisions |",
              "|---|---|---|---|---:|---:|---|---:|---:|"]
    for model, block in result["models"].items():
        for w in ("overall", "primary"):
            for c in (("naive",) if w == "overall" else conditions.CONDITIONS):
                for g, b in block["D_regime"][w][c].items():
                    d = b["discrimination"]
                    lines.append(f'| {short[model]} | {w} | {c} | {g} | {fmt(b["driver"]["mean"])} | {fmt(b["non_driver"]["mean"])} | '
                                 f'{estimate_text(d)} | {d["n_seed_pairs"]} | {d["n_common_decisions"]} |')
    lines += ["", "| Model | Regime | Contrast | Δ [95% CI] | Raw p | Seeds | Common n |", "|---|---|---|---|---:|---:|---:|"]
    for model, block in result["models"].items():
        for g, contrasts in block["D_primary_by_regime"].items():
            for i, key in enumerate(PRIMARY, 1):
                b = contrasts[key]
                lines.append(f'| {short[model]} | {g} | P{i} | {estimate_text(b)} | {b["paired_t_p"]:.5g} | {b["n_seed_pairs"]} | {b["n_common_decisions"]} |')
    lines += ["", "## E. Identical-prompt noise and additive sensitivity", "", result["metadata"]["noise_recipe_deviation"], "",
              "The two recipes share seed and probability but map RNG draws to different decisions. "
              "Every actual mask is asserted against the implemented scalar recipe, and no run matches the registered full-mask recipe. "
              "The sole invalid-base null call is Haiku evidence seed 203, tick 3, agent 4; its flip is undefined and excluded. "
              "Valid-base null missingness and selected counts are retained in JSON. Null-rate intervals there are descriptive Wilson intervals "
              "for pooled responses plus seed-bootstrap intervals for equal-seed rates. n below is the number of valid observed nulls.", "",
              "| Model | Condition | Regime | Overall null flips/n (rate) | Primary null flips/n (rate) | Overall null selections / CF selected |",
              "|---|---|---|---|---|---|"]
    for model, block in result["models"].items():
        for c, windows in block["E_null_rates"].items():
            for g in PROBES:
                a, b = [windows[w][g] for w in ("overall", "primary")]
                cells = []
                for x in (a, b):
                    z = x["flip_rate"]
                    cells.append(f'{z["sum"]:g}/{z["n"]} ({fmt(z["mean"])})')
                lines.append(f'| {short[model]} | {c} | {g} | {cells[0]} | {cells[1]} | {fraction_text(a["n_selected"], a["cf_sampled_decisions"])} |')
    lines += ["", "Realized null sampling rates, all conditions and all ticks combined:", ""]
    for model, block in result["models"].items():
        cells = [w["overall"]["pooled"] for w in block["E_null_rates"].values()]
        lines.append(f'- {short[model]}: ' + fraction_text(sum(x["n_selected"] for x in cells), sum(x["cf_sampled_decisions"] for x in cells)) +
                     ' of CF-selected decisions; ' + fraction_text(sum(x["n_selected"] for x in cells), sum(x["n_decisions"] for x in cells)) + ' of assigned decisions.')
    lines += ["", result["metadata"]["noise_adjustment"], "",
              "| Model | Adjusted contrast | Δ [95% CI] | Raw p | Seeds | Fallback cells used |", "|---|---|---|---:|---:|---:|"]
    for model, block in result["models"].items():
        for key, b in block["E_null_adjusted"].items():
            lines.append(f'| {short[model]} | {key} | {estimate_text(b)} | {b["paired_t_p"]:.5g} | {b["n_seed_pairs"]} | {b["n_fallback_cells_used"]} |')
    lines += ["", "Condition noise differences use paired seed rates on common valid null coordinates. All ten condition pairs "
              "per model, and pooled/news/momentum tests in both windows, are in `E_null_condition_tests`. "
              "All-tick omnibus and contrasts against naive are shown below; these tests are exploratory.", "",
              "| Model | Test, all ticks pooled | Δ [95% CI] or statistic | Raw p |", "|---|---|---|---:|"]
    for model, block in result["models"].items():
        b = block["E_null_condition_tests"]["overall"]["pooled"]
        lines.append(f'| {short[model]} | Friedman, 5 conditions | {fmt(b["omnibus"]["statistic"])} | {fmt(b["omnibus"]["p"], 6)} |')
        for key, item in b["pairwise"].items():
            if key.startswith("naive_"):
                lines.append(f'| {short[model]} | {key} | {estimate_text(item)} | {item["paired_t_p"]:.5g} |')
    lines += ["", "## F. Persisted labels and post-treatment subgroups", "",
              "Correct/stale describes whether the persisted pre-action label equals the current driver; the label condition becomes false when stale, "
              "whereas placebo becomes accidentally true. Shares below use all assigned primary decisions (exposure itself is logged even for invalid bases). "
              "No washout or stale-label exclusion is applied to original primaries.", "",
              "| Model | Condition | Current true label | Currently false label | No feedback yet |", "|---|---|---|---|---|"]
    for model, block in result["models"].items():
        for c, b in block["F_label_staleness"].items():
            lines.append(f'| {short[model]} | {c} | {fraction_text(b["correct"]["count"], b["n_assigned"])} | '
                         f'{fraction_text(b["stale"]["count"], b["n_assigned"])} | {fraction_text(b["no_label"]["count"], b["n_assigned"])} |')
    lines += ["", "Subgroup SCI retains the opposite-current-driver selector of P4 for placebo, even when the actual placebo label is currently true. "
              "For label the table uses the P3 current-true-driver selector. Actual-label SCI and current/opposite citation and dependence in every subgroup "
              "are also reported in JSON. These are selected descriptive comparisons; the subgroup is defined from the target's post-treatment exposure.", "",
              "| Model | Condition | Label currently | Adopt persisted label | Flip persisted label | SCI P3(label)/P4(placebo) [95% CI] | Raw p | Common n |",
              "|---|---|---|---:|---:|---|---:|---:|"]
    for model, block in result["models"].items():
        for c, summary in block["F_label_staleness"].items():
            for state in ("correct", "stale", "no_label"):
                b = summary["split"][state]
                sci = b["SCI_current_true" if c == "label" else "SCI_current_opposite_P4_selector"]
                lines.append(f'| {short[model]} | {c} | {state} | {fmt(b["metrics"]["label_adoption"]["mean"])} | '
                             f'{fmt(b["metrics"]["dependence_revealed"]["mean"])} | {estimate_text(sci)} | {sci["paired_t_p"]:.5g} | {sci["n_common_decisions"]} |')
    lines += ["", "## G. Hedging and specificity", "", result["metadata"]["specificity"], "",
              "Citing both drivers guarantees environmental audit PASS without identifying a specific driver. "
              "These rates use all valid primary base decisions and equal seed weights; counts, SD, CIs and all-tick rates are in JSON.", "",
              "| Model | Condition | Both drivers | Exclusive true within probes | Only true reason | True share of probed citations | True − opposite citation |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for model, block in result["models"].items():
        for c, windows in block["G_hedging"].items():
            b = windows["primary"]
            keys = ("both_news_and_momentum", "exclusive_true_within_probes", "only_true_reason", "true_share_of_probed_citations",
                    "unconditional_true_minus_opposite_citation")
            lines.append(f'| {short[model]} | {c} | ' + ' | '.join(fmt(b[k]["mean"]) for k in keys) + ' |')
    h = result["H_directionality"]
    lines += ["", "## H. Direction of the observed re-asks", "", h["definition"], "", h["interpretation"], "",
              f'{h["verified_sign_flip_records"]} valid primary feature re-ask records were verified against logged perturbed values. '
              "The table shows driver probes; non-driver sign benchmarks, zero-feature counts and transition tables are in JSON. "
              "No claim about economic optimality or full-return prediction follows from matching the fundamental component's sign.", "",
              "| Model | Condition | Regime | Driver probes | Flips | New action follows flipped sign [seed 95% CI] | Among flips, follows sign (pooled) |",
              "|---|---|---|---:|---:|---|---|"]
    for b in h["cells"]:
        if b["probe_role"] != "driver":
            continue
        z = b["seed_new_sign_alignment"]
        f = b["among_action_flips_new_matches_flipped_sign"]
        lines.append(f'| {short[b["model"]]} | {b["condition"]} | {b["regime"]} | {b["n_valid_feature_reasks"]} | '
                     f'{b["n_flips"]} | {fmt(z["mean"])} [{fmt(z["bootstrap_ci_95"][0])}, {fmt(z["bootstrap_ci_95"][1])}] | {fraction_text(f["numerator"], f["n"])} |')
    lines += ["", "## I. Placebo verdict/label conflict", "", result["I_placebo_verdict_conflict"]["timing"], "",
              "| Model | Valid decisions | Persisted false label cited | Audited such citations | Failed and fined | Fine rate among audited citations | Failed/fined share of all valid decisions |",
              "|---|---:|---:|---:|---:|---|---|"]
    for model, b in result["I_placebo_verdict_conflict"]["models"].items():
        lines.append(f'| {short[model]} | {b["n_valid_placebo_decisions"]} | {b["n_persisted_false_label_cited"]} | '
                     f'{b["n_such_citations_audited"]} | {b["n_such_citations_failed_and_fined"]} | '
                     f'{fraction_text(b["n_such_citations_failed_and_fined"], b["n_such_citations_audited"])} | '
                     f'{fraction_text(b["n_such_citations_failed_and_fined"], b["n_valid_placebo_decisions"])} |')
    j = result["J_haiku_P4"]
    lines += ["", "## J. Why Haiku P4 has a negative bootstrap interval and p > .05", "",
              f'Haiku P4 Δ={j["mean_delta"]:.7f}; percentile bootstrap CI [{j["bootstrap_percentile_ci_95"][0]:.7f}, '
              f'{j["bootstrap_percentile_ci_95"][1]:.7f}]. Paired t={j["paired_t"]:.7f}, df={j["df"]}, '
              f'raw p={j["paired_t_p"]:.7f}, Holm p={j["holm_p"]:.7f}. Student-t 95% CI '
              f'[{j["student_t_ci_95"][0]:.7f}, {j["student_t_ci_95"][1]:.7f}]. Seed-difference skewness={j["sample_skewness"]:.4f}.', "",
              j["explanation"], "", "Seed differences: " + ", ".join(f'{v:.6f}' for v in j["seed_deltas"]) + ".", "",
              "## K. Actual evidence-window crossing and endogenous price impact", "",
              result["K_evidence_package"]["implementation_deviation"], "",
              f'Verified {result["K_evidence_package"]["verified_persisted_feedback_instances"]} persisted feedback instances. '
              "All primary audit tables have n=5. Audits on tick 39 are generated after the final decision and have no later prompt exposure; "
              "generation and exposure denominators are therefore distinct. Nominal eight-tick counts below use the same observed audit ticks "
              "and are a counterfactual recipe comparison, not a description of delivered tables.", "",
              "| Model | Window | Actual mixed / generated | Nominal 8 mixed / same audits | Actual mixed / exposed prompts | Exposed windows ending in old regime |",
              "|---|---|---|---|---|---|"]
    for model, b in result["K_evidence_package"]["models"].items():
        for window, z in b["windows"].items():
            rates = [z[k] for k in ("generated_actual_crossing", "generated_nominal8_crossing", "exposed_actual_table_crossing",
                                   "exposed_window_end_regime_disagrees_current")]
            lines.append(f'| {short[model]} | {window} | ' + ' | '.join(fraction_text(v["numerator"], v["n"]) for v in rates) + ' |')
    lines += ["", result["K_evidence_package"]["correlation_definition"], "",
              "An agent's own requested order contributes 0.03*s*q/30=0.001*s*q to the reported raw return, up to ±0.01. "
              "Correlations include this component without residualization. Order signs/sizes depend on feedback and features, "
              "so the correlation table can reflect the agents' own behavior. Spread/volume/orderflow/sentiment also enter the reported table. "
              "Cov(x,r)=0.02 Cov(x,x_driver)+0.03 Cov(x,I)+Cov(x,epsilon); dividing by sd(x)sd(r) gives its Pearson numerator decomposition.", "",
              result["K_evidence_package"]["impact_sensitivity"], "",
              "| Model | Primary mean absolute impact | Impact SD | Fundamental SD | Return SD | Mean absolute table-correlation change after removing impact |",
              "|---|---:|---:|---:|---:|---:|"]
    for model, b in result["K_evidence_package"]["models"].items():
        z = b["windows"]["primary"]["price_impact"]
        keys = ("mean_absolute_impact", "impact_population_sd", "fundamental_population_sd", "return_population_sd", "mean_absolute_r_change_without_impact")
        lines.append(f'| {short[model]} | ' + ' | '.join(fmt(z[k]) for k in keys) + ' |')
    lines += ["", "Implementation-deviation disclosure:", "",
              "> An implementation check established that the evidence builder received the four-tick "
              "display history plus the just-completed audited tick. Its registered eight-tick cap therefore operated on at most five "
              "observations. All primary-window audit tables used five observations; no eight-observation table was delivered. "
              "We retain the original data and confirmatory estimands and report this as an implementation deviation. "
              "The evidence-package estimates describe the implemented five-tick correlation feedback, and do not estimate an eight-tick intervention.", "",
              "## L. Reproducibility facts", "",
              "The literal full prompt definitions, response schema, persona mandates, per-condition sentences, feedback templates and exact "
              "six-feature DGP equations are in [prompt_and_dgp.md](prompt_and_dgp.md). Full payloads without messages, seed recipes, source hashes, "
              "confirmatory/exploratory software versions, retry/error counts, historical preregistration commits and collection timestamps are in `L_reproducibility`.", "",
              "| Model | Provider / served route | Endpoint | Temperature | Collection ledger first UTC | Last UTC |",
              "|---|---|---|---|---|---|"]
    for model, b in result["L_reproducibility"]["models"].items():
        lines.append(f'| {model} | {b["provider"]} / {b["provider_pin"] or "direct"} | {b["endpoint"]} | '
                     f'{"omitted, provider default unrecorded" if b["temperature_omitted"] else "0"} | {b["ledger_first_utc"]} | {b["ledger_last_utc"]} |')
    l = result["L_reproducibility"]
    lines += ["", "Preregistration document date: 2026-10-26; initial committed registration: "
              f'{l["dates"]["original_registration_commit"]} ({l["dates"]["original_registration_commit_date"]}). '
              f'Amendment 1: {l["dates"]["amendment_1_commit"]}; approval: {l["dates"]["amendment_1_approval_commit"]}; '
              f'Amendment 2 (budget/operations, 2026-10-27): {l["dates"]["amendment_2_commit"]}. '
              f'Renewed freeze marker commit: {l["dates"]["renewed_freeze_marker_commit"]}. '
              "The original document's retained DRAFT header causes the confirmatory analyzer's metadata to say draft; "
              "the hash and recorded approval/freeze in FROZEN.json determine freeze provenance.", "",
              "Current environment: " + ", ".join(f'{k} {v}' for k, v in result["metadata"]["versions"].items()) + ".", "",
              "## Not computable / interpretation limits", ""]
    lines += ["- " + s for s in result["not_computable"]]
    lines += ["- " + s for s in l["not_identifiable"]]
    lines += ["", "## Offline reproduction", "",
              "Run `python -m pytest -q tests/v2/test_exploratory_analyses.py` and `python -m pytest -q` "
              "for the focused checks and full public suite. Release validation is recorded in [VERIFICATION.md](../../../../VERIFICATION.md).", "",
              "Reproduce offline with `python src/v2/exploratory_analyses.py`. "
              "The script asserts exact primary and registered-secondary reproduction and deterministic masks before writing. "
              "No volatile execution time is embedded in generated outputs. Public packaging changes documentation, "
              "source hashes and path provenance while preserving the scientific estimates and historical collection facts.", ""]
    return "\n".join(lines).replace("SCI", "CSD").replace("placebo", "false-label")


def main():
    result = analyze_exploratory()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (OUTPUT / "report.md").write_text(write_report(result))
    (OUTPUT / "prompt_and_dgp.md").write_text(prompt_and_dgp_markdown())
    print(f"{LABEL}: {OUTPUT.relative_to(ROOT)}; all confirmatory primary numbers match exactly")


if __name__ == "__main__":
    main()
