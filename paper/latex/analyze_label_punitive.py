"""Offline exploratory (not preregistered) label-minus-punitive package contrasts.

Run from any directory: .venv/bin/python paper/latex/analyze_label_punitive.py
No experiments or network access. Existing estimators and support rules are reused.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.v2.analyze import (BOOTSTRAPS, DATA_ROOT, REQUIRED_MODELS, RNG_SEED,
                            contrast, load_runs)
from src.v2.exploratory_analyses import LABEL, exploratory_contrast, support_counts

OUTPUT = DATA_ROOT / "analysis/exploratory"
SPECS = {metric: ("exploratory (not preregistered)", "label", "punitive", metric)
         for metric in ("environmental_fidelity", "process_precision", "dependence_true")}


def analyze():
    manifest, loaded = load_runs(DATA_ROOT, "confirm", REQUIRED_MODELS)
    assert len(loaded) == 200
    assert all(item["status"] == "included" for item in manifest)
    result = {"metadata": {
        "evidence_label": LABEL,
        "api_calls": 0,
        "input_stage": "confirm",
        "window": [20, 39],
        "estimand": "label minus punitive, equal-seed means on common eligible tick/agent support",
        "inference": "10,000 paired-seed percentile bootstrap draws; raw two-sided paired Student t p; no multiplicity correction; descriptive and non-simultaneous",
        "bootstrap_rng_seed": RNG_SEED,
        "bootstrap_draws": BOOTSTRAPS,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": {"python": platform.python_version(), **{
            key: importlib.metadata.version(key) for key in ("numpy", "scipy")}},
        "raw_input_sha256": {
            str(Path(run["source"]["path"]).relative_to(ROOT)):
                hashlib.sha256(Path(run["source"]["path"]).read_bytes()).hexdigest()
            for run in loaded.values() if run["source"]["condition"] in ("label", "punitive")},
        "limitation": "Non-factorial package contrasts do not isolate a label-only causal mechanism; no new confirmatory family is created.",
    }, "models": {}}
    for model in REQUIRED_MODELS:
        counts = support_counts(loaded, model, SPECS)
        block = {}
        for metric, spec in SPECS.items():
            item = exploratory_contrast(loaded, model, spec)
            original = contrast(loaded, model, "confirm", spec)
            for field in ("mean_delta", "bootstrap_ci_95", "paired_t_p", "n_seed_pairs", "cohen_dz"):
                assert item[field] == original[field], (model, metric, field)
            assert item["n_common_decisions"] == counts[metric]["common_analysed"]
            item["support"] = counts[metric]
            item["matches_existing_estimator"] = True
            block[metric] = item
        result["models"][model] = block
    return result


def write_outputs(result):
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "label_punitive.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    lines = ["# Post hoc label-minus-punitive package contrasts", "",
             "Exploratory (not preregistered), descriptive, non-simultaneous 95% percentile intervals; raw two-sided paired Student t p values, no Holm correction.",
             "Ticks 20–39; equal weights for the 20 DeepSeek seeds and the 10 Haiku/Luna seeds; both arms must have defined values at the same tick/agent coordinate.",
             "The analysis imports the unchanged confirmatory estimators and checks point estimates, intervals, raw p values and effect sizes against the existing confirmatory estimator.",
             "No inference API calls or new experiments were made; frozen confirmatory outputs were not modified.", "",
             "| Model | Metric | n seed pairs | Common decisions | Delta | 95% CI | dz | Cohen h | Raw p |", "|---|---|---:|---:|---:|---|---:|---:|---:|"]
    for model, block in result["models"].items():
        for metric, item in block.items():
            lo, hi = item["bootstrap_ci_95"]
            lines.append(f'| {model} | {metric} | {item["n_seed_pairs"]} | {item["n_common_decisions"]} | {item["mean_delta"]:.6f} | [{lo:.6f}, {hi:.6f}] | {item["cohen_dz"]:.6f} | {item["exploratory"]["cohen_h"]:.6f} | {item["paired_t_p"]:.8f} |')
    lines += ["", "Sensitivity is the frequency of binary action changes after a sign flip. Process precision is restricted to complete probes with nonempty citations; environmental fidelity uses valid original responses, so its support can be larger.",
              "These package contrasts do not identify an isolated label mechanism because the design was not factorial.",
              "The artifact records all per-seed paired means, matched coordinates, support counts and source hashes; RNG 20261026 is reset for each 10,000-draw bootstrap as in the confirmatory estimator."]
    (OUTPUT / "label_punitive.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    write_outputs(analyze())
