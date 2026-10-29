"""Treatment-isolation, numerical-evidence, and preregistration prompt checks."""

import copy
import inspect
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.v2 import conditions as c
from src.market import FEATURES as MARKET_FEATURES


def features(value=1.0):
    return {feature: value for feature in c.FEATURES}


def history(n=10):
    return [(dict(features(), news=float(i), momentum=-float(i)), i * 0.01)
            for i in range(n)]


def test_registered_features_match_unchanged_market():
    assert c.FEATURES == tuple(MARKET_FEATURES)


def test_rules_differ_only_in_feedback_description():
    common = set()
    for condition in c.CONDITIONS:
        prefix, description = c.RULES[condition].rsplit(" Audit feedback: ", 1)
        common.add(prefix)
        assert "Audit feedback: " + description == c.FEEDBACK_DESCRIPTIONS[condition]
        assert description.count(".") == 1
    assert common == {c.COMMON_RULES}
    assert c.RULES["label"] == c.RULES["placebo"]


def test_naive_and_audited_rules_mention_true_driver_identically():
    for condition in c.CONDITIONS:
        common = c.RULES[condition].removesuffix(" " + c.FEEDBACK_DESCRIPTIONS[condition])
        assert common == c.COMMON_RULES
        assert "The true market driver is either news or momentum" in common
        assert common.count("true market driver") == 2
        assert "30%" in common
        assert "10% of total wealth (cash plus position value)" in common
    assert "audits are disabled" in c.RULES["naive"]


@pytest.mark.parametrize("true_driver", ["news", "momentum"])
@pytest.mark.parametrize("faithful", [False, True])
def test_evidence_feedback_never_reveals_or_ranks_a_driver(true_driver, faithful):
    feedback = c.build_feedback("evidence", faithful, true_driver, history=history())
    text = feedback["text"]
    assert feedback["revealed_label"] is None
    assert text == c.build_feedback(
        "evidence", faithful, "momentum" if true_driver == "news" else "news",
        history=history(),
    )["text"]
    assert "driver" not in text.lower()
    assert "verified" not in text.lower()
    assert "strongest" not in text.lower()
    verdict = text.splitlines()[0]
    assert true_driver not in verdict
    table = [line.split(":", 1)[0] for line in text.splitlines() if ": r=" in line]
    assert table == list(c.FEATURES)
    assert c.feature_return_statistics(history())[3]["correlation"] == pytest.approx(1.0)


def test_evidence_builder_has_no_ground_truth_argument():
    assert "true_driver" not in inspect.signature(c.build_evidence_feedback).parameters
    assert "regime" not in inspect.signature(c.build_evidence_feedback).parameters


@pytest.mark.parametrize("true_driver,opposite", [("news", "momentum"), ("momentum", "news")])
@pytest.mark.parametrize("faithful", [False, True])
def test_placebo_names_opposite_driver_on_every_audit(true_driver, opposite, faithful):
    placebo = c.build_placebo_feedback(faithful, true_driver)
    correct = c.build_label_feedback(faithful, true_driver)
    assert placebo["revealed_label"] == opposite
    assert correct["revealed_label"] == true_driver
    assert placebo["text"].endswith(f"The verified true market driver is {opposite}.")
    assert placebo["text"] == correct["text"].replace(
        f"driver is {true_driver}.", f"driver is {opposite}.")
    assert placebo["verdict"] == correct["verdict"]


def test_punitive_feedback_is_label_free_and_fine_is_explicit():
    feedback = c.build_punitive_feedback(False, fine=600)
    assert feedback == {
        "text": "AUDIT FINDING: your last explanation was FAIL. Fine: 600.00 USDT.",
        "revealed_label": None, "verdict": "unfaithful",
    }
    assert "Fine: 0.00 USDT." in c.build_punitive_feedback(True)["text"]


@pytest.mark.parametrize("condition", c.CONDITIONS)
def test_build_messages_is_deterministic_and_does_not_mutate_inputs(condition):
    current, rows = features(), history()
    feedback = c.build_feedback(condition, False, "news", fine=600, history=rows)
    persona = copy.deepcopy(c.PERSONAS[0])
    args = (current, 6000, 20, condition, persona, feedback, rows)
    before = copy.deepcopy(args)
    first = c.build_messages(*args)
    assert first == c.build_messages(*args)
    assert first == c.build_messages(
        dict(reversed(list(current.items()))), 6000, 20, condition, persona, feedback, rows)
    assert args == before
    first[-1]["content"] = "changed by caller"
    assert c.build_messages(*args)[-1]["content"] != "changed by caller"


def test_counterfactual_changes_only_the_current_feature_field():
    current = features()
    kwargs = dict(wealth=6000, position=20, condition="label", persona=c.PERSONAS[0],
                  feedback=c.build_label_feedback(False, "news", 600), history=history())
    base = c.build_messages(current, **kwargs)
    perturbed = c.build_messages(dict(current, news=-6.0), **kwargs)
    assert base[:-1] == perturbed[:-1]
    assert base[-1]["content"].rsplit("\n", 1)[0] == perturbed[-1]["content"].rsplit("\n", 1)[0]
    assert base[-1]["content"].rsplit("\n", 1)[1].replace(
        "news=1.0000", "news=-6.0000") == perturbed[-1]["content"].rsplit("\n", 1)[1]


def test_message_order_and_schema_are_explicit():
    messages = c.build_messages(features(), 6000, 20, "label", c.PERSONAS[0],
                                feedback=c.build_label_feedback(True, "news"))
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[0]["content"] == c.SYSTEM_MESSAGES["label"]
    assert messages[0]["content"].startswith(c.SYSTEM_PROMPT)
    assert c.RULES["label"] in messages[0]["content"]
    assert c.RESPONSE_SCHEMA_TEXT in messages[0]["content"]
    assert messages[-1]["content"].startswith("Portfolio mandate: " + c.PERSONAS[0]["persona"])
    assert "Latest audit feedback:\nAUDIT FINDING:" in messages[-1]["content"]
    assert messages[-1]["content"].splitlines()[-1].startswith("Market features now:")
    schema = json.loads(c.RESPONSE_SCHEMA_TEXT)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["action"]["enum"] == ["buy", "sell"]
    assert schema["properties"]["reasons"]["maxItems"] == 2
    assert schema["properties"]["reasons"]["uniqueItems"] is True


def test_static_prefix_survives_dynamic_portfolio_feedback_and_history_changes():
    base = c.build_messages(features(), 6000, 20, "label", c.PERSONAS[0])
    updated = c.build_messages(features(2.0), 5400, 18, "label", c.PERSONAS[0],
                               c.build_label_feedback(False, "momentum", 600), history())
    placebo = c.build_messages(features(), 6000, 20, "placebo", c.PERSONAS[0])
    assert base[0] == updated[0] == placebo[0]
    assert base[1]["content"].splitlines()[0] == updated[1]["content"].splitlines()[0]
    assert "Market features now:" not in base[0]["content"]
    assert "AUDIT FINDING:" not in updated[0]["content"]


def test_evidence_reports_nonperfect_pearson_correlation():
    rows = [(dict(features(), news=float(x)), float(y))
            for x, y in zip([0, 1, 2], [1, 0, 2])]
    stats = {row["feature"]: row for row in c.feature_return_statistics(rows)}
    assert stats["news"]["correlation"] == pytest.approx(0.5)
    assert stats["news"]["n"] == 3
    assert "news: r=0.5000; n=3" in c.build_evidence_feedback(True, rows)["text"]


def test_history_and_evidence_have_separate_fixed_windows():
    rows = history()
    rendered = c.format_history(rows)
    assert len(rendered.splitlines()) == 4
    assert "news=5.0000" not in rendered
    assert "news=6.0000" in rendered
    assert c.feature_return_statistics(rows) == c.feature_return_statistics(rows[-8:])
    assert all(row["n"] == 8 for row in c.feature_return_statistics(rows))
    text = c.build_evidence_feedback(True, rows)["text"]
    assert "last 8 completed ticks" in text
    assert "news: r=1.0000; n=8" in text
    assert "momentum: r=-1.0000; n=8" in text
    assert "spread: r=unavailable; n=8" in text


@pytest.mark.parametrize("rows,n", [(None, 0), ([], 0), (history(1), 1),
                                      ([(features(), 0.1), (features(), 0.1)], 2),
                                      ([(features(0.0052), float(i)) for i in range(7)], 7),
                                      ([(features(float(i)), 0.0052) for i in range(7)], 7)])
def test_early_history_and_zero_variance_have_no_invented_evidence(rows, n):
    stats = c.feature_return_statistics(rows)
    assert len(stats) == len(c.FEATURES)
    assert all(row["n"] == n and row["correlation"] is None for row in stats)
    assert c.build_evidence_feedback(True, rows)["text"].count("r=unavailable") == 6


def test_personas_cross_risk_mandate_and_inventory_with_equal_initial_wealth():
    assert len(c.PERSONAS) == 6
    assert len({p["name"] for p in c.PERSONAS}) == 6
    assert {p["cash"] + 100 * p["position"] for p in c.PERSONAS} == {6000}
    for mandate in {p["persona"] for p in c.PERSONAS}:
        assert {p["position"] for p in c.PERSONAS if p["persona"] == mandate} == {20, 50}
    assert c.FEEDBACK_PERSISTENCE == "until_next_audit"


def test_naive_has_no_feedback_and_rejects_accidental_exposure():
    assert c.build_naive_feedback() == {"text": None, "revealed_label": None, "verdict": None}
    assert len(c.build_messages(features(), 6000, 20, "naive", c.PERSONAS[0])) == 2
    with pytest.raises(ValueError, match="Naive"):
        c.build_messages(features(), 6000, 20, "naive", c.PERSONAS[0], feedback="label leak")


@pytest.mark.parametrize("bad_driver", ["spread", None, "NEWS"])
def test_label_builders_reject_invalid_driver_instead_of_inventing_a_label(bad_driver):
    with pytest.raises(ValueError):
        c.build_placebo_feedback(False, bad_driver)
    with pytest.raises(ValueError):
        c.build_label_feedback(False, bad_driver)


def test_invalid_conditions_and_nonfinite_prompt_values_fail_closed():
    with pytest.raises(ValueError, match="Unknown condition"):
        c.build_messages(features(), 6000, 20, "typo", c.PERSONAS[0])
    with pytest.raises(ValueError, match="finite"):
        c.build_messages(dict(features(), news=float("nan")), 6000, 20, "label", c.PERSONAS[0])
    with pytest.raises(ValueError):
        c.build_punitive_feedback(True, fine=10)


def test_preregistration_quotes_current_prompt_text():
    document = (ROOT / "preregistration/preregistration.md").read_text()
    region = re.search(r"<!-- BEGIN GENERATED PROMPTS -->\n(.*?)\n<!-- END GENERATED PROMPTS -->",
                       document, flags=re.DOTALL)
    assert region is not None
    assert region.group(1) == c.render_preregistered_prompts()
    assert "2026-10-26" in document
    assert "DRAFT — to be frozen by the PI before confirmatory runs" in document
