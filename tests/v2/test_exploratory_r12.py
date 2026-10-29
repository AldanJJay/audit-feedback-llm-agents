import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.v2.analyze import _prepare, contrast, paired_bootstrap
from src.v2.exploratory_r12 import (ADDITIONAL, LABEL, archive_frozen,
                                    noise_cells, paired_estimate, write_outputs)

MODEL = "deepseek-v4-flash"


def row(tick=20, agent=0, regime="news", cites=("news",), news=True, momentum=False, **updates):
    item = {"tick": tick, "agent": agent, "regime": regime, "action": "buy", "size": 1,
            "parse_ok": True, "reasons": list(cites), "cf_sampled": True,
            "cf_flips": {"news": news, "momentum": momentum},
            "revealed_label": None, "null_monitor_sampled": False}
    item.update(updates)
    return _prepare(item)


def add(loaded, condition, seed, rows):
    loaded[f"{MODEL}|{condition}|{seed}"] = {
        "source": {"model": MODEL, "condition": condition, "seed": seed},
        "rows": rows, "coordinates": {(r["tick"], r["agent"]): r for r in rows}}


@pytest.mark.parametrize("key", ADDITIONAL)
def test_added_estimators_preserve_registered_support_and_statistics(key):
    loaded = {}
    spec = ADDITIONAL[key]
    for seed in range(200, 203):
        add(loaded, spec[1], seed, [row(agent=a, news=a < seed - 199, momentum=a > 1)
                                  for a in range(4)])
        add(loaded, spec[2], seed, [row(agent=a, cites=("momentum",), news=False, momentum=False)
                                  for a in range(4)])
    actual = paired_estimate(loaded, MODEL, spec)
    registered = contrast(loaded, MODEL, "confirm", spec)
    for field in ("mean_delta", "bootstrap_ci_95", "paired_t_p", "n_seed_pairs"):
        assert actual[field] == registered[field]
    assert "holm" not in actual
    assert actual["evidence_label"] == LABEL


def test_equal_seed_weights_bootstrap_and_raw_p_not_row_weights():
    loaded = {}
    for seed, n, flips in ((200, 1, True), (201, 5, False), (202, 2, True)):
        add(loaded, "evidence", seed, [row(agent=a, news=flips) for a in range(n)])
        add(loaded, "punitive", seed, [row(agent=a, news=False) for a in range(n)])
    actual = paired_estimate(loaded, MODEL, ADDITIONAL["evidence_minus_punitive_dependence"])
    assert actual["mean_delta"] == pytest.approx(2 / 3)
    assert actual["bootstrap_ci_95"] == paired_bootstrap([1, 0, 1])
    assert actual["paired_t_p"] == pytest.approx(stats.ttest_1samp([1, 0, 1], 0).pvalue)


def test_regime_strata_and_primary_window_keep_both_regimes():
    loaded = {}
    add(loaded, "evidence", 200, [row(tick=19), row(tick=20), row(tick=30, regime="momentum")])
    add(loaded, "punitive", 200, [row(tick=19, news=False), row(tick=20, news=False),
                                  row(tick=30, regime="momentum", momentum=True)])
    spec = ADDITIONAL["evidence_minus_punitive_dependence"]
    assert paired_estimate(loaded, MODEL, spec, "news")["mean_delta"] == 1
    assert paired_estimate(loaded, MODEL, spec, "momentum")["mean_delta"] == -1
    pooled = paired_estimate(loaded, MODEL, spec)
    assert pooled["mean_delta"] == 0
    assert pooled["seed_pairs"][0]["n_common_coordinates"] == 2


def test_sci_selects_opposite_current_driver_for_both_conditions():
    loaded = {}
    add(loaded, "placebo", 200, [row(cites=("momentum",), momentum=True),
                                 row(tick=30, regime="momentum", cites=("news",), news=True)])
    add(loaded, "label", 200, [row(cites=(), news=False),
                               row(tick=30, regime="momentum", cites=(), news=False)])
    actual = paired_estimate(loaded, MODEL, ADDITIONAL["placebo_minus_label_sci"])
    assert actual["components"] == {"citation_delta": 1, "dependence_delta": 1}
    assert actual["mean_delta"] == 0


def test_exposure_selector_is_actual_stale_target_label_in_both_prompts():
    loaded = {}
    add(loaded, "placebo", 200, [row(revealed_label="news"),
                                 row(agent=1, revealed_label=None)])
    add(loaded, "naive", 200, [row(cites=(), news=False), row(agent=1, cites=(), news=False)])
    actual = paired_estimate(loaded, MODEL, ("review", "placebo", "naive", "gap_exposed"))
    assert actual["seed_pairs"][0]["coordinates"] == ["20:0"]
    assert actual["components"] == {"citation_delta": 1, "dependence_delta": 1}


def test_noise_subtraction_sci_sign_and_fallback_counts():
    loaded = {}
    add(loaded, "evidence", 200, [row(news=False, null_monitor_sampled=True, null_monitor_flip=True)])
    add(loaded, "evidence", 201, [row(news=False)])
    add(loaded, "punitive", 200, [row(news=False, null_monitor_sampled=True, null_monitor_flip=False)])
    add(loaded, "punitive", 201, [row(news=False, null_monitor_sampled=True, null_monitor_flip=False)])
    noise = noise_cells(loaded, MODEL)
    assert noise["n_fallback_cells"] == 1
    assert noise["cells"]["evidence|201"]["rate_source"] == "model_condition_all_ticks"
    dep = paired_estimate(loaded, MODEL, ADDITIONAL["evidence_minus_punitive_dependence"], noise=noise)
    sci = paired_estimate(loaded, MODEL, ADDITIONAL["evidence_minus_punitive_sci"], noise=noise)
    assert dep["mean_delta"] == -1  # No clipping, including negative adjusted rates.
    assert sci["mean_delta"] == 1
    assert sci["components"] == {"citation_delta": 0, "dependence_delta": -1}
    assert dep["n_fallback_cells_used"] == sci["n_fallback_cells_used"] == 1


def test_invalid_missing_nulls_and_unestimable_noise_do_not_fabricate_zero():
    loaded = {}
    add(loaded, "evidence", 200, [row(parse_ok=False, null_monitor_sampled=True, null_monitor_flip=True),
                                 row(agent=1, null_monitor_sampled=True, null_monitor_flip=None)])
    add(loaded, "punitive", 200, [row(null_monitor_sampled=True, null_monitor_flip=False), row(agent=1)])
    noise = noise_cells(loaded, MODEL)
    assert noise["n_unestimable_cells"] == 1
    actual = paired_estimate(loaded, MODEL, ADDITIONAL["evidence_minus_punitive_dependence"], noise=noise)
    assert actual["mean_delta"] is None
    assert actual["excluded_seed_pairs"][0]["reason"] == "unestimable_null_rate"


def test_common_support_excludes_incomplete_counterfactual_and_regime_mismatch():
    loaded = {}
    add(loaded, "evidence", 200, [row(news=None), row(agent=1), row(agent=2)])
    add(loaded, "punitive", 200, [row(news=False), row(agent=1, regime="momentum"), row(agent=2, news=False)])
    actual = paired_estimate(loaded, MODEL, ADDITIONAL["evidence_minus_punitive_dependence"])
    assert actual["seed_pairs"][0]["coordinates"] == ["20:2"]


def test_archive_copies_original_bytes_with_hash_manifest(tmp_path):
    archive_frozen(tmp_path)
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["evidence_label"] == LABEL
    with zipfile.ZipFile(tmp_path / "EXPLORATORY_frozen_inputs.zip") as archive:
        assert archive.testzip() is None
        assert archive.read("src/v2/analyze.py") == Path("src/v2/analyze.py").read_bytes()


def test_output_label_and_no_holm(tmp_path):
    write_outputs({"metadata": {"evidence_label": LABEL}, "models": {}}, tmp_path)
    assert "EXPLORATORY / not preregistered" in (tmp_path / "report.md").read_text()
    assert json.loads((tmp_path / "results.json").read_text())["metadata"]["evidence_label"] == LABEL
