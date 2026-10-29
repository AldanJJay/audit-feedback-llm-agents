"""EXPLORATORY / not preregistered: offline analyses requested in round 12."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np

from .analyze import (DATA_ROOT, PRIMARY, PROBES, REQUIRED_MODELS, ROOT,
                      _matched_rows, _null_summary, _seeds, contrast, load_runs,
                      paired_statistics)

LABEL = "EXPLORATORY / not preregistered; descriptive, non-simultaneous intervals; no Holm"
ADDITIONAL = {
    "evidence_minus_punitive_dependence": ("review 1", "evidence", "punitive", "dependence_true"),
    "evidence_minus_punitive_sci": ("review 1", "evidence", "punitive", "gap_true"),
    "placebo_minus_label_dependence": ("review 1", "placebo", "label", "dependence_true"),
    "placebo_minus_label_sci": ("review 1", "placebo", "label", "gap_false"),
}
EXPOSURE = {
    "label": ("review 3", "label", "naive", "gap_exposed"),
    "placebo": ("review 3", "placebo", "naive", "gap_exposed"),
}
SPECS = {**PRIMARY, **ADDITIONAL}
OUTPUT = DATA_ROOT / "analysis/confirm_exploratory_r12"


def noise_cells(loaded, model):
    """Use all-tick valid nulls per seed/condition, falling back only if absent."""
    runs = [run for run in loaded.values() if run["source"]["model"] == model]
    pooled = {}
    for condition in sorted({run["source"]["condition"] for run in runs}):
        pooled[condition] = _null_summary([row for run in runs
                                         if run["source"]["condition"] == condition
                                         for row in run["rows"]])
    cells = {}
    for run in runs:
        source = run["source"]
        summary = _null_summary(run["rows"])
        own_rate = summary["flip_rate"]["mean"]
        fallback = own_rate is None
        cells[f'{source["condition"]}|{source["seed"]}'] = {
            "evidence_label": LABEL, "null": summary,
            "rate_subtracted": pooled[source["condition"]]["flip_rate"]["mean"] if fallback else own_rate,
            "fallback_used": fallback,
            "rate_source": "model_condition_all_ticks" if fallback else "seed_condition_all_ticks",
        }
    return {"evidence_label": LABEL, "cells": cells, "pooled": pooled,
            "n_cells": len(cells), "n_fallback_cells": sum(c["fallback_used"] for c in cells.values()),
            "n_unestimable_cells": sum(c["rate_subtracted"] is None for c in cells.values())}


def paired_estimate(loaded, model, specification, regime=None, noise=None):
    """Preserve registered common support, window and seed weighting."""
    hypothesis, target, reference, metric = specification
    if noise is not None and not metric.startswith(("dependence_", "gap_")):
        raise ValueError("Noise subtraction is defined only for dependence and SCI")
    pairs, excluded, used_cells = [], [], set()
    for seed in _seeds("confirm", model):
        left = loaded.get(f"{model}|{target}|{seed}")
        right = loaded.get(f"{model}|{reference}|{seed}")
        if left is None or right is None:
            excluded.append({"seed": seed, "reason": "missing_run"})
            continue
        matched = [item for item in _matched_rows(left, right, metric, "primary")
                   if regime is None or item[1]["regime"] == regime]
        if not matched:
            excluded.append({"seed": seed, "reason": "no_common_eligible_coordinates"})
            continue
        cell_keys = [f"{condition}|{seed}" for condition in (target, reference)]
        rates = [noise["cells"][key]["rate_subtracted"] for key in cell_keys] if noise else [0., 0.]
        if any(rate is None for rate in rates):
            excluded.append({"seed": seed, "reason": "unestimable_null_rate"})
            continue
        used_cells.update(cell_keys)
        direction = 1 if metric.startswith("gap_") else -1
        a = float(np.mean([item[3] for item in matched])) + direction * rates[0]
        b = float(np.mean([item[4] for item in matched])) + direction * rates[1]
        pair = {"seed": seed, "target_mean": a, "reference_mean": b, "delta": a - b,
                "n_common_coordinates": len(matched),
                "coordinates": [f"{item[0][0]}:{item[0][1]}" for item in matched],
                "target_null_rate": rates[0] if noise else None,
                "reference_null_rate": rates[1] if noise else None}
        if metric.startswith("gap_"):
            citation, dependence = [], []
            for _, ar, br, _, _ in matched:
                selector = ar.get("revealed_label") if metric == "gap_exposed" else ar["regime"]
                if metric == "gap_false":
                    selector = "momentum" if selector == "news" else "news"
                citation.append(float(selector in ar["reasons"]) - float(selector in br["reasons"]))
                dependence.append(float(ar["cf_flips"][selector]) - float(br["cf_flips"][selector]))
            pair.update(citation_delta=float(np.mean(citation)),
                        dependence_delta=float(np.mean(dependence)) - rates[0] + rates[1])
        pairs.append(pair)
    summary = paired_statistics(pairs)
    if metric.startswith("gap_"):
        summary["exploratory"]["cohen_h"] = None
        summary["components"] = {
            key: float(np.mean([pair[key] for pair in pairs])) if pairs else None
            for key in ("citation_delta", "dependence_delta")}
    return {"evidence_label": LABEL, "hypothesis": hypothesis, "target": target,
            "reference": reference, "metric": metric, "window": [20, 39],
            "regime": regime or "pooled", "noise_adjusted": noise is not None,
            "seed_pairs": pairs, "excluded_seed_pairs": excluded,
            "n_fallback_cells_used": sum(noise["cells"][key]["fallback_used"] for key in used_cells) if noise else 0,
            **summary}


def analyze_exploratory(data_root=DATA_ROOT, models=REQUIRED_MODELS):
    manifest, loaded = load_runs(Path(data_root), "confirm", models)
    if any(item["status"] != "included" for item in manifest):
        raise ValueError("Exploratory release requires all frozen assignments")
    result = {"metadata": {
        "evidence_label": LABEL, "api_calls": 0, "input_stage": "confirm",
        "estimand": "equal-seed paired means on common eligible tick/agent coordinates, ticks 20–39",
        "inference": "10,000 paired-seed percentile bootstrap draws, RNG 20261026; raw two-sided paired t p; no Holm",
        "selectors": "SCI evidence-minus-punitive: current true driver; placebo-minus-label: opposite current driver; exposure: actual target label in both prompts",
        "noise": "Subtract all-tick seed × condition valid null rate from dependence, add it to citation-minus-dependence; no clipping; model × condition fallback if no observed valid nulls",
        "noise_limit": "Additive sensitivity, not deconvolution; seed bootstrap resamples estimated cell rates with their seed, with no separate within-cell null resampling",
        "registered_secondary": "Evidence-minus-punitive dependence and exposure SCI were registered secondary; their re-reporting and all additions here are descriptive and not a new confirmatory family",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }, "manifest": manifest, "models": {}}
    for model in models:
        noise = noise_cells(loaded, model)
        result["models"][model] = {
            "evidence_label": LABEL,
            "incremental": {key: paired_estimate(loaded, model, spec) for key, spec in ADDITIONAL.items()},
            "regime": {regime: {key: paired_estimate(loaded, model, spec, regime=regime)
                                 for key, spec in PRIMARY.items()} for regime in PROBES},
            "noise": noise,
            "noise_adjusted": {key: paired_estimate(loaded, model, spec, noise=noise)
                               for key, spec in SPECS.items() if spec[3].startswith(("dependence_", "gap_"))},
            "exposure": {key: paired_estimate(loaded, model, spec) for key, spec in EXPOSURE.items()},
            "itt": {key: paired_estimate(loaded, model, spec) for key, spec in PRIMARY.items()},
            "regime_nulls": {condition: {window: {regime: _null_summary([
                row for run in loaded.values() if run["source"]["model"] == model
                and run["source"]["condition"] == condition for row in run["rows"]
                if first <= row["tick"] <= last and row["regime"] == regime])
                for regime in PROBES} for window, (first, last) in {"overall": (0, 39), "primary": (20, 39)}.items()}
                for condition in ("naive", "punitive", "label", "evidence", "placebo")},
        }
        # Imported estimator provides an independent invariance check on unstratified results.
        for key, spec in {**PRIMARY, **ADDITIONAL, **EXPOSURE}.items():
            new = paired_estimate(loaded, model, spec)
            old = contrast(loaded, model, "confirm", spec)
            for field in ("mean_delta", "bootstrap_ci_95", "paired_t_p", "n_seed_pairs"):
                if new[field] != old[field]:
                    raise AssertionError(f"Registered-estimator mismatch: {model}/{key}/{field}")
    return result


def fmt_estimate(item):
    low, high = item["bootstrap_ci_95"]
    if item["mean_delta"] is None:
        return "unestimable"
    return f'{item["mean_delta"]:.4f} [{low:.4f}, {high:.4f}]'


def write_outputs(result, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    lines = ["# EXPLORATORY / not preregistered — round 12", "",
             "All estimates and intervals are descriptive and non-simultaneous; raw p values only, no Holm.",
             "These analyses neither replace nor modify the frozen primary family. All use ticks 20–39, equal seed weights and registered common support.",
             "Noise rates use ticks 0–39; subtract within seed × condition without clipping, falling back to model × condition only if unestimable.",
             "Evidence–punitive SCI uses the current true driver; placebo–label SCI uses its opposite. Exposure SCI uses the target's actual revealed label in both prompts.",
             "Evidence–punitive dependence and exposure SCI repeat registered secondary estimates; the review-requested reporting remains descriptive.", ""]
    for model, block in result["models"].items():
        lines += [f"## {model} — EXPLORATORY / not preregistered", "",
                  f'Noise fallback: {block["noise"]["n_fallback_cells"]}/{block["noise"]["n_cells"]} cells; '
                  f'{block["noise"]["n_unestimable_cells"]} remain unestimable.', "",
                  "| Analysis / JSON path within model | Estimate [95% bootstrap CI] | Raw p | Seed pairs | Citation / dependence changes |", "|---|---|---|---|---|"]
        groups = {key: block[key] for key in ("incremental", "noise_adjusted", "exposure", "itt")}
        groups.update({f"regime.{regime}": estimates for regime, estimates in block["regime"].items()})
        for group, estimates in groups.items():
            for key, item in estimates.items():
                components = item.get("components")
                decomposition = (f'{components["citation_delta"]:.4f} / {components["dependence_delta"]:.4f}'
                                 if components and components["citation_delta"] is not None else "—")
                lines.append(f'| `{group}.{key}` | {fmt_estimate(item)} | {item["paired_t_p"]:.4g} | {item["n_seed_pairs"]} | {decomposition} |')
        lines += ["", "Regime null rates (pooled observed responses; descriptive, not seed-cluster inference):", "",
                  "| Condition | Overall news flips/n | Overall momentum flips/n | Primary news flips/n | Primary momentum flips/n |", "|---|---|---|---|---|"]
        for condition, windows in block["regime_nulls"].items():
            cells = [windows[window][regime]["flip_rate"] for window in ("overall", "primary") for regime in PROBES]
            lines.append(f'| {condition} | ' + " | ".join(f'{cell["sum"]:g}/{cell["n"]}' for cell in cells) + " |")
        lines.append("")
    (output_dir / "report.md").write_text("\n".join(lines) + "\n")


def archive_frozen(output_dir):
    """Self-contained immutable input snapshot, distinct from exploratory inference."""
    paths = ["preregistration/preregistration.md", "preregistration/FROZEN.json", "src/v2/analyze.py",
             "data/v2/analysis/confirm/results.json", "data/v2/analysis/confirm/report.md",
             "results/confirmatory_results.md"]
    files = {path: (ROOT / path).read_bytes() for path in paths}
    manifest = {"evidence_label": LABEL, "purpose": "Archival copy of frozen inputs; original bytes retain historical headings. Not a new preregistration.",
                "preregistration_includes": "Original plan, both amendments, verbatim prompts and recorded PI answers",
                "public_packaging_note": "Snapshot rebuilt from portable public copies; only preregistration and freeze-marker bytes are the unchanged development originals. Scientific results are unchanged; paths and public code provenance differ.",
                "sha256": {path: hashlib.sha256(data).hexdigest() for path, data in files.items()}}
    with zipfile.ZipFile(Path(output_dir) / "EXPLORATORY_frozen_inputs.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path, data in {**files, "EXPLORATORY_ARCHIVE_MANIFEST.json": json.dumps(manifest, indent=2).encode()}.items():
            archive.writestr(zipfile.ZipInfo(path, (2026, 10, 28, 0, 0, 0)), data, compress_type=zipfile.ZIP_DEFLATED)
    (Path(output_dir) / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")


def write_table(result):
    rows = [
        ("Evidence $-$ punitive: true sensitivity", "incremental.evidence_minus_punitive_dependence"),
        ("Evidence $-$ punitive: true-selector SCI", "incremental.evidence_minus_punitive_sci"),
        ("Placebo $-$ label: true sensitivity", "incremental.placebo_minus_label_dependence"),
        ("Placebo $-$ label: opposite-selector SCI", "incremental.placebo_minus_label_sci"),
        ("P2: news regime", "regime.news.H1_dependence_evidence_minus_naive"),
        ("P2: momentum regime", "regime.momentum.H1_dependence_evidence_minus_naive"),
        ("P4: news regime", "regime.news.H4_sci_placebo"),
        ("P4: momentum regime", "regime.momentum.H4_sci_placebo"),
        ("Noise-adjusted P2", "noise_adjusted.H1_dependence_evidence_minus_naive"),
        ("Noise-adjusted P3", "noise_adjusted.H3_sci_label"),
        ("Noise-adjusted P4", "noise_adjusted.H4_sci_placebo"),
        ("Actual-label exposure SCI: label", "exposure.label"),
        ("Actual-label exposure SCI: placebo", "exposure.placebo"),
    ]
    lines = [r"% EXPLORATORY / not preregistered; generated by src/v2/exploratory_r12.py",
             r"\begin{table}[tbp]",
             r"\caption{Exploratory analyses requested in review (not preregistered). Equal-seed estimates [descriptive, non-simultaneous 95\% bootstrap intervals], ticks 20--39; 20 DeepSeek and 10 Haiku/Luna pairs throughout. Evidence--punitive dependence and exposure SCI repeat registered secondary estimands. All other entries are new exploratory estimands. Raw paired $p$ values (no Holm), P1/P3 strata, noise-adjusted incremental contrasts and regime null counts are in the exploratory report.}",
             r"\label{tab:exploratory}", r"\centering\footnotesize",
             r"\setlength{\tabcolsep}{3pt}", r"\begin{adjustbox}{max width=\linewidth}",
             r"\begin{tabular}{llll}", r"\toprule",
             r"Contrast & DeepSeek & Haiku & Luna \\", r"\midrule"]
    for title, path in rows:
        estimates = []
        for model in REQUIRED_MODELS:
            item = result["models"][model]
            for key in path.split("."):
                item = item[key]
            estimates.append(fmt_estimate(item))
        lines.append(title + " & " + " & ".join(estimates) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{adjustbox}", r"\end{table}"]
    destination = ROOT / "paper/latex/figures/v10"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "exploratory_table.tex").write_text("\n".join(lines) + "\n")
    (destination / "EXPLORATORY_table_provenance.json").write_text(json.dumps({
        "evidence_label": LABEL, "source": "data/v2/analysis/confirm_exploratory_r12/results.json",
        "rows": {title: f"models.<model>.{path}" for title, path in rows},
        "fields": ["mean_delta", "bootstrap_ci_95"],
        "generator": "src/v2/exploratory_r12.py"}, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.resolve() != OUTPUT.resolve():
        raise ValueError("Release output is restricted to confirm_exploratory_r12")
    result = analyze_exploratory()
    write_outputs(result, args.output)
    archive_frozen(args.output)
    write_table(result)
    print(f"{LABEL}: {args.output}")


if __name__ == "__main__":
    main()
