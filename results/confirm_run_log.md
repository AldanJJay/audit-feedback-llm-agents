# Confirmatory run log

## Run window

- First confirmatory API request: 2026-10-27 12:45:03 UTC.
- DeepSeek completed: 2026-10-27 16:11:57 UTC.
- Haiku completed: 2026-10-27 16:05:38 UTC.
- Luna completed: 2026-10-27 16:32:47 UTC.
- All three collection processes had exited after writing their completion summaries by 2026-10-27 16:32:48 UTC.

## Pre-flight

- `.venv/bin/pytest tests/v2 -q`: **99 passed**.
- `git status --short -- src/ docs/`: no modified tracked files before collection.
- `ps -ef | rg '[s]rc.v2.simulate'`: no simulation process was running before collection.
- Confirm dry-runs completed for each requested model. The projections reported DeepSeek USD 4.227, Haiku USD 2.786, and Luna USD 1.963. These were projections; actual spend is below.

## Commands

One detached process per model, using provider keys supplied through `DEEPSEEK_API_KEY` and `OPENROUTER_API_KEY` (public copy: local credential paths removed):

```sh
setsid nohup .venv/bin/python -m src.v2.simulate --model deepseek-v4-flash --stage confirm --parallel 4 > logs/confirm_deepseek-v4-flash.log 2>&1 < /dev/null &
setsid nohup .venv/bin/python -m src.v2.simulate --model anthropic/claude-haiku-5.5 --stage confirm --parallel 3 > logs/confirm_anthropic-claude-haiku-5.5.log 2>&1 < /dev/null &
setsid nohup .venv/bin/python -m src.v2.simulate --model openai/gpt-6-luna --stage confirm --parallel 3 > logs/confirm_openai-gpt-6-luna.log 2>&1 < /dev/null &
```

## Results and ledger

| Model | Complete blocks | Parse failures / base decisions | Null-monitor samples | Confirm ledger spend |
|---|---:|---:|---:|---:|
| deepseek-v4-flash | 100/100 | 0/24,000 (0.000%) | 2,250 | USD 5.438 |
| anthropic/claude-haiku-5.5 | 50/50 | 6/12,000 (0.050%) | 1,110 | USD 3.487 |
| openai/gpt-6-luna | 50/50 | 3/12,000 (0.025%) | 1,110 | USD 2.033 |

Cumulative ledger spend at completion, including earlier project activity, was **DeepSeek USD 6.381** and **OpenRouter USD 7.184**. Both remained below their stop thresholds of USD 7.000 and USD 7.400 respectively. No ProviderMismatch was found. The last 200 base decisions for each model contained zero parse failures.

Two Luna calls returned HTTP 503. Each was automatically retried and succeeded on the next same-tag attempt; no other confirm-stage HTTP errors or retries were recorded. This is 2 HTTP failures in 25,098 Luna confirm ledger entries (0.008%), with 0 for DeepSeek and Haiku. Retry count: DeepSeek 0, Haiku 0, Luna 2.

## Integrity check

Read-only JSONL integrity audit over the expected seed and condition paths returned:

```text
deepseek-v4-flash files 100 expected 100 missing 0 extra 0 run_ends 100 bad_blocks 0 duplicate_decision_keys 0 decisions 24000 parse_failures 0 null_monitor_samples 2250
anthropic-claude-haiku-5.5 files 50 expected 50 missing 0 extra 0 run_ends 50 bad_blocks 0 duplicate_decision_keys 0 decisions 12000 parse_failures 6 null_monitor_samples 1110
openai-gpt-6-luna files 50 expected 50 missing 0 extra 0 run_ends 50 bad_blocks 0 duplicate_decision_keys 0 decisions 12000 parse_failures 3 null_monitor_samples 1110
INTEGRITY PASS
```

Each expected confirm file had exactly one `run_end` with status `complete`; there were no duplicate `(tick, agent)` decision keys. Final block counts were 100 DeepSeek, 50 Haiku, and 50 Luna.

## Incidents

- The first nohup launch attempt exited before producing data or logs. A one-time diagnosis and detached relaunch were authorized. The detached processes were verified alive with in-progress blocks; the failed attempt left no files, locks, or API ledger entries.
- Two recoverable OpenRouter HTTP 503 responses occurred during Luna collection, as detailed above. All prescribed blocks completed, and no stop rule was triggered.
