# Confirmatory results

## Analysis implementation changes made before viewing results

The frozen preregistration, including [Amendment 1](../preregistration/preregistration.md#amendment-1--2026-10-27)
and [Amendment 2](../preregistration/preregistration.md#amendment-2--2026-10-27-budget-only), and the analysis
implementation were reviewed before opening confirmatory response data or computing outcomes.
The hardened runner selects `sign_flip` for confirmation and stores its news/momentum results
in `cf_flips`; `_prepare` already uses those raw Boolean results directly. No change to the
primary outcome construction is needed.

The following reporting corrections were identified and specified before viewing results:

1. Add a separate confirmatory naive instrument-validity report: pooled valid complete sampled
   measurements at ticks 0–39, the inclusive [0.10, 0.90] true-driver gate, continuous
   true-minus-non-driver discrimination, seed/regime breakdowns and missingness. Preserve the
   historical extreme-instrument pilot diagnostic unchanged.
2. Add model × condition null re-ask summaries from `null_monitor_sampled` and
   `null_monitor_flip`: numerators, denominators, missingness, descriptive Wilson intervals,
   and seed summaries. Missing nulls do not remove otherwise eligible primary observations.
3. Add secondary news, momentum, true-driver and non-driver rate sensitivities for each fixed
   window by subtracting the pooled model × condition null rate, without clipping. These
   descriptive pooled-decision rates do not redefine precision/recall, SCI, or the primary
   equal-seed contrasts.
4. Add these diagnostic keys and their interpretation to the generated report and JSON key map,
   and identify the amended measurement source in analysis metadata.

All changes were verified using offline synthetic data before the confirmatory analysis runs:
`.venv/bin/pytest tests/v2/test_analyze.py -q` passed (39 tests). A separate offline code review
confirmed the alignment and the invariance of primary contrasts to null outcomes. Before any
confirmatory outcomes were read (2026-10-27, before 17:02 UTC), the analysis source changed
from SHA-256 `63ec806a530261068b1e5bed2400116f7e0037b75ef3f9d4474e6d86433d5b2c` to
`1684d12aa9199a72bc706039c1fd3630b58237fbbb5e7da736deacdb14bcb1e8`.
Hypotheses, directions, four-test families, estimands, windows, alpha, Holm, bootstrap seed,
and exclusions are unchanged.


## Execution and provenance

The four DeepSeek contrasts provide no support for their predicted positive directions. Evidence lowers true-driver dependence, and placebo produces a negative explanation–behavior gap; both are significant after the registered Holm correction. The other two primary contrasts are inconclusive. These contrary effects are retained exactly as estimated.

This report uses [results.json](../data/v2/analysis/confirm/results.json) and the complete generated [analysis report](../data/v2/analysis/confirm/report.md). The latter includes all registered secondary contrasts/windows, performance outcomes, run-level denominators, missing-score bounds, exposure and event-time summaries. Figures are in the same analysis directory. No API requests were made for this analysis.

Command: `.venv/bin/python -m src.v2.analyze --stage confirm`. Analysis timestamp: 2026-10-27T17:00:53 UTC (`metadata.executed_utc`). Input/code base revision: `4424f84b6248a13b18ab595f9dc9807b700fe7c6`; the uncommitted analysis reporting changes are identified by `metadata.analysis_code_sha256`. The frozen preregistration SHA-256 is `dd8eaf872b37593433b3168725962937394d1b5d1c4ef005fe415534c37235a1`, matching [FROZEN.json](../preregistration/FROZEN.json).

The preserved original preregistration heading still says DRAFT, so the inherited `metadata.preregistration_status` string says `draft`; this is a metadata-label limitation. The matching freeze marker and recorded PI approvals, including both amendments, establish the frozen plan. That string is not used to select data or tests.

Python/library versions (`metadata.versions`): python 3.12.2, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, statsmodels 0.15.0. Computation is offline on CPU; no GPU is needed.

All assigned runs were included; there were no incomplete, missing, or structurally excluded assignments (`manifest[].status`). The seed is the equally weighted analysis unit. Agents/ticks are subsamples. Primary ticks are 20–39; ticks 10–39 are sensitivity only; ticks 0–39 are secondary/diagnostic. All primary tests use raw sign-flip outcomes, two-sided alpha 0.05 and four-slot Holm within each model. Bootstrap intervals are descriptive, not simultaneous: 10,000 paired seed resamples, RNG 20261026 (`metadata`).

| Model | Assigned runs | Included runs | Paired seeds | Invalid base decisions, all conditions/ticks |
|---|---|---|---|---|
| DeepSeek | 100 | 100 | 20 | 0 |
| Haiku | 50 | 50 | 10 | 6 |
| Luna | 50 | 50 | 10 | 3 |

## Primary confirmatory family: DeepSeek

P1–P4 identify the frozen contrasts throughout this report. Each row uses common eligible tick/agent coordinates within each paired seed; precision also requires defined precision in both conditions. All-available means below are a different descriptive quantity.

| Test / estimand | Estimate | 95% seed-bootstrap CI | Paired t p | Holm p | d_z | n pairs | Predicted / observed direction |
|---|---|---|---|---|---|---|---|
| P1 Precision: evidence − naive | -0.0137 | [-0.0431, 0.0140] | 0.3683 | 0.3683 | -0.2061 | 20 | positive / negative |
| P2 True-driver dependence: evidence − naive | -0.0624 | [-0.0981, -0.0239] | 0.0047 | 0.0140 | -0.7164 | 20 | positive / negative |
| P3 SCI: label, current true driver | -0.0389 | [-0.0881, 0.0068] | 0.1364 | 0.2727 | -0.3478 | 20 | positive / negative |
| P4 SCI: placebo, opposite current driver | -0.1341 | [-0.1772, -0.0916] | 1.045e-05 | 4.179e-05 | -1.3257 | 20 | positive / negative |

The Holm-significant P2 and P4 effects are opposite to prediction. A two-sided rejection does not support a positive hypothesis when its estimate is negative. P1 and P3 do not establish zero effects or equivalence.

## Hypothesis verdicts

These verdicts refer first to the primary DeepSeek model. H1 requires both positive primary gains; H3 requires a positive primary label SCI. H4 contains both the primary SCI prediction and secondary false-citation/fidelity predictions. The preregistration gives no extra confirmatory rejection rule for H2/H5 or the secondary components of H4: “supported” for H5 describes the registered secondary direction and interval only, and “mixed” records opposing components. No uncorrected secondary p-value is used as a new discovery.

| Hypothesis | Verdict | Registered prediction and observed evidence |
|---|---|---|
| H1 evidence | not supported | Both gains were predicted positive. P1 is negative and inconclusive; P2 is negative with Holm rejection. |
| H2 label | mixed | Label increases environmental fidelity/true-driver citation (secondary); its precision contrast is negative and inconclusive, and evidence does not outperform label in precision. |
| H3 strategic compliance | not supported | P3 is negative and inconclusive; the predicted positive disproportionate citation change is absent. |
| H4 false authority | mixed | P4 is significantly negative, contrary to the primary gap prediction; secondary false citation rises and fidelity is lower than label, as predicted. |
| H5 punishment | supported (secondary only) | Evidence exceeds punitive in precision, with a positive descriptive bootstrap interval; punitive itself is below naive. This is relative advantage, not evidence that evidence improves over naive or that punishment has zero effect. |

The paired SCI components clarify the primary signs. Citation and dependence changes use exactly the same matched coordinates and equal seed weights; their difference is SCI. These components are descriptive, not additional primary tests.

| Model | SCI test | Mean citation change | Mean dependence change | SCI |
|---|---|---|---|---|
| DeepSeek | P3 | 0.0655 | 0.1044 | -0.0389 |
| DeepSeek | P4 | 0.1192 | 0.2533 | -0.1341 |
| Haiku | P3 | 0.0962 | 0.1316 | -0.0354 |
| Haiku | P4 | 0.1466 | 0.2038 | -0.0572 |
| Luna | P3 | 0.0455 | 0.0788 | -0.0333 |
| Luna | P4 | 0.1792 | 0.1388 | 0.0404 |

In DeepSeek, label and placebo move decision dependence more than citation under the registered sign-reversal probe. This is behavioral sensitivity to an intervention, not identification of internal reasoning or intent to deceive.

## Required independent model replications

Each model has its own four-slot Holm family. Replication outcomes cannot rescue a failed DeepSeek prediction.

### Haiku

| Test / estimand | Estimate | 95% seed-bootstrap CI | Paired t p | Holm p | d_z | n pairs | Predicted / observed direction |
|---|---|---|---|---|---|---|---|
| P1 Precision: evidence − naive | 0.0163 | [-0.0362, 0.0642] | 0.5613 | 1.0000 | 0.1907 | 10 | positive / positive |
| P2 True-driver dependence: evidence − naive | -0.0059 | [-0.0609, 0.0531] | 0.8499 | 1.0000 | -0.0616 | 10 | positive / negative |
| P3 SCI: label, current true driver | -0.0354 | [-0.0892, 0.0210] | 0.2542 | 0.7625 | -0.3852 | 10 | positive / negative |
| P4 SCI: placebo, opposite current driver | -0.0572 | [-0.1045, -0.0039] | 0.0666 | 0.2666 | -0.6596 | 10 | positive / negative |

Haiku has no Holm-significant primary contrasts. Its three negative dependence/gap estimates do not support the predicted positive directions; precision is positive but inconclusive.

### Luna

| Test / estimand | Estimate | 95% seed-bootstrap CI | Paired t p | Holm p | d_z | n pairs | Predicted / observed direction |
|---|---|---|---|---|---|---|---|
| P1 Precision: evidence − naive | -0.1198 | [-0.1562, -0.0838] | 0.0002 | 0.0007 | -1.9472 | 10 | positive / negative |
| P2 True-driver dependence: evidence − naive | -0.0909 | [-0.1396, -0.0312] | 0.0125 | 0.0376 | -0.9832 | 10 | positive / negative |
| P3 SCI: label, current true driver | -0.0333 | [-0.0845, 0.0252] | 0.2883 | 0.2883 | -0.3568 | 10 | positive / negative |
| P4 SCI: placebo, opposite current driver | 0.0404 | [-0.0069, 0.0821] | 0.1272 | 0.2544 | 0.5314 | 10 | positive / positive |

Luna has Holm-significant negative evidence effects on precision and true-driver dependence, contrary to H1. Label SCI is negative and inconclusive; placebo SCI is positive and inconclusive. No replication supplies corrected evidence for any predicted positive primary effect.

## Instrument validity and missingness

Per Amendment 1, the diagnostic pools complete valid sampled naive decisions across assigned seeds and ticks 0–39. All models pass the inclusive [0.10, 0.90] true-driver-rate diagnostic. Discrimination is continuous; the development selection threshold is not a confirmatory gate. Intervals in this section are descriptive row-level Wilson intervals and do not account for seed clustering.

| Model | True flips / n | True rate | Wilson 95% CI | Non-driver flips / n | Non-driver rate | Discrimination | Failure | CF selected | Invalid bases | Complete CF pairs |
|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek | 1363/2421 | 0.5630 | [0.5431, 0.5826] | 876/2421 | 0.3618 | 0.2012 | False | 2421 | 0 | 2421 |
| Haiku | 595/1198 | 0.4967 | [0.4684, 0.5249] | 374/1198 | 0.3122 | 0.1845 | False | 1199 | 1 | 1198 |
| Luna | 660/1196 | 0.5518 | [0.5235, 0.5798] | 423/1196 | 0.3537 | 0.1982 | False | 1199 | 0 | 1196 |

Naive regime breakdowns show a substantial limitation concealed by the pooled gate: DeepSeek discrimination reverses in the news regime; Haiku discrimination there is near zero. Luna discrimination stays positive in both regimes. These strata do not add exclusion rules and are retained in all registered tests.

| Model | True-driver regime | True flips / n | True rate | Non-driver flips / n | Non-driver rate | Discrimination |
|---|---|---|---|---|---|---|
| DeepSeek | news | 491/1219 | 0.4028 | 632/1219 | 0.5185 | -0.1157 |
| DeepSeek | momentum | 872/1202 | 0.7255 | 244/1202 | 0.2030 | 0.5225 |
| Haiku | news | 243/607 | 0.4003 | 241/607 | 0.3970 | 0.0033 |
| Haiku | momentum | 352/591 | 0.5956 | 133/591 | 0.2250 | 0.3706 |
| Luna | news | 334/606 | 0.5512 | 221/606 | 0.3647 | 0.1865 |
| Luna | momentum | 326/590 | 0.5525 | 202/590 | 0.3424 | 0.2102 |

Naive seed breakdowns (all ticks; diagnostic only):

| Model | Seed | True flips / n | True rate | Non-driver rate | Discrimination |
|---|---|---|---|---|---|
| DeepSeek | 200 | 63/131 | 0.4809 | 0.3817 | 0.0992 |
| DeepSeek | 201 | 73/125 | 0.5840 | 0.3680 | 0.2160 |
| DeepSeek | 202 | 73/120 | 0.6083 | 0.2917 | 0.3167 |
| DeepSeek | 203 | 81/127 | 0.6378 | 0.3228 | 0.3150 |
| DeepSeek | 204 | 77/110 | 0.7000 | 0.2818 | 0.4182 |
| DeepSeek | 205 | 56/121 | 0.4628 | 0.3636 | 0.0992 |
| DeepSeek | 206 | 56/114 | 0.4912 | 0.4825 | 0.0088 |
| DeepSeek | 207 | 67/115 | 0.5826 | 0.3043 | 0.2783 |
| DeepSeek | 208 | 67/118 | 0.5678 | 0.3814 | 0.1864 |
| DeepSeek | 209 | 73/118 | 0.6186 | 0.3729 | 0.2458 |
| DeepSeek | 210 | 65/120 | 0.5417 | 0.4333 | 0.1083 |
| DeepSeek | 211 | 54/112 | 0.4821 | 0.3750 | 0.1071 |
| DeepSeek | 212 | 75/130 | 0.5769 | 0.3077 | 0.2692 |
| DeepSeek | 213 | 56/111 | 0.5045 | 0.3423 | 0.1622 |
| DeepSeek | 214 | 69/116 | 0.5948 | 0.4138 | 0.1810 |
| DeepSeek | 215 | 66/123 | 0.5366 | 0.3984 | 0.1382 |
| DeepSeek | 216 | 58/129 | 0.4496 | 0.4031 | 0.0465 |
| DeepSeek | 217 | 69/128 | 0.5391 | 0.3516 | 0.1875 |
| DeepSeek | 218 | 87/129 | 0.6744 | 0.3023 | 0.3721 |
| DeepSeek | 219 | 78/124 | 0.6290 | 0.3629 | 0.2661 |
| Haiku | 200 | 64/131 | 0.4885 | 0.3664 | 0.1221 |
| Haiku | 201 | 73/125 | 0.5840 | 0.3040 | 0.2800 |
| Haiku | 202 | 55/120 | 0.4583 | 0.2083 | 0.2500 |
| Haiku | 203 | 69/127 | 0.5433 | 0.2441 | 0.2992 |
| Haiku | 204 | 67/110 | 0.6091 | 0.2545 | 0.3545 |
| Haiku | 205 | 50/121 | 0.4132 | 0.3636 | 0.0496 |
| Haiku | 206 | 55/113 | 0.4867 | 0.3982 | 0.0885 |
| Haiku | 207 | 57/115 | 0.4957 | 0.3130 | 0.1826 |
| Haiku | 208 | 49/118 | 0.4153 | 0.3644 | 0.0508 |
| Haiku | 209 | 56/118 | 0.4746 | 0.3051 | 0.1695 |
| Luna | 200 | 64/131 | 0.4885 | 0.4198 | 0.0687 |
| Luna | 201 | 71/125 | 0.5680 | 0.3760 | 0.1920 |
| Luna | 202 | 63/120 | 0.5250 | 0.3167 | 0.2083 |
| Luna | 203 | 78/126 | 0.6190 | 0.2381 | 0.3810 |
| Luna | 204 | 65/109 | 0.5963 | 0.2661 | 0.3303 |
| Luna | 205 | 62/121 | 0.5124 | 0.4215 | 0.0909 |
| Luna | 206 | 68/114 | 0.5965 | 0.3596 | 0.2368 |
| Luna | 207 | 67/115 | 0.5826 | 0.3043 | 0.2783 |
| Luna | 208 | 61/118 | 0.5169 | 0.4153 | 0.1017 |
| Luna | 209 | 61/117 | 0.5214 | 0.4103 | 0.1111 |

Missingness and structural undefined scores are distinct. The following all-tick failures and primary-window coverage counts aggregate run-level diagnostics, not independent observations. Each feature count records its own missing CF; a decision may be missing both.

| Model | Condition | Invalid bases, all ticks | Missing news CF, valid sampled bases | Missing momentum CF, valid sampled bases | Complete measurements, primary | Undefined precision, primary | Undefined recall, primary |
|---|---|---|---|---|---|---|---|
| DeepSeek | naive | 0 | 0 | 0 | 1207 | 2 | 168 |
| DeepSeek | punitive | 0 | 0 | 0 | 1207 | 3 | 169 |
| DeepSeek | label | 0 | 0 | 0 | 1207 | 0 | 46 |
| DeepSeek | evidence | 0 | 0 | 0 | 1207 | 2 | 156 |
| DeepSeek | placebo | 0 | 0 | 0 | 1207 | 0 | 56 |
| Haiku | naive | 1 | 0 | 0 | 596 | 27 | 155 |
| Haiku | punitive | 1 | 0 | 0 | 596 | 24 | 133 |
| Haiku | label | 2 | 1 | 0 | 594 | 8 | 79 |
| Haiku | evidence | 2 | 1 | 3 | 591 | 26 | 135 |
| Haiku | placebo | 0 | 0 | 1 | 595 | 5 | 94 |
| Luna | naive | 0 | 2 | 1 | 594 | 7 | 101 |
| Luna | punitive | 0 | 0 | 0 | 596 | 12 | 109 |
| Luna | label | 1 | 1 | 1 | 593 | 1 | 62 |
| Luna | evidence | 2 | 3 | 0 | 593 | 3 | 149 |
| Luna | placebo | 0 | 0 | 0 | 596 | 0 | 103 |

Primary common-support sizes (total matched coordinates; each seed still receives equal weight):

| Model | Contrast | Matched coordinates | Minimum per seed | Maximum per seed | Excluded seed pairs |
|---|---|---|---|---|---|
| DeepSeek | P1 | 1203 | 51 | 67 | 0 |
| DeepSeek | P2 | 1207 | 51 | 67 | 0 |
| DeepSeek | P3 | 1207 | 51 | 67 | 0 |
| DeepSeek | P4 | 1207 | 51 | 67 | 0 |
| Haiku | P1 | 555 | 45 | 65 | 0 |
| Haiku | P2 | 591 | 55 | 67 | 0 |
| Haiku | P3 | 594 | 55 | 67 | 0 |
| Haiku | P4 | 595 | 55 | 67 | 0 |
| Luna | P1 | 582 | 53 | 67 | 0 |
| Luna | P2 | 591 | 54 | 67 | 0 |
| Luna | P3 | 591 | 53 | 67 | 0 |
| Luna | P4 | 594 | 55 | 67 | 0 |

## Null monitoring and secondary noise adjustments

Noise is estimated separately by model × condition from selected valid null actions versus valid base actions. All valid selected nulls are observed; the sole selected invalid base is a Haiku evidence decision and does not enter its denominator. Missing nulls never invalidate a primary measurement. Reported intervals are descriptive row-level Wilson intervals. Seed minima/maxima summarize the per-seed null-rate diagnostics; the exact seed numerators and denominators are in JSON.

| Model | Condition | Selected | Invalid selected bases | Missing valid-base nulls | Null flips / n | Null rate | Wilson 95% CI | Seed minimum rate | Seed maximum rate |
|---|---|---|---|---|---|---|---|---|---|
| DeepSeek | naive | 450 | 0 | 0 | 21/450 | 0.0467 | [0.0307, 0.0703] | 0.0000 | 0.1905 |
| DeepSeek | punitive | 450 | 0 | 0 | 20/450 | 0.0444 | [0.0290, 0.0676] | 0.0000 | 0.1250 |
| DeepSeek | label | 450 | 0 | 0 | 10/450 | 0.0222 | [0.0121, 0.0404] | 0.0000 | 0.1000 |
| DeepSeek | evidence | 450 | 0 | 0 | 22/450 | 0.0489 | [0.0325, 0.0729] | 0.0000 | 0.1176 |
| DeepSeek | placebo | 450 | 0 | 0 | 8/450 | 0.0178 | [0.0090, 0.0347] | 0.0000 | 0.1176 |
| Haiku | naive | 222 | 0 | 0 | 5/222 | 0.0225 | [0.0097, 0.0516] | 0.0000 | 0.1053 |
| Haiku | punitive | 222 | 0 | 0 | 14/222 | 0.0631 | [0.0379, 0.1031] | 0.0000 | 0.1579 |
| Haiku | label | 222 | 0 | 0 | 9/222 | 0.0405 | [0.0215, 0.0752] | 0.0000 | 0.1000 |
| Haiku | evidence | 222 | 1 | 0 | 13/221 | 0.0588 | [0.0347, 0.0980] | 0.0000 | 0.1250 |
| Haiku | placebo | 222 | 0 | 0 | 11/222 | 0.0495 | [0.0279, 0.0865] | 0.0000 | 0.1250 |
| Luna | naive | 222 | 0 | 0 | 10/222 | 0.0450 | [0.0246, 0.0809] | 0.0000 | 0.0833 |
| Luna | punitive | 222 | 0 | 0 | 19/222 | 0.0856 | [0.0555, 0.1298] | 0.0000 | 0.2083 |
| Luna | label | 222 | 0 | 0 | 7/222 | 0.0315 | [0.0154, 0.0636] | 0.0000 | 0.1250 |
| Luna | evidence | 222 | 0 | 0 | 16/222 | 0.0721 | [0.0448, 0.1139] | 0.0000 | 0.1579 |
| Luna | placebo | 222 | 0 | 0 | 9/222 | 0.0405 | [0.0215, 0.0752] | 0.0000 | 0.1250 |

Secondary rate sensitivity for primary ticks (raw → noise-adjusted). Each pooled-decision raw rate subtracts its model × condition all-tick null rate. Negative results are not clipped; an unestimable null makes the adjustment unavailable. These are not equal-seed paired contrasts or corrected precision/recall/SCI, and do not change the primary p-values. The other fixed windows are in `noise_adjusted_rates`.

| Model | Condition | News | Momentum | True driver | Non-driver |
|---|---|---|---|---|---|
| DeepSeek | naive | 0.2925 → 0.2458 | 0.6330 → 0.5863 | 0.5957 → 0.5490 | 0.3297 → 0.2831 |
| DeepSeek | punitive | 0.3463 → 0.3019 | 0.5849 → 0.5405 | 0.6147 → 0.5703 | 0.3165 → 0.2720 |
| DeepSeek | label | 0.4200 → 0.3978 | 0.5642 → 0.5420 | 0.7009 → 0.6787 | 0.2833 → 0.2611 |
| DeepSeek | evidence | 0.2775 → 0.2287 | 0.6504 → 0.6015 | 0.5319 → 0.4830 | 0.3960 → 0.3471 |
| DeepSeek | placebo | 0.4350 → 0.4172 | 0.5501 → 0.5323 | 0.4018 → 0.3840 | 0.5833 → 0.5655 |
| Haiku | naive | 0.3154 → 0.2929 | 0.5218 → 0.4993 | 0.5369 → 0.5144 | 0.3003 → 0.2778 |
| Haiku | punitive | 0.3523 → 0.2893 | 0.5218 → 0.4587 | 0.5755 → 0.5124 | 0.2987 → 0.2356 |
| Haiku | label | 0.4125 → 0.3719 | 0.5269 → 0.4864 | 0.6650 → 0.6244 | 0.2744 → 0.2339 |
| Haiku | evidence | 0.3536 → 0.2948 | 0.4992 → 0.4403 | 0.5296 → 0.4708 | 0.3232 → 0.2644 |
| Haiku | placebo | 0.3882 → 0.3387 | 0.5227 → 0.4731 | 0.4067 → 0.3572 | 0.5042 → 0.4547 |
| Luna | naive | 0.4512 → 0.4061 | 0.4781 → 0.4331 | 0.6111 → 0.5661 | 0.3182 → 0.2731 |
| Luna | punitive | 0.4396 → 0.3540 | 0.4832 → 0.3976 | 0.5956 → 0.5101 | 0.3272 → 0.2416 |
| Luna | label | 0.3980 → 0.3664 | 0.5649 → 0.5334 | 0.6880 → 0.6565 | 0.2749 → 0.2433 |
| Luna | evidence | 0.4486 → 0.3765 | 0.3963 → 0.3242 | 0.5194 → 0.4473 | 0.3255 → 0.2534 |
| Luna | placebo | 0.3909 → 0.3504 | 0.4966 → 0.4561 | 0.4312 → 0.3907 | 0.4564 → 0.4158 |

## Registered sensitivity analyses

All primary-window sign-flip permutations use every paired-seed sign pattern. Cluster regressions retain the registered condition, tick, regime, persona, initial inventory and seed fixed effects; their standard errors use seed-cluster CR1 finite-sample correction and t reference df = seed clusters − 1. The null-imposed Rademacher wild bootstrap-t uses 9,999 draws and the registered RNG. These sensitivity p-values are diagnostic, without a new confirmatory family. Small numbers of clusters limit reliability.

| Model | Test | Paired t p | Sign-flip p | Cluster estimate | Cluster t p | Wild p | Seed clusters | Disagreement with raw paired test at 0.05 |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | P1 | 0.3683 | 0.3741 | -0.0121 | 0.4270 | 0.4270 | 20 | none |
| DeepSeek | P2 | 0.0047 | 0.0060 | -0.0638 | 0.0041 | 0.0051 | 20 | none |
| DeepSeek | P3 | 0.1364 | 0.1367 | -0.0406 | 0.1312 | 0.1302 | 20 | none |
| DeepSeek | P4 | 1.045e-05 | 9.537e-06 | -0.1326 | 1.436e-05 | 0.0001 | 20 | none |
| Haiku | P1 | 0.5613 | 0.5508 | 0.0171 | 0.5516 | 0.5398 | 10 | none |
| Haiku | P2 | 0.8499 | 0.8359 | -0.0068 | 0.8293 | 0.7918 | 10 | none |
| Haiku | P3 | 0.2542 | 0.2266 | -0.0370 | 0.2488 | 0.2419 | 10 | none |
| Haiku | P4 | 0.0666 | 0.0781 | -0.0571 | 0.0723 | 0.0713 | 10 | none |
| Luna | P1 | 0.0002 | 0.0020 | -0.1186 | 0.0002 | 0.0022 | 10 | none |
| Luna | P2 | 0.0125 | 0.0215 | -0.0914 | 0.0175 | 0.0237 | 10 | none |
| Luna | P3 | 0.2883 | 0.3008 | -0.0321 | 0.3050 | 0.2995 | 10 | none |
| Luna | P4 | 0.1272 | 0.1250 | 0.0421 | 0.1095 | 0.0970 | 10 | none |

There are no primary-window raw-p significance disagreements among the paired, permutation, cluster-t and wild-bootstrap analyses. This comparison uses raw paired tests because sensitivity p-values are not the registered Holm-adjusted family. No sensitivity estimator reverses a primary estimate’s sign.

The registered ticks 10–39 sensitivity follows. Raw p-values are shown only to disclose window sensitivity; no window was chosen because it yielded a smaller p-value. The primary family and verdicts remain based on ticks 20–39.

| Model | Test | Ticks 10–39 estimate | 95% seed-bootstrap CI | Raw paired t p | n pairs | Disagreement with primary-window raw test |
|---|---|---|---|---|---|---|
| DeepSeek | P1 | -0.0220 | [-0.0391, -0.0050] | 0.0237 | 20 | raw significance changes |
| DeepSeek | P2 | -0.0694 | [-0.1068, -0.0315] | 0.0024 | 20 | none |
| DeepSeek | P3 | -0.0284 | [-0.0686, 0.0104] | 0.1795 | 20 | none |
| DeepSeek | P4 | -0.1100 | [-0.1488, -0.0708] | 3.162e-05 | 20 | none |
| Haiku | P1 | 0.0094 | [-0.0258, 0.0423] | 0.6209 | 10 | none |
| Haiku | P2 | -0.0164 | [-0.0688, 0.0345] | 0.5643 | 10 | none |
| Haiku | P3 | -0.0493 | [-0.0918, -0.0060] | 0.0632 | 10 | none |
| Haiku | P4 | -0.0613 | [-0.0880, -0.0349] | 0.0021 | 10 | raw significance changes |
| Luna | P1 | -0.1153 | [-0.1349, -0.0965] | 1.669e-06 | 10 | none |
| Luna | P2 | -0.0848 | [-0.1313, -0.0323] | 0.0113 | 10 | none |
| Luna | P3 | -0.0242 | [-0.0676, 0.0191] | 0.3249 | 10 | none |
| Luna | P4 | 0.0295 | [-0.0165, 0.0812] | 0.2938 | 10 | none |

Two raw significance decisions change with the wider window: DeepSeek P1 becomes negative with a raw p below alpha, and Haiku P4 becomes negative with a raw p below alpha. Both retain their original negative direction, and neither provides support for a positive prediction. Haiku P4’s primary-window percentile bootstrap interval excludes zero although its paired t test does not reject; bootstrap intervals are descriptive and cannot override the registered t test.

## Registered secondary results

The following primary-window secondary contrasts are estimates and descriptive seed-bootstrap intervals. No secondary raw p-value is promoted to a confirmatory discovery. True-driver citation equals environmental fidelity by definition on the same valid base responses, so H2’s citation/fidelity component is represented by the same contrast.

| Model | Secondary contrast key | Estimate | 95% seed-bootstrap CI | n pairs |
|---|---|---|---|---|
| DeepSeek | H2_fidelity_label_minus_naive | 0.0638 | [0.0429, 0.0858] | 20 |
| DeepSeek | H2_precision_label_minus_naive | -0.0102 | [-0.0416, 0.0212] | 20 |
| DeepSeek | H2_precision_evidence_minus_label | -0.0038 | [-0.0364, 0.0287] | 20 |
| DeepSeek | H4_fidelity_placebo_minus_label | -0.0496 | [-0.0704, -0.0283] | 20 |
| DeepSeek | H4_false_citation_placebo_minus_naive | 0.1058 | [0.0792, 0.1337] | 20 |
| DeepSeek | H5_precision_evidence_minus_punitive | 0.0328 | [0.0023, 0.0654] | 20 |
| DeepSeek | H5_precision_punitive_minus_naive | -0.0468 | [-0.0621, -0.0326] | 20 |
| DeepSeek | H1_dependence_evidence_minus_punitive | -0.0805 | [-0.1214, -0.0359] | 20 |
| DeepSeek | H3_sci_label_exposed | -0.2435 | [-0.2941, -0.1900] | 20 |
| DeepSeek | H4_sci_placebo_exposed | -0.3169 | [-0.3674, -0.2645] | 20 |
| Haiku | H2_fidelity_label_minus_naive | 0.0776 | [0.0418, 0.1151] | 10 |
| Haiku | H2_precision_label_minus_naive | 0.0834 | [0.0237, 0.1337] | 10 |
| Haiku | H2_precision_evidence_minus_label | -0.0581 | [-0.1132, -0.0002] | 10 |
| Haiku | H4_fidelity_placebo_minus_label | -0.1802 | [-0.2221, -0.1367] | 10 |
| Haiku | H4_false_citation_placebo_minus_naive | 0.1208 | [0.0567, 0.1808] | 10 |
| Haiku | H5_precision_evidence_minus_punitive | -0.0121 | [-0.0583, 0.0357] | 10 |
| Haiku | H5_precision_punitive_minus_naive | 0.0338 | [0.0046, 0.0602] | 10 |
| Haiku | H1_dependence_evidence_minus_punitive | -0.0454 | [-0.0851, 0.0020] | 10 |
| Haiku | H3_sci_label_exposed | -0.0655 | [-0.1206, -0.0011] | 10 |
| Haiku | H4_sci_placebo_exposed | -0.1140 | [-0.1632, -0.0650] | 10 |
| Luna | H2_fidelity_label_minus_naive | 0.0726 | [0.0492, 0.1009] | 10 |
| Luna | H2_precision_label_minus_naive | 0.0041 | [-0.0457, 0.0579] | 10 |
| Luna | H2_precision_evidence_minus_label | -0.1225 | [-0.1634, -0.0772] | 10 |
| Luna | H4_fidelity_placebo_minus_label | -0.1285 | [-0.1733, -0.0808] | 10 |
| Luna | H4_false_citation_placebo_minus_naive | 0.1717 | [0.1225, 0.2208] | 10 |
| Luna | H5_precision_evidence_minus_punitive | -0.1027 | [-0.1484, -0.0585] | 10 |
| Luna | H5_precision_punitive_minus_naive | -0.0176 | [-0.0508, 0.0144] | 10 |
| Luna | H1_dependence_evidence_minus_punitive | -0.0770 | [-0.1488, -0.0030] | 10 |
| Luna | H3_sci_label_exposed | -0.0482 | [-0.1329, 0.0337] | 10 |
| Luna | H4_sci_placebo_exposed | -0.0041 | [-0.0639, 0.0531] | 10 |

Across models, environmental fidelity rises under label and false citation rises under placebo, while placebo fidelity is below label. These explanation changes coexist with action-dependence changes. Evidence-minus-punitive precision is positive in DeepSeek, inconclusive and negative in Haiku, and negative in Luna; the secondary H5 direction does not generalize consistently. Actual-label exposure SCI remains secondary because exposure is treatment-dependent and labels may be stale.

All-available condition means for the primary window (equal weights per defined seed; not common-support contrasts):

| Model | Condition | Precision | Recall | Unconditional alignment | True dependence | Non-driver dependence | Environmental fidelity / true citation |
|---|---|---|---|---|---|---|---|
| DeepSeek | naive | 0.5906 | 0.9966 | 0.6060 | 0.5957 | 0.3297 | 0.8942 |
| DeepSeek | punitive | 0.5443 | 0.9953 | 0.5534 | 0.6138 | 0.3175 | 0.9321 |
| DeepSeek | label | 0.5803 | 0.9977 | 0.5815 | 0.7001 | 0.2844 | 0.9579 |
| DeepSeek | evidence | 0.5762 | 0.9754 | 0.5924 | 0.5333 | 0.3954 | 0.8533 |
| DeepSeek | placebo | 0.5664 | 0.9990 | 0.5677 | 0.4024 | 0.5830 | 0.9083 |
| Haiku | naive | 0.6514 | 0.9348 | 0.7234 | 0.5352 | 0.3003 | 0.7258 |
| Haiku | punitive | 0.6843 | 0.9315 | 0.7430 | 0.5760 | 0.2956 | 0.7100 |
| Haiku | label | 0.7280 | 0.9583 | 0.7631 | 0.6652 | 0.2725 | 0.8032 |
| Haiku | evidence | 0.6654 | 0.9378 | 0.7289 | 0.5291 | 0.3232 | 0.6832 |
| Haiku | placebo | 0.7210 | 0.9481 | 0.7505 | 0.4059 | 0.5048 | 0.6233 |
| Luna | naive | 0.6694 | 0.9753 | 0.6911 | 0.6099 | 0.3187 | 0.8183 |
| Luna | punitive | 0.6517 | 0.9602 | 0.6809 | 0.5942 | 0.3301 | 0.8183 |
| Luna | label | 0.6703 | 0.9825 | 0.6747 | 0.6873 | 0.2737 | 0.8916 |
| Luna | evidence | 0.5476 | 0.9728 | 0.5894 | 0.5184 | 0.3258 | 0.8363 |
| Luna | placebo | 0.6058 | 0.9682 | 0.6197 | 0.4285 | 0.4576 | 0.7625 |

High recall is conditional on a nonempty dependence set; it does not resolve treatment-dependent undefined denominators. Precision concerns only the two probed features, not all cited features. Unconditional alignment counts empty sets as agreement and is a distinct secondary estimand. Per-run worst/best missing-score bounds are reported in `runs.*.windows.*.bounds` and the generated report.

Conditional label adoption at primary ticks: pooled numerators/denominators and pooled proportions among valid exposed prompts. The correct/stale columns refer to whether the persisted label matches the current driver, including placebo labels that become correct after a switch. They are not all-available equal-seed means.

| Model | Condition | All exposed: cited / n (rate) | Currently correct: cited / n (rate) | Currently stale: cited / n (rate) |
|---|---|---|---|---|
| DeepSeek | label | 2393/2400 (0.9971) | 1644/1644 (1.0000) | 749/756 (0.9907) |
| DeepSeek | placebo | 2391/2400 (0.9962) | 756/756 (1.0000) | 1635/1644 (0.9945) |
| Haiku | label | 1041/1199 (0.8682) | 751/827 (0.9081) | 290/372 (0.7796) |
| Haiku | placebo | 1026/1200 (0.8550) | 338/372 (0.9086) | 688/828 (0.8309) |
| Luna | label | 1161/1199 (0.9683) | 807/827 (0.9758) | 354/372 (0.9516) |
| Luna | placebo | 1158/1200 (0.9650) | 366/372 (0.9839) | 792/828 (0.9565) |

The pooled Gaussian run-level REML models are secondary: condition, model and their interaction are fixed effects; seed and model-by-seed are random intercepts. Fits use all-available run means rather than the primary pair-specific common support, so they estimate a different descriptive quantity. All fits converged, all returned an optimizer warning about a possible variance boundary, and the gap_false fit has its model-by-seed variance flagged at the boundary. No model was replaced or selected by fit significance.

| Outcome | Fit status | Observed runs | Missing outcomes | Boundary flag | Warnings |
|---|---|---|---|---|---|
| process_precision | ok | 200 | 0 | False | The MLE may be on the boundary of the parameter space. |
| dependence_true | ok | 200 | 0 | False | The MLE may be on the boundary of the parameter space. |
| gap_true | ok | 200 | 0 | False | The MLE may be on the boundary of the parameter space. |
| gap_false | ok | 200 | 0 | True | The MLE may be on the boundary of the parameter space. |

Model interactions (difference from the DeepSeek condition effect, relative to naive; descriptive Wald intervals):

| Outcome | Interaction term | Estimate | 95% descriptive Wald CI |
|---|---|---|---|
| process_precision | condition[punitive]:model[anthropic/claude-haiku-5.5] | 0.0792 | [0.0230, 0.1354] |
| process_precision | condition[label]:model[anthropic/claude-haiku-5.5] | 0.0870 | [0.0308, 0.1431] |
| process_precision | condition[evidence]:model[anthropic/claude-haiku-5.5] | 0.0284 | [-0.0278, 0.0846] |
| process_precision | condition[placebo]:model[anthropic/claude-haiku-5.5] | 0.0937 | [0.0376, 0.1499] |
| process_precision | condition[punitive]:model[openai/gpt-6-luna] | 0.0286 | [-0.0276, 0.0848] |
| process_precision | condition[label]:model[openai/gpt-6-luna] | 0.0112 | [-0.0450, 0.0674] |
| process_precision | condition[evidence]:model[openai/gpt-6-luna] | -0.1074 | [-0.1636, -0.0512] |
| process_precision | condition[placebo]:model[openai/gpt-6-luna] | -0.0395 | [-0.0957, 0.0167] |
| dependence_true | condition[punitive]:model[anthropic/claude-haiku-5.5] | 0.0226 | [-0.0580, 0.1033] |
| dependence_true | condition[label]:model[anthropic/claude-haiku-5.5] | 0.0256 | [-0.0550, 0.1063] |
| dependence_true | condition[evidence]:model[anthropic/claude-haiku-5.5] | 0.0563 | [-0.0243, 0.1369] |
| dependence_true | condition[placebo]:model[anthropic/claude-haiku-5.5] | 0.0640 | [-0.0167, 0.1446] |
| dependence_true | condition[punitive]:model[openai/gpt-6-luna] | -0.0338 | [-0.1144, 0.0469] |
| dependence_true | condition[label]:model[openai/gpt-6-luna] | -0.0269 | [-0.1076, 0.0537] |
| dependence_true | condition[evidence]:model[openai/gpt-6-luna] | -0.0291 | [-0.1098, 0.0515] |
| dependence_true | condition[placebo]:model[openai/gpt-6-luna] | 0.0119 | [-0.0687, 0.0925] |
| gap_true | condition[punitive]:model[anthropic/claude-haiku-5.5] | -0.0716 | [-0.1546, 0.0113] |
| gap_true | condition[label]:model[anthropic/claude-haiku-5.5] | 0.0041 | [-0.0789, 0.0870] |
| gap_true | condition[evidence]:model[anthropic/claude-haiku-5.5] | -0.0492 | [-0.1321, 0.0338] |
| gap_true | condition[placebo]:model[anthropic/claude-haiku-5.5] | -0.2083 | [-0.2913, -0.1254] |
| gap_true | condition[punitive]:model[openai/gpt-6-luna] | -0.0194 | [-0.1024, 0.0635] |
| gap_true | condition[label]:model[openai/gpt-6-luna] | 0.0081 | [-0.0748, 0.0911] |
| gap_true | condition[evidence]:model[openai/gpt-6-luna] | 0.0621 | [-0.0208, 0.1451] |
| gap_true | condition[placebo]:model[openai/gpt-6-luna] | -0.1173 | [-0.2003, -0.0343] |
| gap_false | condition[punitive]:model[anthropic/claude-haiku-5.5] | -0.0795 | [-0.1637, 0.0047] |
| gap_false | condition[label]:model[anthropic/claude-haiku-5.5] | -0.1005 | [-0.1846, -0.0163] |
| gap_false | condition[evidence]:model[anthropic/claude-haiku-5.5] | 0.0581 | [-0.0261, 0.1423] |
| gap_false | condition[placebo]:model[anthropic/claude-haiku-5.5] | 0.0770 | [-0.0072, 0.1612] |
| gap_false | condition[punitive]:model[openai/gpt-6-luna] | -0.0874 | [-0.1716, -0.0032] |
| gap_false | condition[label]:model[openai/gpt-6-luna] | -0.0080 | [-0.0922, 0.0762] |
| gap_false | condition[evidence]:model[openai/gpt-6-luna] | 0.1689 | [0.0847, 0.2530] |
| gap_false | condition[placebo]:model[openai/gpt-6-luna] | 0.1749 | [0.0907, 0.2591] |

The complete mixed-model fixed effects, random-effect variances, and equal-model-weighted summaries are in JSON and the generated report. They do not alter the primary claims. Registered persona/inventory/regime/exposure, event-lag and market-performance results are also reported there, without ranking conditions by realized performance.

## Exploratory supplements

Wilcoxon signed-rank p-values and Cohen’s h were implemented before this analysis but are not in the frozen statistical plan. They remain explicitly exploratory in `primary_contrasts.*.exploratory` and the generated report. They are not used for any hypothesis verdict. No additional specification search, alternate window selection, noise-corrected primary test, optional model selection, or data-dependent exclusion was performed.

## Deviations and incidents

Collection history is in [confirm_run_log.md](confirm_run_log.md). The first detached-launch failure produced no data; the authorized relaunch and recoverable Luna transport errors are documented there. The [first amendment](../preregistration/preregistration.md#amendment-1--2026-10-27), its [development evidence](amendment_1_evidence.md), and the [budget-only second amendment](../preregistration/preregistration.md#amendment-2--2026-10-27-budget-only) remain preserved. The run-log reference to the older OpenRouter procedural threshold does not change the second amendment’s frozen threshold; collection finished below both. No outcome-based stopping, replacement seeds, or rerun of completed responses was used.

Two collection implementation deviations were identified from source before viewing outcomes. `src/v2/simulate.py` advances the independent null RNG only at CF-selected coordinates after the base response, rather than presampling a full tick-by-agent null mask. Fixed CF selection and response-independent RNG consumption preserve pairing and independence from response validity/outcomes, but the realized coordinate mask differs from the exact registered RNG recipe. Also, a selected invalid base still receives a null re-ask and logs an undefined null flip, whereas Amendment 1 specified no null call for invalid bases. The Haiku evidence null summary has one selected invalid base; it is excluded from the valid null denominator. These affect protocol fidelity and the noise diagnostic, not the raw primary outcome definitions; they were disclosed rather than repaired or used to discard runs.

The analysis implementation changes are listed at the start of this document. Primary code, hypotheses, estimands, windows, alpha, four-slot Holm, resampling seed and exclusions were unchanged. Raw data, ledger, preregistration and freeze marker were not edited. No commit was made. A read-only [integrity audit](../data/v2/analysis/confirm/integrity_checks.json) confirms committed input hashes, the raw `cf_flips` source, the sign-reversal values, and the disclosed null-mask behavior.

Validation: `.venv/bin/pytest tests/v2 -q` passed with 107 tests. The confirmatory command completed with all 200 assigned runs included and no missing/excluded assignments; see [execution.log](../data/v2/analysis/confirm/execution.log).

## Results JSON key map

All numeric result tables are rendered from the unrounded JSON values. Display rounding is to four decimals, with scientific notation for very small p-values. Let `R` denote `data/v2/analysis/confirm/results.json`; model keys are DeepSeek = `deepseek-v4-flash`, Haiku = `anthropic/claude-haiku-5.5`, Luna = `openai/gpt-6-luna`. JSON keys containing punctuation are literal keys, not path separators.

Primary/replication row keys:

| Row ID | Literal contrast key |
|---|---|
| P1 | H1_precision_evidence_minus_naive |
| P2 | H1_dependence_evidence_minus_naive |
| P3 | H3_sci_label |
| P4 | H4_sci_placebo |

| Report result | JSON subtree | Fields / explicit aggregation |
|---|---|---|
| Primary and replication table, all columns | `R.models[model].primary_contrasts[contrast]` | `mean_delta`, `bootstrap_ci_95`, `paired_t_p`, `holm_p`, `cohen_dz`, `n_seed_pairs`; observed direction is sign of `mean_delta`; prediction is frozen plan |
| SCI decomposition | same primary contrast | equal mean of `seed_pairs[].citation_delta` and `seed_pairs[].dependence_delta`; `mean_delta` is their difference |
| Assigned/included runs and seed counts | `R.manifest[]` | count entries grouped by `model`, `status`, distinct `seed`; invalid bases are sums of `R.runs[*].windows.overall.missingness.all.base_invalid` |
| Validity pooled and regime tables | `R.confirm_validity[model]`, `.by_true_driver[regime]` | `true_driver_flip_rate.{sum,n,mean,wilson_ci_95}`, `non_driver_flip_rate.{sum,n,mean}`, `true_minus_non_driver`, `design_validity_failure`, `missingness.{sampled,base_invalid,complete_measurements}` |
| Validity seed table | `R.confirm_validity[model].by_seed[seed]` | same true/non-driver/discrimination fields; strata are diagnostics, not new gates |
| Coverage/missingness table | `R.runs[model\|condition\|seed].windows` | sum `.overall.missingness.all.{base_invalid,cf_missing_valid_base.news,cf_missing_valid_base.momentum}`; sum `.primary.coverage.{n_complete_measured,undefined_precision.sum,undefined_recall.sum}` across assigned seeds |
| Primary support table | `R.models[model].primary_contrasts[contrast]` | sum/min/max `seed_pairs[].n_common_coordinates`; length of `excluded_seed_pairs` |
| Null monitoring table | `R.noise_monitoring[model][condition].null` | `n_selected`, `n_selected_base_invalid`, `n_missing_null_valid_base`, `flip_rate.{sum,n,mean,wilson_ci_95}`; seed minima/maxima from sibling `by_seed[seed].flip_rate.mean` |
| Noise adjusted rate table | `R.noise_monitoring[model][condition].noise_adjusted_rates.primary[feature]` | `raw_rate.mean`, `adjusted_rate`; subtraction source is `null_rate_subtracted`; other fixed windows have identical fields |
| Sensitivity permutation and regressions | `R.models[model].sensitivity[contrast]` | `sign_flip.p`; `cluster_regression.terms[cluster_regression.target_coefficient].{estimate,p_t_cluster_df}`; `.wild_bootstrap.p`, `.n_clusters`; raw paired p is from the primary contrast |
| Sensitivity disagreement flags | same sensitivity and primary subtrees | compare each diagnostic p with `metadata.alpha_two_sided` and primary `paired_t_p`; compare estimate signs; no adjustment or primary reinterpretation |
| Ticks 10–39 table | `R.models[model].secondary_contrasts.sensitivity[contrast]` | `mean_delta`, `bootstrap_ci_95`, `paired_t_p`, `n_seed_pairs`; disagreement compares raw p with primary-window raw p |
| Secondary contrast table | `R.models[model].secondary_contrasts.primary[secondary_key]` | `mean_delta`, `bootstrap_ci_95`, `n_seed_pairs`; row gives the complete literal secondary key |
| All-available means | `R.models[model].condition_summaries.primary[condition][metric]` | `mean`; corresponding number of defined seed means is `n_runs_defined` |
| Label adoption fractions | `R.runs[model\|condition\|seed].windows.primary.metrics[metric]` | sum `sum` and `n` across seeds for `label_adoption`, `label_adoption_correct`, `label_adoption_stale`; displayed pooled proportion = summed numerator / summed denominator |
| Pooled fit table | `R.pooled.mixed_models[outcome]` | `status`, `n_observations`, `missing_run_outcomes`, `boundary_variance`, `warnings` |
| Pooled interactions | `R.pooled.mixed_models[outcome].terms[term]` | `estimate`, `wald_ci_95`; row gives complete literal term key |
| Versions, analysis time, source hashes, design constants | `R.metadata` | `versions`, `executed_utc`, `code_revision`, `analysis_code_sha256`, `preregistration_sha256`, `windows`, `bootstrap_rng_seed`, `bootstrap_draws`, `wild_bootstrap_draws`, `alpha_two_sided` |
| Additional registered results and exploratory supplements | `R.output_key_hypothesis_map` | maps every remaining output subtree, including run breakdowns, missing-score bounds, performance and exploratory supplement fields |

Hypothesis verdicts use P1/P2 (H1), the secondary H2 keys plus the definition linking citation_true and environmental_fidelity (H2), P3 (H3), P4 plus secondary H4 keys (H4), and `H5_precision_evidence_minus_punitive` (H5). Incident statements additionally link their source documents/code; they are not new statistical results. The offline test counts are command output, not experimental outcome quantities.
