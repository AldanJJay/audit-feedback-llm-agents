# Null re-ask noise floor and sign-flip comparison

**Development data only.** These measurements use dev seeds 100–101 and are intended only for a preregistration amendment. They are not confirmatory evidence.

## Design, spend, and file checks

The `noise` stage used six agents and 40 ticks per run, a reproducible 50% counterfactual mask, naive seeds 100 and 101, and label seed 100. For each sampled valid decision it sent null re-asks with the exact base messages and one `sign_flip` re-ask for each feature. OpenRouter requests were pinned to Anthropic for Haiku and OpenAI for Luna, with fallbacks disabled; every noise-tagged response reported the pinned provider.

Corrected dry-run projections based on measured pilot cost per call are USD 0.228 for DeepSeek, USD 0.277 for Haiku, and USD 0.160 for Luna. The initial projections were checked before live requests; these corrected projections reflect two null calls per sampled decision. Actual noise-tagged spend, including requests charged during the duplicate-run incident and the extra null calls below, was **USD 0.433** on DeepSeek and **USD 0.563** on OpenRouter (exact values in data/v2/ledger.jsonl). Both remained within the task limits of USD 0.50 and USD 0.60, respectively.

Each final model × condition × seed file has 240 decision rows, exactly one `run_end` marker with status `complete`, and no duplicate `(tick, agent)` decision keys. All nine intended files passed these checks. The corrupted DeepSeek artifacts described below were excluded from analysis.

### Run incident

A second DeepSeek stage process was launched while the original stage process was still active. The coordinator stopped both processes and quarantined the overlapping `naive_seed_101` and `label_seed_100` artifacts under `data/v2/deepseek-v4-flash/noise_quarantine/`. Those artifacts were not used. The intact DeepSeek `naive_seed_100` run was retained; one process then reran only `naive_seed_101` and `label_seed_100`. The final files passed the completion-marker and duplicate-decision checks above.

### Null-call implementation deviation

The first implementation placed null re-asks inside the existing per-feature loop, so completed runs made four null calls per sampled decision (two byte-identical re-asks for each feature) instead of two. This added **USD 0.095348** in DeepSeek charges and **USD 0.138745** in OpenRouter charges for the extra momentum-feature null calls, for **USD 0.234093** total; these ledger sums include any duplicate-process charges recorded under those tags. The prompts and request settings were identical, and the re-asks are exchangeable samples from the same provider/model, so the primary estimate pools all valid null calls and the fixed-news first-pair sensitivity below checks the conclusion using only two calls per decision. The code is corrected so future noise runs make exactly two null calls per sampled decision.

## Rates

The primary null flip rate pools all valid null re-asks and both feature probes; Wilson 95% intervals use `z = 1.96`. The decision-level null mean first averages the valid null indicators within each sampled decision, then averages those means. Sign-flip true-driver rows use the feature matching the current regime; non-driver rows use the other feature. Rates pool regimes, and naive pools both dev seeds. `Net true` and `net non-driver` subtract the pooled null rate. The final discrimination column is the difference between the two net rates (algebraically, true-driver minus non-driver).

| Model | Condition | Null flips / probes | Null rate [95% Wilson CI] | Decision-level null mean | Sign-flip true / n [95% Wilson CI] | Sign-flip non-driver / n [95% Wilson CI] | Net true | Net non-driver | Net discrimination | Decisions with any null pair disagree |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `deepseek-v4-flash` | naive | 39 / 912 | 0.043 [0.031, 0.058] | 0.043 | 0.570 (130/228) [0.505, 0.633] | 0.338 (77/228) [0.279, 0.401] | 0.527 | 0.295 | 0.232 | 9/228 (0.039) |
| `deepseek-v4-flash` | label | 4 / 456 | 0.009 [0.003, 0.022] | 0.009 | 0.728 (83/114) [0.640, 0.801] | 0.175 (20/114) [0.117, 0.256] | 0.719 | 0.167 | 0.553 | 0/114 (0.000) |
| `anthropic/claude-haiku-5.5` | naive | 37 / 910 | 0.041 [0.030, 0.056] | 0.041 | 0.478 (109/228) [0.414, 0.543] | 0.281 (64/228) [0.226, 0.342] | 0.437 | 0.240 | 0.197 | 20/228 (0.088) |
| `anthropic/claude-haiku-5.5` | label | 29 / 456 | 0.064 [0.045, 0.090] | 0.064 | 0.640 (73/114) [0.549, 0.723] | 0.184 (21/114) [0.124, 0.265] | 0.577 | 0.121 | 0.456 | 9/114 (0.079) |
| `openai/gpt-6-luna` | naive | 48 / 912 | 0.053 [0.040, 0.069] | 0.053 | 0.500 (114/228) [0.436, 0.564] | 0.294 (67/228) [0.239, 0.356] | 0.447 | 0.241 | 0.206 | 18/228 (0.079) |
| `openai/gpt-6-luna` | label | 15 / 456 | 0.033 [0.020, 0.054] | 0.033 | 0.640 (73/114) [0.549, 0.723] | 0.219 (25/114) [0.153, 0.304] | 0.607 | 0.186 | 0.421 | 8/114 (0.070) |

The primary null disagreement share counts a sampled decision once if any two valid null re-asks among its four calls disagree; its denominator is sampled decisions with a valid base action. Haiku had two invalid/missing null outcomes in its naive blocks, hence 910 rather than 912 usable null probes.

### Two-call sensitivity check

This sensitivity uses only `null_1` and `null_2` for the fixed `news` feature, giving exactly two null results per decision. It reports the same null-floor subtraction and Wilson interval for the null rate.

| Model | Condition | First-pair null flips / probes | First-pair null rate [95% Wilson CI] | Net true | Net non-driver | Net discrimination | Decisions where this pair disagrees |
|---|---|---:|---:|---:|---:|---:|---:|
| `deepseek-v4-flash` | naive | 20/456 | 0.044 [0.029, 0.067] | 0.526 | 0.294 | 0.232 | 4/228 (0.018) |
| `deepseek-v4-flash` | label | 2/228 | 0.009 [0.002, 0.031] | 0.719 | 0.167 | 0.553 | 0/114 (0.000) |
| `anthropic/claude-haiku-5.5` | naive | 15/456 | 0.033 [0.020, 0.054] | 0.445 | 0.248 | 0.197 | 11/228 (0.048) |
| `anthropic/claude-haiku-5.5` | label | 15/228 | 0.066 [0.040, 0.106] | 0.575 | 0.118 | 0.456 | 7/114 (0.061) |
| `openai/gpt-6-luna` | naive | 22/456 | 0.048 [0.032, 0.072] | 0.452 | 0.246 | 0.206 | 8/228 (0.035) |
| `openai/gpt-6-luna` | label | 6/228 | 0.026 [0.012, 0.056] | 0.614 | 0.193 | 0.421 | 4/114 (0.035) |

The first-pair null rates are also below their corresponding non-driver rates: all six non-driver Wilson intervals remain separated from the first-pair null intervals. The net discrimination and the T7 eligibility conclusion are unchanged.

## Answers to the calibration questions

**(a) Is the sign-flip non-driver rate distinguishable from the null rate?** Yes, by the requested Wilson-interval comparison in every model × condition under the primary pooled estimate: the non-driver interval does not overlap the corresponding null interval. For example, naive DeepSeek has non-driver `[0.279, 0.401]` versus null `[0.031, 0.058]`; label Haiku has non-driver `[0.124, 0.265]` versus null `[0.045, 0.090]`. All six first-pair sensitivity comparisons are also separated.

**(b) Does `sign_flip` still meet the T7 selection rule when rates are net of null?** Yes, on the naive pooled development runs. Net true-driver rates are DeepSeek 0.527, Haiku 0.437, and Luna 0.447, all within the T7 eligibility interval `[0.10, 0.90]`. Net discriminations are 0.232, 0.197, and 0.206; the minimum across models is 0.197, above the T7 threshold of 0.15. Thus the dev-seed result still selects `sign_flip` under the same rule after subtracting the null floor. This remains calibration evidence only and requires a dated preregistration amendment before confirmatory data collection.
