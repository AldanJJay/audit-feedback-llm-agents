#!/usr/bin/env python3
"""Offline, deterministic audit-service summary of the confirmatory run.

Run: .venv/bin/python paper/latex/summarize_audit_traffic.py
Reads the persistent ledger and exploratory decision counts.
No provider client is imported and no network requests are made.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import platform

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "data/v2/ledger.jsonl"
ANALYSIS = ROOT / "data/v2/analysis/exploratory/results.json"
OUT = ROOT / "data/v2/analysis/exploratory"
MODEL_NAMES = {
    "deepseek-v4-flash": "DeepSeek",
    "anthropic/claude-haiku-5.5": "Haiku",
    "openai/gpt-6-luna": "Luna",
}
KINDS = ("base", "sign_flip_news", "sign_flip_momentum", "null")
CONDITIONS = ("naive", "punitive", "label", "evidence", "placebo")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_kind(row):
    suffix = row["tag"].split(":")[5:]
    if suffix == []:
        return "base"
    if suffix == ["cf", "null_1"]:
        return "null"
    if suffix in (["cf", "sign_flip", "news"], ["cf", "sign_flip", "momentum"]):
        return "sign_flip_" + suffix[-1]
    raise ValueError(f"Unexpected confirmatory tag {row['tag']}")


def summarize(rows):
    """Token means exclude unavailable usage and failed HTTP attempts."""
    measured = [r for r in rows if not r.get("usage_missing") and not r.get("error_class")
                and (r.get("prompt_tokens", 0) + r.get("completion_tokens", 0) > 0)]
    assert all(r.get("prompt_tokens", 0) == r.get("completion_tokens", 0) == 0
               for r in rows if r.get("usage_missing") or r.get("error_class"))
    cost = math.fsum(float(r["cost_usd"]) for r in rows)
    prompt = sum(r["prompt_tokens"] for r in measured)
    completion = sum(r["completion_tokens"] for r in measured)
    return {
        "ledger_attempts": len(rows),
        "reported_usage_calls": len(measured),
        "usage_missing_calls": sum(bool(r.get("usage_missing")) for r in rows),
        "error_attempts": sum(bool(r.get("error_class")) for r in rows),
        "conservatively_billed_attempts": sum(bool(r.get("billed_conservatively")) for r in rows),
        "recorded_prompt_tokens": prompt,
        "recorded_completion_tokens": completion,
        "mean_prompt_tokens_reported_usage_calls": prompt / len(measured),
        "mean_completion_tokens_reported_usage_calls": completion / len(measured),
        "ledger_cost_usd": cost,
        "ledger_cost_usd_per_attempt": cost / len(rows),
        "conservative_cost_usd": math.fsum(float(r["cost_usd"]) for r in rows
                                          if r.get("usage_missing") or r.get("billed_conservatively")),
    }


def main():
    analysis = json.loads(ANALYSIS.read_text())
    rows = []
    for line in LEDGER.read_text().splitlines():
        r = json.loads(line)
        if r["model"] not in MODEL_NAMES:
            continue
        parts = r.get("tag", "").split(":")
        if len(parts) < 5 or parts[:3] != ["nsb2", r["model"].replace("/", "-"), "confirm"]:
            continue
        assert parts[3] in CONDITIONS
        assert int(parts[4]) in range(200, 220 if r["model"] == "deepseek-v4-flash" else 210)
        rows.append(r)
    summary = {
        "metadata": {
            "script": "paper/latex/summarize_audit_traffic.py",
            "python_version": platform.python_version(),
            "ledger": "data/v2/ledger.jsonl",
            "ledger_sha256": sha256(LEDGER),
            "analysis": "data/v2/analysis/exploratory/results.json",
            "analysis_sha256": sha256(ANALYSIS),
            "scope": "All ticks, all five conditions; confirmatory tags only; development excluded",
            "units": "API ledger attempts, token counts, and US dollars from this run",
            "latency": "Unavailable: ledger records only completion timestamps, without request-start times or durations; inter-completion gaps are not latencies because calls overlap",
            "cost_caveat": "Recorded ledger cost is not an invoice: DeepSeek uses recorded cache counts and configured rates; OpenRouter uses returned usage.cost if present, otherwise configured token rates; missing usage and failed 5xx requests use conservative reservations",
            "usage_caveat": "Token averages use calls with reported usage only; missing usage and error rows record zero tokens and are excluded from token-mean denominators; token totals are lower bounds",
            "prospective_multiplier_caveat": "Full-audit call and equal-duration serial-latency multipliers are design extrapolations, not measured deployed latency; monetary/token multipliers below are measured aggregate ratios at the realized approximately half-decision sampling rate",
        },
        "models": {},
    }
    for model, short in MODEL_NAMES.items():
        selected = [r for r in rows if r["model"] == model]
        by_kind = {kind: summarize([r for r in selected if call_kind(r) == kind]) for kind in KINDS}
        block = analysis["models"][model]
        assigned = sum(x["overall"]["assigned_decisions"] for x in block["B_flow"].values())
        cf_selected = sum(x["overall"]["cf_mask_selected"] for x in block["B_flow"].values())
        probed = sum(x["overall"]["probed_decisions"] for x in block["B_flow"].values())
        feature_reasks = sum(x["overall"]["feature_reasks_attempted"] for x in block["B_flow"].values())
        nulls = sum(x["overall"]["pooled"]["n_selected"] for x in block["E_null_rates"].values())
        assert by_kind["null"]["ledger_attempts"] == nulls
        assert by_kind["base"]["ledger_attempts"] == assigned + by_kind["base"]["error_attempts"]
        assert sum(by_kind[k]["ledger_attempts"] - by_kind[k]["error_attempts"]
                   for k in ("sign_flip_news", "sign_flip_momentum")) == feature_reasks
        total = summarize(selected)
        base = by_kind["base"]
        token_total = total["recorded_prompt_tokens"] + total["recorded_completion_tokens"]
        token_base = base["recorded_prompt_tokens"] + base["recorded_completion_tokens"]
        r_null = nulls / cf_selected
        summary["models"][model] = {
            "short_name": short,
            "providers": dict(Counter(r["provider"] for r in selected)),
            "served_by": dict(Counter(str(r.get("served_by", "unrecorded")) for r in selected)),
            "first_completion_utc": min(r["timestamp"] for r in selected),
            "last_completion_utc": max(r["timestamp"] for r in selected),
            "by_call_type": by_kind,
            "all_calls": total,
            "sampling_and_multipliers": {
                "assigned_decisions": assigned,
                "cf_mask_selected": cf_selected,
                "valid_base_probed_decisions": probed,
                "logical_feature_reasks": feature_reasks,
                "null_reasks": nulls,
                "null_reasks_on_invalid_base": sum(x["overall"]["pooled"]["n_selected_base_invalid"]
                                                   for x in block["E_null_rates"].values()),
                "cf_sampling_share_assigned": cf_selected / assigned,
                "realized_null_share_of_cf_selected": r_null,
                "realized_null_share_of_assigned": nulls / assigned,
                "full_audit_expected_calls_per_decision_at_realized_null_share": 3 + r_null,
                "full_audit_equal_duration_serial_latency_multiplier": 3 + r_null,
                "realized_logical_calls_per_assigned_decision": (assigned + feature_reasks + nulls) / assigned,
                "realized_ledger_attempts_per_assigned_decision": len(selected) / assigned,
                "measured_recorded_token_multiplier_vs_base_calls": token_total / token_base,
                "measured_ledger_cost_multiplier_vs_base_calls": total["ledger_cost_usd"] / base["ledger_cost_usd"],
                "ledger_cost_usd_per_assigned_decision": total["ledger_cost_usd"] / assigned,
                "base_ledger_cost_usd_per_assigned_decision": base["ledger_cost_usd"] / assigned,
            },
        }
    output = OUT / "network_service_summary.json"
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    lines = ["# Offline network-audit measurements", "",
             "The statistics below are measured from this run's confirmatory ledger only, pooled over all ticks and conditions. Reproduce with `.venv/bin/python paper/latex/summarize_audit_traffic.py`.", "",
             "| Model | Type | Attempts | Calls with usage | Mean prompt tokens | Mean completion tokens | Ledger cost (USD) |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for m in summary["models"].values():
        for kind, b in m["by_call_type"].items():
            lines.append(f'| {m["short_name"]} | {kind} | {b["ledger_attempts"]} | {b["reported_usage_calls"]} | {b["mean_prompt_tokens_reported_usage_calls"]:.2f} | {b["mean_completion_tokens_reported_usage_calls"]:.2f} | {b["ledger_cost_usd"]:.6f} |')
    lines.extend(["", "| Model | CF share of decisions | Null share of selected | Full-audit calls | Realized attempts/decision | Token multiplier | Cost multiplier | USD/assigned decision |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for m in summary["models"].values():
        s = m["sampling_and_multipliers"]
        lines.append(f'| {m["short_name"]} | {s["cf_sampling_share_assigned"]:.6f} | {s["realized_null_share_of_cf_selected"]:.6f} | {s["full_audit_expected_calls_per_decision_at_realized_null_share"]:.6f} | {s["realized_ledger_attempts_per_assigned_decision"]:.6f} | {s["measured_recorded_token_multiplier_vs_base_calls"]:.4f} | {s["measured_ledger_cost_multiplier_vs_base_calls"]:.4f} | {s["ledger_cost_usd_per_assigned_decision"]:.7f} |')
    lines.extend(["", "## Interpretation and missing data", "",
                  summary["metadata"]["latency"] + ".", "",
                  summary["metadata"]["usage_caveat"] + ".", "",
                  summary["metadata"]["cost_caveat"] + ".", "",
                  summary["metadata"]["prospective_multiplier_caveat"] + ".", "",
                  "There are five Luna entries with unavailable usage and two Luna HTTP 503 attempts conservatively booked before retries. They are included in attempt/cost totals; their zero token placeholders are excluded from token means. One Haiku null call had an invalid base, matching the disclosed deviation.", "",
                  "## Suggested concise manuscript paragraph", "",
                  "A networked audit sidecar would retain the original context and issue two non-trading sign-flip requests after each sampled base decision, plus an identical-prompt null request at the realized 18.52–18.59% share of sampled decisions. Full coverage would therefore require about 3.19 calls per decision; the approximately one-half sampling used here required 2.09–2.10 attempts per assigned decision. Measured in this run, the confirmatory ledger records mean input/output usage of " +
                  "; ".join(f'{m["short_name"]} {m["all_calls"]["mean_prompt_tokens_reported_usage_calls"]:.1f}/{m["all_calls"]["mean_completion_tokens_reported_usage_calls"]:.1f} tokens per call' for m in summary["models"].values()) +
                  ". Relative to base calls alone, recorded token traffic rose " +
                  ", ".join(f'{m["sampling_and_multipliers"]["measured_recorded_token_multiplier_vs_base_calls"]:.2f}×' for m in summary["models"].values()) +
                  " and ledger cost rose " +
                  ", ".join(f'{m["sampling_and_multipliers"]["measured_ledger_cost_multiplier_vs_base_calls"]:.2f}×' for m in summary["models"].values()) +
                  " (DeepSeek, Haiku, Luna). Token averages exclude five Luna responses without usage and two failed attempts; booked costs include conservative estimates. Request durations were not logged, so latency multipliers are architectural scenarios: serialized equal-duration calls scale with call count, while parallel probes can share a second request round. Lower audit sampling reduces traffic approximately linearly while leaving fewer observations for regime-specific instrument and null checks.", ""])
    (OUT / "network_service_summary.md").write_text("\n".join(lines))
    print(output.relative_to(ROOT))
    for m in summary["models"].values():
        print(m["short_name"], json.dumps({"all_calls": m["all_calls"], "sampling": m["sampling_and_multipliers"]}))


if __name__ == "__main__":
    main()
