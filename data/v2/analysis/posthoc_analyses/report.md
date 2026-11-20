# Post hoc analyses: existing data only

POST HOC / EXPLORATORY; not preregistered

All A–I additions below are post hoc. Registered pooled primaries reproduce EXACTLY, including every seed coordinate, estimate, CI, paired-t p and Holm p. DeepSeek has 20 seeds; Haiku and Luna 10 each. Primary decisions: ticks 20–39. Equal seed weights; 95% percentile seed-bootstrap CIs (10,000 draws, seed 20261026), raw two-sided paired-t diagnostics. CIs are descriptive and not simultaneous. Packages are whole interventions, not factorial components.

## Definitional choices and denominators

1. All new analyses are post hoc. Equal seed weights; 10,000 percentile seed bootstraps, RNG 20261026; paired two-sided t diagnostics. Only A adds separate within-model, within-regime four-slot Holm families; no simultaneous CI coverage.
2. P1 has no additive citation-minus-sensitivity component. Its numerator is decomposed into true/opposite credited overlaps divided by original |C|. Exclusive P1 gives zero numerator credit to both-driver citations on ORIGINAL nonempty-C common support (a specificity-weighted score). The separate at-most-one analysis excludes both-driver bases in BOTH paired packages, retaining ordinary precision with nonempty C. Exclusive CSD replaces citation membership by 1[C={selector}], retaining sensitivity unchanged on complete-probe support.
3. Exactly one means |C|=1 within {news,momentum}; an additional unprobed reason is allowed. Single-driver fidelity/recall are conditional on |C|=1; at-most-one includes empty C. These are post-treatment denominators, as are response/probe validity, nonempty C and nonempty D. Undefined precision/recall remain undefined.
4. C uses seed-only PLANNED audit draw persistence and current regime, before the current action. Label and false-label have opposite label contents, not identical contents; hypothetical labels/subgroups for each target are identical across paired packages. Actual audit receipt is response-validity gated; planned labels are asserted equal to all observed labels before claiming the reconstructed truth subgroup is exogenous. JSON state 'stale' means currently FALSE/incorrect: for label it became stale after a switch; for false-label it can be false from issuance. Tables display this state as false. Comparisons remain whole-package effects, not isolated label mechanisms.
5. D matches target, naive and punitive on jointly valid base coordinates and exposed planned labels, so all three adoption rates share a denominator. All rates cite the ACTUAL communicated label, including stale ones; naive/punitive have only the hypothetical matched label. Eligibility is post-treatment.
6. E defines the true driver at audit time for generated and unique delivered tables, and at prompt time for repeated exposures. Largest |r| is weak maximum (ties included) among all SIX features, with a two-probe comparison also reported. Correct sign means r_true>0. Unavailable correlations are omitted from that metric's denominator. Mixed windows use actual constituent tick regimes; fundamental-only returns use each tick's own driver. Tables are counted per recipient audit; shared identical same-tick tables count once per recipient. Unique delivered means each recipient-audit table appearing at least once in a prompt in the window, including earlier audits; generated tick39 tables are not delivered. JSON reports all generated tables, primary/overall and repeated exposures separately.
7. F uses feature-specific naive primary seed-tick |x| terciles, independent of probe validity, pooling both regimes with numpy linear quantiles. Cutpoints stay fixed across all packages/regimes; low<=q1, middle<=q2, high>q2. Perturbation magnitude is 2|x|. Flip rates use every valid feature re-ask separately, without requiring its other probe valid. Zero feature/proxy signs are separate; after-flip agreement reverses before-flip agreement. Proxy disagreement is an observable consistency diagnostic, not a measure of distributional implausibility.
8. G uses exact noncentral t power for normal paired differences, observed SDs and actual n. Required n is the smallest integer >=2 for the absolute DeepSeek pooled point effect and each model's own SD, at both alpha values; these are planning sensitivities, not achieved-power claims or proof that true effects are shared.
9. H pools one row per market tick across all five packages, and also reports each package. Shared exogenous values are thus repeated, intentionally, for return variance comparisons. SD is population SD. Var(component)/Var(r) does not sum to1 when components covary; Cov(component,r)/Var(r) allocates cross-covariance and sums to1. eta is exact return residual after requested-order impact and fundamental; price flooring does not alter logged returns. Volume frequency deduplicated by seed-tick is also reported.
10. I keeps P4's opposite-CURRENT-driver selector even when the communicated false-label becomes currently true. Citation and sensitivity components use identical complete-probe support. CSD headroom is 1 minus naive citation on the corresponding P3/P4 support; negative citation change can reach minus that baseline. Headroom constrains citation but does not calibrate CSD as faithfulness.

## A. Regime-restricted primary estimates

| Model | Contrast | Regime | Δ [95% CI] | t p | Holm p | Seeds | Paired decisions |
|---|---|---|---|---|---|---|---|
| DeepSeek | P1 | pooled (registered) | -0.0137 [-0.0431, 0.0140] | 0.368275 | 0.368275 | 20 | 1203 |
| DeepSeek | P1 | news | 0.0082 [-0.0319, 0.0494] | 0.706414 | 0.706414 | 20 | 602 |
| DeepSeek | P1 | momentum | -0.0348 [-0.0729, 0.0023] | 0.098507 | 0.197014 | 20 | 601 |
| DeepSeek | P2 | pooled (registered) | -0.0624 [-0.0981, -0.0239] | 0.004672 | 0.014015 | 20 | 1207 |
| DeepSeek | P2 | news | -0.0721 [-0.1401, -0.0050] | 0.057710 | 0.115419 | 20 | 603 |
| DeepSeek | P2 | momentum | -0.0493 [-0.0993, -0.0045] | 0.061413 | 0.184240 | 20 | 604 |
| DeepSeek | P3 | pooled (registered) | -0.0389 [-0.0881, 0.0068] | 0.136375 | 0.272749 | 20 | 1207 |
| DeepSeek | P3 | news | -0.1004 [-0.1727, -0.0238] | 0.017998 | 0.053995 | 20 | 603 |
| DeepSeek | P3 | momentum | 0.0271 [-0.0376, 0.0912] | 0.432034 | 0.432034 | 20 | 604 |
| DeepSeek | P4 | pooled (registered) | -0.1341 [-0.1772, -0.0916] | 0.000010 | 0.000042 | 20 | 1207 |
| DeepSeek | P4 | news | -0.1162 [-0.1771, -0.0545] | 0.001628 | 0.006511 | 20 | 603 |
| DeepSeek | P4 | momentum | -0.1503 [-0.2189, -0.0846] | 0.000439 | 0.001755 | 20 | 604 |
| Haiku | P1 | pooled (registered) | 0.0163 [-0.0362, 0.0642] | 0.561301 | 1.000000 | 10 | 555 |
| Haiku | P1 | news | 0.0415 [-0.0201, 0.1020] | 0.241537 | 0.724610 | 10 | 274 |
| Haiku | P1 | momentum | -0.0115 [-0.0793, 0.0513] | 0.749545 | 0.940167 | 10 | 281 |
| Haiku | P2 | pooled (registered) | -0.0059 [-0.0609, 0.0531] | 0.849851 | 1.000000 | 10 | 591 |
| Haiku | P2 | news | 0.0457 [-0.0055, 0.1074] | 0.169627 | 0.678510 | 10 | 291 |
| Haiku | P2 | momentum | -0.0572 [-0.1577, 0.0405] | 0.313389 | 0.940167 | 10 | 300 |
| Haiku | P3 | pooled (registered) | -0.0354 [-0.0892, 0.0210] | 0.254170 | 0.762510 | 10 | 594 |
| Haiku | P3 | news | -0.0256 [-0.0852, 0.0430] | 0.473084 | 0.724610 | 10 | 296 |
| Haiku | P3 | momentum | -0.0462 [-0.1338, 0.0261] | 0.314117 | 0.940167 | 10 | 298 |
| Haiku | P4 | pooled (registered) | -0.0572 [-0.1045, -0.0039] | 0.066643 | 0.266571 | 10 | 595 |
| Haiku | P4 | news | -0.0350 [-0.0976, 0.0312] | 0.337644 | 0.724610 | 10 | 296 |
| Haiku | P4 | momentum | -0.0766 [-0.1550, -0.0023] | 0.099844 | 0.399375 | 10 | 299 |
| Luna | P1 | pooled (registered) | -0.1198 [-0.1562, -0.0838] | 0.000167 | 0.000669 | 10 | 582 |
| Luna | P1 | news | -0.1076 [-0.1608, -0.0572] | 0.003659 | 0.014635 | 10 | 292 |
| Luna | P1 | momentum | -0.1272 [-0.1720, -0.0826] | 0.000468 | 0.001873 | 10 | 290 |
| Luna | P2 | pooled (registered) | -0.0909 [-0.1396, -0.0312] | 0.012535 | 0.037606 | 10 | 591 |
| Luna | P2 | news | -0.0309 [-0.1269, 0.0638] | 0.556364 | 0.556364 | 10 | 293 |
| Luna | P2 | momentum | -0.1426 [-0.2063, -0.0833] | 0.001937 | 0.005812 | 10 | 298 |
| Luna | P3 | pooled (registered) | -0.0333 [-0.0845, 0.0252] | 0.288327 | 0.288327 | 10 | 591 |
| Luna | P3 | news | 0.0730 [-0.0021, 0.1704] | 0.149322 | 0.298644 | 10 | 292 |
| Luna | P3 | momentum | -0.1390 [-0.2306, -0.0468] | 0.020231 | 0.020231 | 10 | 299 |
| Luna | P4 | pooled (registered) | 0.0404 [-0.0069, 0.0821] | 0.127198 | 0.254396 | 10 | 594 |
| Luna | P4 | news | -0.0765 [-0.1259, -0.0249] | 0.020361 | 0.061082 | 10 | 295 |
| Luna | P4 | momentum | 0.1589 [0.0762, 0.2519] | 0.008233 | 0.016466 | 10 | 299 |

| Model | Window | Naive regime | True − opposite sensitivity [CI] | t p | Seeds | Decisions |
|---|---|---|---|---|---|---|
| DeepSeek | primary | news | -0.0750 [-0.1645, 0.0187] | 0.135845 | 20 | 603 |
| DeepSeek | primary | momentum | 0.6112 [0.5156, 0.6971] | 8.87312e-11 | 20 | 604 |
| DeepSeek | overall | news | -0.1190 [-0.1970, -0.0438] | 0.008670 | 20 | 1219 |
| DeepSeek | overall | momentum | 0.5224 [0.4471, 0.5918] | 2.05324e-11 | 20 | 1202 |
| Haiku | primary | news | 0.0330 [-0.0770, 0.1586] | 0.614577 | 10 | 296 |
| Haiku | primary | momentum | 0.4346 [0.3152, 0.5419] | 0.000063 | 10 | 300 |
| Haiku | overall | news | -0.0011 [-0.1007, 0.0999] | 0.983455 | 10 | 607 |
| Haiku | overall | momentum | 0.3700 [0.2792, 0.4589] | 0.000033 | 10 | 591 |
| Luna | primary | news | 0.2639 [0.1575, 0.3755] | 0.001534 | 10 | 295 |
| Luna | primary | momentum | 0.3158 [0.1940, 0.4347] | 0.000929 | 10 | 299 |
| Luna | overall | news | 0.1806 [0.0908, 0.2630] | 0.003588 | 10 | 606 |
| Luna | overall | momentum | 0.2131 [0.0701, 0.3413] | 0.017052 | 10 | 590 |

## B. Single-driver citations

All rates below condition on valid bases; single-driver precision/recall additionally require complete probes and their defined denominators. These restrictions are post-treatment.

| Model | Package | Both [CI] | Exactly one [CI] | Exclusive true [CI] | Single fidelity [CI] | Single recall [CI] | Single bases | Recall n |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | naive | 0.7200 [0.6800, 0.7600] | 0.2783 [0.2388, 0.3183] | 0.1742 [0.1475, 0.2013] | 0.6263 [0.5717, 0.6830] | 0.9893 [0.9770, 0.9984] | 668 | 314 |
| DeepSeek | punitive | 0.8238 [0.7933, 0.8529] | 0.1750 [0.1463, 0.2050] | 0.1083 [0.0850, 0.1333] | 0.5971 [0.5308, 0.6601] | 0.9726 [0.9373, 0.9969] | 420 | 198 |
| DeepSeek | label | 0.8229 [0.7900, 0.8558] | 0.1771 [0.1442, 0.2100] | 0.1350 [0.1079, 0.1621] | 0.7573 [0.6909, 0.8166] | 0.9921 [0.9821, 1.0000] | 425 | 219 |
| DeepSeek | evidence | 0.6800 [0.6192, 0.7392] | 0.3192 [0.2596, 0.3804] | 0.1733 [0.1375, 0.2121] | 0.5488 [0.4779, 0.6220] | 0.9140 [0.8567, 0.9612] | 766 | 321 |
| DeepSeek | false-label | 0.8383 [0.8167, 0.8604] | 0.1617 [0.1396, 0.1833] | 0.0700 [0.0525, 0.0887] | 0.4168 [0.3437, 0.4923] | 0.9969 [0.9906, 1.0000] | 388 | 178 |
| Haiku | naive | 0.3150 [0.2633, 0.3742] | 0.6500 [0.5975, 0.7009] | 0.4108 [0.3667, 0.4600] | 0.6340 [0.5768, 0.6876] | 0.9456 [0.9244, 0.9675] | 780 | 289 |
| Haiku | punitive | 0.2833 [0.2283, 0.3450] | 0.6850 [0.6275, 0.7367] | 0.4267 [0.3858, 0.4683] | 0.6260 [0.5770, 0.6751] | 0.9332 [0.9059, 0.9621] | 822 | 317 |
| Haiku | label | 0.3177 [0.2670, 0.3675] | 0.6723 [0.6240, 0.7213] | 0.4855 [0.4430, 0.5255] | 0.7223 [0.6831, 0.7566] | 0.9368 [0.9112, 0.9611] | 806 | 339 |
| Haiku | evidence | 0.2980 [0.2375, 0.3745] | 0.6678 [0.5943, 0.7292] | 0.3852 [0.3381, 0.4310] | 0.5802 [0.5328, 0.6338] | 0.9320 [0.9045, 0.9592] | 801 | 299 |
| Haiku | false-label | 0.3042 [0.2625, 0.3492] | 0.6900 [0.6442, 0.7317] | 0.3192 [0.2808, 0.3633] | 0.4646 [0.4091, 0.5220] | 0.9406 [0.9005, 0.9722] | 828 | 356 |
| Luna | naive | 0.4708 [0.4125, 0.5375] | 0.5192 [0.4550, 0.5742] | 0.3475 [0.2900, 0.3958] | 0.6634 [0.6010, 0.7166] | 0.9534 [0.9311, 0.9745] | 623 | 258 |
| Luna | punitive | 0.4750 [0.4258, 0.5300] | 0.5108 [0.4608, 0.5542] | 0.3433 [0.2933, 0.3825] | 0.6693 [0.5980, 0.7312] | 0.9449 [0.9069, 0.9757] | 613 | 243 |
| Luna | label | 0.5721 [0.5393, 0.6088] | 0.4270 [0.3907, 0.4599] | 0.3194 [0.2772, 0.3592] | 0.7459 [0.6738, 0.8003] | 0.9650 [0.9466, 0.9814] | 512 | 242 |
| Luna | evidence | 0.6093 [0.5630, 0.6667] | 0.3866 [0.3300, 0.4328] | 0.2271 [0.1856, 0.2704] | 0.5955 [0.5066, 0.6705] | 0.9254 [0.8841, 0.9618] | 463 | 170 |
| Luna | false-label | 0.5775 [0.5292, 0.6233] | 0.4217 [0.3758, 0.4692] | 0.1850 [0.1475, 0.2283] | 0.4334 [0.3695, 0.5036] | 0.9277 [0.8971, 0.9539] | 506 | 227 |

| Model | Citation rule | Contrast/component | Δ [CI] | t p | Seeds | Common n |
|---|---|---|---|---|---|---|
| DeepSeek | ordinary | P1 | -0.0137 [-0.0431, 0.0140] | 0.368275 | 20 | 1203 |
| DeepSeek | ordinary | P1_true_component | -0.0469 [-0.0692, -0.0254] | 0.000670 | 20 | 1203 |
| DeepSeek | ordinary | P1_false_component | 0.0332 [0.0064, 0.0620] | 0.032897 | 20 | 1203 |
| DeepSeek | ordinary | P3_citation | 0.0655 [0.0437, 0.0863] | 0.000012 | 20 | 1207 |
| DeepSeek | ordinary | P3_CSD | -0.0389 [-0.0881, 0.0068] | 0.136375 | 20 | 1207 |
| DeepSeek | ordinary | P4_citation | 0.1192 [0.0907, 0.1501] | 3.15326e-07 | 20 | 1207 |
| DeepSeek | ordinary | P4_CSD | -0.1341 [-0.1772, -0.0916] | 0.000010 | 20 | 1207 |
| DeepSeek | exclusive | P1 | -0.0110 [-0.0654, 0.0425] | 0.698194 | 20 | 1203 |
| DeepSeek | exclusive | P1_true_component | -0.0275 [-0.0622, 0.0067] | 0.144157 | 20 | 1203 |
| DeepSeek | exclusive | P1_false_component | 0.0165 [-0.0148, 0.0482] | 0.316687 | 20 | 1203 |
| DeepSeek | exclusive | P3_citation | -0.0442 [-0.0714, -0.0160] | 0.006637 | 20 | 1207 |
| DeepSeek | exclusive | P3_CSD | -0.1486 [-0.1929, -0.1086] | 0.000002 | 20 | 1207 |
| DeepSeek | exclusive | P4_citation | -0.0220 [-0.0500, 0.0035] | 0.136075 | 20 | 1207 |
| DeepSeek | exclusive | P4_CSD | -0.2753 [-0.3158, -0.2363] | 4.26943e-11 | 20 | 1207 |
| DeepSeek | at_most_one | P1 | -0.1009 [-0.2368, 0.0117] | 0.136969 | 20 | 160 |
| DeepSeek | at_most_one | P1_true_component | 0.0139 [-0.0317, 0.0606] | 0.575937 | 20 | 160 |
| DeepSeek | at_most_one | P1_false_component | -0.1148 [-0.2646, 0.0133] | 0.130256 | 20 | 160 |
| DeepSeek | at_most_one | P3_citation | 0.0261 [-0.0239, 0.0824] | 0.347271 | 20 | 157 |
| DeepSeek | at_most_one | P3_CSD | -0.0427 [-0.0813, -0.0083] | 0.039671 | 20 | 157 |
| DeepSeek | at_most_one | P4_citation | -0.0126 [-0.0750, 0.0325] | 0.663354 | 20 | 115 |
| DeepSeek | at_most_one | P4_CSD | -0.0482 [-0.0904, -0.0148] | 0.031872 | 20 | 115 |
| Haiku | ordinary | P1 | 0.0163 [-0.0362, 0.0642] | 0.561301 | 10 | 555 |
| Haiku | ordinary | P1_true_component | -0.0052 [-0.0494, 0.0416] | 0.836623 | 10 | 555 |
| Haiku | ordinary | P1_false_component | 0.0215 [-0.0134, 0.0595] | 0.298669 | 10 | 555 |
| Haiku | ordinary | P3_citation | 0.0962 [0.0503, 0.1459] | 0.004673 | 10 | 594 |
| Haiku | ordinary | P3_CSD | -0.0354 [-0.0892, 0.0210] | 0.254170 | 10 | 594 |
| Haiku | ordinary | P4_citation | 0.1466 [0.0843, 0.2096] | 0.001910 | 10 | 595 |
| Haiku | ordinary | P4_CSD | -0.0572 [-0.1045, -0.0039] | 0.066643 | 10 | 595 |
| Haiku | exclusive | P1 | 0.0135 [-0.0476, 0.0715] | 0.685191 | 10 | 555 |
| Haiku | exclusive | P1_true_component | -0.0060 [-0.0461, 0.0375] | 0.796935 | 10 | 555 |
| Haiku | exclusive | P1_false_component | 0.0194 [-0.0211, 0.0621] | 0.413277 | 10 | 555 |
| Haiku | exclusive | P3_citation | 0.0688 [0.0174, 0.1255] | 0.043458 | 10 | 594 |
| Haiku | exclusive | P3_CSD | -0.0627 [-0.1350, 0.0098] | 0.143450 | 10 | 594 |
| Haiku | exclusive | P4_citation | 0.1588 [0.0986, 0.2231] | 0.001150 | 10 | 595 |
| Haiku | exclusive | P4_CSD | -0.0450 [-0.0905, 0.0096] | 0.129010 | 10 | 595 |
| Haiku | at_most_one | P1 | 0.0210 [-0.0583, 0.0983] | 0.633500 | 10 | 317 |
| Haiku | at_most_one | P1_true_component | 0.0254 [-0.0465, 0.0954] | 0.521441 | 10 | 317 |
| Haiku | at_most_one | P1_false_component | -0.0044 [-0.0549, 0.0438] | 0.874271 | 10 | 317 |
| Haiku | at_most_one | P3_citation | 0.0586 [-0.0056, 0.1332] | 0.152184 | 10 | 333 |
| Haiku | at_most_one | P3_CSD | -0.0384 [-0.0975, 0.0241] | 0.270143 | 10 | 333 |
| Haiku | at_most_one | P4_citation | 0.1613 [0.0758, 0.2503] | 0.007522 | 10 | 352 |
| Haiku | at_most_one | P4_CSD | -0.0262 [-0.0931, 0.0457] | 0.504198 | 10 | 352 |
| Luna | ordinary | P1 | -0.1198 [-0.1562, -0.0838] | 0.000167 | 10 | 582 |
| Luna | ordinary | P1_true_component | -0.1048 [-0.1374, -0.0656] | 0.000411 | 10 | 582 |
| Luna | ordinary | P1_false_component | -0.0150 [-0.0506, 0.0225] | 0.464031 | 10 | 582 |
| Luna | ordinary | P3_citation | 0.0455 [0.0130, 0.0797] | 0.032689 | 10 | 591 |
| Luna | ordinary | P3_CSD | -0.0333 [-0.0845, 0.0252] | 0.288327 | 10 | 591 |
| Luna | ordinary | P4_citation | 0.1792 [0.1126, 0.2399] | 0.000538 | 10 | 594 |
| Luna | ordinary | P4_CSD | 0.0404 [-0.0069, 0.0821] | 0.127198 | 10 | 594 |
| Luna | exclusive | P1 | -0.1563 [-0.2055, -0.1015] | 0.000360 | 10 | 582 |
| Luna | exclusive | P1_true_component | -0.1154 [-0.1479, -0.0786] | 0.000171 | 10 | 582 |
| Luna | exclusive | P1_false_component | -0.0409 [-0.0756, -0.0025] | 0.067593 | 10 | 582 |
| Luna | exclusive | P3_citation | -0.0289 [-0.0683, 0.0182] | 0.249039 | 10 | 591 |
| Luna | exclusive | P3_CSD | -0.1077 [-0.1655, -0.0549] | 0.005492 | 10 | 591 |
| Luna | exclusive | P4_citation | 0.0947 [0.0652, 0.1250] | 0.000274 | 10 | 594 |
| Luna | exclusive | P4_CSD | -0.0441 [-0.0899, 0.0023] | 0.110408 | 10 | 594 |
| Luna | at_most_one | P1 | -0.1144 [-0.1816, -0.0493] | 0.010905 | 10 | 172 |
| Luna | at_most_one | P1_true_component | -0.0875 [-0.1528, -0.0243] | 0.035146 | 10 | 172 |
| Luna | at_most_one | P1_false_component | -0.0269 [-0.1021, 0.0321] | 0.484691 | 10 | 172 |
| Luna | at_most_one | P3_citation | 0.0061 [-0.0322, 0.0436] | 0.774465 | 10 | 190 |
| Luna | at_most_one | P3_CSD | -0.0580 [-0.1058, -0.0148] | 0.041870 | 10 | 190 |
| Luna | at_most_one | P4_citation | 0.1295 [0.0372, 0.2179] | 0.025593 | 10 | 175 |
| Luna | at_most_one | P4_CSD | 0.0751 [0.0155, 0.1351] | 0.045749 | 10 | 175 |

## C. Exogenous planned label truth and package contrasts

Use planned draw persistence, not actual receipt, to define subgroup. Realized audits require valid bases, but in these logs all persisted label values equal the seed-only planned values, including after the one skipped label audit. Truth status is exogenous; outcome eligibility remains post-treatment. Label and false-label contents are opposites, not identical; the schedule and the corresponding hypothetical label for every package are identical.

Verified 48000 regime/draw records and 19200 persisted label values. The one skipped selected audit was Haiku label, seed 209, tick 25, agent 5; it repeated the already persisted driver, so planned/observed label identity still matched.

- src/v2/simulate.py:172-173 sets seed parity and switches; src/market.py:70-76 implements deterministic regime_at.
- src/v2/simulate.py:174-178 seeds and pre-draws the full independent audit mask; :233-234 gates selection by package and realized audit by valid decision.
- src/v2/conditions.py:179-186 deterministically returns driver/opposite; src/v2/simulate.py:265-267 builds content and persists feedback; :288 logs PREVIOUS label then :299-300 updates it. Verdict/fine depend on citations; label feature identity does not.

simulate.py:233 leaves selected_audit as the final agent's scalar; :297 copies that scalar to every row in the settlement loop. Reconstruct the full mask from its seed; actual audited flags match reconstructed selection times validity exactly.

Logged audit_selected mismatches by model: {'deepseek-v4-flash': 6916, 'anthropic/claude-haiku-5.5': 3456, 'openai/gpt-6-luna': 3456}.

| Model | Target−naive | Communicated label | Assigned | Metric | Δ [CI] | t p | Seeds | Common n |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | label | true | 1644 | environmental_fidelity | 0.1137 [0.0903, 0.1377] | 2.00107e-08 | 20 | 1644 |
| DeepSeek | label | true | 1644 | process_precision | -0.0072 [-0.0436, 0.0282] | 0.705260 | 20 | 835 |
| DeepSeek | label | true | 1644 | process_recall | 0.0025 [0.0000, 0.0057] | 0.116304 | 20 | 713 |
| DeepSeek | label | true | 1644 | dependence_true | 0.3299 [0.2854, 0.3746] | 1.39994e-11 | 20 | 837 |
| DeepSeek | label | true | 1644 | dependence_false | -0.2821 [-0.3069, -0.2582] | 4.84396e-15 | 20 | 837 |
| DeepSeek | label | true | 1644 | citation_true | 0.1137 [0.0903, 0.1377] | 2.00107e-08 | 20 | 1644 |
| DeepSeek | label | true | 1644 | citation_false | -0.0200 [-0.0477, 0.0045] | 0.163189 | 20 | 1644 |
| DeepSeek | label | true | 1644 | gap_true | -0.2169 [-0.2669, -0.1653] | 1.28934e-07 | 20 | 837 |
| DeepSeek | label | true | 1644 | gap_false | 0.2668 [0.2307, 0.3028] | 1.73235e-11 | 20 | 837 |
| DeepSeek | label | true | 1644 | actual_label_CSD | -0.2169 [-0.2669, -0.1653] | 1.28934e-07 | 20 | 837 |
| DeepSeek | label | false | 756 | environmental_fidelity | -0.0467 [-0.0889, -0.0093] | 0.038038 | 20 | 756 |
| DeepSeek | label | false | 756 | process_precision | -0.0109 [-0.0583, 0.0386] | 0.674095 | 20 | 370 |
| DeepSeek | label | false | 756 | process_recall | 0.0000 [0.0000, 0.0000] | 1.000000 | 20 | 301 |
| DeepSeek | label | false | 756 | dependence_true | -0.3784 [-0.4396, -0.3163] | 3.74592e-10 | 20 | 370 |
| DeepSeek | label | false | 756 | dependence_false | 0.4695 [0.3947, 0.5404] | 1.43576e-10 | 20 | 370 |
| DeepSeek | label | false | 756 | citation_true | -0.0467 [-0.0889, -0.0093] | 0.038038 | 20 | 756 |
| DeepSeek | label | false | 756 | citation_false | 0.1684 [0.1254, 0.2121] | 5.49868e-07 | 20 | 756 |
| DeepSeek | label | false | 756 | gap_true | 0.3325 [0.2531, 0.4138] | 2.35353e-07 | 20 | 370 |
| DeepSeek | label | false | 756 | gap_false | -0.2893 [-0.3880, -0.1820] | 0.000030 | 20 | 370 |
| DeepSeek | label | false | 756 | actual_label_CSD | -0.2893 [-0.3880, -0.1820] | 0.000030 | 20 | 370 |
| DeepSeek | false-label | true | 756 | environmental_fidelity | 0.0913 [0.0566, 0.1330] | 0.000209 | 20 | 756 |
| DeepSeek | false-label | true | 756 | process_precision | 0.0161 [-0.0357, 0.0703] | 0.566742 | 20 | 370 |
| DeepSeek | false-label | true | 756 | process_recall | 0.0000 [0.0000, 0.0000] | 1.000000 | 20 | 309 |
| DeepSeek | false-label | true | 756 | dependence_true | 0.4109 [0.3589, 0.4633] | 5.59519e-12 | 20 | 370 |
| DeepSeek | false-label | true | 756 | dependence_false | -0.3117 [-0.3648, -0.2600] | 6.84808e-10 | 20 | 370 |
| DeepSeek | false-label | true | 756 | citation_true | 0.0913 [0.0566, 0.1330] | 0.000209 | 20 | 756 |
| DeepSeek | false-label | true | 756 | citation_false | -0.0251 [-0.0625, 0.0149] | 0.232594 | 20 | 756 |
| DeepSeek | false-label | true | 756 | gap_true | -0.3016 [-0.3696, -0.2337] | 6.74585e-08 | 20 | 370 |
| DeepSeek | false-label | true | 756 | gap_false | 0.2983 [0.2295, 0.3630] | 6.72509e-08 | 20 | 370 |
| DeepSeek | false-label | true | 756 | actual_label_CSD | -0.3016 [-0.3696, -0.2337] | 6.74585e-08 | 20 | 370 |
| DeepSeek | false-label | false | 1644 | environmental_fidelity | -0.0203 [-0.0487, 0.0086] | 0.199912 | 20 | 1644 |
| DeepSeek | false-label | false | 1644 | process_precision | -0.0401 [-0.0714, -0.0090] | 0.023805 | 20 | 835 |
| DeepSeek | false-label | false | 1644 | process_recall | 0.0047 [0.0006, 0.0100] | 0.075992 | 20 | 696 |
| DeepSeek | false-label | false | 1644 | dependence_true | -0.4568 [-0.5168, -0.3986] | 6.76765e-12 | 20 | 837 |
| DeepSeek | false-label | false | 1644 | dependence_false | 0.5034 [0.4626, 0.5476] | 3.34512e-15 | 20 | 837 |
| DeepSeek | false-label | false | 1644 | citation_true | -0.0203 [-0.0487, 0.0086] | 0.199912 | 20 | 1644 |
| DeepSeek | false-label | false | 1644 | citation_false | 0.1654 [0.1372, 0.1951] | 1.39076e-09 | 20 | 1644 |
| DeepSeek | false-label | false | 1644 | gap_true | 0.4450 [0.3964, 0.4925] | 3.19935e-13 | 20 | 837 |
| DeepSeek | false-label | false | 1644 | gap_false | -0.3284 [-0.3928, -0.2687] | 4.3038e-09 | 20 | 837 |
| DeepSeek | false-label | false | 1644 | actual_label_CSD | -0.3284 [-0.3928, -0.2687] | 4.3038e-09 | 20 | 837 |
| Haiku | label | true | 828 | environmental_fidelity | 0.1972 [0.1445, 0.2537] | 0.000087 | 10 | 827 |
| Haiku | label | true | 828 | process_precision | 0.1330 [0.0648, 0.1927] | 0.003872 | 10 | 396 |
| Haiku | label | true | 828 | process_recall | 0.0212 [-0.0128, 0.0630] | 0.338213 | 10 | 296 |
| Haiku | label | true | 828 | dependence_true | 0.3024 [0.2233, 0.3817] | 0.000056 | 10 | 417 |
| Haiku | label | true | 828 | dependence_false | -0.1697 [-0.2097, -0.1308] | 0.000025 | 10 | 417 |
| Haiku | label | true | 828 | citation_true | 0.1972 [0.1445, 0.2537] | 0.000087 | 10 | 827 |
| Haiku | label | true | 828 | citation_false | -0.2103 [-0.2412, -0.1774] | 6.67004e-07 | 10 | 827 |
| Haiku | label | true | 828 | gap_true | -0.1029 [-0.1676, -0.0317] | 0.020546 | 10 | 417 |
| Haiku | label | true | 828 | gap_false | -0.0287 [-0.0728, 0.0281] | 0.326380 | 10 | 417 |
| Haiku | label | true | 828 | actual_label_CSD | -0.1029 [-0.1676, -0.0317] | 0.020546 | 10 | 417 |
| Haiku | label | false | 372 | environmental_fidelity | -0.1676 [-0.2186, -0.1145] | 0.000228 | 10 | 372 |
| Haiku | label | false | 372 | process_precision | -0.0541 [-0.1392, 0.0277] | 0.259513 | 10 | 169 |
| Haiku | label | false | 372 | process_recall | 0.0209 [-0.0445, 0.0834] | 0.555149 | 10 | 119 |
| Haiku | label | false | 372 | dependence_true | -0.2634 [-0.3628, -0.1782] | 0.000521 | 10 | 177 |
| Haiku | label | false | 372 | dependence_false | 0.3076 [0.2249, 0.3861] | 0.000056 | 10 | 177 |
| Haiku | label | false | 372 | citation_true | -0.1676 [-0.2186, -0.1145] | 0.000228 | 10 | 372 |
| Haiku | label | false | 372 | citation_false | 0.3175 [0.2421, 0.3931] | 0.000029 | 10 | 372 |
| Haiku | label | false | 372 | gap_true | 0.1384 [0.0525, 0.2241] | 0.014484 | 10 | 177 |
| Haiku | label | false | 372 | gap_false | 0.0384 [-0.0519, 0.1367] | 0.465071 | 10 | 177 |
| Haiku | label | false | 372 | actual_label_CSD | 0.0384 [-0.0519, 0.1367] | 0.465071 | 10 | 177 |
| Haiku | false-label | true | 372 | environmental_fidelity | 0.1593 [0.1091, 0.2079] | 0.000222 | 10 | 372 |
| Haiku | false-label | true | 372 | process_precision | 0.1299 [0.0873, 0.1704] | 0.000261 | 10 | 169 |
| Haiku | false-label | true | 372 | process_recall | 0.0087 [-0.0449, 0.0611] | 0.763597 | 10 | 126 |
| Haiku | false-label | true | 372 | dependence_true | 0.3373 [0.2636, 0.4150] | 0.000018 | 10 | 177 |
| Haiku | false-label | true | 372 | dependence_false | -0.1848 [-0.2969, -0.0966] | 0.007506 | 10 | 177 |
| Haiku | false-label | true | 372 | citation_true | 0.1593 [0.1091, 0.2079] | 0.000222 | 10 | 372 |
| Haiku | false-label | true | 372 | citation_false | -0.1306 [-0.2026, -0.0605] | 0.008610 | 10 | 372 |
| Haiku | false-label | true | 372 | gap_true | -0.1746 [-0.2144, -0.1338] | 0.000023 | 10 | 177 |
| Haiku | false-label | true | 372 | gap_false | 0.0624 [-0.0416, 0.1712] | 0.304195 | 10 | 177 |
| Haiku | false-label | true | 372 | actual_label_CSD | -0.1746 [-0.2144, -0.1338] | 0.000023 | 10 | 177 |
| Haiku | false-label | false | 828 | environmental_fidelity | -0.2248 [-0.2739, -0.1728] | 0.000018 | 10 | 828 |
| Haiku | false-label | false | 828 | process_precision | 0.0590 [0.0069, 0.1028] | 0.045457 | 10 | 398 |
| Haiku | false-label | false | 828 | process_recall | 0.0217 [-0.0195, 0.0707] | 0.401043 | 10 | 278 |
| Haiku | false-label | false | 828 | dependence_true | -0.3159 [-0.3934, -0.2324] | 0.000041 | 10 | 418 |
| Haiku | false-label | false | 828 | dependence_false | 0.3606 [0.3015, 0.4185] | 0.000001 | 10 | 418 |
| Haiku | false-label | false | 828 | citation_true | -0.2248 [-0.2739, -0.1728] | 0.000018 | 10 | 828 |
| Haiku | false-label | false | 828 | citation_false | 0.2438 [0.1870, 0.2987] | 0.000020 | 10 | 828 |
| Haiku | false-label | false | 828 | gap_true | 0.0699 [-0.0077, 0.1521] | 0.142985 | 10 | 418 |
| Haiku | false-label | false | 828 | gap_false | -0.0940 [-0.1600, -0.0265] | 0.028993 | 10 | 418 |
| Haiku | false-label | false | 828 | actual_label_CSD | -0.0940 [-0.1600, -0.0265] | 0.028993 | 10 | 418 |
| Luna | label | true | 828 | environmental_fidelity | 0.1457 [0.1179, 0.1787] | 0.000009 | 10 | 827 |
| Luna | label | true | 828 | process_precision | 0.0517 [0.0034, 0.1025] | 0.083058 | 10 | 409 |
| Luna | label | true | 828 | process_recall | -0.0142 [-0.0322, 0.0006] | 0.147135 | 10 | 323 |
| Luna | label | true | 828 | dependence_true | 0.2432 [0.1838, 0.3081] | 0.000047 | 10 | 415 |
| Luna | label | true | 828 | dependence_false | -0.1860 [-0.2252, -0.1472] | 0.000010 | 10 | 415 |
| Luna | label | true | 828 | citation_true | 0.1457 [0.1179, 0.1787] | 0.000009 | 10 | 827 |
| Luna | label | true | 828 | citation_false | -0.1055 [-0.1322, -0.0775] | 0.000051 | 10 | 827 |
| Luna | label | true | 828 | gap_true | -0.1234 [-0.2010, -0.0427] | 0.017598 | 10 | 415 |
| Luna | label | true | 828 | gap_false | 0.0633 [0.0145, 0.1161] | 0.044363 | 10 | 415 |
| Luna | label | true | 828 | actual_label_CSD | -0.1234 [-0.2010, -0.0427] | 0.017598 | 10 | 415 |
| Luna | label | false | 372 | environmental_fidelity | -0.0931 [-0.1155, -0.0688] | 0.000043 | 10 | 372 |
| Luna | label | false | 372 | process_precision | -0.1207 [-0.2143, -0.0268] | 0.041342 | 10 | 174 |
| Luna | label | false | 372 | process_recall | 0.0417 [0.0067, 0.0950] | 0.128264 | 10 | 132 |
| Luna | label | false | 372 | dependence_true | -0.3083 [-0.3935, -0.2314] | 0.000058 | 10 | 176 |
| Luna | label | false | 372 | dependence_false | 0.2695 [0.1872, 0.3479] | 0.000155 | 10 | 176 |
| Luna | label | false | 372 | citation_true | -0.0931 [-0.1155, -0.0688] | 0.000043 | 10 | 372 |
| Luna | label | false | 372 | citation_false | 0.3604 [0.2770, 0.4601] | 0.000052 | 10 | 372 |
| Luna | label | false | 372 | gap_true | 0.1786 [0.1021, 0.2574] | 0.002005 | 10 | 176 |
| Luna | label | false | 372 | gap_false | 0.1462 [-0.0166, 0.3043] | 0.125163 | 10 | 176 |
| Luna | label | false | 372 | actual_label_CSD | 0.1462 [-0.0166, 0.3043] | 0.125163 | 10 | 176 |
| Luna | false-label | true | 372 | environmental_fidelity | 0.1763 [0.1050, 0.2516] | 0.001573 | 10 | 372 |
| Luna | false-label | true | 372 | process_precision | -0.0129 [-0.0722, 0.0514] | 0.707338 | 10 | 174 |
| Luna | false-label | true | 372 | process_recall | -0.0087 [-0.0332, 0.0138] | 0.509251 | 10 | 145 |
| Luna | false-label | true | 372 | dependence_true | 0.1960 [0.1366, 0.2574] | 0.000222 | 10 | 176 |
| Luna | false-label | true | 372 | dependence_false | -0.1728 [-0.2231, -0.1238] | 0.000118 | 10 | 176 |
| Luna | false-label | true | 372 | citation_true | 0.1763 [0.1050, 0.2516] | 0.001573 | 10 | 372 |
| Luna | false-label | true | 372 | citation_false | -0.0902 [-0.1358, -0.0402] | 0.006733 | 10 | 372 |
| Luna | false-label | true | 372 | gap_true | -0.0456 [-0.1343, 0.0386] | 0.346749 | 10 | 176 |
| Luna | false-label | true | 372 | gap_false | 0.0948 [0.0322, 0.1660] | 0.029071 | 10 | 176 |
| Luna | false-label | true | 372 | actual_label_CSD | -0.0456 [-0.1343, 0.0386] | 0.346749 | 10 | 176 |
| Luna | false-label | false | 828 | environmental_fidelity | -0.1692 [-0.1958, -0.1387] | 0.000002 | 10 | 828 |
| Luna | false-label | false | 828 | process_precision | -0.0850 [-0.1149, -0.0511] | 0.000773 | 10 | 413 |
| Luna | false-label | false | 828 | process_recall | -0.0150 [-0.0357, 0.0035] | 0.192336 | 10 | 292 |
| Luna | false-label | false | 828 | dependence_true | -0.3525 [-0.3749, -0.3295] | 3.89819e-10 | 10 | 418 |
| Luna | false-label | false | 828 | dependence_false | 0.2782 [0.2489, 0.3082] | 3.32173e-08 | 10 | 418 |
| Luna | false-label | false | 828 | citation_true | -0.1692 [-0.1958, -0.1387] | 0.000002 | 10 | 828 |
| Luna | false-label | false | 828 | citation_false | 0.2954 [0.2370, 0.3492] | 0.000005 | 10 | 828 |
| Luna | false-label | false | 828 | gap_true | 0.1693 [0.1338, 0.2015] | 0.000007 | 10 | 418 |
| Luna | false-label | false | 828 | gap_false | 0.0151 [-0.0519, 0.0794] | 0.678996 | 10 | 418 |
| Luna | false-label | false | 828 | actual_label_CSD | 0.0151 [-0.0519, 0.0794] | 0.678996 | 10 | 418 |

## D. Adoption of the actual communicated label

Rates share jointly valid target/naive/punitive coordinates; baseline packages are evaluated against the target's seed-planned communicated label. Labels can be stale.

| Model | Label source | Package citing it | Adoption [CI] | Seeds | Citations | Bases |
|---|---|---|---|---|---|---|
| DeepSeek | label | label | 0.9971 [0.9933, 1.0000] | 20 | 2393 | 2400 |
| DeepSeek | label | naive | 0.8654 [0.8421, 0.8887] | 20 | 2077 | 2400 |
| DeepSeek | label | punitive | 0.9104 [0.8950, 0.9254] | 20 | 2185 | 2400 |
| DeepSeek | false-label | false-label | 0.9963 [0.9925, 0.9992] | 20 | 2391 | 2400 |
| DeepSeek | false-label | naive | 0.8529 [0.8238, 0.8800] | 20 | 2047 | 2400 |
| DeepSeek | false-label | punitive | 0.9121 [0.8892, 0.9325] | 20 | 2189 | 2400 |
| Haiku | label | label | 0.8681 [0.8392, 0.8908] | 10 | 1041 | 1199 |
| Haiku | label | naive | 0.6429 [0.5845, 0.7000] | 10 | 771 | 1199 |
| Haiku | label | punitive | 0.6279 [0.5746, 0.6804] | 10 | 753 | 1199 |
| Haiku | false-label | false-label | 0.8550 [0.8108, 0.8975] | 10 | 1026 | 1200 |
| Haiku | false-label | naive | 0.6367 [0.5925, 0.6800] | 10 | 764 | 1200 |
| Haiku | false-label | punitive | 0.6233 [0.5758, 0.6733] | 10 | 748 | 1200 |
| Luna | label | label | 0.9682 [0.9481, 0.9850] | 10 | 1161 | 1199 |
| Luna | label | naive | 0.7580 [0.7155, 0.7967] | 10 | 909 | 1199 |
| Luna | label | punitive | 0.7555 [0.7127, 0.7933] | 10 | 906 | 1199 |
| Luna | false-label | false-label | 0.9650 [0.9533, 0.9750] | 10 | 1158 | 1200 |
| Luna | false-label | naive | 0.7033 [0.6558, 0.7567] | 10 | 844 | 1200 |
| Luna | false-label | punitive | 0.7058 [0.6608, 0.7508] | 10 | 847 | 1200 |

## E. Informativeness of evidence actually delivered

Main table counts each distinct recipient-audit table delivered at least once in a primary-window prompt, including tables generated earlier. The driver is the one current at audit time. JSON also has every generated table (including undelivered tick39 tables), all-tick delivery summaries and repeated prompt exposures evaluated against the then-current driver. 'Largest' compares all six features; the two-probe alternative is in JSON.

| Model | Return target | Delivered tables | Mean |r| true [CI] | Mean |r| opposite [CI] | True largest |r| [CI] | True sign positive [CI] | Mixed regimes [CI] |
|---|---|---|---|---|---|---|---|
| DeepSeek | realized | 798 | 0.7741 [0.7457, 0.8024] | 0.6009 [0.5644, 0.6354] | 0.5067 [0.4581, 0.5525] | 0.9552 [0.9344, 0.9741] | 0.3833 [0.3475, 0.4165] |
| DeepSeek | without_impact | 798 | 0.8540 [0.8303, 0.8769] | 0.5161 [0.4817, 0.5521] | 0.7392 [0.6960, 0.7798] | 0.9466 [0.9190, 0.9705] | 0.3833 [0.3475, 0.4165] |
| DeepSeek | fundamental | 798 | 0.8748 [0.8529, 0.8960] | 0.5227 [0.4926, 0.5549] | 0.7797 [0.7419, 0.8128] | 0.9638 [0.9447, 0.9802] | 0.3833 [0.3475, 0.4165] |
| Haiku | realized | 385 | 0.8080 [0.7730, 0.8461] | 0.6169 [0.5780, 0.6539] | 0.5706 [0.4813, 0.6449] | 0.9470 [0.9014, 0.9841] | 0.4041 [0.3582, 0.4455] |
| Haiku | without_impact | 385 | 0.8528 [0.8164, 0.8870] | 0.5223 [0.4810, 0.5653] | 0.7589 [0.6892, 0.8197] | 0.9493 [0.9028, 0.9868] | 0.4041 [0.3582, 0.4455] |
| Haiku | fundamental | 385 | 0.8802 [0.8504, 0.9078] | 0.5232 [0.4890, 0.5581] | 0.7867 [0.7351, 0.8330] | 0.9727 [0.9521, 0.9907] | 0.4041 [0.3582, 0.4455] |
| Luna | realized | 385 | 0.8039 [0.7673, 0.8427] | 0.6062 [0.5597, 0.6533] | 0.5703 [0.5080, 0.6234] | 0.9736 [0.9530, 0.9919] | 0.4041 [0.3582, 0.4455] |
| Luna | without_impact | 385 | 0.8528 [0.8164, 0.8870] | 0.5223 [0.4810, 0.5653] | 0.7589 [0.6892, 0.8197] | 0.9493 [0.9028, 0.9868] | 0.4041 [0.3582, 0.4455] |
| Luna | fundamental | 385 | 0.8802 [0.8504, 0.9078] | 0.5232 [0.4890, 0.5581] | 0.7867 [0.7351, 0.8330] | 0.9727 [0.9521, 0.9907] | 0.4041 [0.3582, 0.4455] |

The following table instead counts every primary prompt exposure, and evaluates the table against the driver CURRENT WHEN READ. Persistence can therefore reduce informativeness even when its audit-time driver was identified correctly.

| Model | Return target | Prompt exposures | Mean |r| current driver [CI] | Mean |r| opposite [CI] | Current largest |r| [CI] | Current sign positive [CI] | Mixed regimes [CI] |
|---|---|---|---|---|---|---|---|
| DeepSeek | realized | 2400 | 0.6627 [0.6248, 0.6993] | 0.7054 [0.6827, 0.7277] | 0.3417 [0.3075, 0.3796] | 0.8642 [0.8125, 0.9121] | 0.4150 [0.3729, 0.4575] |
| DeepSeek | without_impact | 2400 | 0.6907 [0.6584, 0.7241] | 0.6739 [0.6523, 0.6958] | 0.4529 [0.4167, 0.4904] | 0.8067 [0.7475, 0.8604] | 0.4150 [0.3729, 0.4575] |
| DeepSeek | fundamental | 2400 | 0.7069 [0.6736, 0.7405] | 0.6880 [0.6691, 0.7074] | 0.4742 [0.4300, 0.5175] | 0.8204 [0.7737, 0.8671] | 0.4150 [0.3729, 0.4575] |
| Haiku | realized | 1200 | 0.7011 [0.6681, 0.7458] | 0.7083 [0.6801, 0.7363] | 0.3808 [0.2958, 0.4625] | 0.8500 [0.7717, 0.9250] | 0.4575 [0.3967, 0.5175] |
| Haiku | without_impact | 1200 | 0.6910 [0.6545, 0.7377] | 0.6689 [0.6454, 0.6908] | 0.4692 [0.4125, 0.5225] | 0.8100 [0.7067, 0.8983] | 0.4575 [0.3967, 0.5175] |
| Haiku | fundamental | 1200 | 0.7107 [0.6760, 0.7519] | 0.6813 [0.6581, 0.7046] | 0.4808 [0.4133, 0.5458] | 0.8492 [0.7750, 0.9158] | 0.4575 [0.3967, 0.5175] |
| Luna | realized | 1200 | 0.6807 [0.6289, 0.7370] | 0.7093 [0.6803, 0.7352] | 0.3458 [0.2725, 0.4175] | 0.8908 [0.8417, 0.9400] | 0.4575 [0.3967, 0.5175] |
| Luna | without_impact | 1200 | 0.6910 [0.6545, 0.7377] | 0.6689 [0.6454, 0.6908] | 0.4692 [0.4125, 0.5225] | 0.8100 [0.7067, 0.8983] | 0.4575 [0.3967, 0.5175] |
| Luna | fundamental | 1200 | 0.7107 [0.6760, 0.7519] | 0.6813 [0.6581, 0.7046] | 0.4808 [0.4133, 0.5458] | 0.8492 [0.7750, 0.9158] | 0.4575 [0.3967, 0.5175] |

## F. Perturbation magnitude and unperturbed proxies

The feature is changed by 2|x|. Cutpoints come from unique naive seed-ticks in the primary window, separately by feature; they are fixed across regimes and packages. After-flip disagreement means the reversed feature now contradicts its unaltered proxy. Zero signs remain separate. This quantifies sign inconsistency without establishing out-of-distribution status.

| Model | Feature | q1 |x| | q2 |x| | Naive seed-ticks |
|---|---|---|---|---|
| DeepSeek | news | 0.396000 | 0.898000 | 400 |
| DeepSeek | momentum | 0.354000 | 0.870000 | 400 |
| Haiku | news | 0.399333 | 0.904000 | 200 |
| Haiku | momentum | 0.335000 | 0.818333 | 200 |
| Luna | news | 0.399333 | 0.904000 | 200 |
| Luna | momentum | 0.335000 | 0.818333 | 200 |

| Model | Package | Feature | Regime | |x| tercile | Proxy after flip | Flip rate [CI] | Seeds | Flips | Re-asks |
|---|---|---|---|---|---|---|---|---|---|
| DeepSeek | evidence | momentum | momentum | all | agree | 0.6100 [0.5002, 0.7174] | 20 | 125 | 206 |
| DeepSeek | evidence | momentum | momentum | all | disagree | 0.7780 [0.6862, 0.8615] | 20 | 310 | 396 |
| DeepSeek | evidence | momentum | momentum | all | zero | 1.0000 [1.0000, 1.0000] | 1 | 2 | 2 |
| DeepSeek | evidence | momentum | momentum | high | all | 0.8931 [0.8231, 0.9516] | 20 | 249 | 280 |
| DeepSeek | evidence | momentum | momentum | low | all | 0.4729 [0.3105, 0.6377] | 18 | 58 | 129 |
| DeepSeek | evidence | momentum | momentum | middle | all | 0.6107 [0.4941, 0.7241] | 20 | 130 | 195 |
| DeepSeek | evidence | momentum | news | all | agree | 0.5762 [0.4778, 0.6733] | 20 | 132 | 234 |
| DeepSeek | evidence | momentum | news | all | disagree | 0.5989 [0.5224, 0.6741] | 20 | 216 | 369 |
| DeepSeek | evidence | momentum | news | high | all | 0.7806 [0.6332, 0.8992] | 19 | 106 | 141 |
| DeepSeek | evidence | momentum | news | low | all | 0.3655 [0.2616, 0.4708] | 20 | 101 | 272 |
| DeepSeek | evidence | momentum | news | middle | all | 0.7247 [0.6263, 0.8209] | 19 | 141 | 190 |
| DeepSeek | evidence | news | momentum | all | agree | 0.1675 [0.0869, 0.2605] | 20 | 42 | 238 |
| DeepSeek | evidence | news | momentum | all | disagree | 0.2457 [0.1674, 0.3288] | 20 | 88 | 363 |
| DeepSeek | evidence | news | momentum | all | zero | 0.0000 [0.0000, 0.0000] | 1 | 0 | 3 |
| DeepSeek | evidence | news | momentum | high | all | 0.4445 [0.2851, 0.6111] | 18 | 47 | 119 |
| DeepSeek | evidence | news | momentum | low | all | 0.1121 [0.0570, 0.1816] | 20 | 27 | 286 |
| DeepSeek | evidence | news | momentum | middle | all | 0.2545 [0.1386, 0.3835] | 20 | 56 | 199 |
| DeepSeek | evidence | news | news | all | agree | 0.3301 [0.1954, 0.4715] | 20 | 55 | 204 |
| DeepSeek | evidence | news | news | all | disagree | 0.3792 [0.2842, 0.4757] | 20 | 150 | 399 |
| DeepSeek | evidence | news | news | high | all | 0.5063 [0.3804, 0.6324] | 20 | 156 | 287 |
| DeepSeek | evidence | news | news | low | all | 0.1707 [0.0771, 0.2815] | 18 | 18 | 121 |
| DeepSeek | evidence | news | news | middle | all | 0.1526 [0.0761, 0.2498] | 19 | 31 | 195 |
| DeepSeek | label | momentum | momentum | all | agree | 0.7007 [0.5880, 0.8017] | 20 | 143 | 206 |
| DeepSeek | label | momentum | momentum | all | disagree | 0.8079 [0.7440, 0.8649] | 20 | 325 | 396 |
| DeepSeek | label | momentum | momentum | all | zero | 1.0000 [1.0000, 1.0000] | 1 | 2 | 2 |
| DeepSeek | label | momentum | momentum | high | all | 0.8815 [0.8181, 0.9328] | 20 | 244 | 280 |
| DeepSeek | label | momentum | momentum | low | all | 0.6660 [0.5566, 0.7693] | 18 | 88 | 129 |
| DeepSeek | label | momentum | momentum | middle | all | 0.6668 [0.5397, 0.7801] | 20 | 138 | 195 |
| DeepSeek | label | momentum | news | all | agree | 0.3393 [0.2547, 0.4277] | 20 | 84 | 234 |
| DeepSeek | label | momentum | news | all | disagree | 0.3443 [0.2831, 0.4068] | 20 | 127 | 369 |
| DeepSeek | label | momentum | news | high | all | 0.4016 [0.2592, 0.5487] | 19 | 48 | 141 |
| DeepSeek | label | momentum | news | low | all | 0.3113 [0.2367, 0.3912] | 20 | 80 | 272 |
| DeepSeek | label | momentum | news | middle | all | 0.4391 [0.3546, 0.5151] | 19 | 83 | 190 |
| DeepSeek | label | news | momentum | all | agree | 0.1830 [0.1141, 0.2552] | 20 | 41 | 238 |
| DeepSeek | label | news | momentum | all | disagree | 0.2365 [0.1742, 0.3021] | 20 | 90 | 363 |
| DeepSeek | label | news | momentum | all | zero | 0.0000 [0.0000, 0.0000] | 1 | 0 | 3 |
| DeepSeek | label | news | momentum | high | all | 0.3150 [0.2062, 0.4327] | 18 | 36 | 119 |
| DeepSeek | label | news | momentum | low | all | 0.1701 [0.1060, 0.2370] | 20 | 44 | 286 |
| DeepSeek | label | news | momentum | middle | all | 0.2662 [0.1882, 0.3496] | 20 | 51 | 199 |
| DeepSeek | label | news | news | all | agree | 0.6045 [0.5060, 0.7063] | 20 | 121 | 204 |
| DeepSeek | label | news | news | all | disagree | 0.6341 [0.5699, 0.6969] | 20 | 255 | 399 |
| DeepSeek | label | news | news | high | all | 0.6582 [0.5829, 0.7344] | 20 | 195 | 287 |
| DeepSeek | label | news | news | low | all | 0.4500 [0.3060, 0.5991] | 18 | 54 | 121 |
| DeepSeek | label | news | news | middle | all | 0.6576 [0.5695, 0.7497] | 19 | 127 | 195 |
| DeepSeek | naive | momentum | momentum | all | agree | 0.6519 [0.5332, 0.7616] | 20 | 139 | 206 |
| DeepSeek | naive | momentum | momentum | all | disagree | 0.8329 [0.7688, 0.8945] | 20 | 326 | 396 |
| DeepSeek | naive | momentum | momentum | all | zero | 0.5000 [0.5000, 0.5000] | 1 | 1 | 2 |
| DeepSeek | naive | momentum | momentum | high | all | 0.9641 [0.9173, 1.0000] | 20 | 268 | 280 |
| DeepSeek | naive | momentum | momentum | low | all | 0.4990 [0.3315, 0.6625] | 18 | 63 | 129 |
| DeepSeek | naive | momentum | momentum | middle | all | 0.6826 [0.5731, 0.7802] | 20 | 135 | 195 |
| DeepSeek | naive | momentum | news | all | agree | 0.4555 [0.3672, 0.5438] | 20 | 103 | 234 |
| DeepSeek | naive | momentum | news | all | disagree | 0.5489 [0.4733, 0.6294] | 20 | 195 | 369 |
| DeepSeek | naive | momentum | news | high | all | 0.7329 [0.6071, 0.8478] | 19 | 105 | 141 |
| DeepSeek | naive | momentum | news | low | all | 0.2566 [0.1938, 0.3188] | 20 | 73 | 272 |
| DeepSeek | naive | momentum | news | middle | all | 0.6028 [0.4649, 0.7269] | 19 | 120 | 190 |
| DeepSeek | naive | news | momentum | all | agree | 0.1462 [0.0720, 0.2314] | 20 | 38 | 238 |
| DeepSeek | naive | news | momentum | all | disagree | 0.1636 [0.1096, 0.2208] | 20 | 62 | 363 |
| DeepSeek | naive | news | momentum | all | zero | 0.0000 [0.0000, 0.0000] | 1 | 0 | 3 |
| DeepSeek | naive | news | momentum | high | all | 0.4295 [0.2726, 0.5841] | 18 | 45 | 119 |
| DeepSeek | naive | news | momentum | low | all | 0.0886 [0.0321, 0.1553] | 20 | 22 | 286 |
| DeepSeek | naive | news | momentum | middle | all | 0.1614 [0.0836, 0.2505] | 20 | 33 | 199 |
| DeepSeek | naive | news | news | all | agree | 0.3707 [0.2579, 0.4898] | 20 | 71 | 204 |
| DeepSeek | naive | news | news | all | disagree | 0.4618 [0.3886, 0.5345] | 20 | 182 | 399 |
| DeepSeek | naive | news | news | high | all | 0.6305 [0.5524, 0.7088] | 20 | 188 | 287 |
| DeepSeek | naive | news | news | low | all | 0.1252 [0.0444, 0.2199] | 18 | 17 | 121 |
| DeepSeek | naive | news | news | middle | all | 0.2204 [0.1176, 0.3384] | 19 | 48 | 195 |
| DeepSeek | false-label | momentum | momentum | all | agree | 0.3954 [0.2872, 0.5031] | 20 | 84 | 206 |
| DeepSeek | false-label | momentum | momentum | all | disagree | 0.5042 [0.4318, 0.5805] | 20 | 189 | 396 |
| DeepSeek | false-label | momentum | momentum | all | zero | 0.0000 [0.0000, 0.0000] | 1 | 0 | 2 |
| DeepSeek | false-label | momentum | momentum | high | all | 0.5030 [0.4152, 0.5865] | 20 | 141 | 280 |
| DeepSeek | false-label | momentum | momentum | low | all | 0.2813 [0.1550, 0.4182] | 18 | 38 | 129 |
| DeepSeek | false-label | momentum | momentum | middle | all | 0.5070 [0.3967, 0.6247] | 20 | 94 | 195 |
| DeepSeek | false-label | momentum | news | all | agree | 0.6322 [0.5447, 0.7201] | 20 | 146 | 234 |
| DeepSeek | false-label | momentum | news | all | disagree | 0.6597 [0.6092, 0.7129] | 20 | 245 | 369 |
| DeepSeek | false-label | momentum | news | high | all | 0.6902 [0.5489, 0.8216] | 19 | 107 | 141 |
| DeepSeek | false-label | momentum | news | low | all | 0.5877 [0.5121, 0.6615] | 20 | 162 | 272 |
| DeepSeek | false-label | momentum | news | middle | all | 0.6402 [0.5684, 0.7154] | 19 | 122 | 190 |
| DeepSeek | false-label | news | momentum | all | agree | 0.4762 [0.3464, 0.6004] | 20 | 122 | 238 |
| DeepSeek | false-label | news | momentum | all | disagree | 0.5490 [0.4762, 0.6193] | 20 | 191 | 363 |
| DeepSeek | false-label | news | momentum | all | zero | 0.0000 [0.0000, 0.0000] | 1 | 0 | 3 |
| DeepSeek | false-label | news | momentum | high | all | 0.7239 [0.6117, 0.8327] | 18 | 83 | 119 |
| DeepSeek | false-label | news | momentum | low | all | 0.3458 [0.2485, 0.4458] | 20 | 101 | 286 |
| DeepSeek | false-label | news | momentum | middle | all | 0.6582 [0.5594, 0.7539] | 20 | 129 | 199 |
| DeepSeek | false-label | news | news | all | agree | 0.3467 [0.2425, 0.4519] | 20 | 72 | 204 |
| DeepSeek | false-label | news | news | all | disagree | 0.3566 [0.2996, 0.4153] | 20 | 140 | 399 |
| DeepSeek | false-label | news | news | high | all | 0.4453 [0.3536, 0.5386] | 20 | 122 | 287 |
| DeepSeek | false-label | news | news | low | all | 0.2016 [0.1127, 0.2999] | 18 | 26 | 121 |
| DeepSeek | false-label | news | news | middle | all | 0.3290 [0.2320, 0.4271] | 19 | 64 | 195 |
| DeepSeek | punitive | momentum | momentum | all | agree | 0.5881 [0.4760, 0.6956] | 20 | 131 | 206 |
| DeepSeek | punitive | momentum | momentum | all | disagree | 0.7977 [0.7333, 0.8615] | 20 | 313 | 396 |
| DeepSeek | punitive | momentum | momentum | all | zero | 0.5000 [0.5000, 0.5000] | 1 | 1 | 2 |
| DeepSeek | punitive | momentum | momentum | high | all | 0.9200 [0.8518, 0.9763] | 20 | 257 | 280 |
| DeepSeek | punitive | momentum | momentum | low | all | 0.4512 [0.2948, 0.6070] | 18 | 56 | 129 |
| DeepSeek | punitive | momentum | momentum | middle | all | 0.6628 [0.5476, 0.7658] | 20 | 132 | 195 |
| DeepSeek | punitive | momentum | news | all | agree | 0.4193 [0.3164, 0.5318] | 20 | 87 | 234 |
| DeepSeek | punitive | momentum | news | all | disagree | 0.4728 [0.3939, 0.5500] | 20 | 174 | 369 |
| DeepSeek | punitive | momentum | news | high | all | 0.6446 [0.4866, 0.7963] | 19 | 95 | 141 |
| DeepSeek | punitive | momentum | news | low | all | 0.2040 [0.1351, 0.2777] | 20 | 54 | 272 |
| DeepSeek | punitive | momentum | news | middle | all | 0.5613 [0.4208, 0.6946] | 19 | 112 | 190 |
| DeepSeek | punitive | news | momentum | all | agree | 0.1712 [0.0934, 0.2609] | 20 | 41 | 238 |
| DeepSeek | punitive | news | momentum | all | disagree | 0.2162 [0.1438, 0.2941] | 20 | 80 | 363 |
| DeepSeek | punitive | news | momentum | all | zero | 0.0000 [0.0000, 0.0000] | 1 | 0 | 3 |
| DeepSeek | punitive | news | momentum | high | all | 0.4992 [0.3368, 0.6536] | 18 | 56 | 119 |
| DeepSeek | punitive | news | momentum | low | all | 0.1017 [0.0423, 0.1701] | 20 | 25 | 286 |
| DeepSeek | punitive | news | momentum | middle | all | 0.2062 [0.1060, 0.3203] | 20 | 40 | 199 |
| DeepSeek | punitive | news | news | all | agree | 0.4459 [0.3302, 0.5594] | 20 | 90 | 204 |
| DeepSeek | punitive | news | news | all | disagree | 0.5340 [0.4529, 0.6153] | 20 | 207 | 399 |
| DeepSeek | punitive | news | news | high | all | 0.7004 [0.6184, 0.7842] | 20 | 208 | 287 |
| DeepSeek | punitive | news | news | low | all | 0.2375 [0.1345, 0.3502] | 18 | 30 | 121 |
| DeepSeek | punitive | news | news | middle | all | 0.2746 [0.1455, 0.4126] | 19 | 59 | 195 |
| Haiku | evidence | momentum | momentum | all | agree | 0.5738 [0.3810, 0.7461] | 10 | 71 | 113 |
| Haiku | evidence | momentum | momentum | all | disagree | 0.5486 [0.4238, 0.6679] | 10 | 106 | 187 |
| Haiku | evidence | momentum | momentum | high | all | 0.6795 [0.5434, 0.8069] | 10 | 102 | 149 |
| Haiku | evidence | momentum | momentum | low | all | 0.3285 [0.1386, 0.5403] | 8 | 20 | 55 |
| Haiku | evidence | momentum | momentum | middle | all | 0.5555 [0.4284, 0.6909] | 10 | 55 | 96 |
| Haiku | evidence | momentum | news | all | agree | 0.3862 [0.2881, 0.4917] | 10 | 38 | 94 |
| Haiku | evidence | momentum | news | all | disagree | 0.4102 [0.3136, 0.4989] | 10 | 81 | 198 |
| Haiku | evidence | momentum | news | high | all | 0.3748 [0.1600, 0.5967] | 10 | 33 | 68 |
| Haiku | evidence | momentum | news | low | all | 0.2475 [0.1900, 0.2964] | 10 | 33 | 135 |
| Haiku | evidence | momentum | news | middle | all | 0.5619 [0.3674, 0.7484] | 9 | 53 | 89 |
| Haiku | evidence | news | momentum | all | agree | 0.2496 [0.1250, 0.3958] | 10 | 33 | 143 |
| Haiku | evidence | news | momentum | all | disagree | 0.2527 [0.1431, 0.3776] | 10 | 40 | 157 |
| Haiku | evidence | news | momentum | high | all | 0.3453 [0.1843, 0.5324] | 9 | 19 | 53 |
| Haiku | evidence | news | momentum | low | all | 0.1897 [0.0849, 0.3143] | 10 | 21 | 141 |
| Haiku | evidence | news | momentum | middle | all | 0.3110 [0.1905, 0.4390] | 10 | 33 | 106 |
| Haiku | evidence | news | news | all | agree | 0.4365 [0.2805, 0.6116] | 10 | 33 | 89 |
| Haiku | evidence | news | news | all | disagree | 0.5018 [0.3610, 0.6173] | 10 | 106 | 205 |
| Haiku | evidence | news | news | high | all | 0.5998 [0.4619, 0.7374] | 10 | 94 | 152 |
| Haiku | evidence | news | news | low | all | 0.2722 [0.1899, 0.3647] | 8 | 13 | 50 |
| Haiku | evidence | news | news | middle | all | 0.3108 [0.1749, 0.4524] | 9 | 32 | 92 |
| Haiku | label | momentum | momentum | all | agree | 0.5914 [0.4035, 0.7505] | 10 | 74 | 112 |
| Haiku | label | momentum | momentum | all | disagree | 0.7331 [0.6229, 0.8291] | 10 | 140 | 187 |
| Haiku | label | momentum | momentum | high | all | 0.7951 [0.7194, 0.8666] | 10 | 117 | 148 |
| Haiku | label | momentum | momentum | low | all | 0.4764 [0.3361, 0.6220] | 8 | 28 | 55 |
| Haiku | label | momentum | momentum | middle | all | 0.6990 [0.6108, 0.7990] | 10 | 69 | 96 |
| Haiku | label | momentum | news | all | agree | 0.3689 [0.2854, 0.4633] | 10 | 36 | 97 |
| Haiku | label | momentum | news | all | disagree | 0.3094 [0.2316, 0.3911] | 10 | 64 | 199 |
| Haiku | label | momentum | news | high | all | 0.4033 [0.1767, 0.6433] | 10 | 25 | 68 |
| Haiku | label | momentum | news | low | all | 0.2862 [0.1729, 0.4099] | 10 | 34 | 138 |
| Haiku | label | momentum | news | middle | all | 0.5158 [0.3764, 0.6675] | 9 | 41 | 90 |
| Haiku | label | news | momentum | all | agree | 0.1853 [0.1192, 0.2435] | 10 | 25 | 142 |
| Haiku | label | news | momentum | all | disagree | 0.2318 [0.1193, 0.3426] | 10 | 38 | 156 |
| Haiku | label | news | momentum | high | all | 0.2826 [0.0758, 0.5286] | 9 | 12 | 51 |
| Haiku | label | news | momentum | low | all | 0.1547 [0.0815, 0.2329] | 10 | 21 | 141 |
| Haiku | label | news | momentum | middle | all | 0.2798 [0.1665, 0.3980] | 10 | 30 | 106 |
| Haiku | label | news | news | all | agree | 0.6361 [0.4913, 0.7820] | 10 | 55 | 90 |
| Haiku | label | news | news | all | disagree | 0.5995 [0.4736, 0.7013] | 10 | 127 | 206 |
| Haiku | label | news | news | high | all | 0.7086 [0.6022, 0.8128] | 10 | 108 | 153 |
| Haiku | label | news | news | low | all | 0.4103 [0.3223, 0.4946] | 8 | 21 | 50 |
| Haiku | label | news | news | middle | all | 0.4985 [0.2855, 0.7058] | 9 | 53 | 93 |
| Haiku | naive | momentum | momentum | all | agree | 0.5492 [0.3445, 0.7273] | 10 | 72 | 113 |
| Haiku | naive | momentum | momentum | all | disagree | 0.6733 [0.5630, 0.7771] | 10 | 121 | 187 |
| Haiku | naive | momentum | momentum | high | all | 0.8195 [0.6782, 0.9216] | 10 | 117 | 149 |
| Haiku | naive | momentum | momentum | low | all | 0.2964 [0.1282, 0.4914] | 8 | 19 | 55 |
| Haiku | naive | momentum | momentum | middle | all | 0.5584 [0.4340, 0.6696] | 10 | 57 | 96 |
| Haiku | naive | momentum | news | all | agree | 0.3866 [0.2750, 0.4869] | 10 | 39 | 97 |
| Haiku | naive | momentum | news | all | disagree | 0.3910 [0.2958, 0.4864] | 10 | 79 | 199 |
| Haiku | naive | momentum | news | high | all | 0.2990 [0.0900, 0.5164] | 10 | 29 | 68 |
| Haiku | naive | momentum | news | low | all | 0.2339 [0.1568, 0.3091] | 10 | 33 | 138 |
| Haiku | naive | momentum | news | middle | all | 0.6661 [0.4669, 0.8548] | 9 | 56 | 90 |
| Haiku | naive | news | momentum | all | agree | 0.1970 [0.1112, 0.2936] | 10 | 27 | 143 |
| Haiku | naive | news | momentum | all | disagree | 0.2156 [0.1300, 0.3016] | 10 | 34 | 157 |
| Haiku | naive | news | momentum | high | all | 0.4631 [0.2336, 0.7127] | 9 | 20 | 53 |
| Haiku | naive | news | momentum | low | all | 0.1081 [0.0363, 0.1939] | 10 | 14 | 141 |
| Haiku | naive | news | momentum | middle | all | 0.2900 [0.1823, 0.3997] | 10 | 27 | 106 |
| Haiku | naive | news | news | all | agree | 0.4078 [0.2366, 0.5941] | 10 | 32 | 90 |
| Haiku | naive | news | news | all | disagree | 0.4424 [0.3172, 0.5464] | 10 | 95 | 206 |
| Haiku | naive | news | news | high | all | 0.6042 [0.4858, 0.7392] | 10 | 95 | 153 |
| Haiku | naive | news | news | low | all | 0.1451 [0.0357, 0.2902] | 8 | 7 | 50 |
| Haiku | naive | news | news | middle | all | 0.2134 [0.1208, 0.2972] | 9 | 25 | 93 |
| Haiku | false-label | momentum | momentum | all | agree | 0.4190 [0.2710, 0.5574] | 10 | 49 | 113 |
| Haiku | false-label | momentum | momentum | all | disagree | 0.4997 [0.3870, 0.6161] | 10 | 90 | 186 |
| Haiku | false-label | momentum | momentum | high | all | 0.5396 [0.3505, 0.7128] | 10 | 87 | 149 |
| Haiku | false-label | momentum | momentum | low | all | 0.1819 [0.0857, 0.3004] | 8 | 12 | 54 |
| Haiku | false-label | momentum | momentum | middle | all | 0.3947 [0.2774, 0.5025] | 10 | 40 | 96 |
| Haiku | false-label | momentum | news | all | agree | 0.5681 [0.4383, 0.6845] | 10 | 55 | 97 |
| Haiku | false-label | momentum | news | all | disagree | 0.5820 [0.4959, 0.6712] | 10 | 117 | 199 |
| Haiku | false-label | momentum | news | high | all | 0.6057 [0.4157, 0.7757] | 10 | 47 | 68 |
| Haiku | false-label | momentum | news | low | all | 0.4518 [0.3845, 0.5191] | 10 | 65 | 138 |
| Haiku | false-label | momentum | news | middle | all | 0.6901 [0.5514, 0.8191] | 9 | 60 | 90 |
| Haiku | false-label | news | momentum | all | agree | 0.5015 [0.3593, 0.6458] | 10 | 67 | 143 |
| Haiku | false-label | news | momentum | all | disagree | 0.4079 [0.3188, 0.5017] | 10 | 61 | 157 |
| Haiku | false-label | news | momentum | high | all | 0.7073 [0.5115, 0.8918] | 9 | 35 | 53 |
| Haiku | false-label | news | momentum | low | all | 0.2412 [0.1283, 0.3637] | 10 | 33 | 141 |
| Haiku | false-label | news | momentum | middle | all | 0.5909 [0.4533, 0.7326] | 10 | 60 | 106 |
| Haiku | false-label | news | news | all | agree | 0.3484 [0.1617, 0.5614] | 10 | 28 | 90 |
| Haiku | false-label | news | news | all | disagree | 0.3572 [0.2721, 0.4374] | 10 | 75 | 206 |
| Haiku | false-label | news | news | high | all | 0.4529 [0.3756, 0.5293] | 10 | 70 | 153 |
| Haiku | false-label | news | news | low | all | 0.2920 [0.1027, 0.5357] | 8 | 12 | 50 |
| Haiku | false-label | news | news | middle | all | 0.2108 [0.1270, 0.3042] | 9 | 21 | 93 |
| Haiku | punitive | momentum | momentum | all | agree | 0.5551 [0.3496, 0.7301] | 10 | 73 | 113 |
| Haiku | punitive | momentum | momentum | all | disagree | 0.6922 [0.5968, 0.7883] | 10 | 126 | 187 |
| Haiku | punitive | momentum | momentum | high | all | 0.8325 [0.7225, 0.9166] | 10 | 121 | 149 |
| Haiku | punitive | momentum | momentum | low | all | 0.3399 [0.1393, 0.5818] | 8 | 22 | 55 |
| Haiku | punitive | momentum | momentum | middle | all | 0.5428 [0.3702, 0.6929] | 10 | 56 | 96 |
| Haiku | punitive | momentum | news | all | agree | 0.4301 [0.3067, 0.5567] | 10 | 40 | 97 |
| Haiku | punitive | momentum | news | all | disagree | 0.3364 [0.2140, 0.4600] | 10 | 72 | 199 |
| Haiku | punitive | momentum | news | high | all | 0.4207 [0.1900, 0.6514] | 10 | 36 | 68 |
| Haiku | punitive | momentum | news | low | all | 0.2023 [0.1210, 0.2850] | 10 | 27 | 138 |
| Haiku | punitive | momentum | news | middle | all | 0.4840 [0.3279, 0.6254] | 9 | 49 | 90 |
| Haiku | punitive | news | momentum | all | agree | 0.2259 [0.1038, 0.3698] | 10 | 33 | 143 |
| Haiku | punitive | news | momentum | all | disagree | 0.1953 [0.1154, 0.2701] | 10 | 33 | 157 |
| Haiku | punitive | news | momentum | high | all | 0.3816 [0.1481, 0.6270] | 9 | 19 | 53 |
| Haiku | punitive | news | momentum | low | all | 0.1070 [0.0353, 0.1938] | 10 | 16 | 141 |
| Haiku | punitive | news | momentum | middle | all | 0.3250 [0.2126, 0.4499] | 10 | 31 | 106 |
| Haiku | punitive | news | news | all | agree | 0.4716 [0.3304, 0.6314] | 10 | 38 | 90 |
| Haiku | punitive | news | news | all | disagree | 0.5013 [0.3828, 0.5991] | 10 | 106 | 206 |
| Haiku | punitive | news | news | high | all | 0.6478 [0.5408, 0.7607] | 10 | 102 | 153 |
| Haiku | punitive | news | news | low | all | 0.3400 [0.2204, 0.4583] | 8 | 16 | 50 |
| Haiku | punitive | news | news | middle | all | 0.2204 [0.1245, 0.3097] | 9 | 26 | 93 |
| Luna | evidence | momentum | momentum | all | agree | 0.3991 [0.2414, 0.5454] | 10 | 47 | 113 |
| Luna | evidence | momentum | momentum | all | disagree | 0.4915 [0.4197, 0.5654] | 10 | 95 | 187 |
| Luna | evidence | momentum | momentum | high | all | 0.5469 [0.4236, 0.6735] | 10 | 84 | 149 |
| Luna | evidence | momentum | momentum | low | all | 0.2797 [0.1526, 0.3856] | 8 | 17 | 55 |
| Luna | evidence | momentum | momentum | middle | all | 0.4475 [0.3373, 0.5536] | 10 | 41 | 96 |
| Luna | evidence | momentum | news | all | agree | 0.2905 [0.2006, 0.3771] | 10 | 32 | 96 |
| Luna | evidence | momentum | news | all | disagree | 0.3129 [0.2395, 0.3805] | 10 | 62 | 199 |
| Luna | evidence | momentum | news | high | all | 0.3555 [0.1850, 0.5214] | 10 | 28 | 68 |
| Luna | evidence | momentum | news | low | all | 0.2200 [0.1573, 0.2978] | 10 | 29 | 138 |
| Luna | evidence | momentum | news | middle | all | 0.3551 [0.1912, 0.5209] | 9 | 37 | 89 |
| Luna | evidence | news | momentum | all | agree | 0.2777 [0.1860, 0.3726] | 10 | 37 | 142 |
| Luna | evidence | news | momentum | all | disagree | 0.3777 [0.2490, 0.5054] | 10 | 62 | 157 |
| Luna | evidence | news | momentum | high | all | 0.5345 [0.3193, 0.7520] | 9 | 31 | 53 |
| Luna | evidence | news | momentum | low | all | 0.2147 [0.1298, 0.2992] | 10 | 28 | 140 |
| Luna | evidence | news | momentum | middle | all | 0.3262 [0.1813, 0.4847] | 10 | 40 | 106 |
| Luna | evidence | news | news | all | agree | 0.5180 [0.3416, 0.6924] | 10 | 43 | 89 |
| Luna | evidence | news | news | all | disagree | 0.5849 [0.4326, 0.7133] | 10 | 124 | 205 |
| Luna | evidence | news | news | high | all | 0.7067 [0.5700, 0.8405] | 10 | 110 | 152 |
| Luna | evidence | news | news | low | all | 0.3540 [0.2482, 0.4598] | 8 | 17 | 50 |
| Luna | evidence | news | news | middle | all | 0.5226 [0.3638, 0.7060] | 9 | 40 | 92 |
| Luna | label | momentum | momentum | all | agree | 0.7709 [0.6685, 0.8560] | 10 | 84 | 113 |
| Luna | label | momentum | momentum | all | disagree | 0.7593 [0.6769, 0.8457] | 10 | 148 | 187 |
| Luna | label | momentum | momentum | high | all | 0.8754 [0.8074, 0.9377] | 10 | 129 | 149 |
| Luna | label | momentum | momentum | low | all | 0.5298 [0.3068, 0.7463] | 8 | 30 | 55 |
| Luna | label | momentum | momentum | middle | all | 0.7298 [0.6044, 0.8492] | 10 | 73 | 96 |
| Luna | label | momentum | news | all | agree | 0.3066 [0.2053, 0.4058] | 10 | 33 | 97 |
| Luna | label | momentum | news | all | disagree | 0.3459 [0.2656, 0.4121] | 10 | 70 | 197 |
| Luna | label | momentum | news | high | all | 0.4445 [0.2433, 0.6450] | 10 | 26 | 68 |
| Luna | label | momentum | news | low | all | 0.2405 [0.1506, 0.3408] | 10 | 33 | 136 |
| Luna | label | momentum | news | middle | all | 0.5165 [0.3601, 0.6801] | 9 | 44 | 90 |
| Luna | label | news | momentum | all | agree | 0.1700 [0.1179, 0.2260] | 10 | 22 | 143 |
| Luna | label | news | momentum | all | disagree | 0.2225 [0.1361, 0.3090] | 10 | 38 | 157 |
| Luna | label | news | momentum | high | all | 0.2960 [0.1198, 0.5143] | 9 | 12 | 53 |
| Luna | label | news | momentum | low | all | 0.1888 [0.1192, 0.2626] | 10 | 22 | 141 |
| Luna | label | news | momentum | middle | all | 0.2509 [0.1700, 0.3400] | 10 | 26 | 106 |
| Luna | label | news | news | all | agree | 0.5856 [0.4478, 0.7191] | 10 | 54 | 89 |
| Luna | label | news | news | all | disagree | 0.5833 [0.4652, 0.6769] | 10 | 123 | 205 |
| Luna | label | news | news | high | all | 0.7315 [0.6530, 0.8087] | 10 | 111 | 152 |
| Luna | label | news | news | low | all | 0.2259 [0.1107, 0.3482] | 8 | 12 | 49 |
| Luna | label | news | news | middle | all | 0.4650 [0.2720, 0.6323] | 9 | 54 | 93 |
| Luna | naive | momentum | momentum | all | agree | 0.5388 [0.3856, 0.6635] | 10 | 64 | 113 |
| Luna | naive | momentum | momentum | all | disagree | 0.6366 [0.5505, 0.7251] | 10 | 118 | 187 |
| Luna | naive | momentum | momentum | high | all | 0.7662 [0.6714, 0.8523] | 10 | 114 | 149 |
| Luna | naive | momentum | momentum | low | all | 0.3119 [0.1807, 0.4512] | 8 | 19 | 55 |
| Luna | naive | momentum | momentum | middle | all | 0.4789 [0.3214, 0.6226] | 10 | 49 | 96 |
| Luna | naive | momentum | news | all | agree | 0.3590 [0.2383, 0.4800] | 10 | 32 | 97 |
| Luna | naive | momentum | news | all | disagree | 0.3443 [0.2303, 0.4609] | 10 | 70 | 198 |
| Luna | naive | momentum | news | high | all | 0.4036 [0.1750, 0.6186] | 10 | 36 | 68 |
| Luna | naive | momentum | news | low | all | 0.1953 [0.1277, 0.2594] | 10 | 26 | 137 |
| Luna | naive | momentum | news | middle | all | 0.4838 [0.2797, 0.6926] | 9 | 40 | 90 |
| Luna | naive | news | momentum | all | agree | 0.2782 [0.1564, 0.4101] | 10 | 38 | 142 |
| Luna | naive | news | momentum | all | disagree | 0.2975 [0.1784, 0.4120] | 10 | 49 | 157 |
| Luna | naive | news | momentum | high | all | 0.7039 [0.4430, 0.9365] | 9 | 34 | 52 |
| Luna | naive | news | momentum | low | all | 0.1331 [0.0592, 0.2174] | 10 | 17 | 141 |
| Luna | naive | news | momentum | middle | all | 0.3336 [0.2040, 0.4684] | 10 | 36 | 106 |
| Luna | naive | news | news | all | agree | 0.5836 [0.4061, 0.7482] | 10 | 53 | 90 |
| Luna | naive | news | news | all | disagree | 0.6123 [0.5036, 0.7064] | 10 | 129 | 206 |
| Luna | naive | news | news | high | all | 0.8435 [0.7492, 0.9257] | 10 | 130 | 153 |
| Luna | naive | news | news | low | all | 0.2546 [0.1504, 0.3586] | 8 | 13 | 50 |
| Luna | naive | news | news | middle | all | 0.3437 [0.2189, 0.4555] | 9 | 39 | 93 |
| Luna | false-label | momentum | momentum | all | agree | 0.3511 [0.2154, 0.4900] | 10 | 44 | 113 |
| Luna | false-label | momentum | momentum | all | disagree | 0.5122 [0.4194, 0.6053] | 10 | 94 | 187 |
| Luna | false-label | momentum | momentum | high | all | 0.5685 [0.4380, 0.6866] | 10 | 87 | 149 |
| Luna | false-label | momentum | momentum | low | all | 0.1527 [0.0519, 0.2679] | 8 | 10 | 55 |
| Luna | false-label | momentum | momentum | middle | all | 0.4059 [0.3302, 0.4768] | 10 | 41 | 96 |
| Luna | false-label | momentum | news | all | agree | 0.4714 [0.3817, 0.5508] | 10 | 45 | 97 |
| Luna | false-label | momentum | news | all | disagree | 0.5715 [0.4739, 0.6753] | 10 | 113 | 199 |
| Luna | false-label | momentum | news | high | all | 0.6631 [0.4583, 0.8433] | 10 | 53 | 68 |
| Luna | false-label | momentum | news | low | all | 0.3713 [0.2913, 0.4434] | 10 | 53 | 138 |
| Luna | false-label | momentum | news | middle | all | 0.6116 [0.4473, 0.7674] | 9 | 52 | 90 |
| Luna | false-label | news | momentum | all | agree | 0.4017 [0.3184, 0.4950] | 10 | 57 | 143 |
| Luna | false-label | news | momentum | all | disagree | 0.3822 [0.3013, 0.4620] | 10 | 57 | 157 |
| Luna | false-label | news | momentum | high | all | 0.6686 [0.4226, 0.8889] | 9 | 33 | 53 |
| Luna | false-label | news | momentum | low | all | 0.1875 [0.1399, 0.2345] | 10 | 27 | 141 |
| Luna | false-label | news | momentum | middle | all | 0.5888 [0.4321, 0.7480] | 10 | 54 | 106 |
| Luna | false-label | news | news | all | agree | 0.4294 [0.3111, 0.5439] | 10 | 39 | 90 |
| Luna | false-label | news | news | all | disagree | 0.3859 [0.3027, 0.4739] | 10 | 80 | 206 |
| Luna | false-label | news | news | high | all | 0.5356 [0.4669, 0.5924] | 10 | 82 | 153 |
| Luna | false-label | news | news | low | all | 0.1804 [0.0625, 0.3179] | 8 | 8 | 50 |
| Luna | false-label | news | news | middle | all | 0.2923 [0.1649, 0.4206] | 9 | 29 | 93 |
| Luna | punitive | momentum | momentum | all | agree | 0.4470 [0.2784, 0.5925] | 10 | 60 | 113 |
| Luna | punitive | momentum | momentum | all | disagree | 0.6511 [0.5792, 0.7329] | 10 | 120 | 187 |
| Luna | punitive | momentum | momentum | high | all | 0.7509 [0.6521, 0.8455] | 10 | 114 | 149 |
| Luna | punitive | momentum | momentum | low | all | 0.3096 [0.1331, 0.4807] | 8 | 20 | 55 |
| Luna | punitive | momentum | momentum | middle | all | 0.5292 [0.3903, 0.6810] | 10 | 46 | 96 |
| Luna | punitive | momentum | news | all | agree | 0.3961 [0.2505, 0.5350] | 10 | 34 | 97 |
| Luna | punitive | momentum | news | all | disagree | 0.3651 [0.2493, 0.4722] | 10 | 74 | 199 |
| Luna | punitive | momentum | news | high | all | 0.4786 [0.2729, 0.6814] | 10 | 39 | 68 |
| Luna | punitive | momentum | news | low | all | 0.2474 [0.1526, 0.3490] | 10 | 33 | 138 |
| Luna | punitive | momentum | news | middle | all | 0.4445 [0.2189, 0.6880] | 9 | 36 | 90 |
| Luna | punitive | news | momentum | all | agree | 0.2627 [0.1635, 0.3627] | 10 | 38 | 143 |
| Luna | punitive | news | momentum | all | disagree | 0.3060 [0.1794, 0.4371] | 10 | 49 | 157 |
| Luna | punitive | news | momentum | high | all | 0.6441 [0.3831, 0.8875] | 9 | 30 | 53 |
| Luna | punitive | news | momentum | low | all | 0.1943 [0.0926, 0.3115] | 10 | 26 | 141 |
| Luna | punitive | news | momentum | middle | all | 0.2994 [0.1893, 0.4313] | 10 | 31 | 106 |
| Luna | punitive | news | news | all | agree | 0.5519 [0.3614, 0.7318] | 10 | 51 | 90 |
| Luna | punitive | news | news | all | disagree | 0.5903 [0.4750, 0.6993] | 10 | 124 | 206 |
| Luna | punitive | news | news | high | all | 0.8244 [0.7538, 0.8969] | 10 | 126 | 153 |
| Luna | punitive | news | news | low | all | 0.2266 [0.1086, 0.3665] | 8 | 12 | 50 |
| Luna | punitive | news | news | middle | all | 0.2921 [0.1270, 0.4578] | 9 | 37 | 93 |

| Model | Package | Feature | Regime | Proxy agrees before [CI] | Disagrees before [CI] | Zero signs | Re-asks |
|---|---|---|---|---|---|---|---|
| DeepSeek | evidence | momentum | momentum | 0.6511 [0.5816, 0.7198] | 0.3450 [0.2747, 0.4160] | 2 | 604 |
| DeepSeek | evidence | momentum | news | 0.6134 [0.5232, 0.6907] | 0.3866 [0.3093, 0.4768] | 0 | 603 |
| DeepSeek | evidence | news | momentum | 0.6002 [0.5290, 0.6645] | 0.3930 [0.3281, 0.4654] | 3 | 604 |
| DeepSeek | evidence | news | news | 0.6637 [0.5921, 0.7347] | 0.3363 [0.2653, 0.4079] | 0 | 603 |
| DeepSeek | label | momentum | momentum | 0.6511 [0.5816, 0.7198] | 0.3450 [0.2747, 0.4160] | 2 | 604 |
| DeepSeek | label | momentum | news | 0.6134 [0.5232, 0.6907] | 0.3866 [0.3093, 0.4768] | 0 | 603 |
| DeepSeek | label | news | momentum | 0.6002 [0.5290, 0.6645] | 0.3930 [0.3281, 0.4654] | 3 | 604 |
| DeepSeek | label | news | news | 0.6637 [0.5921, 0.7347] | 0.3363 [0.2653, 0.4079] | 0 | 603 |
| DeepSeek | naive | momentum | momentum | 0.6511 [0.5816, 0.7198] | 0.3450 [0.2747, 0.4160] | 2 | 604 |
| DeepSeek | naive | momentum | news | 0.6134 [0.5232, 0.6907] | 0.3866 [0.3093, 0.4768] | 0 | 603 |
| DeepSeek | naive | news | momentum | 0.6002 [0.5290, 0.6645] | 0.3930 [0.3281, 0.4654] | 3 | 604 |
| DeepSeek | naive | news | news | 0.6637 [0.5921, 0.7347] | 0.3363 [0.2653, 0.4079] | 0 | 603 |
| DeepSeek | false-label | momentum | momentum | 0.6511 [0.5816, 0.7198] | 0.3450 [0.2747, 0.4160] | 2 | 604 |
| DeepSeek | false-label | momentum | news | 0.6134 [0.5232, 0.6907] | 0.3866 [0.3093, 0.4768] | 0 | 603 |
| DeepSeek | false-label | news | momentum | 0.6002 [0.5290, 0.6645] | 0.3930 [0.3281, 0.4654] | 3 | 604 |
| DeepSeek | false-label | news | news | 0.6637 [0.5921, 0.7347] | 0.3363 [0.2653, 0.4079] | 0 | 603 |
| DeepSeek | punitive | momentum | momentum | 0.6511 [0.5816, 0.7198] | 0.3450 [0.2747, 0.4160] | 2 | 604 |
| DeepSeek | punitive | momentum | news | 0.6134 [0.5232, 0.6907] | 0.3866 [0.3093, 0.4768] | 0 | 603 |
| DeepSeek | punitive | news | momentum | 0.6002 [0.5290, 0.6645] | 0.3930 [0.3281, 0.4654] | 3 | 604 |
| DeepSeek | punitive | news | news | 0.6637 [0.5921, 0.7347] | 0.3363 [0.2653, 0.4079] | 0 | 603 |
| Haiku | evidence | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Haiku | evidence | momentum | news | 0.6775 [0.5905, 0.7605] | 0.3225 [0.2395, 0.4095] | 0 | 292 |
| Haiku | evidence | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Haiku | evidence | news | news | 0.7050 [0.6131, 0.7899] | 0.2950 [0.2101, 0.3869] | 0 | 294 |
| Haiku | label | momentum | momentum | 0.6220 [0.5223, 0.7337] | 0.3780 [0.2663, 0.4777] | 0 | 299 |
| Haiku | label | momentum | news | 0.6705 [0.5901, 0.7480] | 0.3295 [0.2520, 0.4099] | 0 | 296 |
| Haiku | label | news | momentum | 0.5287 [0.4267, 0.6155] | 0.4713 [0.3845, 0.5733] | 0 | 298 |
| Haiku | label | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |
| Haiku | naive | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Haiku | naive | momentum | news | 0.6705 [0.5901, 0.7480] | 0.3295 [0.2520, 0.4099] | 0 | 296 |
| Haiku | naive | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Haiku | naive | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |
| Haiku | false-label | momentum | momentum | 0.6184 [0.5178, 0.7319] | 0.3816 [0.2681, 0.4822] | 0 | 299 |
| Haiku | false-label | momentum | news | 0.6705 [0.5901, 0.7480] | 0.3295 [0.2520, 0.4099] | 0 | 296 |
| Haiku | false-label | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Haiku | false-label | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |
| Haiku | punitive | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Haiku | punitive | momentum | news | 0.6705 [0.5901, 0.7480] | 0.3295 [0.2520, 0.4099] | 0 | 296 |
| Haiku | punitive | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Haiku | punitive | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |
| Luna | evidence | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Luna | evidence | momentum | news | 0.6726 [0.5941, 0.7488] | 0.3274 [0.2512, 0.4059] | 0 | 295 |
| Luna | evidence | news | momentum | 0.5302 [0.4278, 0.6175] | 0.4698 [0.3825, 0.5722] | 0 | 299 |
| Luna | evidence | news | news | 0.7050 [0.6157, 0.7855] | 0.2950 [0.2145, 0.3843] | 0 | 294 |
| Luna | label | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Luna | label | momentum | news | 0.6680 [0.5878, 0.7459] | 0.3320 [0.2541, 0.4122] | 0 | 294 |
| Luna | label | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Luna | label | news | news | 0.7041 [0.6145, 0.7855] | 0.2959 [0.2145, 0.3855] | 0 | 294 |
| Luna | naive | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Luna | naive | momentum | news | 0.6687 [0.5871, 0.7475] | 0.3313 [0.2525, 0.4129] | 0 | 295 |
| Luna | naive | news | momentum | 0.5302 [0.4278, 0.6175] | 0.4698 [0.3825, 0.5722] | 0 | 299 |
| Luna | naive | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |
| Luna | false-label | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Luna | false-label | momentum | news | 0.6705 [0.5901, 0.7480] | 0.3295 [0.2520, 0.4099] | 0 | 296 |
| Luna | false-label | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Luna | false-label | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |
| Luna | punitive | momentum | momentum | 0.6203 [0.5205, 0.7328] | 0.3797 [0.2672, 0.4795] | 0 | 300 |
| Luna | punitive | momentum | news | 0.6705 [0.5901, 0.7480] | 0.3295 [0.2520, 0.4099] | 0 | 296 |
| Luna | punitive | news | momentum | 0.5289 [0.4264, 0.6169] | 0.4711 [0.3831, 0.5736] | 0 | 300 |
| Luna | punitive | news | news | 0.7033 [0.6135, 0.7851] | 0.2967 [0.2149, 0.3865] | 0 | 296 |

## G. Minimum detectable effects and required paired seeds

Exact two-sided noncentral-t power at 80%, using observed seed-difference SD. Alpha .0125 is the most stringent Holm threshold, not the full step-down procedure's achieved power. Required n uses the magnitude of each DeepSeek point estimate and each model's own observed SD; it is a planning calculation, not evidence of a common true effect.

| Model | Contrast | Actual n | Observed SD | Alpha | MDE dz | MDE raw | DeepSeek target Δ | Required n |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | P1 | 20 | 0.066673 | 0.05 | 0.6604 | 0.044034 | -0.013740 | 187 |
| DeepSeek | P1 | 20 | 0.066673 | 0.0125 | 0.8146 | 0.054311 | -0.013740 | 266 |
| DeepSeek | P2 | 20 | 0.087048 | 0.05 | 0.6604 | 0.057490 | -0.062365 | 18 |
| DeepSeek | P2 | 20 | 0.087048 | 0.0125 | 0.8146 | 0.070908 | -0.062365 | 25 |
| DeepSeek | P3 | 20 | 0.111912 | 0.05 | 0.6604 | 0.073911 | -0.038920 | 67 |
| DeepSeek | P3 | 20 | 0.111912 | 0.0125 | 0.8146 | 0.091162 | -0.038920 | 96 |
| DeepSeek | P4 | 20 | 0.101172 | 0.05 | 0.6604 | 0.066818 | -0.134126 | 7 |
| DeepSeek | P4 | 20 | 0.101172 | 0.0125 | 0.8146 | 0.082414 | -0.134126 | 10 |
| Haiku | P1 | 10 | 0.085678 | 0.05 | 0.9960 | 0.085335 | -0.013740 | 308 |
| Haiku | P1 | 10 | 0.085678 | 0.0125 | 1.2843 | 0.110036 | -0.013740 | 437 |
| Haiku | P2 | 10 | 0.096266 | 0.05 | 0.9960 | 0.095881 | -0.062365 | 21 |
| Haiku | P2 | 10 | 0.096266 | 0.0125 | 1.2843 | 0.123634 | -0.062365 | 30 |
| Haiku | P3 | 10 | 0.091814 | 0.05 | 0.9960 | 0.091446 | -0.038920 | 46 |
| Haiku | P3 | 10 | 0.091814 | 0.0125 | 1.2843 | 0.117916 | -0.038920 | 66 |
| Haiku | P4 | 10 | 0.086697 | 0.05 | 0.9960 | 0.086350 | -0.134126 | 6 |
| Haiku | P4 | 10 | 0.086697 | 0.0125 | 1.2843 | 0.111344 | -0.134126 | 8 |
| Luna | P1 | 10 | 0.061530 | 0.05 | 0.9960 | 0.061284 | -0.013740 | 160 |
| Luna | P1 | 10 | 0.061530 | 0.0125 | 1.2843 | 0.079023 | -0.013740 | 227 |
| Luna | P2 | 10 | 0.092451 | 0.05 | 0.9960 | 0.092082 | -0.062365 | 20 |
| Luna | P2 | 10 | 0.092451 | 0.0125 | 1.2843 | 0.118735 | -0.062365 | 28 |
| Luna | P3 | 10 | 0.093292 | 0.05 | 0.9960 | 0.092919 | -0.038920 | 48 |
| Luna | P3 | 10 | 0.093292 | 0.0125 | 1.2843 | 0.119815 | -0.038920 | 68 |
| Luna | P4 | 10 | 0.075958 | 0.05 | 0.9960 | 0.075655 | -0.134126 | 5 |
| Luna | P4 | 10 | 0.075958 | 0.0125 | 1.2843 | 0.097553 | -0.134126 | 7 |

## H. DGP checks and fine timing

src/market.py:31 defines unbounded 1+0.3 Normal volume and :38 rounds without clipping; negative values are possible. The probability after rounding is P(V<-.0005), ignoring measure-zero ties.

src/market.py:45-59 defines fundamental .02*x_driver, requested imbalance sum(signed sizes)/(n_agents*5), impact .03*I and independent Normal(0,.005) shock; price floor follows return calculation.

src/v2/simulate.py:196-197 builds the prompt; :199-234 obtains decisions and probes; :246-248 steps the market with requested orders; :255-264 audits citations, marks wealth at POST-step price, then applies 10% haircut to cash and position; :265-267 constructs next feedback; :270-279 settles the selected order subject to the reduced portfolio. The current action cannot react to its later fine; the next prompt at :196-197 sees persisted feedback and updated portfolio. Haircuts do not enter order imbalance.

Primary-window component scales below pool one market tick per package. Variance ratios omit covariance; allocated shares include it and sum to one. All-tick and per-package decompositions are in JSON.

| Model | Market ticks | Component | SD | SD(return) | Var(component)/Var(r) | Cov(component,r)/Var(r) |
|---|---|---|---|---|---|---|
| DeepSeek | 2000 | fundamental | 0.02385676 | 0.04936756 | 0.233528 | 0.428259 |
| DeepSeek | 2000 | impact | 0.02949494 | 0.04936756 | 0.356953 | 0.554446 |
| DeepSeek | 2000 | eta | 0.00494298 | 0.04936756 | 0.010025 | 0.017295 |
| Haiku | 1000 | fundamental | 0.02523935 | 0.04178014 | 0.364936 | 0.560870 |
| Haiku | 1000 | impact | 0.01966446 | 0.04178014 | 0.221526 | 0.417733 |
| Haiku | 1000 | eta | 0.00504626 | 0.04178014 | 0.014588 | 0.021397 |
| Luna | 1000 | fundamental | 0.02523935 | 0.04397120 | 0.329473 | 0.536693 |
| Luna | 1000 | impact | 0.02130083 | 0.04397120 | 0.234669 | 0.443063 |
| Luna | 1000 | eta | 0.00504626 | 0.04397120 | 0.013171 | 0.020245 |

| Model | Unique negative-volume ticks | Unique seed-ticks | Frequency | Minimum V | Theoretical P after rounding |
|---|---|---|---|---|---|
| DeepSeek | 0 | 800 | 0.0000000 | 0.204 | 0.00042650 |
| Haiku | 0 | 400 | 0.0000000 | 0.204 | 0.00042650 |
| Luna | 0 | 400 | 0.0000000 | 0.204 | 0.00042650 |

## I. False-label P4 decomposition and citation ceilings

Every row keeps the opposite-current-driver P4 selector; communicated label truth uses the seed-only schedule. All three components in a row have identical eligible decision support.

| Model | Regime | Label currently | Δ citation [CI] | p | Δ sensitivity [CI] | p | CSD [CI] | p | Seeds | Common n |
|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek | pooled | pooled | 0.1192 [0.0907, 0.1501] | 3.15326e-07 | 0.2533 [0.2170, 0.2893] | 5.63668e-11 | -0.1341 [-0.1772, -0.0916] | 0.000010 | 20 | 1207 |
| DeepSeek | pooled | true | -0.0134 [-0.0540, 0.0301] | 0.548617 | -0.3117 [-0.3648, -0.2600] | 6.84808e-10 | 0.2983 [0.2295, 0.3630] | 6.72509e-08 | 20 | 370 |
| DeepSeek | pooled | false | 0.1751 [0.1438, 0.2074] | 2.78184e-09 | 0.5034 [0.4626, 0.5476] | 3.34512e-15 | -0.3284 [-0.3928, -0.2687] | 4.3038e-09 | 20 | 837 |
| DeepSeek | news | pooled | 0.0352 [0.0121, 0.0645] | 0.020655 | 0.1515 [0.0996, 0.2018] | 0.000019 | -0.1162 [-0.1771, -0.0545] | 0.001628 | 20 | 603 |
| DeepSeek | news | true | 0.0283 [0.0003, 0.0638] | 0.112006 | -0.4540 [-0.5495, -0.3607] | 2.47376e-08 | 0.4824 [0.3926, 0.5721] | 3.42107e-09 | 20 | 197 |
| DeepSeek | news | false | 0.0399 [0.0140, 0.0712] | 0.016217 | 0.4438 [0.3871, 0.5053] | 1.19877e-11 | -0.4039 [-0.4666, -0.3455] | 9.0067e-11 | 20 | 406 |
| DeepSeek | momentum | pooled | 0.2033 [0.1471, 0.2660] | 0.000003 | 0.3535 [0.2917, 0.4175] | 2.0037e-09 | -0.1503 [-0.2189, -0.0846] | 0.000439 | 20 | 604 |
| DeepSeek | momentum | true | -0.0814 [-0.1655, 0.0078] | 0.083958 | -0.1748 [-0.2414, -0.1099] | 0.000073 | 0.0934 [-0.0071, 0.1895] | 0.090417 | 20 | 173 |
| DeepSeek | momentum | false | 0.3146 [0.2466, 0.3832] | 3.94375e-08 | 0.5634 [0.4978, 0.6299] | 1.63267e-12 | -0.2487 [-0.3423, -0.1572] | 0.000060 | 20 | 431 |
| Haiku | pooled | pooled | 0.1466 [0.0843, 0.2096] | 0.001910 | 0.2038 [0.1630, 0.2377] | 0.000004 | -0.0572 [-0.1045, -0.0039] | 0.066643 | 10 | 595 |
| Haiku | pooled | true | -0.1224 [-0.2188, -0.0227] | 0.045300 | -0.1848 [-0.2969, -0.0966] | 0.007506 | 0.0624 [-0.0416, 0.1712] | 0.304195 | 10 | 177 |
| Haiku | pooled | false | 0.2666 [0.2050, 0.3267] | 0.000018 | 0.3606 [0.3015, 0.4185] | 0.000001 | -0.0940 [-0.1600, -0.0265] | 0.028993 | 10 | 418 |
| Haiku | news | pooled | 0.1458 [0.0632, 0.2261] | 0.008712 | 0.1807 [0.1328, 0.2292] | 0.000070 | -0.0350 [-0.0976, 0.0312] | 0.337644 | 10 | 296 |
| Haiku | news | true | -0.0861 [-0.1825, 0.0114] | 0.136616 | -0.2428 [-0.3706, -0.1291] | 0.004688 | 0.1567 [0.0286, 0.2799] | 0.044456 | 10 | 90 |
| Haiku | news | false | 0.2602 [0.1585, 0.3610] | 0.001076 | 0.3672 [0.2984, 0.4327] | 0.000003 | -0.1070 [-0.1772, -0.0228] | 0.030252 | 10 | 206 |
| Haiku | momentum | pooled | 0.1478 [0.0749, 0.2274] | 0.005714 | 0.2244 [0.1631, 0.2802] | 0.000060 | -0.0766 [-0.1550, -0.0023] | 0.099844 | 10 | 299 |
| Haiku | momentum | true | -0.1658 [-0.2858, -0.0464] | 0.029610 | -0.1260 [-0.2336, -0.0214] | 0.052763 | -0.0399 [-0.1700, 0.0932] | 0.588380 | 10 | 87 |
| Haiku | momentum | false | 0.2888 [0.2327, 0.3488] | 0.000007 | 0.3611 [0.2812, 0.4441] | 0.000017 | -0.0723 [-0.1815, 0.0349] | 0.252370 | 10 | 212 |
| Luna | pooled | pooled | 0.1792 [0.1126, 0.2399] | 0.000538 | 0.1388 [0.1014, 0.1737] | 0.000057 | 0.0404 [-0.0069, 0.0821] | 0.127198 | 10 | 594 |
| Luna | pooled | true | -0.0780 [-0.1401, -0.0157] | 0.049048 | -0.1728 [-0.2231, -0.1238] | 0.000118 | 0.0948 [0.0322, 0.1660] | 0.029071 | 10 | 176 |
| Luna | pooled | false | 0.2933 [0.2280, 0.3516] | 0.000011 | 0.2782 [0.2489, 0.3082] | 3.32173e-08 | 0.0151 [-0.0519, 0.0794] | 0.678996 | 10 | 418 |
| Luna | news | pooled | 0.1138 [0.0610, 0.1677] | 0.003306 | 0.1903 [0.1473, 0.2375] | 0.000028 | -0.0765 [-0.1259, -0.0249] | 0.020361 | 10 | 295 |
| Luna | news | true | -0.0712 [-0.1665, 0.0537] | 0.263987 | -0.2072 [-0.3168, -0.1206] | 0.003910 | 0.1360 [0.0217, 0.2710] | 0.070023 | 10 | 89 |
| Luna | news | false | 0.1964 [0.1564, 0.2366] | 0.000008 | 0.3704 [0.3041, 0.4439] | 0.000004 | -0.1740 [-0.2396, -0.1118] | 0.000670 | 10 | 206 |
| Luna | momentum | pooled | 0.2475 [0.1283, 0.3727] | 0.004297 | 0.0886 [0.0121, 0.1551] | 0.046713 | 0.1589 [0.0762, 0.2519] | 0.008233 | 10 | 299 |
| Luna | momentum | true | -0.0964 [-0.2014, 0.0000] | 0.092017 | -0.1515 [-0.2543, -0.0509] | 0.021044 | 0.0551 [-0.0575, 0.1771] | 0.404602 | 10 | 87 |
| Luna | momentum | false | 0.4034 [0.2821, 0.5168] | 0.000134 | 0.1892 [0.1435, 0.2374] | 0.000036 | 0.2142 [0.0987, 0.3292] | 0.007428 | 10 | 212 |

| Model | CSD | Naive citation [CI] | Max citation increase [CI] | Max citation decrease [CI] | Observed Δ citation [CI] | Observed Δ sensitivity [CI] |
|---|---|---|---|---|---|---|
| DeepSeek | P3 | 0.8910 [0.8635, 0.9180] | 0.1090 [0.0820, 0.1365] | -0.8910 [-0.9180, -0.8635] | 0.0655 [0.0437, 0.0863] | 0.1044 [0.0671, 0.1424] |
| DeepSeek | P4 | 0.8142 [0.7826, 0.8436] | 0.1858 [0.1564, 0.2174] | -0.8142 [-0.8436, -0.7826] | 0.1192 [0.0907, 0.1501] | 0.2533 [0.2170, 0.2893] |
| Haiku | P3 | 0.7293 [0.6756, 0.7864] | 0.2707 [0.2136, 0.3244] | -0.7293 [-0.7864, -0.6756] | 0.0962 [0.0503, 0.1459] | 0.1316 [0.0685, 0.1892] |
| Haiku | P4 | 0.5302 [0.4904, 0.5708] | 0.4698 [0.4292, 0.5096] | -0.5302 [-0.5708, -0.4904] | 0.1466 [0.0843, 0.2096] | 0.2038 [0.1630, 0.2377] |
| Luna | P3 | 0.8480 [0.8149, 0.8820] | 0.1520 [0.1180, 0.1851] | -0.8480 [-0.8820, -0.8149] | 0.0455 [0.0130, 0.0797] | 0.0788 [0.0347, 0.1215] |
| Luna | P4 | 0.6320 [0.5792, 0.6955] | 0.3680 [0.3045, 0.4208] | -0.6320 [-0.6955, -0.5792] | 0.1792 [0.1126, 0.2399] | 0.1388 [0.1014, 0.1737] |

## Facts for the manuscript (all new facts are post hoc)

- DeepSeek: momentum P2 -0.0493 [-0.0993, -0.0045], Holm p=0.184240; momentum P4 -0.1503 [-0.2189, -0.0846], Holm p=0.001755. News discrimination primary -0.0750 [-0.1645, 0.0187].
- DeepSeek: exclusive P4 CSD -0.2753 [-0.3158, -0.2363], raw p=4.26943e-11, 20 seeds/1207 paired decisions; this changes the estimand and does not replace P4.
- DeepSeek: at_most_one P4 CSD -0.0482 [-0.0904, -0.0148], raw p=0.031872, 20 seeds/115 paired decisions; this changes the estimand and does not replace P4.
- DeepSeek false-label currently true: opposite-current-driver citation change -0.0134 [-0.0540, 0.0301], sensitivity change -0.3117 [-0.3648, -0.2600], CSD 0.2983 [0.2295, 0.3630].
- DeepSeek false-label currently false: opposite-current-driver citation change 0.1751 [0.1438, 0.2074], sensitivity change 0.5034 [0.4626, 0.5476], CSD -0.3284 [-0.3928, -0.2687].
- DeepSeek naive citation headroom: P3 0.109016, P4 0.185798 on the respective complete-probe support.
- DeepSeek delivered unique tables: realized: true mean |r|=0.774124, opposite=0.600929, true largest among six=0.506715; without_impact: true mean |r|=0.854030, opposite=0.516106, true largest among six=0.739214; fundamental: true mean |r|=0.874756, opposite=0.522690, true largest among six=0.779677. These are fixed-path summaries.
- DeepSeek P4 at alpha .0125: 80%-power raw MDE 0.082414; detecting the DeepSeek point estimate with this SD requires 10 paired seeds.
- DeepSeek adoption of communicated labels: label 0.9971 [0.9933, 1.0000], false-label 0.9963 [0.9925, 0.9992]; matched naive rates 0.865417 and 0.852917, respectively.
- DeepSeek naive news in its own regime: low-|x| flip rate 0.1252 [0.0444, 0.2199] (n=121), high-|x| 0.6305 [0.5524, 0.7088] (n=287); after-flip proxy agreement 0.370710 vs disagreement 0.461798. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.
- DeepSeek naive momentum in its own regime: low-|x| flip rate 0.4990 [0.3315, 0.6625] (n=129), high-|x| 0.9641 [0.9173, 1.0000] (n=280); after-flip proxy agreement 0.651910 vs disagreement 0.832915. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.
- Haiku: momentum P2 -0.0572 [-0.1577, 0.0405], Holm p=0.940167; momentum P4 -0.0766 [-0.1550, -0.0023], Holm p=0.399375. News discrimination primary 0.0330 [-0.0770, 0.1586].
- Haiku: exclusive P4 CSD -0.0450 [-0.0905, 0.0096], raw p=0.129010, 10 seeds/595 paired decisions; this changes the estimand and does not replace P4.
- Haiku: at_most_one P4 CSD -0.0262 [-0.0931, 0.0457], raw p=0.504198, 10 seeds/352 paired decisions; this changes the estimand and does not replace P4.
- Haiku false-label currently true: opposite-current-driver citation change -0.1224 [-0.2188, -0.0227], sensitivity change -0.1848 [-0.2969, -0.0966], CSD 0.0624 [-0.0416, 0.1712].
- Haiku false-label currently false: opposite-current-driver citation change 0.2666 [0.2050, 0.3267], sensitivity change 0.3606 [0.3015, 0.4185], CSD -0.0940 [-0.1600, -0.0265].
- Haiku naive citation headroom: P3 0.270723, P4 0.469810 on the respective complete-probe support.
- Haiku delivered unique tables: realized: true mean |r|=0.807981, opposite=0.616947, true largest among six=0.570608; without_impact: true mean |r|=0.852838, opposite=0.522271, true largest among six=0.758893; fundamental: true mean |r|=0.880154, opposite=0.523223, true largest among six=0.786675. These are fixed-path summaries.
- Haiku P4 at alpha .0125: 80%-power raw MDE 0.111344; detecting the DeepSeek point estimate with this SD requires 8 paired seeds.
- Haiku adoption of communicated labels: label 0.8681 [0.8392, 0.8908], false-label 0.8550 [0.8108, 0.8975]; matched naive rates 0.642892 and 0.636667, respectively.
- Haiku naive news in its own regime: low-|x| flip rate 0.1451 [0.0357, 0.2902] (n=50), high-|x| 0.6042 [0.4858, 0.7392] (n=153); after-flip proxy agreement 0.407819 vs disagreement 0.442406. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.
- Haiku naive momentum in its own regime: low-|x| flip rate 0.2964 [0.1282, 0.4914] (n=55), high-|x| 0.8195 [0.6782, 0.9216] (n=149); after-flip proxy agreement 0.549230 vs disagreement 0.673337. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.
- Luna: momentum P2 -0.1426 [-0.2063, -0.0833], Holm p=0.005812; momentum P4 0.1589 [0.0762, 0.2519], Holm p=0.016466. News discrimination primary 0.2639 [0.1575, 0.3755].
- Luna: exclusive P4 CSD -0.0441 [-0.0899, 0.0023], raw p=0.110408, 10 seeds/594 paired decisions; this changes the estimand and does not replace P4.
- Luna: at_most_one P4 CSD 0.0751 [0.0155, 0.1351], raw p=0.045749, 10 seeds/175 paired decisions; this changes the estimand and does not replace P4.
- Luna false-label currently true: opposite-current-driver citation change -0.0780 [-0.1401, -0.0157], sensitivity change -0.1728 [-0.2231, -0.1238], CSD 0.0948 [0.0322, 0.1660].
- Luna false-label currently false: opposite-current-driver citation change 0.2933 [0.2280, 0.3516], sensitivity change 0.2782 [0.2489, 0.3082], CSD 0.0151 [-0.0519, 0.0794].
- Luna naive citation headroom: P3 0.151997, P4 0.367970 on the respective complete-probe support.
- Luna delivered unique tables: realized: true mean |r|=0.803860, opposite=0.606187, true largest among six=0.570348; without_impact: true mean |r|=0.852838, opposite=0.522271, true largest among six=0.758893; fundamental: true mean |r|=0.880154, opposite=0.523223, true largest among six=0.786675. These are fixed-path summaries.
- Luna P4 at alpha .0125: 80%-power raw MDE 0.097553; detecting the DeepSeek point estimate with this SD requires 7 paired seeds.
- Luna adoption of communicated labels: label 0.9682 [0.9481, 0.9850], false-label 0.9650 [0.9533, 0.9750]; matched naive rates 0.758025 and 0.703333, respectively.
- Luna naive news in its own regime: low-|x| flip rate 0.2546 [0.1504, 0.3586] (n=50), high-|x| 0.8435 [0.7492, 0.9257] (n=153); after-flip proxy agreement 0.583644 vs disagreement 0.612346. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.
- Luna naive momentum in its own regime: low-|x| flip rate 0.3119 [0.1807, 0.4512] (n=55), high-|x| 0.7662 [0.6714, 0.8523] (n=149); after-flip proxy agreement 0.538768 vs disagreement 0.636556. Magnitude and proxy conflict both track the probe response descriptively; these strata do not separate their causal contributions.
- Planned audit/label truth is a seed-defined subgroup matching every observed label; actual audit delivery is validity-gated, so the construction and caveat must be reported together.
- DeepSeek P4 sensitivity increased 0.253285, exceeding the maximum possible citation increase of 0.185798 from its naive baseline. With that sensitivity change, even universal target citation would force a negative CSD; citation saturation therefore materially constrains the sign's interpretation.
- Under observed Haiku/Luna P4 SDs, 8/7 paired seeds would give 80% power at alpha .0125 for a true effect as large as DeepSeek's pooled point estimate, versus 10 actually observed. This conditional planning result does not explain the model differences or establish effect heterogeneity; a generic low-power explanation alone is incomplete.
- Both-driver citations can guarantee audit passing, and exclusive/selected comparisons have different denominators. Neither CSD nor single-driver recall establishes explanation faithfulness.
- Negative volume is possible by construction. Fundamental and order-impact components covary substantially; unallocated variance ratios cannot be presented as additive shares.

## Not computable and interpretation limits

- The registered eight-observation evidence intervention was never delivered; no effect of that intervention can be estimated.
- Internal reasoning, individual feature causality or action probabilities cannot be recovered from a single re-ask per feature; no new re-asks or API calls are made.
- Proxy sign agreement alone cannot establish how far perturbed prompts depart from the joint prompt distribution; it quantifies sign conflict only.
- Historical counterfactual trajectories with impact removed cannot be computed from fixed observed decisions. E is a fixed-path arithmetic sensitivity, not a re-simulated market.
- Exogenous subgroup construction does not isolate label content from verdict/fine or downstream history, and response-validity selection remains post-treatment.
- P1 is precision, not a citation-minus-sensitivity contrast; its numerator components and explicitly defined specificity-weighted alternative are supplied instead of inventing an additive citation component.

## Validation

Run `python -m pytest -q tests/v2/test_posthoc_analyses.py` for the focused checks and `python -m pytest -q` for the full offline suite. Current release results are in [VERIFICATION.md](../../../../VERIFICATION.md). Original runs, existing outputs and frozen documents are preserved.

## Reproducibility

Run `python src/v2/posthoc_analyses.py`. All statistical resampling uses fixed seed 20261026. No volatile timestamps are embedded. Exact source/input hashes are recorded in results.json. Public packaging changes source and frozen-output provenance hashes and validation prose; statistical values are unchanged. Versions: python 3.12.2, numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, matplotlib 3.11.2, statsmodels 0.15.0, pytest 9.1.1.
