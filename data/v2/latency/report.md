# Post hoc audit-sidecar latency benchmark

November 2026 operational measurement; separate from the preregistered study.

Fixed sample seed: 20261119. Total cost: USD 0.14055746; cost by provider: {'deepseek': 0.044888064, 'openrouter': 0.0956694}.

Run UTC window: {'start': '2026-11-19T16:16:03.664825+00:00', 'end': '2026-11-19T16:33:25.617946+00:00'}.

Main statistics use full-run rows only; pilot measurements are reported separately. Costs and the overall run window above include both stages.

## Measurement and limitations

- Prompts use the original build_messages and _perturbed_messages functions, with max_tokens=512 and unchanged study provider routing/parameters.
- Portfolios are replayed from initial personas and logged actions, settlement prices and 10% fines; every logged wealth is checked. Features, input feedback and completed history come directly from confirmatory logs. No prompt-state approximation is used.
- Each decision has a fresh base response, news and momentum sign flips, and an identical-prompt null. Action-change rates are sanity checks, not inferential estimates.
- Deployment sidecar-added latency is last probe end minus first probe start per decision, using only news, momentum and null re-asks. The agent decision already exists in deployment, so the benchmark base call is excluded. This is measured wall time, including gaps between probes and client overhead; it is not an arithmetic sum or maximum of durations.
- Sequential sums and parallel critical paths are paired arithmetic estimates from the same four request latencies. They exclude orchestration overhead; the parallel estimate on sequential observations does not measure contention. Observed audit times are measured wall time, including scheduling; schedule-specific tables distinguish actual sequential and parallel execution.
- Pilot: five decisions/model, sequential probes, one audited decision in flight. Full target: 60/model at c=1 split equally across sequential/parallel probes, then 20/model at c=4 and c=8 with parallel probes. Concurrency means audited decisions; up to 3*c probe HTTP calls may be in flight. Models are measured separately in bounded waves, rather than a steady-state load generator; the final wave may be smaller than the target concurrency.
- End-to-end client request latency includes budget locks/reservation, HTTP attempts, retries/backoff, parsing and ledger writes. Pure HTTP attempt latency measures client.post through receipt of the full buffered response. Overhead is end-to-end latency minus the sum of attempt durations; it includes backoff when retries occur. At most three attempts/request use the study retry policy. No whole batch is retried.
- OpenRouter charged cost uses reported usage.cost when supplied; native DeepSeek cost uses the study price snapshot and reported cache/token usage (an estimate of charge, not an invoice). Unknown charges on transport/5xx failures are conservatively reserved and labelled. Balance deltas may differ due to display precision, delayed usage reporting or other account activity. DeepSeek served provider is identified by the native endpoint; it does not independently report a served-provider field.
- USD 0.50/provider reservations enforce the USD 1.00 aggregate cap in a separate latency ledger. Dry-run costs and timings are synthetic and must never be interpreted as measurements.
- All calls originate from a single client host, a container in the research workspace. Physical host location, egress region, route and competing network load are not independently verified; timezone settings do not establish location. No streaming/TTFT is measured.
- Percentiles use linear interpolation on order statistics; small-sample tail percentiles are descriptive only. The fixed condition/regime round-robin sample is not a population-representative efficacy sample.

- Models and schedules run in a fixed chronological order with disjoint prompts. Concurrency inflation is descriptive and may include prompt composition, cache warming, provider load and time-of-run differences; it is not a randomized estimate of the effect of concurrency.

## Runs

### pilot

```json
{
  "stage": "pilot",
  "status": "complete",
  "start_utc": "2026-11-19T16:16:03.664825+00:00",
  "dry_run": false,
  "host": "BullSAIserverUbuntu",
  "platform": "Linux-6.8.0-138-generic-x86_64-with-glibc2.35",
  "python": "3.12.2",
  "versions": {
    "httpx": "0.28.1",
    "numpy": "2.5.4"
  },
  "full_counts_per_model": [
    60,
    20,
    20
  ],
  "seed": 20261119,
  "client_location": "Unverified physical host/egress location; container timezone is not geolocation",
  "balances_before": {
    "deepseek": {
      "remaining_usd": 10.09,
      "checked_utc": "2026-11-19T16:16:04.032668+00:00"
    },
    "openrouter": {
      "remaining_usd": 11.421646828999997,
      "checked_utc": "2026-11-19T16:16:04.119159+00:00"
    }
  },
  "sample_plan": [
    {
      "concurrency": 1,
      "schedule": "sequential",
      "decisions_per_model": 5
    }
  ],
  "end_utc": "2026-11-19T16:18:12.164676+00:00",
  "balances_after": {
    "deepseek": {
      "remaining_usd": 10.09,
      "checked_utc": "2026-11-19T16:18:12.466853+00:00"
    },
    "openrouter": {
      "remaining_usd": 11.418383328999994,
      "checked_utc": "2026-11-19T16:18:12.492334+00:00"
    }
  }
}
```

### full

```json
{
  "stage": "full",
  "status": "complete",
  "start_utc": "2026-11-19T16:19:58.340707+00:00",
  "dry_run": false,
  "host": "BullSAIserverUbuntu",
  "platform": "Linux-6.8.0-138-generic-x86_64-with-glibc2.35",
  "python": "3.12.2",
  "versions": {
    "httpx": "0.28.1",
    "httpcore": "1.0.9",
    "anyio": "4.15.1",
    "numpy": "2.5.4"
  },
  "full_counts_per_model": [
    60,
    20,
    20
  ],
  "seed": 20261119,
  "client_location": "Unverified physical host/egress location; container timezone is not geolocation",
  "balances_before": {
    "deepseek": {
      "remaining_usd": 10.09,
      "checked_utc": "2026-11-19T16:19:58.734937+00:00"
    },
    "openrouter": {
      "remaining_usd": 11.417128528999996,
      "checked_utc": "2026-11-19T16:19:58.985669+00:00"
    }
  },
  "sample_plan": [
    {
      "concurrency": 1,
      "schedule": "sequential",
      "decisions_per_model": 30
    },
    {
      "concurrency": 1,
      "schedule": "parallel",
      "decisions_per_model": 30
    },
    {
      "concurrency": 4,
      "schedule": "parallel",
      "decisions_per_model": 20
    },
    {
      "concurrency": 8,
      "schedule": "parallel",
      "decisions_per_model": 20
    }
  ],
  "end_utc": "2026-11-19T16:33:25.617946+00:00",
  "balances_after": {
    "deepseek": {
      "remaining_usd": 10.07,
      "checked_utc": "2026-11-19T16:33:25.939139+00:00"
    },
    "openrouter": {
      "remaining_usd": 11.335973328999998,
      "checked_utc": "2026-11-19T16:33:25.974367+00:00"
    }
  }
}
```

## Original run validation and deviations

Historical validation snapshot from the paid run; its test counts and code hashes predate this offline amendment. Current input hashes are in summary.json.

```json
{
  "checked_utc": "2026-11-19T16:34:41.412150+00:00",
  "requests": 1260,
  "audited_decisions": 315,
  "unique_source_files_verified_unchanged": 113,
  "ledger_records": 1260,
  "checks": [
    "Exact four-call protocol and logged prompt perturbations/null identity",
    "Distinct deterministic pilot/full samples",
    "Source SHA256 unchanged",
    "Monotonic timing identities and nonnegative overhead",
    "Base before all probes; sequential probes ordered",
    "Audited decisions in flight never exceed group concurrency",
    "Dedicated ledger totals equal request totals and satisfy both provider and aggregate caps",
    "Both stages complete; no stage relaunched"
  ],
  "peak_audited_decisions_in_flight": {
    "pilot:deepseek-v4-flash:c1:sequential": 1,
    "pilot:anthropic/claude-haiku-5.5:c1:sequential": 1,
    "pilot:openai/gpt-6-luna:c1:sequential": 1,
    "full:deepseek-v4-flash:c1:sequential": 1,
    "full:deepseek-v4-flash:c1:parallel": 1,
    "full:deepseek-v4-flash:c4:parallel": 4,
    "full:deepseek-v4-flash:c8:parallel": 8,
    "full:anthropic/claude-haiku-5.5:c1:sequential": 1,
    "full:anthropic/claude-haiku-5.5:c1:parallel": 1,
    "full:anthropic/claude-haiku-5.5:c4:parallel": 4,
    "full:anthropic/claude-haiku-5.5:c8:parallel": 8,
    "full:openai/gpt-6-luna:c1:sequential": 1,
    "full:openai/gpt-6-luna:c1:parallel": 1,
    "full:openai/gpt-6-luna:c4:parallel": 4,
    "full:openai/gpt-6-luna:c8:parallel": 8
  },
  "deviations": [
    "Native DeepSeek charged cost cannot be directly retrieved per request; reported token/cache usage is priced with the unchanged study snapshot and labelled estimated",
    "Physical single-client host/egress location is unverified and reported as such"
  ],
  "clarifications": [
    "No prompt-state approximation was needed: every source portfolio was replayed and checked against logged wealth before selection",
    "Measured sequential and parallel schedules use disjoint samples; arithmetic critical-path estimates remain clearly labelled",
    "Light concurrency checks use bounded waves, with a partial final c8 wave; no steady-state throughput claim",
    "Full run exactly matches approved 30 sequential plus 30 parallel c1, 20 c4 and 20 c8 decisions per model"
  ],
  "tests": {
    "historical_benchmark": "7 passed at collection time",
    "current_release": "See VERIFICATION.md for the current complete offline suite"
  },
  "code_sha256_at_collection": {
    "src/v2/latency_benchmark.py": "f7e106df81b044f8c0369196e3e3505688cd18c57bdd3b3df0061ea67bd1c03f",
    "tests/v2/test_latency_benchmark.py": "29a955ad86aa229479a990c5e66af43d0f0488e046e14e6dd77fb858bb2433b9"
  },
  "public_packaging": "Historical collection validation; source hashes identify the original collection implementation, before portable-path and public documentation changes."
}
```

## Measured sidecar-added latency (probes only)

Base excluded; n counts decisions with exactly one news, momentum and null probe. Each span runs from first probe start to last probe end. Full-run and pilot groups remain separate.

| Model / stage / concurrency / schedule | n | Median / p90 / p95 / max added latency (s) |
|---|---:|---:|
| deepseek-v4-flash / full:c1:parallel | 30 | 0.818220 / 1.104251 / 1.217594 / 1.303404 |
| deepseek-v4-flash / full:c1:sequential | 30 | 2.453871 / 2.774238 / 2.798788 / 2.875763 |
| deepseek-v4-flash / full:c4:parallel | 20 | 0.887008 / 1.040086 / 1.047989 / 1.182922 |
| deepseek-v4-flash / full:c8:parallel | 20 | 0.851931 / 1.075202 / 1.129210 / 1.360737 |
| anthropic/claude-haiku-5.5 / full:c1:parallel | 30 | 1.783962 / 2.661844 / 3.001649 / 3.318919 |
| anthropic/claude-haiku-5.5 / full:c1:sequential | 30 | 4.321260 / 6.321783 / 7.240038 / 9.257241 |
| anthropic/claude-haiku-5.5 / full:c4:parallel | 20 | 2.324039 / 3.701350 / 6.401173 / 11.058205 |
| anthropic/claude-haiku-5.5 / full:c8:parallel | 20 | 1.941774 / 2.989497 / 4.193452 / 10.876872 |
| openai/gpt-6-luna / full:c1:parallel | 30 | 1.371787 / 1.833843 / 2.052309 / 2.860402 |
| openai/gpt-6-luna / full:c1:sequential | 30 | 3.835658 / 4.754279 / 4.923437 / 6.350491 |
| openai/gpt-6-luna / full:c4:parallel | 20 | 1.581434 / 1.851259 / 2.456122 / 3.731645 |
| openai/gpt-6-luna / full:c8:parallel | 20 | 1.546472 / 2.057705 / 2.143234 / 2.411991 |
| deepseek-v4-flash / pilot:c1:sequential | 5 | 2.490158 / 2.627105 / 2.646619 / 2.666132 |
| anthropic/claude-haiku-5.5 / pilot:c1:sequential | 5 | 3.850136 / 5.777779 / 5.873546 / 5.969314 |
| openai/gpt-6-luna / pilot:c1:sequential | 5 | 10.412116 / 23.127180 / 26.178191 / 29.229202 |

Reference reconciliation: deepseek-v4-flash: 0.818220 s (reference rounded check 0.82 s; matches); anthropic/claude-haiku-5.5: 1.783962 s (reference rounded check 1.78 s; matches); openai/gpt-6-luna: 1.371787 s (reference rounded check 1.37 s; matches). The larger base-inclusive observed audit medians below measure a different interval.

## Pilot measurements (separate from main statistics)

| Model | Valid / total | Request median / p95 (s) | Base-inclusive observed audit median / p95 (s) | Cost USD | Request UTC window |
|---|---:|---:|---:|---:|---|
| deepseek-v4-flash | 20/20 | 0.788744 / 0.944497 | 3.250026 / 3.357788 | 0.002399952 | {'start': '2026-11-19T16:16:06.194122+00:00', 'end': '2026-11-19T16:16:22.347296+00:00'} |
| anthropic/claude-haiku-5.5 | 20/20 | 1.096449 / 2.844868 | 4.972679 / 7.255282 | 0.002873500 | {'start': '2026-11-19T16:16:22.347535+00:00', 'end': '2026-11-19T16:16:49.882446+00:00'} |
| openai/gpt-6-luna | 20/20 | 3.436309 / 10.569022 | 13.711020 / 33.222691 | 0.001644800 | {'start': '2026-11-19T16:16:49.882876+00:00', 'end': '2026-11-19T16:18:12.164266+00:00'} |

## Temporal variability

Luna in the pilot stage (stage UTC window 2026-11-19T16:16:03.664825+00:00 to 2026-11-19T16:18:12.164676+00:00; exact model request window {'start': '2026-11-19T16:16:49.882876+00:00', 'end': '2026-11-19T16:18:12.164266+00:00'}) had request median / p95 3.436309 / 10.569022 s (3.44 / 10.57 s) and base-inclusive observed audit median 13.711020 s (about 13.7 s). Full-run Luna request median / p95 was 1.273542 / 1.961976 s (about 1.27 / 1.96 s). Full-run c1 sequential base-inclusive audit median was 5.207458 s (about 5.2 s).

Haiku full-run maximum request latency was 11.056041 s (11.06 s).

One approximately 17-minute window from a single host cannot characterize provider latency distributions or tails. Pilot/full differences demonstrate temporal variability; chronology, disjoint prompts and network conditions prevent a causal attribution to provider load or concurrency.

## Facts for the manuscript

Full-run facts below exclude the pilot. Times are seconds, displayed to six decimals; unrounded values are in summary.json. Costs distinguish the three deployment probes from the four-call benchmark protocol. Concurrency ratios are descriptive comparisons between separate time windows and samples.

- deepseek-v4-flash: 400 requests / 100 audited decisions; per-request median / p95 0.780799 / 1.061301 s; c1 probes-only median / p95 sequential 2.453871 / 2.798788 s versus parallel 0.818220 / 1.217594 s; c4 parallel request median / p95 0.782874 / 1.025324 s (1.045730x c1 request median), probes-only median / p95 0.887008 / 1.047989 s (1.084071x c1 probes-only median); c8 parallel request median / p95 0.770072 / 0.994629 s (1.028629x c1 request median), probes-only median / p95 0.851931 / 1.129210 s (1.041200x c1 probes-only median); errors / 429 / 5xx / retries / invalid 0 / 0 / 0 / 0 / 0; USD per audited decision: probes only 0.000253139, base plus probes 0.000424881; full model request UTC window {'start': '2026-11-19T16:20:01.149191+00:00', 'end': '2026-11-19T16:22:45.415042+00:00'}.
- anthropic/claude-haiku-5.5: 400 requests / 100 audited decisions; per-request median / p95 1.403870 / 2.939775 s; c1 probes-only median / p95 sequential 4.321260 / 7.240038 s versus parallel 1.783962 / 3.001649 s; c4 parallel request median / p95 1.592195 / 3.011974 s (1.111441x c1 request median), probes-only median / p95 2.324039 / 6.401173 s (1.302740x c1 probes-only median); c8 parallel request median / p95 1.272363 / 2.742294 s (0.888180x c1 request median), probes-only median / p95 1.941774 / 4.193452 s (1.088462x c1 probes-only median); errors / 429 / 5xx / retries / invalid 0 / 0 / 0 / 0 / 0; USD per audited decision: probes only 0.000434978, base plus probes 0.000576641; full model request UTC window {'start': '2026-11-19T16:22:45.415987+00:00', 'end': '2026-11-19T16:28:53.331554+00:00'}.
- openai/gpt-6-luna: 400 requests / 100 audited decisions; per-request median / p95 1.273542 / 1.961976 s; c1 probes-only median / p95 sequential 3.835658 / 4.923437 s versus parallel 1.371787 / 2.052309 s; c4 parallel request median / p95 1.369146 / 2.000592 s (1.128357x c1 request median), probes-only median / p95 1.581434 / 2.456122 s (1.152828x c1 probes-only median); c8 parallel request median / p95 1.344344 / 1.985448 s (1.107916x c1 request median), probes-only median / p95 1.546472 / 2.143234 s (1.127342x c1 probes-only median); errors / 429 / 5xx / retries / invalid 0 / 0 / 0 / 0 / 0; USD per audited decision: probes only 0.000251135, base plus probes 0.000334870; full model request UTC window {'start': '2026-11-19T16:28:53.332817+00:00', 'end': '2026-11-19T16:33:25.616800+00:00'}.

- Overall stage UTC window (pilot included): {'start': '2026-11-19T16:16:03.664825+00:00', 'end': '2026-11-19T16:33:25.617946+00:00'}; total cost USD 0.140557464. DeepSeek costs are estimates from recorded token/cache usage and the study price snapshot; OpenRouter costs use reported charges.

## Full-run per-model measurements

| Model / group | Requests valid/total | Median / p90 / p95 / max request (s) | Sequential sum median (s) | Parallel path median (s) | Observed audit median (s) | Errors / 429 / 5xx | Cost USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-v4-flash / full only | 400/400 | 0.781 / 1.000 / 1.061 / 1.361 | 3.200 | 1.699 | 1.784 | 0 / 0 / 0 | 0.042488 |
| deepseek-v4-flash / full:c1:parallel | 120/120 | 0.749 / 1.001 / 1.125 / 1.298 | 3.045 | 1.627 | 1.629 | 0 / 0 / 0 | 0.012675 |
| deepseek-v4-flash / full:c1:sequential | 120/120 | 0.801 / 1.012 / 1.095 / 1.277 | 3.285 | 1.752 | 3.286 | 0 / 0 / 0 | 0.012876 |
| deepseek-v4-flash / full:c4:parallel | 80/80 | 0.783 / 1.001 / 1.025 / 1.175 | 3.191 | 1.702 | 1.705 | 0 / 0 / 0 | 0.008511 |
| deepseek-v4-flash / full:c8:parallel | 80/80 | 0.770 / 0.954 / 0.995 / 1.361 | 3.147 | 1.651 | 1.657 | 0 / 0 / 0 | 0.008426 |
| anthropic/claude-haiku-5.5 / full only | 400/400 | 1.404 / 2.443 / 2.940 / 11.056 | 5.902 | 3.506 | 4.118 | 0 / 0 / 0 | 0.057664 |
| anthropic/claude-haiku-5.5 / full:c1:parallel | 120/120 | 1.433 / 2.298 / 2.452 / 3.312 | 6.045 | 3.453 | 3.456 | 0 / 0 / 0 | 0.017475 |
| anthropic/claude-haiku-5.5 / full:c1:sequential | 120/120 | 1.359 / 2.499 / 3.979 / 10.834 | 5.738 | 3.224 | 5.740 | 0 / 0 / 0 | 0.017525 |
| anthropic/claude-haiku-5.5 / full:c4:parallel | 80/80 | 1.592 / 2.781 / 3.012 / 11.056 | 7.222 | 4.312 | 4.321 | 0 / 0 / 0 | 0.011755 |
| anthropic/claude-haiku-5.5 / full:c8:parallel | 80/80 | 1.272 / 2.430 / 2.742 / 10.877 | 5.781 | 3.739 | 3.746 | 0 / 0 / 0 | 0.010910 |
| openai/gpt-6-luna / full only | 400/400 | 1.274 / 1.736 / 1.962 / 3.732 | 5.230 | 2.733 | 3.107 | 0 / 0 / 0 | 0.033487 |
| openai/gpt-6-luna / full:c1:parallel | 120/120 | 1.213 / 1.605 / 1.767 / 3.255 | 4.968 | 2.630 | 2.630 | 0 / 0 / 0 | 0.010048 |
| openai/gpt-6-luna / full:c1:sequential | 120/120 | 1.243 / 1.702 / 1.922 / 2.380 | 5.206 | 2.702 | 5.207 | 0 / 0 / 0 | 0.010050 |
| openai/gpt-6-luna / full:c4:parallel | 80/80 | 1.369 / 1.789 / 2.001 / 3.732 | 5.297 | 2.902 | 2.907 | 0 / 0 / 0 | 0.006713 |
| openai/gpt-6-luna / full:c8:parallel | 80/80 | 1.344 / 1.810 / 1.985 / 2.406 | 5.515 | 2.918 | 2.918 | 0 / 0 / 0 | 0.006677 |

## Full-run base-inclusive audit completion by actual schedule

These are observed four-call audit wall times, including the base call and orchestration. Deployment probes-only added latency is reported separately above. Arithmetic parallel-path estimates above are not measured parallel completion times.

| Model / actual schedule | Decisions | Median / p90 / p95 / max audit (s) |
|---|---:|---:|
| deepseek-v4-flash / full:c1:parallel | 30 | 1.629 / 1.859 / 2.012 / 2.114 |
| deepseek-v4-flash / full:c1:sequential | 30 | 3.286 / 3.694 / 3.765 / 3.975 |
| deepseek-v4-flash / full:c4:parallel | 20 | 1.705 / 1.927 / 2.018 / 2.243 |
| deepseek-v4-flash / full:c8:parallel | 20 | 1.657 / 1.812 / 1.880 / 2.210 |
| anthropic/claude-haiku-5.5 / full:c1:parallel | 30 | 3.456 / 4.312 / 4.670 / 4.995 |
| anthropic/claude-haiku-5.5 / full:c1:sequential | 30 | 5.740 / 10.683 / 13.343 / 16.346 |
| anthropic/claude-haiku-5.5 / full:c4:parallel | 20 | 4.321 / 5.955 / 7.326 / 12.120 |
| anthropic/claude-haiku-5.5 / full:c8:parallel | 20 | 3.746 / 5.502 / 11.275 / 12.110 |
| openai/gpt-6-luna / full:c1:parallel | 30 | 2.630 / 3.297 / 4.081 / 4.440 |
| openai/gpt-6-luna / full:c1:sequential | 30 | 5.207 / 6.004 / 6.183 / 8.495 |
| openai/gpt-6-luna / full:c4:parallel | 20 | 2.907 / 3.882 / 4.457 / 5.777 |
| openai/gpt-6-luna / full:c8:parallel | 20 | 2.918 / 3.738 / 3.808 / 3.816 |

## Pure HTTP latency, client overhead and validity

| Model | HTTP attempt median / p95 (s) | Client overhead median / p95 (s) | Invalid / all requests | Invalid share | Routing deviations |
|---|---:|---:|---:|---:|---:|
| deepseek-v4-flash | 0.7727 / 1.0538 | 0.0077 / 0.0150 | 0/400 | 0.0000% | 0 |
| anthropic/claude-haiku-5.5 | 1.3908 / 2.9319 | 0.0128 / 0.0159 | 0/400 | 0.0000% | 0 |
| openai/gpt-6-luna | 1.2613 / 1.9458 | 0.0127 / 0.0164 | 0/400 | 0.0000% | 0 |

## Concurrency and sanity checks

| Model / group | Request median inflation vs full c1 parallel | Error rate | HTTP 429 rate |
|---|---:|---:|---:|
| deepseek-v4-flash / full:c1:parallel | 1.0 | 0.0 | 0.0 |
| deepseek-v4-flash / full:c1:sequential | 1.0694757956207663 | 0.0 | 0.0 |
| deepseek-v4-flash / full:c4:parallel | 1.0457295176739927 | 0.0 | 0.0 |
| deepseek-v4-flash / full:c8:parallel | 1.0286289721539121 | 0.0 | 0.0 |
| anthropic/claude-haiku-5.5 / full:c1:parallel | 1.0 | 0.0 | 0.0 |
| anthropic/claude-haiku-5.5 / full:c1:sequential | 0.9483210825928982 | 0.0 | 0.0 |
| anthropic/claude-haiku-5.5 / full:c4:parallel | 1.11144120019285 | 0.0 | 0.0 |
| anthropic/claude-haiku-5.5 / full:c8:parallel | 0.8881803216262231 | 0.0 | 0.0 |
| openai/gpt-6-luna / full:c1:parallel | 1.0 | 0.0 | 0.0 |
| openai/gpt-6-luna / full:c1:sequential | 1.0244951736036727 | 0.0 | 0.0 |
| openai/gpt-6-luna / full:c4:parallel | 1.1283566563754202 | 0.0 | 0.0 |
| openai/gpt-6-luna / full:c8:parallel | 1.1079161745883566 | 0.0 | 0.0 |

| Model | Probe | Changes / valid pairs | Rate (sanity check only) |
|---|---|---:|---:|
| deepseek-v4-flash | news | 34/100 | 0.34 |
| deepseek-v4-flash | momentum | 60/100 | 0.6 |
| deepseek-v4-flash | null | 0/100 | 0.0 |
| anthropic/claude-haiku-5.5 | news | 34/100 | 0.34 |
| anthropic/claude-haiku-5.5 | momentum | 53/100 | 0.53 |
| anthropic/claude-haiku-5.5 | null | 5/100 | 0.05 |
| openai/gpt-6-luna | news | 48/100 | 0.48 |
| openai/gpt-6-luna | momentum | 42/100 | 0.42 |
| openai/gpt-6-luna | null | 6/100 | 0.06 |

Full median/p90/p95/max, concurrency inflation, action-change counts/rates, source hashes, and all per-request details are in summary.json and requests.jsonl.
