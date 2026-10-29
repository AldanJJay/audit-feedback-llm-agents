# EXPLORATORY / not preregistered — round 12

All estimates and intervals are descriptive and non-simultaneous; raw p values only, no Holm.
These analyses neither replace nor modify the frozen primary family. All use ticks 20–39, equal seed weights and registered common support.
Noise rates use ticks 0–39; subtract within seed × condition without clipping, falling back to model × condition only if unestimable.
Evidence–punitive SCI uses the current true driver; placebo–label SCI uses its opposite. Exposure SCI uses the target's actual revealed label in both prompts.
Evidence–punitive dependence and exposure SCI repeat registered secondary estimates; the review-requested reporting remains descriptive.

## deepseek-v4-flash — EXPLORATORY / not preregistered

Noise fallback: 0/100 cells; 0 remain unestimable.

| Analysis / JSON path within model | Estimate [95% bootstrap CI] | Raw p | Seed pairs | Citation / dependence changes |
|---|---|---|---|---|
| `incremental.evidence_minus_punitive_dependence` | -0.0805 [-0.1214, -0.0359] | 0.001822 | 20 | — |
| `incremental.evidence_minus_punitive_sci` | 0.0102 [-0.0327, 0.0568] | 0.6704 | 20 | -0.0703 / -0.0805 |
| `incremental.placebo_minus_label_dependence` | -0.2977 [-0.3650, -0.2289] | 1.015e-07 | 20 | — |
| `incremental.placebo_minus_label_sci` | -0.2252 [-0.2838, -0.1669] | 5.098e-07 | 20 | 0.0733 / 0.2985 |
| `noise_adjusted.H1_dependence_evidence_minus_naive` | -0.0627 [-0.1046, -0.0202] | 0.009973 | 20 | — |
| `noise_adjusted.H3_sci_label` | -0.0653 [-0.1192, -0.0162] | 0.02497 | 20 | 0.0655 / 0.1308 |
| `noise_adjusted.H4_sci_placebo` | -0.1631 [-0.2093, -0.1158] | 2.439e-06 | 20 | 0.1192 / 0.2822 |
| `noise_adjusted.evidence_minus_punitive_dependence` | -0.0855 [-0.1253, -0.0429] | 0.0007648 | 20 | — |
| `noise_adjusted.evidence_minus_punitive_sci` | 0.0151 [-0.0289, 0.0625] | 0.54 | 20 | -0.0703 / -0.0855 |
| `noise_adjusted.placebo_minus_label_dependence` | -0.2951 [-0.3657, -0.2237] | 1.961e-07 | 20 | — |
| `noise_adjusted.placebo_minus_label_sci` | -0.2278 [-0.2925, -0.1623] | 2.209e-06 | 20 | 0.0733 / 0.3011 |
| `exposure.label` | -0.2435 [-0.2941, -0.1900] | 2.89e-08 | 20 | 0.1327 / 0.3762 |
| `exposure.placebo` | -0.3169 [-0.3674, -0.2645] | 4.028e-10 | 20 | 0.1556 / 0.4725 |
| `itt.H1_precision_evidence_minus_naive` | -0.0137 [-0.0431, 0.0140] | 0.3683 | 20 | — |
| `itt.H1_dependence_evidence_minus_naive` | -0.0624 [-0.0981, -0.0239] | 0.004672 | 20 | — |
| `itt.H3_sci_label` | -0.0389 [-0.0881, 0.0068] | 0.1364 | 20 | 0.0655 / 0.1044 |
| `itt.H4_sci_placebo` | -0.1341 [-0.1772, -0.0916] | 1.045e-05 | 20 | 0.1192 / 0.2533 |
| `regime.news.H1_precision_evidence_minus_naive` | 0.0082 [-0.0319, 0.0494] | 0.7064 | 20 | — |
| `regime.news.H1_dependence_evidence_minus_naive` | -0.0721 [-0.1401, -0.0050] | 0.05771 | 20 | — |
| `regime.news.H3_sci_label` | -0.1004 [-0.1727, -0.0238] | 0.018 | 20 | 0.0991 / 0.1994 |
| `regime.news.H4_sci_placebo` | -0.1162 [-0.1771, -0.0545] | 0.001628 | 20 | 0.0352 / 0.1515 |
| `regime.momentum.H1_precision_evidence_minus_naive` | -0.0348 [-0.0729, 0.0023] | 0.09851 | 20 | — |
| `regime.momentum.H1_dependence_evidence_minus_naive` | -0.0493 [-0.0993, -0.0045] | 0.06141 | 20 | — |
| `regime.momentum.H3_sci_label` | 0.0271 [-0.0376, 0.0912] | 0.432 | 20 | 0.0289 / 0.0018 |
| `regime.momentum.H4_sci_placebo` | -0.1503 [-0.2189, -0.0846] | 0.0004388 | 20 | 0.2033 / 0.3535 |

Regime null rates (pooled observed responses; descriptive, not seed-cluster inference):

| Condition | Overall news flips/n | Overall momentum flips/n | Primary news flips/n | Primary momentum flips/n |
|---|---|---|---|---|
| naive | 11/228 | 10/222 | 9/112 | 2/113 |
| punitive | 9/228 | 11/222 | 6/112 | 4/113 |
| label | 6/228 | 4/222 | 3/112 | 1/113 |
| evidence | 16/228 | 6/222 | 7/112 | 2/113 |
| placebo | 5/228 | 3/222 | 2/112 | 2/113 |

## anthropic/claude-haiku-5.5 — EXPLORATORY / not preregistered

Noise fallback: 0/50 cells; 0 remain unestimable.

| Analysis / JSON path within model | Estimate [95% bootstrap CI] | Raw p | Seed pairs | Citation / dependence changes |
|---|---|---|---|---|
| `incremental.evidence_minus_punitive_dependence` | -0.0454 [-0.0851, 0.0020] | 0.08469 | 10 | — |
| `incremental.evidence_minus_punitive_sci` | 0.0317 [-0.0325, 0.0898] | 0.3665 | 10 | -0.0137 / -0.0454 |
| `incremental.placebo_minus_label_dependence` | -0.2576 [-0.3219, -0.1847] | 7.166e-05 | 10 | — |
| `incremental.placebo_minus_label_sci` | -0.0477 [-0.1002, 0.0068] | 0.1324 | 10 | 0.1829 / 0.2306 |
| `noise_adjusted.H1_dependence_evidence_minus_naive` | -0.0394 [-0.1089, 0.0441] | 0.3617 | 10 | — |
| `noise_adjusted.H3_sci_label` | -0.0156 [-0.0919, 0.0622] | 0.7132 | 10 | 0.0962 / 0.1118 |
| `noise_adjusted.H4_sci_placebo` | -0.0324 [-0.0998, 0.0309] | 0.3857 | 10 | 0.1466 / 0.1790 |
| `noise_adjusted.evidence_minus_punitive_dependence` | -0.0387 [-0.1083, 0.0498] | 0.3873 | 10 | — |
| `noise_adjusted.evidence_minus_punitive_sci` | 0.0250 [-0.0773, 0.1127] | 0.64 | 10 | -0.0137 / -0.0387 |
| `noise_adjusted.placebo_minus_label_dependence` | -0.2627 [-0.3259, -0.1983] | 3.291e-05 | 10 | — |
| `noise_adjusted.placebo_minus_label_sci` | -0.0427 [-0.1126, 0.0302] | 0.3044 | 10 | 0.1829 / 0.2256 |
| `exposure.label` | -0.0655 [-0.1206, -0.0011] | 0.07404 | 10 | 0.2347 / 0.3002 |
| `exposure.placebo` | -0.1140 [-0.1632, -0.0650] | 0.002209 | 10 | 0.2387 / 0.3527 |
| `itt.H1_precision_evidence_minus_naive` | 0.0163 [-0.0362, 0.0642] | 0.5613 | 10 | — |
| `itt.H1_dependence_evidence_minus_naive` | -0.0059 [-0.0609, 0.0531] | 0.8499 | 10 | — |
| `itt.H3_sci_label` | -0.0354 [-0.0892, 0.0210] | 0.2542 | 10 | 0.0962 / 0.1316 |
| `itt.H4_sci_placebo` | -0.0572 [-0.1045, -0.0039] | 0.06664 | 10 | 0.1466 / 0.2038 |
| `regime.news.H1_precision_evidence_minus_naive` | 0.0415 [-0.0201, 0.1020] | 0.2415 | 10 | — |
| `regime.news.H1_dependence_evidence_minus_naive` | 0.0457 [-0.0055, 0.1074] | 0.1696 | 10 | — |
| `regime.news.H3_sci_label` | -0.0256 [-0.0852, 0.0430] | 0.4731 | 10 | 0.1590 / 0.1846 |
| `regime.news.H4_sci_placebo` | -0.0350 [-0.0976, 0.0312] | 0.3376 | 10 | 0.1458 / 0.1807 |
| `regime.momentum.H1_precision_evidence_minus_naive` | -0.0115 [-0.0793, 0.0513] | 0.7495 | 10 | — |
| `regime.momentum.H1_dependence_evidence_minus_naive` | -0.0572 [-0.1577, 0.0405] | 0.3134 | 10 | — |
| `regime.momentum.H3_sci_label` | -0.0462 [-0.1338, 0.0261] | 0.3141 | 10 | 0.0304 / 0.0766 |
| `regime.momentum.H4_sci_placebo` | -0.0766 [-0.1550, -0.0023] | 0.09984 | 10 | 0.1478 / 0.2244 |

Regime null rates (pooled observed responses; descriptive, not seed-cluster inference):

| Condition | Overall news flips/n | Overall momentum flips/n | Primary news flips/n | Primary momentum flips/n |
|---|---|---|---|---|
| naive | 2/110 | 3/112 | 1/54 | 1/57 |
| punitive | 10/110 | 4/112 | 5/54 | 1/57 |
| label | 2/110 | 7/112 | 2/54 | 3/57 |
| evidence | 5/110 | 8/111 | 1/54 | 4/57 |
| placebo | 8/110 | 3/112 | 4/54 | 1/57 |

## openai/gpt-6-luna — EXPLORATORY / not preregistered

Noise fallback: 0/50 cells; 0 remain unestimable.

| Analysis / JSON path within model | Estimate [95% bootstrap CI] | Raw p | Seed pairs | Citation / dependence changes |
|---|---|---|---|---|
| `incremental.evidence_minus_punitive_dependence` | -0.0770 [-0.1488, -0.0030] | 0.07941 | 10 | — |
| `incremental.evidence_minus_punitive_sci` | 0.0940 [0.0160, 0.1681] | 0.04528 | 10 | 0.0170 / -0.0770 |
| `incremental.placebo_minus_label_dependence` | -0.2591 [-0.3279, -0.1806] | 0.0001274 | 10 | — |
| `incremental.placebo_minus_label_sci` | -0.0446 [-0.1039, 0.0108] | 0.1874 | 10 | 0.1406 / 0.1852 |
| `noise_adjusted.H1_dependence_evidence_minus_naive` | -0.1212 [-0.1902, -0.0376] | 0.01591 | 10 | — |
| `noise_adjusted.H3_sci_label` | -0.0453 [-0.1199, 0.0302] | 0.2915 | 10 | 0.0455 / 0.0908 |
| `noise_adjusted.H4_sci_placebo` | 0.0348 [-0.0311, 0.0883] | 0.3085 | 10 | 0.1792 / 0.1444 |
| `noise_adjusted.evidence_minus_punitive_dependence` | -0.0621 [-0.1407, 0.0276] | 0.1978 | 10 | — |
| `noise_adjusted.evidence_minus_punitive_sci` | 0.0791 [-0.0138, 0.1765] | 0.1521 | 10 | 0.0170 / -0.0621 |
| `noise_adjusted.placebo_minus_label_dependence` | -0.2655 [-0.3323, -0.2004] | 3.882e-05 | 10 | — |
| `noise_adjusted.placebo_minus_label_sci` | -0.0382 [-0.1276, 0.0462] | 0.4405 | 10 | 0.1406 / 0.1788 |
| `exposure.label` | -0.0482 [-0.1329, 0.0337] | 0.3093 | 10 | 0.2039 / 0.2522 |
| `exposure.placebo` | -0.0041 [-0.0639, 0.0531] | 0.8979 | 10 | 0.2542 / 0.2583 |
| `itt.H1_precision_evidence_minus_naive` | -0.1198 [-0.1562, -0.0838] | 0.0001672 | 10 | — |
| `itt.H1_dependence_evidence_minus_naive` | -0.0909 [-0.1396, -0.0312] | 0.01254 | 10 | — |
| `itt.H3_sci_label` | -0.0333 [-0.0845, 0.0252] | 0.2883 | 10 | 0.0455 / 0.0788 |
| `itt.H4_sci_placebo` | 0.0404 [-0.0069, 0.0821] | 0.1272 | 10 | 0.1792 / 0.1388 |
| `regime.news.H1_precision_evidence_minus_naive` | -0.1076 [-0.1608, -0.0572] | 0.003659 | 10 | — |
| `regime.news.H1_dependence_evidence_minus_naive` | -0.0309 [-0.1269, 0.0638] | 0.5564 | 10 | — |
| `regime.news.H3_sci_label` | 0.0730 [-0.0021, 0.1704] | 0.1493 | 10 | 0.0640 / -0.0089 |
| `regime.news.H4_sci_placebo` | -0.0765 [-0.1259, -0.0249] | 0.02036 | 10 | 0.1138 / 0.1903 |
| `regime.momentum.H1_precision_evidence_minus_naive` | -0.1272 [-0.1720, -0.0826] | 0.0004684 | 10 | — |
| `regime.momentum.H1_dependence_evidence_minus_naive` | -0.1426 [-0.2063, -0.0833] | 0.001937 | 10 | — |
| `regime.momentum.H3_sci_label` | -0.1390 [-0.2306, -0.0468] | 0.02023 | 10 | 0.0241 / 0.1631 |
| `regime.momentum.H4_sci_placebo` | 0.1589 [0.0762, 0.2519] | 0.008233 | 10 | 0.2475 / 0.0886 |

Regime null rates (pooled observed responses; descriptive, not seed-cluster inference):

| Condition | Overall news flips/n | Overall momentum flips/n | Primary news flips/n | Primary momentum flips/n |
|---|---|---|---|---|
| naive | 6/110 | 4/112 | 3/54 | 3/57 |
| punitive | 15/110 | 4/112 | 7/54 | 2/57 |
| label | 5/110 | 2/112 | 2/54 | 1/57 |
| evidence | 10/110 | 6/112 | 7/54 | 3/57 |
| placebo | 3/110 | 6/112 | 1/54 | 4/57 |

