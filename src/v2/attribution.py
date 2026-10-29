"""Counterfactual decision dependence for the registered feature probes."""

import re

from .llm import chat, extract_json

FEATURES = ("news", "momentum")
VARIANTS = ("zero", "sign_flip", "adverse_1sd", "adverse_2sd", "extreme_v1")
NOISE_VARIANTS = ("null_1", "null_2", "sign_flip")
FEATURE_SD = {"news": 0.99498743710662, "momentum": 0.99498743710662}
EXTREMES = {
    "buy": {"news": -6.0, "momentum": -10.0},
    "sell": {"news": 6.0, "momentum": 10.0},
}
_FEATURE_VALUE = re.compile(r"\b(news|momentum)=(-?\d+(?:\.\d+)?)")


def _perturbed_messages(messages, feature, value):
    """Replace only one value on the final Market features now line."""
    copied = [dict(message) for message in messages]
    user = copied[-1]["content"]
    prefix, marker, tail = user.rpartition("Market features now: ")
    if not marker:
        raise ValueError("Prompt has no final Market features now line")
    match = None
    for candidate in _FEATURE_VALUE.finditer(tail):
        if candidate.group(1) == feature:
            match = candidate
    if match is None:
        raise ValueError(f"Current feature {feature} is missing from prompt")
    tail = tail[:match.start(2)] + f"{value:.4f}" + tail[match.end(2):]
    copied[-1]["content"] = prefix + marker + tail
    return copied


def _valid_action(text):
    value = extract_json(text)
    if (not isinstance(value, dict) or set(value) != {"action", "size", "reasons"}
            or value.get("action") not in ("buy", "sell")
            or isinstance(value.get("size"), bool)
            or not isinstance(value.get("size"), int)
            or not 1 <= value["size"] <= 10
            or not isinstance(value.get("reasons"), list)
            or len(value["reasons"]) > 2
            or any(not isinstance(reason, str) or reason not in
                   ("momentum", "spread", "volume", "news", "orderflow", "sentiment")
                   for reason in value["reasons"])
            or len(set(value["reasons"])) != len(value["reasons"])):
        return None
    return value["action"]


async def counterfactual_flips(messages, base_action, *, model, budget,
                               tag="", call_fn=None, variants=("extreme_v1",)):
    """Re-ask requested interventions; return flip values and auditable rows."""
    unknown = set(variants) - set(VARIANTS) - set(NOISE_VARIANTS)
    if unknown:
        raise ValueError(f"Unknown counterfactual variant: {sorted(unknown)[0]}")
    call_fn = call_fn or chat
    if any(not variant.startswith("null_") for variant in variants) and base_action not in EXTREMES:
        raise ValueError("base_action must be buy or sell for feature interventions")
    result = {variant: {} for variant in variants}
    rows = []
    current = _current_features(messages)
    for variant in variants:
        if variant.startswith("null_"):
            flipped = None
            try:
                response = await call_fn(
                    [dict(message) for message in messages], model=model,
                    temperature=0.0, max_tokens=512, budget=budget,
                    tag=f"{tag}:cf:{variant}")
            except Exception as exc:
                if exc.__class__.__name__ == "BudgetExceeded":
                    raise
            else:
                action = _valid_action(getattr(response, "text", response))
                flipped = None if action is None or base_action is None else action != base_action
            result[variant] = {"decision": flipped}
            rows.append({"cf_variant": variant, "feature": "decision",
                         "perturbed_value": None, "flipped": flipped})
            continue
        for feature in FEATURES:
            value = _variant_value(variant, feature, current[feature], base_action)
            flipped = None
            try:
                response = await call_fn(
                    _perturbed_messages(messages, feature, value), model=model,
                    temperature=0.0, max_tokens=512, budget=budget,
                    tag=f"{tag}:cf:{variant}:{feature}")
            except Exception as exc:
                if exc.__class__.__name__ == "BudgetExceeded":
                    raise
            else:
                action = _valid_action(getattr(response, "text", response))
                flipped = None if action is None else action != base_action
            result[variant][feature] = flipped
            rows.append({"cf_variant": variant, "feature": feature,
                         "perturbed_value": value, "flipped": flipped})
    return result, rows


def _current_features(messages):
    tail = messages[-1]["content"].rpartition("Market features now: ")[2]
    values = {match.group(1): float(match.group(2)) for match in _FEATURE_VALUE.finditer(tail)}
    if any(feature not in values for feature in FEATURES):
        raise ValueError("Current news or momentum is missing from prompt")
    return values


def _variant_value(variant, feature, value, base_action):
    if variant.startswith("null_"):
        return value
    if variant == "zero":
        return 0.0
    if variant == "sign_flip":
        return -value
    if variant in ("adverse_1sd", "adverse_2sd"):
        direction = -1 if base_action == "buy" else 1
        multiplier = 1 if variant == "adverse_1sd" else 2
        return value + direction * multiplier * FEATURE_SD[feature]
    if variant == "extreme_v1":
        return EXTREMES[base_action][feature]
    raise ValueError(f"Unknown counterfactual variant: {variant}")
