# Offline network-audit measurements

The statistics below are measured from this run's confirmatory ledger only, pooled over all ticks and conditions. Reproduce with `.venv/bin/python paper/latex/summarize_audit_traffic.py`.

| Model | Type | Attempts | Calls with usage | Mean prompt tokens | Mean completion tokens | Ledger cost (USD) |
|---|---|---:|---:|---:|---:|---:|
| DeepSeek | base | 24000 | 24000 | 712.56 | 19.28 | 3.175453 |
| DeepSeek | sign_flip_news | 12105 | 12105 | 713.06 | 19.26 | 1.021414 |
| DeepSeek | sign_flip_momentum | 12105 | 12105 | 713.06 | 19.18 | 1.052136 |
| DeepSeek | null | 2250 | 2250 | 716.55 | 19.23 | 0.188902 |
| Haiku | base | 12000 | 12000 | 975.20 | 80.50 | 1.653269 |
| Haiku | sign_flip_news | 5989 | 5989 | 975.49 | 84.41 | 0.836998 |
| Haiku | sign_flip_momentum | 5989 | 5989 | 975.53 | 86.30 | 0.842657 |
| Haiku | null | 1110 | 1110 | 984.87 | 80.47 | 0.153983 |
| Luna | base | 12001 | 11999 | 683.00 | 25.10 | 0.970916 |
| Luna | sign_flip_news | 5994 | 5990 | 683.19 | 25.15 | 0.486269 |
| Luna | sign_flip_momentum | 5993 | 5992 | 683.23 | 25.14 | 0.485084 |
| Luna | null | 1110 | 1110 | 690.44 | 25.13 | 0.090586 |

| Model | CF share of decisions | Null share of selected | Full-audit calls | Realized attempts/decision | Token multiplier | Cost multiplier | USD/assigned decision |
|---|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek | 0.504375 | 0.185874 | 3.185874 | 2.102500 | 2.1036 | 1.7125 | 0.0002266 |
| Haiku | 0.499583 | 0.185154 | 3.185154 | 2.090667 | 2.0964 | 2.1091 | 0.0002906 |
| Luna | 0.499583 | 0.185154 | 3.185154 | 2.091500 | 2.0924 | 2.0938 | 0.0001694 |

## Interpretation and missing data

Unavailable: ledger records only completion timestamps, without request-start times or durations; inter-completion gaps are not latencies because calls overlap.

Token averages use calls with reported usage only; missing usage and error rows record zero tokens and are excluded from token-mean denominators; token totals are lower bounds.

Recorded ledger cost is not an invoice: DeepSeek uses recorded cache counts and configured rates; OpenRouter uses returned usage.cost if present, otherwise configured token rates; missing usage and failed 5xx requests use conservative reservations.

Full-audit call and equal-duration serial-latency multipliers are design extrapolations, not measured deployed latency; monetary/token multipliers below are measured aggregate ratios at the realized approximately half-decision sampling rate.

There are five Luna entries with unavailable usage and two Luna HTTP 503 attempts conservatively booked before retries. They are included in attempt/cost totals; their zero token placeholders are excluded from token means. One Haiku null call had an invalid base, matching the disclosed deviation.

## Suggested concise manuscript paragraph

A networked audit sidecar would retain the original context and issue two non-trading sign-flip requests after each sampled base decision, plus an identical-prompt null request at the realized 18.52–18.59% share of sampled decisions. Full coverage would therefore require about 3.19 calls per decision; the approximately one-half sampling used here required 2.09–2.10 attempts per assigned decision. Measured in this run, the confirmatory ledger records mean input/output usage of DeepSeek 713.0/19.3 tokens per call; Haiku 975.8/82.8 tokens per call; Luna 683.4/25.1 tokens per call. Relative to base calls alone, recorded token traffic rose 2.10×, 2.10×, 2.09× and ledger cost rose 1.71×, 2.11×, 2.09× (DeepSeek, Haiku, Luna). Token averages exclude five Luna responses without usage and two failed attempts; booked costs include conservative estimates. Request durations were not logged, so latency multipliers are architectural scenarios: serialized equal-duration calls scale with call count, while parallel probes can share a second request round. Lower audit sampling reduces traffic approximately linearly while leaving fewer observations for regime-specific instrument and null checks.
