"""POST HOC / post hoc analyses; disk inputs only.

Reproduce: .venv/bin/python src/v2/posthoc_analyses.py
Frozen estimators and results are never modified. The seed is the inference unit.
"""
import hashlib
import importlib.metadata
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from scipy import optimize, stats

from src.market import Market
from src.v2 import conditions
from src.v2.analyze import (
    DATA_ROOT, PRIMARY, PROBES, REQUIRED_MODELS, RNG_SEED, ROOT, _finite,
    _matched_rows, holm, load_runs,
)
from src.v2.exploratory_analyses import (
    exploratory_contrast, hedging_description, hik_evidence, metric_description,
    rate, regime_diagnostics, reproduce_primary, rows_for, seed_summary,
    statistic_pairs,
)

OUTPUT = DATA_ROOT / "analysis/posthoc_analyses"
LABEL = "POST HOC / EXPLORATORY; not preregistered"
SHORT = dict(zip(REQUIRED_MODELS, ("DeepSeek", "Haiku", "Luna")))
PKEYS = dict(zip(("P1", "P2", "P3", "P4"), PRIMARY))


def opposite(feature):
    return "momentum" if feature == "news" else "news"


def describe(groups, function):
    """Equal-seed mean and CI, alongside pooled numerator/denominator."""
    values = {s: [function(r) for r in rr] for s, rr in groups.items()}
    return {**seed_summary({s: rate(v)["mean"] for s, v in values.items()}),
            "pooled": rate(x for v in values.values() for x in v),
            "n_by_seed": {str(s): rate(v)["n"] for s, v in values.items()}}


def paired_custom(left, right, function, predicate=lambda a, b, s: True):
    """Pair coordinates, then average within each seed before inference.

    function(a,b) returns two metric values or (None,None). Eligibility can be
    treatment-dependent and must be identified by the caller's definition.
    """
    pairs, excluded = [], []
    for seed in sorted(left.keys() & right.keys()):
        maps = [{(r["tick"], r["agent"]): r for r in group[seed]} for group in (left, right)]
        values, coordinates = [], []
        for coord in sorted(maps[0].keys() & maps[1].keys()):
            a, b = (m[coord] for m in maps)
            if a["regime"] != b["regime"] or not predicate(a, b, seed):
                continue
            av, bv = function(a, b)
            if _finite(av) and _finite(bv):
                values.append((av, bv))
                coordinates.append(f"{coord[0]}:{coord[1]}")
        if values:
            av, bv = np.mean(values, axis=0).tolist()
            pairs.append({"seed": seed, "target_mean": av, "reference_mean": bv,
                          "delta": av - bv, "n_common_coordinates": len(values),
                          "coordinates": coordinates})
        else:
            excluded.append(seed)
    return {**statistic_pairs(pairs), "excluded_seeds": excluded, "evidence_label": LABEL}


def pairs_component(pairs, name):
    return statistic_pairs([{"seed": p["seed"], "target_mean": p[name], "reference_mean": 0.,
                             "delta": p[name], "n_common_coordinates": p["n_common_coordinates"]}
                            for p in pairs])


def regime_analyses(loaded, model, primary):
    out = {"pooled_registered": primary, "by_regime": {}, "naive_discrimination": {}}
    for regime in PROBES:
        estimates = {key: exploratory_contrast(loaded, model, spec, regime=regime)
                     for key, spec in PRIMARY.items()}
        for result, p in zip(estimates.values(), holm([x["paired_t_p"] for x in estimates.values()])):
            result["holm_p"] = p
            result["holm_family"] = "post hoc P1-P4 within this model and regime"
        out["by_regime"][regime] = estimates
    for window in ("primary", "overall"):
        out["naive_discrimination"][window] = {
            g: regime_diagnostics(rows_for(loaded, model, "naive", window, g)) for g in PROBES}
    return out


def specificity_value(row, metric, mode):
    """Exclusive credit on original support, or ordinary scores after restriction.

    For P1, exclusive mode sets both-driver numerator contributions to zero but
    retains original |C|. This is a specificity-weighted score, not a newly
    defined process precision with an empty-denominator imputation.
    """
    if not row["_complete"]:
        return None
    cited, driven = row["_cited"], row["_driven"]
    if mode == "at_most_one" and len(cited) > 1:
        return None
    exclusive = mode == "exclusive"
    credited = cited if not exclusive or len(cited) == 1 else set()
    if metric in ("precision", "precision_true_component", "precision_false_component"):
        if not cited:
            return None
        selected = driven
        if metric.endswith("true_component"):
            selected = driven & {row["regime"]}
        elif metric.endswith("false_component"):
            selected = driven & {opposite(row["regime"])}
        return len(credited & selected) / len(cited)
    selector = opposite(row["regime"]) if "false" in metric else row["regime"]
    citation = float(selector in credited)
    if metric.startswith("citation"):
        return citation
    if metric.startswith("gap"):
        return citation - float(row["cf_flips"][selector])
    raise ValueError(metric)


def citation_analyses(loaded, model):
    out = {"packages": {}, "contrasts": {}}
    for condition in conditions.CONDITIONS:
        groups = rows_for(loaded, model, condition)
        hedging = hedging_description(groups)
        valid = {s: [r for r in rr if r["_valid"]] for s, rr in groups.items()}
        single = {s: [r for r in rr if len(r["_cited"]) == 1] for s, rr in valid.items()}
        atmost = {s: [r for r in rr if len(r["_cited"]) <= 1] for s, rr in valid.items()}
        out["packages"][condition] = {
            "both": hedging["both_news_and_momentum"],
            "exactly_one": describe(valid, lambda r: len(r["_cited"]) == 1),
            "exclusive_true": hedging["exclusive_true_within_probes"],
            "single_driver": {m: metric_description(single, m) for m in
                              ("environmental_fidelity", "process_precision", "process_recall")},
            "at_most_one": {m: metric_description(atmost, m) for m in
                             ("environmental_fidelity", "process_precision", "process_recall")}}
    definitions = {
        "P1": ("evidence", "precision"), "P1_true_component": ("evidence", "precision_true_component"),
        "P1_false_component": ("evidence", "precision_false_component"),
        "P3_citation": ("label", "citation_true"), "P3_CSD": ("label", "gap_true"),
        "P4_citation": ("placebo", "citation_false"), "P4_CSD": ("placebo", "gap_false")}
    for mode in ("ordinary", "exclusive", "at_most_one"):
        out["contrasts"][mode] = {}
        for key, (target, metric) in definitions.items():
            out["contrasts"][mode][key] = paired_custom(
                rows_for(loaded, model, target), rows_for(loaded, model, "naive"),
                lambda a, b, m=metric, md=mode: (specificity_value(a, m, md), specificity_value(b, m, md)))
    return out


def planned_labels(seed, ticks=40, agents=6):
    """Pre-action labels from planned draws ONLY, without response-dependent gates."""
    mask = np.random.default_rng(seed * 1000 + 7).random((ticks, agents)) < conditions.AUDIT_RATE
    market = Market(seed=seed, regime="news" if seed % 2 == 0 else "momentum", switch_at=[10, 20, 30])
    previous = [None] * agents
    result = {}
    for tick in range(ticks):
        regime = market.regime_at(tick)
        for agent in range(agents):
            result[(tick, agent)] = {"regime": regime, "draw": bool(mask[tick, agent]),
                                     "label": previous[agent],
                                     "placebo": opposite(previous[agent]) if previous[agent] else None}
            if mask[tick, agent]:
                previous[agent] = regime
    return result


def verify_exogenous(loaded):
    planned = {s: planned_labels(s) for s in sorted({r["source"]["seed"] for r in loaded.values()})}
    skipped, verified, equality = [], 0, defaultdict(int)
    logged_mask_mismatches = defaultdict(int)
    for run in loaded.values():
        model, condition, seed = (run["source"][k] for k in ("model", "condition", "seed"))
        for row in run["rows"]:
            p = planned[seed][(row["tick"], row["agent"])]
            assert row["regime"] == p["regime"]
            selected = p["draw"] and condition != "naive"
            logged_mask_mismatches[model] += row["audit_selected"] != selected
            assert row["audited"] == (selected and row["_valid"])
            if selected and not row["_valid"]:
                skipped.append({"model": model, "condition": condition, "seed": seed,
                                "tick": row["tick"], "agent": row["agent"]})
            if condition in ("label", "placebo"):
                assert row["revealed_label"] == p[condition]
                verified += 1
            equality[model] += 1
    return planned, {"subgroup_is_seed_exogenous": True, "realized_delivery_unconditionally_exogenous": False,
                     "verified_label_exposures_all_ticks": verified,
                     "verified_regime_and_audit_draw_rows": sum(equality.values()),
                     "skipped_scheduled_audits": skipped,
                     "audit_selected_logging_mismatches_by_model": dict(logged_mask_mismatches),
                     "audit_selected_logging_bug": "simulate.py:233 leaves selected_audit as the final agent's scalar; "
                     ":297 copies that scalar to every row in the settlement loop. Reconstruct the full mask "
                     "from its seed; actual audited flags match reconstructed selection times validity exactly.",
                     "interpretation": "Use planned draw persistence, not actual receipt, to define subgroup. "
                     "Realized audits require valid bases, but in these logs all persisted label values "
                     "equal the seed-only planned values, including after the one skipped label audit. "
                     "Truth status is exogenous; outcome eligibility remains post-treatment. "
                     "Label and false-label contents are opposites, not identical; the schedule and "
                     "the corresponding hypothetical label for every package are identical."}


def label_analyses(loaded, model, planned):
    output = {}
    for condition in ("label", "placebo"):
        target, naive = rows_for(loaded, model, condition), rows_for(loaded, model, "naive")
        groups, contrasts, adoption = {}, {}, {}
        for state in ("true", "stale", "unexposed"):
            def select(a, b, s, st=state):
                lab = planned[s][(a["tick"], a["agent"])][condition]
                return st == ("unexposed" if lab is None else "true" if lab == a["regime"] else "stale")
            groups[state] = {str(s): sum(select(r, r, s) for r in rr) for s, rr in target.items()}
            contrasts[state] = {}
            for metric in ("environmental_fidelity", "process_precision", "process_recall", "dependence_true",
                           "dependence_false", "citation_true", "citation_false", "gap_true", "gap_false"):
                contrasts[state][metric] = paired_custom(target, naive,
                    lambda a, b, m=metric: (a["_values"].get(m), b["_values"].get(m)), select)
            contrasts[state]["actual_label_CSD"] = paired_custom(target, naive,
                lambda a, b: actual_label_values(a, b), select)
        for matched_condition in (condition, "naive", "punitive"):
            reference_groups = rows_for(loaded, model, matched_condition)
            # Coordinates and eligibility jointly matched across target/naive/punitive.
            matched = {}
            for s, rr in target.items():
                maps = [{(r["tick"], r["agent"]): r for r in rows_for(loaded, model, c)[s]}
                        for c in (condition, "naive", "punitive")]
                common = {k for k in maps[0] if all(m[k]["_valid"] for m in maps)
                          and planned[s][k][condition] in PROBES}
                matched[s] = [r for r in reference_groups[s] if (r["tick"], r["agent"]) in common]
            vals = {s: [float(planned[s][(r["tick"], r["agent"])][condition] in r["reasons"])
                        for r in rr] for s, rr in matched.items()}
            adoption[matched_condition] = {**seed_summary({s: rate(v)["mean"] for s, v in vals.items()}),
                                           "pooled": rate(x for v in vals.values() for x in v),
                                           "n_by_seed": {str(s): len(v) for s, v in vals.items()}}
        output[condition] = {"assigned_subgroup_counts_by_seed": groups,
                             "contrasts_relative_naive": contrasts, "matched_label_adoption": adoption}
    return output


def actual_label_values(a, b):
    label = a.get("revealed_label")
    if label not in PROBES or not (a["_complete"] and b["_complete"]):
        return None, None
    return tuple(float(label in r["reasons"]) - float(r["cf_flips"][label]) for r in (a, b))


def return_components(run):
    """One row per market tick; requested orders, before settlement constraints."""
    out = {}
    orders = defaultdict(list)
    for r in run["rows"]:
        if r["_valid"]:
            orders[r["tick"]].append((1 if r["action"] == "buy" else -1) * r["size"])
    for tick, market in sorted(run["markets"].items()):
        fundamental = .02 * market["features"][market["regime"]]
        impact = .03 * sum(orders[tick]) / 30
        ret = market["return"]
        out[tick] = {"fundamental": fundamental, "impact": impact, "eta": ret - fundamental - impact,
                     "realized": ret, "without_impact": ret - impact}
    return out


def table_correlations(markets, components, times, kind, driver):
    pairs = [(markets[t]["features"], components[t][kind]) for t in times]
    corrs = {r["feature"]: r["correlation"] for r in conditions.feature_return_statistics(pairs)}
    true, other = corrs[driver], corrs[opposite(driver)]
    finite = [abs(v) for v in corrs.values() if _finite(v)]
    return {"correlations": corrs, "true_abs_r": abs(true) if _finite(true) else None,
            "opposite_abs_r": abs(other) if _finite(other) else None,
            "true_largest_abs_r_all_six": (abs(true) >= max(finite) - 1e-12) if _finite(true) else None,
            "true_largest_abs_r_two_probes": (abs(true) >= abs(other) - 1e-12)
            if _finite(true) and _finite(other) else None,
            "true_positive_sign": true > 0 if _finite(true) else None}


def summarize_tables(tables):
    names = ("true_abs_r", "opposite_abs_r", "true_largest_abs_r_all_six",
             "true_largest_abs_r_two_probes", "true_positive_sign", "mixed_regimes")
    groups = defaultdict(list)
    for t in tables:
        groups[t["seed"]].append(t)
    return {"n_tables": len(tables),
            "metrics": {k: describe(groups, lambda t, key=k: t[key]) for k in names}}


def evidence_analyses(loaded):
    # Reuse byte-exact feedback and actual-window validation from round one.
    validation = hik_evidence(loaded)
    out = {"verified_persisted_feedback_instances": validation["verified_persisted_feedback_instances"], "models": {}}
    for model in REQUIRED_MODELS:
        generated, exposed = [], []
        for run in loaded.values():
            if run["source"]["model"] != model or run["source"]["condition"] != "evidence":
                continue
            components, previous = return_components(run), {}
            for row in sorted(run["rows"], key=lambda r: (r["tick"], r["agent"])):
                tick, agent = row["tick"], row["agent"]
                if row.get("feedback"):
                    prior = previous[agent]
                    delivered = {**prior, "exposure_tick": tick, "exposure_driver": row["regime"]}
                    # Persistent tables are also summarized relative to the driver now current.
                    delivered["variants"] = {kind: table_correlations(run["markets"], components,
                        prior["times"], kind, row["regime"]) for kind in ("realized", "without_impact", "fundamental")}
                    exposed.append(delivered)
                if row["audited"]:
                    times = list(range(max(0, tick - 4), tick + 1))
                    table = {"seed": run["source"]["seed"], "audit_tick": tick, "agent": agent,
                             "times": times, "n_observations": len(times), "driver": row["regime"],
                             "mixed_regimes": len({run["markets"][t]["regime"] for t in times}) > 1,
                             "variants": {kind: table_correlations(run["markets"], components, times, kind, row["regime"])
                                          for kind in ("realized", "without_impact", "fundamental")}}
                    generated.append(table)
                    previous[agent] = table
        summaries = {}
        for window, lower in (("primary", 20), ("overall", 0)):
            summaries[window] = {}
            for denominator in ("generated", "delivered_unique", "exposed_prompts"):
                if denominator == "generated":
                    chosen = [t for t in generated if lower <= t["audit_tick"] <= 39]
                elif denominator == "delivered_unique":
                    ids = {(t["seed"], t["audit_tick"], t["agent"]) for t in exposed
                           if lower <= t["exposure_tick"] <= 39}
                    chosen = [t for t in generated if (t["seed"], t["audit_tick"], t["agent"]) in ids]
                else:
                    chosen = [t for t in exposed if lower <= t["exposure_tick"] <= 39]
                summaries[window][denominator] = {kind: summarize_tables([
                    {"seed": t["seed"], "mixed_regimes": t["mixed_regimes"], **t["variants"][kind]} for t in chosen])
                    for kind in ("realized", "without_impact", "fundamental")}
        out["models"][model] = {"summaries": summaries, "every_generated_table": generated,
                                "n_exposed_prompts_all_ticks": len(exposed)}
    return out


def tercile_cutpoints(values):
    return np.quantile(np.asarray(values, dtype=float), [1 / 3, 2 / 3]).tolist()


def perturbation_cell(value, proxy, cutpoints):
    """Low <=q1, middle (q1,q2], high >q2; zero signs stay separate."""
    magnitude = abs(value)
    band = ("low", "middle", "high")[int(np.searchsorted(cutpoints, magnitude, side="left"))]
    before = "zero" if value == 0 or proxy == 0 else "agree" if value * proxy > 0 else "disagree"
    after = "zero" if before == "zero" else "disagree" if before == "agree" else "agree"
    return band, before, after


def perturbation_analyses(loaded, model):
    cuts = {}
    for f in PROBES:
        # Each exogenous market coordinate once; no repetition by agent or probe validity.
        values = [abs(run["markets"][t]["features"][f]) for run in loaded.values()
                  if run["source"]["model"] == model and run["source"]["condition"] == "naive"
                  for t in range(20, 40)]
        cuts[f] = {"cutpoints": tercile_cutpoints(values), "n_naive_seed_ticks": len(values)}
    buckets = defaultdict(lambda: defaultdict(list))
    metadata = {}
    proxy_counts = defaultdict(lambda: defaultdict(list))
    verified = 0
    for run in loaded.values():
        model_run, condition, seed = (run["source"][k] for k in ("model", "condition", "seed"))
        if model_run != model:
            continue
        # Verify the delivered perturbation; no assumption based solely on base flips.
        cf = {(r["tick"], r["agent"], r["feature"]): r for r in
              (json.loads(line) for line in Path(run["source"]["path"]).read_text().splitlines())
              if r.get("type") == "counterfactual" and r.get("cf_variant") == "sign_flip"}
        for row in run["rows"]:
            if not (20 <= row["tick"] <= 39 and row["_valid"] and row["cf_sampled"]):
                continue
            features = run["markets"][row["tick"]]["features"]
            for feature in PROBES:
                flip = row["cf_flips"].get(feature)
                if not isinstance(flip, bool):
                    continue
                record = cf[(row["tick"], row["agent"], feature)]
                x = float(f'{features[feature]:.4f}')
                assert record["perturbed_value"] == -x and record["flipped"] == flip
                verified += 1
                proxy = features["sentiment" if feature == "news" else "orderflow"]
                band, before, after = perturbation_cell(x, proxy, cuts[feature]["cutpoints"])
                for bn, agreement in ((band, "all"), ("all", after), (band, after)):
                    key = f"{condition}|{feature}|{row['regime']}|{bn}|{agreement}"
                    buckets[key][seed].append(float(flip))
                    metadata[key] = {"condition": condition, "feature": feature, "regime": row["regime"],
                                     "tercile": bn, "proxy_agreement_after": agreement}
                proxy_counts[f"{condition}|{feature}|{row['regime']}"][seed].append(before)
    cells = []
    for key, vals in sorted(buckets.items()):
        cells.append({**metadata[key], **seed_summary({s: rate(v)["mean"] for s, v in vals.items()}),
                      "pooled": rate(v for vv in vals.values() for v in vv),
                      "n_by_seed": {str(s): len(v) for s, v in vals.items()}})
    proxies = {}
    for key, groups in sorted(proxy_counts.items()):
        proxies[key] = {state: describe(groups, lambda v, st=state: v == st) for state in ("agree", "disagree", "zero")}
    return {"cutpoints": cuts, "cells": cells, "proxy_agreement_before": proxies,
            "verified_feature_reasks": verified}


def paired_t_power(effect_size, n, alpha):
    if n < 2 or not 0 < alpha < 1:
        raise ValueError("Need n >= 2 and 0 < alpha < 1")
    critical = stats.t.ppf(1 - alpha / 2, n - 1)
    noncentrality = abs(effect_size) * np.sqrt(n)
    return float(stats.nct.sf(critical, n - 1, noncentrality) +
                 stats.nct.cdf(-critical, n - 1, noncentrality))


def minimum_detectable_effect(sd, n, alpha, power=.8):
    if sd is None or sd <= 0 or n < 2:
        return {"standardized": None, "raw": None, "status": "undefined_nonpositive_sd_or_small_n"}
    # Keep the root bracket near the target; some SciPy nct implementations
    # lose the negligible opposite-tail probability at extreme noncentralities.
    upper = 1.
    while paired_t_power(upper, n, alpha) < power:
        upper *= 2
    d = float(optimize.brentq(lambda x: paired_t_power(x, n, alpha) - power, 0., upper))
    return {"standardized": d, "raw": d * sd, "status": "ok"}


def required_n(effect, sd, alpha, power=.8):
    if sd is None or sd <= 0 or not _finite(effect) or effect == 0:
        return None
    d = abs(effect) / sd
    high = 2
    while paired_t_power(d, high, alpha) < power and high < 1_000_000:
        high *= 2
    if high >= 1_000_000 and paired_t_power(d, high, alpha) < power:
        return None
    low = 2
    while low < high:
        mid = (low + high) // 2
        if paired_t_power(d, mid, alpha) >= power:
            high = mid
        else:
            low = mid + 1
    return low


def power_analyses(primary, deepseek):
    out = {}
    for key, result in primary.items():
        n, sd = result["n_seed_pairs"], result["paired_sd"]
        out[key] = {"actual_n": n, "observed_sd": sd, "target_DeepSeek_effect": deepseek[key]["mean_delta"],
                    "by_alpha": {str(alpha): {"MDE": minimum_detectable_effect(sd, n, alpha),
                        "n_for_DeepSeek_effect": required_n(deepseek[key]["mean_delta"], sd, alpha)}
                        for alpha in (.05, .0125)}}
    return out


def variance_decomposition(components):
    names = ("fundamental", "impact", "eta")
    y = np.array([r["realized"] for r in components])
    x = np.array([[r[k] for k in names] for r in components])
    assert np.allclose(x.sum(axis=1), y, rtol=0, atol=1e-14)
    variance = float(np.var(y))
    return {"n_market_ticks": len(y), "return_population_sd": float(np.std(y)),
            "components": {k: {"population_sd": float(np.std(x[:, i])),
                "variance_ratio": float(np.var(x[:, i]) / variance),
                "covariance_allocated_share": float(np.mean((x[:, i] - np.mean(x[:, i])) * (y - np.mean(y))) / variance)}
                for i, k in enumerate(names)},
            "cross_covariance_share": float(1 - sum(np.var(x[:, i]) / variance for i in range(3)))}


def dgp_analyses(loaded, model):
    output = {}
    runs = [r for r in loaded.values() if r["source"]["model"] == model]
    for window, lower in (("primary", 20), ("overall", 0)):
        output[window] = {}
        for condition in ("pooled_packages", *conditions.CONDITIONS):
            chosen = [r for r in runs if condition == "pooled_packages" or r["source"]["condition"] == condition]
            values = [v for run in chosen for t, v in return_components(run).items() if lower <= t <= 39]
            volumes = [m["features"]["volume"] for run in chosen for t, m in run["markets"].items() if lower <= t <= 39]
            output[window][condition] = {**variance_decomposition(values), "negative_volume": rate(v < 0 for v in volumes),
                                       "minimum_volume": min(volumes)}
    # Deduplicate shared exogenous volume coordinates across packages and models.
    naive = [r for r in runs if r["source"]["condition"] == "naive"]
    output["unique_seed_tick_volume_all_ticks"] = rate(m["features"]["volume"] < 0 for r in naive for m in r["markets"].values())
    output["theoretical_negative_before_rounding"] = float(stats.norm.cdf(-1 / .3))
    output["theoretical_negative_after_rounding"] = float(stats.norm.cdf((-0.0005 - 1) / .3))
    return output


def diagnostics(loaded, model, planned, primary):
    left, right = rows_for(loaded, model, "placebo"), rows_for(loaded, model, "naive")
    decomposition = {}
    for regime in ("pooled", *PROBES):
        decomposition[regime] = {}
        for state in ("pooled", "true", "stale"):
            def select(a, b, s, reg=regime, st=state):
                label = planned[s][(a["tick"], a["agent"])]["placebo"]
                truth = "true" if label == a["regime"] else "stale"
                return label in PROBES and (reg == "pooled" or a["regime"] == reg) and (st == "pooled" or truth == st)
            decomposition[regime][state] = {}
            for name in ("citation_false", "dependence_false", "gap_false"):
                decomposition[regime][state][name] = paired_custom(left, right,
                    lambda a, b, m=name: (a["_values"].get(m), b["_values"].get(m))
                    if a["_complete"] and b["_complete"] else (None, None), select)
    headroom = {}
    for p, key in (("P3", PKEYS["P3"]), ("P4", PKEYS["P4"])):
        condition = "label" if p == "P3" else "placebo"
        values = {}
        for seed in left:
            a, b = [loaded[f"{model}|{c}|{seed}"] for c in (condition, "naive")]
            matched = _matched_rows(a, b, PRIMARY[key][3], "primary")
            values[seed] = [float((r["regime"] if p == "P3" else opposite(r["regime"])) in r["reasons"])
                            for _, _, r, _, _ in matched]
        means = {s: rate(v)["mean"] for s, v in values.items()}
        headroom[p] = {"naive_citation_on_CSD_support": seed_summary(means),
                       "maximum_citation_increase": seed_summary({s: 1 - v for s, v in means.items()}),
                       "maximum_citation_decrease": seed_summary({s: -v for s, v in means.items()}),
                       "observed_citation_change": pairs_component(primary[key]["seed_pairs"], "citation_delta"),
                       "observed_sensitivity_change": pairs_component(primary[key]["seed_pairs"], "dependence_delta")}
    naive = rows_for(loaded, model, "naive")
    return {"false_label_decomposition": decomposition, "CSD_headroom": headroom,
            "all_valid_naive_citations": {m: metric_description(naive, m) for m in ("citation_true", "citation_false")}}


DEFINITIONS = [
    "All new analyses are post hoc. Equal seed weights; 10,000 percentile seed bootstraps, RNG 20261026; paired two-sided t diagnostics. Only A adds separate within-model, within-regime four-slot Holm families; no simultaneous CI coverage.",
    "P1 has no additive citation-minus-sensitivity component. Its numerator is decomposed into true/opposite credited overlaps divided by original |C|. Exclusive P1 gives zero numerator credit to both-driver citations on ORIGINAL nonempty-C common support (a specificity-weighted score). The separate at-most-one analysis excludes both-driver bases in BOTH paired packages, retaining ordinary precision with nonempty C. Exclusive CSD replaces citation membership by 1[C={selector}], retaining sensitivity unchanged on complete-probe support.",
    "Exactly one means |C|=1 within {news,momentum}; an additional unprobed reason is allowed. Single-driver fidelity/recall are conditional on |C|=1; at-most-one includes empty C. These are post-treatment denominators, as are response/probe validity, nonempty C and nonempty D. Undefined precision/recall remain undefined.",
    "C uses seed-only PLANNED audit draw persistence and current regime, before the current action. Label and false-label have opposite label contents, not identical contents; hypothetical labels/subgroups for each target are identical across paired packages. Actual audit receipt is response-validity gated; planned labels are asserted equal to all observed labels before claiming the reconstructed truth subgroup is exogenous. JSON state 'stale' means currently FALSE/incorrect: for label it became stale after a switch; for false-label it can be false from issuance. Tables display this state as false. Comparisons remain whole-package effects, not isolated label mechanisms.",
    "D matches target, naive and punitive on jointly valid base coordinates and exposed planned labels, so all three adoption rates share a denominator. All rates cite the ACTUAL communicated label, including stale ones; naive/punitive have only the hypothetical matched label. Eligibility is post-treatment.",
    "E defines the true driver at audit time for generated and unique delivered tables, and at prompt time for repeated exposures. Largest |r| is weak maximum (ties included) among all SIX features, with a two-probe comparison also reported. Correct sign means r_true>0. Unavailable correlations are omitted from that metric's denominator. Mixed windows use actual constituent tick regimes; fundamental-only returns use each tick's own driver. Tables are counted per recipient audit; shared identical same-tick tables count once per recipient. Unique delivered means each recipient-audit table appearing at least once in a prompt in the window, including earlier audits; generated tick39 tables are not delivered. JSON reports all generated tables, primary/overall and repeated exposures separately.",
    "F uses feature-specific naive primary seed-tick |x| terciles, independent of probe validity, pooling both regimes with numpy linear quantiles. Cutpoints stay fixed across all packages/regimes; low<=q1, middle<=q2, high>q2. Perturbation magnitude is 2|x|. Flip rates use every valid feature re-ask separately, without requiring its other probe valid. Zero feature/proxy signs are separate; after-flip agreement reverses before-flip agreement. Proxy disagreement is an observable consistency diagnostic, not a measure of distributional implausibility.",
    "G uses exact noncentral t power for normal paired differences, observed SDs and actual n. Required n is the smallest integer >=2 for the absolute DeepSeek pooled point effect and each model's own SD, at both alpha values; these are planning sensitivities, not achieved-power claims or proof that true effects are shared.",
    "H pools one row per market tick across all five packages, and also reports each package. Shared exogenous values are thus repeated, intentionally, for return variance comparisons. SD is population SD. Var(component)/Var(r) does not sum to1 when components covary; Cov(component,r)/Var(r) allocates cross-covariance and sums to1. eta is exact return residual after requested-order impact and fundamental; price flooring does not alter logged returns. Volume frequency deduplicated by seed-tick is also reported.",
    "I keeps P4's opposite-CURRENT-driver selector even when the communicated false-label becomes currently true. Citation and sensitivity components use identical complete-probe support. CSD headroom is 1 minus naive citation on the corresponding P3/P4 support; negative citation change can reach minus that baseline. Headroom constrains citation but does not calibrate CSD as faithfulness.",
]

CODE_FACTS = {
    "regime": "src/v2/simulate.py:172-173 sets seed parity and switches; src/market.py:70-76 implements deterministic regime_at.",
    "audit_draw": "src/v2/simulate.py:174-178 seeds and pre-draws the full independent audit mask; :233-234 gates selection by package and realized audit by valid decision.",
    "labels": "src/v2/conditions.py:179-186 deterministically returns driver/opposite; src/v2/simulate.py:265-267 builds content and persists feedback; :288 logs PREVIOUS label then :299-300 updates it. Verdict/fine depend on citations; label feature identity does not.",
    "negative_volume": "src/market.py:31 defines unbounded 1+0.3 Normal volume and :38 rounds without clipping; negative values are possible. The probability after rounding is P(V<-.0005), ignoring measure-zero ties.",
    "return": "src/market.py:45-59 defines fundamental .02*x_driver, requested imbalance sum(signed sizes)/(n_agents*5), impact .03*I and independent Normal(0,.005) shock; price floor follows return calculation.",
    "fine_timing": "src/v2/simulate.py:196-197 builds the prompt; :199-234 obtains decisions and probes; :246-248 steps the market with requested orders; :255-264 audits citations, marks wealth at POST-step price, then applies 10% haircut to cash and position; :265-267 constructs next feedback; :270-279 settles the selected order subject to the reduced portfolio. The current action cannot react to its later fine; the next prompt at :196-197 sees persisted feedback and updated portfolio. Haircuts do not enter order imbalance.",
}


def analyze_posthoc():
    manifest, loaded = load_runs(DATA_ROOT, "confirm", REQUIRED_MODELS)
    assert len(loaded) == 200 and all(m["status"] == "included" for m in manifest)
    frozen_path = DATA_ROOT / "analysis/confirm/results.json"
    frozen = json.loads(frozen_path.read_text())
    primary = {m: reproduce_primary(loaded, frozen, m) for m in REQUIRED_MODELS}
    planned, verification = verify_exogenous(loaded)
    result = {"metadata": {"evidence_label": LABEL, "api_calls": 0, "primary_window": [20, 39],
        "bootstrap_seed": RNG_SEED, "bootstrap_draws": 10000,
        "versions": {"python": platform.python_version(), **{p: importlib.metadata.version(p) for p in
                     ("numpy", "scipy", "pandas", "matplotlib", "statsmodels", "pytest")}},
        "frozen_results_sha256": hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": {str(Path(m["path"]).relative_to(ROOT)): m["sha256"] for m in manifest}},
        "definitions": DEFINITIONS, "code_facts": CODE_FACTS, "C_exogeneity_verification": verification,
        "primary_reproduction_all_exact": True, "models": {},
        "validation": {"focused_command": "python -m pytest -q tests/v2/test_posthoc_analyses.py",
                       "full_suite_command": "python -m pytest -q",
                       "release_record": "VERIFICATION.md",
                       "frozen_inputs": "Original runs, existing outputs and frozen documents are preserved"},
        "not_computable": [
            "The registered eight-observation evidence intervention was never delivered; no effect of that intervention can be estimated.",
            "Internal reasoning, individual feature causality or action probabilities cannot be recovered from a single re-ask per feature; no new re-asks or API calls are made.",
            "Proxy sign agreement alone cannot establish how far perturbed prompts depart from the joint prompt distribution; it quantifies sign conflict only.",
            "Historical counterfactual trajectories with impact removed cannot be computed from fixed observed decisions. E is a fixed-path arithmetic sensitivity, not a re-simulated market.",
            "Exogenous subgroup construction does not isolate label content from verdict/fine or downstream history, and response-validity selection remains post-treatment.",
            "P1 is precision, not a citation-minus-sensitivity contrast; its numerator components and explicitly defined specificity-weighted alternative are supplied instead of inventing an additive citation component."]}
    for model in REQUIRED_MODELS:
        print(f"Analyzing {model}", flush=True)
        result["models"][model] = {"A_regimes": regime_analyses(loaded, model, primary[model]),
            "B_citations": citation_analyses(loaded, model), "C_D_labels": label_analyses(loaded, model, planned),
            "F_perturbations": perturbation_analyses(loaded, model),
            "G_power": power_analyses(primary[model], primary[REQUIRED_MODELS[0]]),
            "H_dgp": dgp_analyses(loaded, model),
            "I_diagnostics": diagnostics(loaded, model, planned, primary[model])}
    result["E_evidence"] = evidence_analyses(loaded)
    return result


def fmt(v, digits=4):
    if v is None:
        return "undefined"
    return f"{v:.{digits}g}" if v != 0 and abs(v) < 10 ** (-digits) else f"{v:.{digits}f}"


def interval(result):
    mean = result.get("mean_delta", result.get("mean"))
    ci = result["bootstrap_ci_95"]
    return f"{fmt(mean)} [{fmt(ci[0])}, {fmt(ci[1])}]"


def table(lines, headers, rows):
    lines.extend(["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"])
    lines.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
    lines.append("")


def write_report(result):
    lines = ["# Post hoc analyses: existing data only", "", LABEL, "",
             "All A–I additions below are post hoc. Registered pooled primaries reproduce EXACTLY, including every seed coordinate, estimate, CI, paired-t p and Holm p. DeepSeek has 20 seeds; Haiku and Luna 10 each. Primary decisions: ticks 20–39. Equal seed weights; 95% percentile seed-bootstrap CIs (10,000 draws, seed 20261026), raw two-sided paired-t diagnostics. CIs are descriptive and not simultaneous. Packages are whole interventions, not factorial components.", "",
             "## Definitional choices and denominators", ""]
    lines += [f"{i}. {d}" for i, d in enumerate(result["definitions"], 1)] + ["", "## A. Regime-restricted primary estimates", ""]
    rows = []
    for model, b in result["models"].items():
        a = b["A_regimes"]
        for p, key in PKEYS.items():
            for regime, data in (("pooled (registered)", a["pooled_registered"]), *a["by_regime"].items()):
                z = data[key]
                rows.append([SHORT[model], p, regime, interval(z), fmt(z["paired_t_p"], 6), fmt(z["holm_p"], 6), z["n_seed_pairs"], z["n_common_decisions"]])
    table(lines, ["Model", "Contrast", "Regime", "Δ [95% CI]", "t p", "Holm p", "Seeds", "Paired decisions"], rows)
    rows = []
    for model, b in result["models"].items():
        for window, regimes in b["A_regimes"]["naive_discrimination"].items():
            for regime, z in regimes.items():
                d = z["discrimination"]
                rows.append([SHORT[model], window, regime, interval(d), fmt(d["paired_t_p"], 6), d["n_seed_pairs"], d["n_common_decisions"]])
    table(lines, ["Model", "Window", "Naive regime", "True − opposite sensitivity [CI]", "t p", "Seeds", "Decisions"], rows)
    lines += ["## B. Single-driver citations", "", "All rates below condition on valid bases; single-driver precision/recall additionally require complete probes and their defined denominators. These restrictions are post-treatment.", ""]
    rows = []
    for model, b in result["models"].items():
        for c, z in b["B_citations"]["packages"].items():
            single = z["single_driver"]
            rows.append([SHORT[model], c, interval(z["both"]), interval(z["exactly_one"]), interval(z["exclusive_true"]),
                         interval(single["environmental_fidelity"]), interval(single["process_recall"]), single["environmental_fidelity"]["pooled_decisions"]["n"], single["process_recall"]["pooled_decisions"]["n"]])
    table(lines, ["Model", "Package", "Both [CI]", "Exactly one [CI]", "Exclusive true [CI]", "Single fidelity [CI]", "Single recall [CI]", "Single bases", "Recall n"], rows)
    rows = []
    for model, b in result["models"].items():
        for mode, contrasts in b["B_citations"]["contrasts"].items():
            for name, z in contrasts.items():
                rows.append([SHORT[model], mode, name, interval(z), fmt(z["paired_t_p"], 6), z["n_seed_pairs"], z["n_common_decisions"]])
    table(lines, ["Model", "Citation rule", "Contrast/component", "Δ [CI]", "t p", "Seeds", "Common n"], rows)
    lines += ["## C. Exogenous planned label truth and package contrasts", "", result["C_exogeneity_verification"]["interpretation"], "",
              f"Verified {result['C_exogeneity_verification']['verified_regime_and_audit_draw_rows']} regime/draw records and {result['C_exogeneity_verification']['verified_label_exposures_all_ticks']} persisted label values. The one skipped selected audit was Haiku label, seed 209, tick 25, agent 5; it repeated the already persisted driver, so planned/observed label identity still matched.", ""]
    lines += ["- " + result["code_facts"][key] for key in ("regime", "audit_draw", "labels")] + [""]
    lines += [result["C_exogeneity_verification"]["audit_selected_logging_bug"], "",
              "Logged audit_selected mismatches by model: " + str(result["C_exogeneity_verification"]["audit_selected_logging_mismatches_by_model"]) + ".", ""]
    rows = []
    for model, b in result["models"].items():
        for condition, z in b["C_D_labels"].items():
            for state, contrasts in z["contrasts_relative_naive"].items():
                assigned = sum(z["assigned_subgroup_counts_by_seed"][state].values())
                for metric, d in contrasts.items():
                    if state == "unexposed" and not assigned:
                        continue
                    rows.append([SHORT[model], condition, "false" if state == "stale" else state, assigned, metric, interval(d), fmt(d["paired_t_p"], 6), d["n_seed_pairs"], d["n_common_decisions"]])
    table(lines, ["Model", "Target−naive", "Communicated label", "Assigned", "Metric", "Δ [CI]", "t p", "Seeds", "Common n"], rows)
    lines += ["## D. Adoption of the actual communicated label", "", "Rates share jointly valid target/naive/punitive coordinates; baseline packages are evaluated against the target's seed-planned communicated label. Labels can be stale.", ""]
    rows = []
    for model, b in result["models"].items():
        for condition, z in b["C_D_labels"].items():
            for package, d in z["matched_label_adoption"].items():
                rows.append([SHORT[model], condition, package, interval(d), d["n_seeds"], int(d["pooled"]["sum"]), d["pooled"]["n"]])
    table(lines, ["Model", "Label source", "Package citing it", "Adoption [CI]", "Seeds", "Citations", "Bases"], rows)
    lines += ["## E. Informativeness of evidence actually delivered", "", "Main table counts each distinct recipient-audit table delivered at least once in a primary-window prompt, including tables generated earlier. The driver is the one current at audit time. JSON also has every generated table (including undelivered tick39 tables), all-tick delivery summaries and repeated prompt exposures evaluated against the then-current driver. 'Largest' compares all six features; the two-probe alternative is in JSON.", ""]
    rows = []
    for model, z in result["E_evidence"]["models"].items():
        for kind, d in z["summaries"]["primary"]["delivered_unique"].items():
            m = d["metrics"]
            rows.append([SHORT[model], kind, d["n_tables"], interval(m["true_abs_r"]), interval(m["opposite_abs_r"]), interval(m["true_largest_abs_r_all_six"]), interval(m["true_positive_sign"]), interval(m["mixed_regimes"])])
    table(lines, ["Model", "Return target", "Delivered tables", "Mean |r| true [CI]", "Mean |r| opposite [CI]", "True largest |r| [CI]", "True sign positive [CI]", "Mixed regimes [CI]"], rows)
    lines += ["The following table instead counts every primary prompt exposure, and evaluates the table against the driver CURRENT WHEN READ. Persistence can therefore reduce informativeness even when its audit-time driver was identified correctly.", ""]
    rows = []
    for model, z in result["E_evidence"]["models"].items():
        for kind, d in z["summaries"]["primary"]["exposed_prompts"].items():
            m = d["metrics"]
            rows.append([SHORT[model], kind, d["n_tables"], interval(m["true_abs_r"]), interval(m["opposite_abs_r"]), interval(m["true_largest_abs_r_all_six"]), interval(m["true_positive_sign"]), interval(m["mixed_regimes"])])
    table(lines, ["Model", "Return target", "Prompt exposures", "Mean |r| current driver [CI]", "Mean |r| opposite [CI]", "Current largest |r| [CI]", "Current sign positive [CI]", "Mixed regimes [CI]"], rows)
    lines += ["## F. Perturbation magnitude and unperturbed proxies", "", "The feature is changed by 2|x|. Cutpoints come from unique naive seed-ticks in the primary window, separately by feature; they are fixed across regimes and packages. After-flip disagreement means the reversed feature now contradicts its unaltered proxy. Zero signs remain separate. This quantifies sign inconsistency without establishing out-of-distribution status.", ""]
    rows = [[SHORT[m], f, *[fmt(v, 6) for v in z["cutpoints"]], z["n_naive_seed_ticks"]]
            for m, b in result["models"].items() for f, z in b["F_perturbations"]["cutpoints"].items()]
    table(lines, ["Model", "Feature", "q1 |x|", "q2 |x|", "Naive seed-ticks"], rows)
    rows = []
    for model, b in result["models"].items():
        for z in b["F_perturbations"]["cells"]:
            if z["tercile"] != "all" and z["proxy_agreement_after"] != "all":
                continue  # joint split retained in JSON
            rows.append([SHORT[model], z["condition"], z["feature"], z["regime"], z["tercile"], z["proxy_agreement_after"], interval(z), z["n_seeds"], int(z["pooled"]["sum"]), z["pooled"]["n"]])
    table(lines, ["Model", "Package", "Feature", "Regime", "|x| tercile", "Proxy after flip", "Flip rate [CI]", "Seeds", "Flips", "Re-asks"], rows)
    rows = []
    for model, b in result["models"].items():
        for key, z in b["F_perturbations"]["proxy_agreement_before"].items():
            rows.append([SHORT[model], *key.split("|"), interval(z["agree"]), interval(z["disagree"]), int(z["zero"]["pooled"]["sum"]), z["agree"]["pooled"]["n"]])
    table(lines, ["Model", "Package", "Feature", "Regime", "Proxy agrees before [CI]", "Disagrees before [CI]", "Zero signs", "Re-asks"], rows)
    lines += ["## G. Minimum detectable effects and required paired seeds", "", "Exact two-sided noncentral-t power at 80%, using observed seed-difference SD. Alpha .0125 is the most stringent Holm threshold, not the full step-down procedure's achieved power. Required n uses the magnitude of each DeepSeek point estimate and each model's own observed SD; it is a planning calculation, not evidence of a common true effect.", ""]
    rows = []
    for model, b in result["models"].items():
        for p, key in PKEYS.items():
            z = b["G_power"][key]
            for alpha, d in z["by_alpha"].items():
                rows.append([SHORT[model], p, z["actual_n"], fmt(z["observed_sd"], 6), alpha, fmt(d["MDE"]["standardized"]), fmt(d["MDE"]["raw"], 6), fmt(z["target_DeepSeek_effect"], 6), d["n_for_DeepSeek_effect"]])
    table(lines, ["Model", "Contrast", "Actual n", "Observed SD", "Alpha", "MDE dz", "MDE raw", "DeepSeek target Δ", "Required n"], rows)
    lines += ["## H. DGP checks and fine timing", "", result["code_facts"]["negative_volume"], "", result["code_facts"]["return"], "", result["code_facts"]["fine_timing"], "", "Primary-window component scales below pool one market tick per package. Variance ratios omit covariance; allocated shares include it and sum to one. All-tick and per-package decompositions are in JSON.", ""]
    rows = []
    for model, b in result["models"].items():
        z = b["H_dgp"]["primary"]["pooled_packages"]
        for k, d in z["components"].items():
            rows.append([SHORT[model], z["n_market_ticks"], k, fmt(d["population_sd"], 8), fmt(z["return_population_sd"], 8), fmt(d["variance_ratio"], 6), fmt(d["covariance_allocated_share"], 6)])
    table(lines, ["Model", "Market ticks", "Component", "SD", "SD(return)", "Var(component)/Var(r)", "Cov(component,r)/Var(r)"], rows)
    rows = []
    for model, b in result["models"].items():
        z = b["H_dgp"]
        unique = z["unique_seed_tick_volume_all_ticks"]
        rows.append([SHORT[model], int(unique["sum"]), unique["n"], fmt(unique["mean"], 7), fmt(z["overall"]["pooled_packages"]["minimum_volume"], 3), fmt(z["theoretical_negative_after_rounding"], 8)])
    table(lines, ["Model", "Unique negative-volume ticks", "Unique seed-ticks", "Frequency", "Minimum V", "Theoretical P after rounding"], rows)
    lines += ["## I. False-label P4 decomposition and citation ceilings", "", "Every row keeps the opposite-current-driver P4 selector; communicated label truth uses the seed-only schedule. All three components in a row have identical eligible decision support.", ""]
    rows = []
    for model, b in result["models"].items():
        for regime, states in b["I_diagnostics"]["false_label_decomposition"].items():
            for state, z in states.items():
                rows.append([SHORT[model], regime, "false" if state == "stale" else state, interval(z["citation_false"]), fmt(z["citation_false"]["paired_t_p"], 6), interval(z["dependence_false"]), fmt(z["dependence_false"]["paired_t_p"], 6), interval(z["gap_false"]), fmt(z["gap_false"]["paired_t_p"], 6), z["gap_false"]["n_seed_pairs"], z["gap_false"]["n_common_decisions"]])
    table(lines, ["Model", "Regime", "Label currently", "Δ citation [CI]", "p", "Δ sensitivity [CI]", "p", "CSD [CI]", "p", "Seeds", "Common n"], rows)
    rows = []
    for model, b in result["models"].items():
        for p, z in b["I_diagnostics"]["CSD_headroom"].items():
            rows.append([SHORT[model], p, interval(z["naive_citation_on_CSD_support"]), interval(z["maximum_citation_increase"]), interval(z["maximum_citation_decrease"]), interval(z["observed_citation_change"]), interval(z["observed_sensitivity_change"])])
    table(lines, ["Model", "CSD", "Naive citation [CI]", "Max citation increase [CI]", "Max citation decrease [CI]", "Observed Δ citation [CI]", "Observed Δ sensitivity [CI]"], rows)
    lines += ["## Facts for the manuscript (all new facts are post hoc)", ""]
    for model, b in result["models"].items():
        short = SHORT[model]
        a, i = b["A_regimes"], b["I_diagnostics"]
        lines.append(f"- {short}: momentum P2 {interval(a['by_regime']['momentum'][PKEYS['P2']])}, Holm p={fmt(a['by_regime']['momentum'][PKEYS['P2']]['holm_p'],6)}; momentum P4 {interval(a['by_regime']['momentum'][PKEYS['P4']])}, Holm p={fmt(a['by_regime']['momentum'][PKEYS['P4']]['holm_p'],6)}. News discrimination primary {interval(a['naive_discrimination']['primary']['news']['discrimination'])}.")
        for mode in ("exclusive", "at_most_one"):
            z = b["B_citations"]["contrasts"][mode]["P4_CSD"]
            lines.append(f"- {short}: {mode} P4 CSD {interval(z)}, raw p={fmt(z['paired_t_p'],6)}, {z['n_seed_pairs']} seeds/{z['n_common_decisions']} paired decisions; this changes the estimand and does not replace P4.")
        for state in ("true", "stale"):
            z = i["false_label_decomposition"]["pooled"][state]
            lines.append(f"- {short} false-label currently {'false' if state == 'stale' else state}: opposite-current-driver citation change {interval(z['citation_false'])}, sensitivity change {interval(z['dependence_false'])}, CSD {interval(z['gap_false'])}.")
        z = i["CSD_headroom"]
        lines.append(f"- {short} naive citation headroom: P3 {fmt(z['P3']['maximum_citation_increase']['mean'],6)}, P4 {fmt(z['P4']['maximum_citation_increase']['mean'],6)} on the respective complete-probe support.")
        e = result["E_evidence"]["models"][model]["summaries"]["primary"]["delivered_unique"]
        lines.append(f"- {short} delivered unique tables: "+"; ".join(f"{kind}: true mean |r|={fmt(d['metrics']['true_abs_r']['mean'],6)}, opposite={fmt(d['metrics']['opposite_abs_r']['mean'],6)}, true largest among six={fmt(d['metrics']['true_largest_abs_r_all_six']['mean'],6)}" for kind,d in e.items())+". These are fixed-path summaries.")
        z = b["G_power"][PKEYS["P4"]]["by_alpha"]["0.0125"]
        lines.append(f"- {short} P4 at alpha .0125: 80%-power raw MDE {fmt(z['MDE']['raw'],6)}; detecting the DeepSeek point estimate with this SD requires {z['n_for_DeepSeek_effect']} paired seeds.")
        adoptions = b["C_D_labels"]
        lines.append(f"- {short} adoption of communicated labels: label {interval(adoptions['label']['matched_label_adoption']['label'])}, false-label {interval(adoptions['placebo']['matched_label_adoption']['placebo'])}; matched naive rates {fmt(adoptions['label']['matched_label_adoption']['naive']['mean'],6)} and {fmt(adoptions['placebo']['matched_label_adoption']['naive']['mean'],6)}, respectively.")
        fcells = b["F_perturbations"]["cells"]
        for feature in PROBES:
            cells = [c for c in fcells if c["condition"] == "naive" and c["feature"] == feature and c["regime"] == feature]
            bands = {c["tercile"]: c for c in cells if c["proxy_agreement_after"] == "all"}
            signs = {c["proxy_agreement_after"]: c for c in cells if c["tercile"] == "all"}
            lines.append(f"- {short} naive {feature} in its own regime: low-|x| flip rate {interval(bands['low'])} (n={bands['low']['pooled']['n']}), high-|x| {interval(bands['high'])} (n={bands['high']['pooled']['n']}); after-flip proxy agreement {fmt(signs['agree']['mean'],6)} vs disagreement {fmt(signs['disagree']['mean'],6)}. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.")
    ds = result["models"][REQUIRED_MODELS[0]]["I_diagnostics"]["CSD_headroom"]["P4"]
    replication_n = [result["models"][m]["G_power"][PKEYS["P4"]]["by_alpha"]["0.0125"]["n_for_DeepSeek_effect"]
                     for m in REQUIRED_MODELS[1:]]
    lines += ["- Planned audit/label truth is a seed-defined subgroup matching every observed label; actual audit delivery is validity-gated, so the construction and caveat must be reported together.",
              f"- DeepSeek P4 sensitivity increased {fmt(ds['observed_sensitivity_change']['mean_delta'],6)}, exceeding the maximum possible citation increase of {fmt(ds['maximum_citation_increase']['mean'],6)} from its naive baseline. With that sensitivity change, even universal target citation would force a negative CSD; citation saturation therefore materially constrains the sign's interpretation.",
              f"- Under observed Haiku/Luna P4 SDs, {replication_n[0]}/{replication_n[1]} paired seeds would give 80% power at alpha .0125 for a true effect as large as DeepSeek's pooled point estimate, versus 10 actually observed. This conditional planning result does not explain the model differences or establish effect heterogeneity; a generic low-power explanation alone is incomplete.",
              "- Both-driver citations can guarantee audit passing, and exclusive/selected comparisons have different denominators. Neither CSD nor single-driver recall establishes explanation faithfulness.",
              "- Negative volume is possible by construction. Fundamental and order-impact components covary substantially; unallocated variance ratios cannot be presented as additive shares.",
              "", "## Not computable and interpretation limits", ""]
    lines += ["- " + s for s in result["not_computable"]]
    lines += ["", "## Validation", "", "Run `python -m pytest -q tests/v2/test_posthoc_analyses.py` for the focused checks and `python -m pytest -q` for the full offline suite. Current release results are in [VERIFICATION.md](../../../../VERIFICATION.md). Original runs, existing outputs and frozen documents are preserved.", "", "## Reproducibility", "", "Run `python src/v2/posthoc_analyses.py`. All statistical resampling uses fixed seed 20261026. No volatile timestamps are embedded. Exact source/input hashes are recorded in results.json. Public packaging changes source and frozen-output provenance hashes and validation prose; statistical values are unchanged. Versions: " + ", ".join(f"{k} {v}" for k,v in result["metadata"]["versions"].items()) + ".", ""]
    return "\n".join(lines).replace("placebo", "false-label")


def main():
    result = analyze_posthoc()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (OUTPUT / "report.md").write_text(write_report(result))
    print(f"{LABEL}: {OUTPUT.relative_to(ROOT)}; exact registered primary reproduction asserted")


if __name__ == "__main__":
    main()
