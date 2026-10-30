# Exploratory analyses of existing confirmatory data

EXPLORATORY (not preregistered); descriptive, non-simultaneous intervals

These analyses are exploratory (not preregistered). Confirmatory results are reproduced exactly, including common support, per-seed differences, 95% intervals, raw p and four-slot within-model Holm p. No API calls, new responses, changed seeds or changed confirmatory files. Primary window: ticks 20–39. DeepSeek: 20 seeds; Haiku and Luna: 10 seeds each. Every estimate weights seeds equally unless explicitly marked pooled. SD denotes the sample SD of seed means. All new intervals are descriptive 95% percentile seed-bootstrap intervals (10,000 draws, RNG 20261026); new p values are raw two-sided paired t diagnostics, without confirmatory rejection rules.

P1=evidence-naive process precision; P2=evidence-naive current true-driver flip; P3=label-naive (current true-driver citation minus flip); P4=false-label-naive (opposite-current-driver citation minus flip). ITT selectors apply to all eligible primary decisions, including unexposed prompts and periods where a persisted label has changed correctness.

## Headline facts for the paper

- **Implementation deviation: evidence tables contain at most five completed ticks, not the registered eight.** Every persisted evidence message is regenerated and matched byte-for-byte. The ordinary four-tick history was reused as the evidence-builder input, then augmented by the audited tick.
- DeepSeek primary: P1 -0.0137 [-0.0431, 0.0140], raw p=0.36828, Holm p=0.36828; P2 -0.0624 [-0.0981, -0.0239], raw p=0.0046715, Holm p=0.014015; P3 -0.0389 [-0.0881, 0.0068], raw p=0.13637, Holm p=0.27275; P4 -0.1341 [-0.1772, -0.0916], raw p=1.0447e-05, Holm p=4.1787e-05.
- DeepSeek naive all-tick discrimination (driver − non-driver flip rates): news pooled -0.1157, seed estimate -0.1190 [-0.1970, -0.0438] (n=1219 decisions); momentum pooled 0.5225, seed estimate 0.5224 [0.4471, 0.5918] (n=1202 decisions).
- DeepSeek regime contrasts: news: P2 -0.0721 [-0.1401, -0.0050], P4 -0.1162 [-0.1771, -0.0545]; momentum: P2 -0.0493 [-0.0993, -0.0045], P4 -0.1503 [-0.2189, -0.0846].
- DeepSeek persisted label false in 756/2400 (31.50%) primary decisions; false-label label accidentally true in 756/2400 (31.50%); no label exposure yet: label 0, false-label 0.
- DeepSeek both-driver citation rates: naive 72.00%; punitive 82.38%; label 82.29%; evidence 68.00%; false-label 83.83%.
- DeepSeek additive noise-adjusted: P2 -0.0627 [-0.1046, -0.0202], p=0.0099727; P3 -0.0653 [-0.1192, -0.0162], p=0.024973; P4 -0.1631 [-0.2093, -0.1158], p=2.439e-06.
- DeepSeek actual mixed-regime audit tables: 294/718 (40.95%); mixed windows carried by 996/2400 (41.50%) primary prompts. Removing realized price impact changes feature correlations by mean |Δr|=0.2021 (fixed-path arithmetic sensitivity).
- Haiku primary: P1 0.0163 [-0.0362, 0.0642], raw p=0.5613, Holm p=1; P2 -0.0059 [-0.0609, 0.0531], raw p=0.84985, Holm p=1; P3 -0.0354 [-0.0892, 0.0210], raw p=0.25417, Holm p=0.76251; P4 -0.0572 [-0.1045, -0.0039], raw p=0.066643, Holm p=0.26657.
- Haiku naive all-tick discrimination (driver − non-driver flip rates): news pooled 0.0033, seed estimate -0.0011 [-0.1007, 0.0999] (n=607 decisions); momentum pooled 0.3706, seed estimate 0.3700 [0.2792, 0.4589] (n=591 decisions).
- Haiku regime contrasts: news: P2 0.0457 [-0.0055, 0.1074], P4 -0.0350 [-0.0976, 0.0312]; momentum: P2 -0.0572 [-0.1577, 0.0405], P4 -0.0766 [-0.1550, -0.0023].
- Haiku persisted label false in 372/1200 (31.00%) primary decisions; false-label label accidentally true in 372/1200 (31.00%); no label exposure yet: label 0, false-label 0.
- Haiku both-driver citation rates: naive 31.50%; punitive 28.33%; label 31.77%; evidence 29.80%; false-label 30.42%.
- Haiku additive noise-adjusted: P2 -0.0394 [-0.1089, 0.0441], p=0.36167; P3 -0.0156 [-0.0919, 0.0622], p=0.71321; P4 -0.0324 [-0.0998, 0.0309], p=0.38566.
- Haiku actual mixed-regime audit tables: 150/344 (43.60%); mixed windows carried by 549/1200 (45.75%) primary prompts. Removing realized price impact changes feature correlations by mean |Δr|=0.1543 (fixed-path arithmetic sensitivity).
- Luna primary: P1 -0.1198 [-0.1562, -0.0838], raw p=0.00016721, Holm p=0.00066885; P2 -0.0909 [-0.1396, -0.0312], raw p=0.012535, Holm p=0.037606; P3 -0.0333 [-0.0845, 0.0252], raw p=0.28833, Holm p=0.28833; P4 0.0404 [-0.0069, 0.0821], raw p=0.1272, Holm p=0.2544.
- Luna naive all-tick discrimination (driver − non-driver flip rates): news pooled 0.1865, seed estimate 0.1806 [0.0908, 0.2630] (n=606 decisions); momentum pooled 0.2102, seed estimate 0.2131 [0.0701, 0.3413] (n=590 decisions).
- Luna regime contrasts: news: P2 -0.0309 [-0.1269, 0.0638], P4 -0.0765 [-0.1259, -0.0249]; momentum: P2 -0.1426 [-0.2063, -0.0833], P4 0.1589 [0.0762, 0.2519].
- Luna persisted label false in 372/1200 (31.00%) primary decisions; false-label label accidentally true in 372/1200 (31.00%); no label exposure yet: label 0, false-label 0.
- Luna both-driver citation rates: naive 47.08%; punitive 47.50%; label 57.21%; evidence 60.93%; false-label 57.75%.
- Luna additive noise-adjusted: P2 -0.1212 [-0.1902, -0.0376], p=0.015913; P3 -0.0453 [-0.1199, 0.0302], p=0.29146; P4 0.0348 [-0.0311, 0.0883], p=0.3085.
- Luna actual mixed-regime audit tables: 150/344 (43.60%); mixed windows carried by 549/1200 (45.75%) primary prompts. Removing realized price impact changes feature correlations by mean |Δr|=0.1474 (fixed-path arithmetic sensitivity).

## Estimands, eligibility and missing responses (B)

CF mask is pre-treatment and independent of responses. Base validity, CF validity, nonempty C/D, and label exposure/correctness are observed post-treatment. Precision common support requires valid base plus both valid CF re-asks and nonempty C in BOTH arms; recall requires nonempty D. Dependence/CSD require complete measurement in both arms but do not require C or D nonempty. Fidelity/citation use valid bases. Match seed, tick, agent and regime; equal-weight per-seed means. Missing/invalid responses are excluded without imputation or resampling; missing nulls never exclude raw primary observations.

Formally, let V_cj denote valid base plus two valid probes. For precision, J_sc={j:20≤t≤39, same seed/tick/agent/regime in c and reference, V_cj=V_rj=1, |C_cj|>0, |C_rj|>0}. For dependence and ITT CSD, drop the C restrictions. For recall replace them with |D_cj|>0 and |D_rj|>0. For fidelity/citation require only valid bases in both arms. Actual-label CSD additionally requires a revealed label in the target and uses that same label to score both arms, including when stale. For any metric Y, Δ_s=mean_(j∈J_sc)Y_cj−mean_(j∈J_sc)Y_rj, then Δ=mean_s Δ_s. C and D eligibility and subgroup membership are post-treatment. Common support therefore defines a selected estimand. All-available descriptive seed means in A have no cross-condition matching.

C=R intersect {news,momentum} is observable for every valid base. D is defined only after both valid feature probes. Report empty C among valid bases and complete measured decisions separately; empty D only among complete measurements.

Primary-window flow (each arm assigns 120 decisions per seed). A probed decision has two attempted feature re-asks; valid re-asks below count calls, whereas eligible counts decisions with both valid re-asks. An invalid base receives no feature re-asks and no market order; invalid or failed re-asks produce undefined flips. A decision with only one valid probe is excluded from process metrics and all raw dependence/CSD comparisons. No failed/invalid response is fabricated or resampled. All-tick flows and failures by feature are in JSON `B_flow`.

| Model | Condition | Assigned | Valid bases | CF selected | Probed | Valid re-asks / attempted | Failed/invalid re-asks | Complete eligible | Defined P | Defined Q |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek | naive | 2400 | 2400 | 1207 | 1207 | 2414/2414 | 0 | 1207 | 1205 | 1039 |
| DeepSeek | punitive | 2400 | 2400 | 1207 | 1207 | 2414/2414 | 0 | 1207 | 1204 | 1038 |
| DeepSeek | label | 2400 | 2400 | 1207 | 1207 | 2414/2414 | 0 | 1207 | 1207 | 1161 |
| DeepSeek | evidence | 2400 | 2400 | 1207 | 1207 | 2414/2414 | 0 | 1207 | 1205 | 1051 |
| DeepSeek | false-label | 2400 | 2400 | 1207 | 1207 | 2414/2414 | 0 | 1207 | 1207 | 1151 |
| Haiku | naive | 1200 | 1200 | 596 | 596 | 1192/1192 | 0 | 596 | 569 | 441 |
| Haiku | punitive | 1200 | 1200 | 596 | 596 | 1192/1192 | 0 | 596 | 572 | 463 |
| Haiku | label | 1200 | 1199 | 596 | 595 | 1189/1190 | 1 | 594 | 586 | 515 |
| Haiku | evidence | 1200 | 1199 | 596 | 595 | 1186/1190 | 4 | 591 | 565 | 456 |
| Haiku | false-label | 1200 | 1200 | 596 | 596 | 1191/1192 | 1 | 595 | 590 | 501 |
| Luna | naive | 1200 | 1200 | 596 | 596 | 1190/1192 | 2 | 594 | 587 | 493 |
| Luna | punitive | 1200 | 1200 | 596 | 596 | 1192/1192 | 0 | 596 | 584 | 487 |
| Luna | label | 1200 | 1199 | 596 | 595 | 1188/1190 | 2 | 593 | 592 | 531 |
| Luna | evidence | 1200 | 1198 | 596 | 595 | 1188/1190 | 2 | 593 | 590 | 444 |
| Luna | false-label | 1200 | 1200 | 596 | 596 | 1192/1192 | 0 | 596 | 596 | 493 |

| Model | Condition | Empty C / valid bases | Empty C / complete measured | Empty D / complete measured |
|---|---|---|---|---|
| DeepSeek | naive | 4/2400 (0.17%) | 2/1207 (0.17%) | 168/1207 (13.92%) |
| DeepSeek | punitive | 3/2400 (0.12%) | 3/1207 (0.25%) | 169/1207 (14.00%) |
| DeepSeek | label | 0/2400 (0.00%) | 0/1207 (0.00%) | 46/1207 (3.81%) |
| DeepSeek | evidence | 2/2400 (0.08%) | 2/1207 (0.17%) | 156/1207 (12.92%) |
| DeepSeek | false-label | 0/2400 (0.00%) | 0/1207 (0.00%) | 56/1207 (4.64%) |
| Haiku | naive | 42/1200 (3.50%) | 27/596 (4.53%) | 155/596 (26.01%) |
| Haiku | punitive | 38/1200 (3.17%) | 24/596 (4.03%) | 133/596 (22.32%) |
| Haiku | label | 12/1199 (1.00%) | 8/594 (1.35%) | 79/594 (13.30%) |
| Haiku | evidence | 41/1199 (3.42%) | 26/591 (4.40%) | 135/591 (22.84%) |
| Haiku | false-label | 7/1200 (0.58%) | 5/595 (0.84%) | 94/595 (15.80%) |
| Luna | naive | 12/1200 (1.00%) | 7/594 (1.18%) | 101/594 (17.00%) |
| Luna | punitive | 17/1200 (1.42%) | 12/596 (2.01%) | 109/596 (18.29%) |
| Luna | label | 1/1199 (0.08%) | 1/593 (0.17%) | 62/593 (10.46%) |
| Luna | evidence | 5/1198 (0.42%) | 3/593 (0.51%) | 149/593 (25.13%) |
| Luna | false-label | 1/1200 (0.08%) | 0/596 (0.00%) | 103/596 (17.28%) |

Common support for every contrast is recorded under `B_common_support` with per-arm eligible/excluded counts and per-seed counts. The primary contrasts are shown here; a seed remains included if at least one eligible matched decision exists.

| Model | Contrast | Target eligible | Reference eligible | Common analysed coordinates | Seed pairs |
|---|---|---:|---:|---:|---:|
| DeepSeek | P1 | 1205 | 1205 | 1203 | 20 |
| DeepSeek | P2 | 1207 | 1207 | 1207 | 20 |
| DeepSeek | P3 | 1207 | 1207 | 1207 | 20 |
| DeepSeek | P4 | 1207 | 1207 | 1207 | 20 |
| Haiku | P1 | 565 | 569 | 555 | 10 |
| Haiku | P2 | 591 | 596 | 591 | 10 |
| Haiku | P3 | 594 | 596 | 594 | 10 |
| Haiku | P4 | 595 | 596 | 595 | 10 |
| Luna | P1 | 590 | 587 | 582 | 10 |
| Luna | P2 | 593 | 594 | 591 | 10 |
| Luna | P3 | 593 | 594 | 591 | 10 |
| Luna | P4 | 596 | 594 | 594 | 10 |

## A. All-available condition means ± seed SD, ticks 20–39

E and true-driver citation are identically defined (the driver is in the reasons), so their numeric columns coincide. Precision and recall use only decisions with defined denominators; JSON includes the exact decision and seed denominators.

| Model | Condition | E | Driver flip | Opposite flip | P | Q | True citation |
|---|---|---|---|---|---|---|---|
| DeepSeek | naive | 0.8942 ± 0.0560 | 0.5957 ± 0.0761 | 0.3297 ± 0.0509 | 0.5906 ± 0.0671 | 0.9966 ± 0.0079 | 0.8942 ± 0.0560 |
| DeepSeek | punitive | 0.9321 ± 0.0352 | 0.6138 ± 0.0819 | 0.3175 ± 0.0681 | 0.5443 ± 0.0595 | 0.9953 ± 0.0119 | 0.9321 ± 0.0352 |
| DeepSeek | label | 0.9579 ± 0.0320 | 0.7001 ± 0.0846 | 0.2844 ± 0.0974 | 0.5803 ± 0.0430 | 0.9977 ± 0.0059 | 0.9579 ± 0.0320 |
| DeepSeek | evidence | 0.8533 ± 0.0834 | 0.5333 ± 0.0858 | 0.3954 ± 0.0795 | 0.5762 ± 0.0899 | 0.9754 ± 0.0285 | 0.8533 ± 0.0834 |
| DeepSeek | false-label | 0.9083 ± 0.0373 | 0.4024 ± 0.0863 | 0.5830 ± 0.0891 | 0.5664 ± 0.0424 | 0.9990 ± 0.0044 | 0.9083 ± 0.0373 |
| Haiku | naive | 0.7258 ± 0.0867 | 0.5352 ± 0.1036 | 0.3003 ± 0.0538 | 0.6514 ± 0.0660 | 0.9348 ± 0.0708 | 0.7258 ± 0.0867 |
| Haiku | punitive | 0.7100 ± 0.0849 | 0.5760 ± 0.0741 | 0.2956 ± 0.0860 | 0.6843 ± 0.0862 | 0.9315 ± 0.0385 | 0.7100 ± 0.0849 |
| Haiku | label | 0.8032 ± 0.0477 | 0.6652 ± 0.0786 | 0.2725 ± 0.0504 | 0.7280 ± 0.0755 | 0.9583 ± 0.0287 | 0.8032 ± 0.0477 |
| Haiku | evidence | 0.6832 ± 0.0862 | 0.5291 ± 0.1080 | 0.3232 ± 0.0694 | 0.6654 ± 0.0795 | 0.9378 ± 0.0455 | 0.6832 ± 0.0862 |
| Haiku | false-label | 0.6233 ± 0.0860 | 0.4059 ± 0.0856 | 0.5048 ± 0.0888 | 0.7210 ± 0.0511 | 0.9481 ± 0.0416 | 0.6233 ± 0.0860 |
| Luna | naive | 0.8183 ± 0.0596 | 0.6099 ± 0.0413 | 0.3187 ± 0.0465 | 0.6694 ± 0.0596 | 0.9753 ± 0.0170 | 0.8183 ± 0.0596 |
| Luna | punitive | 0.8183 ± 0.0638 | 0.5942 ± 0.0697 | 0.3301 ± 0.0822 | 0.6517 ± 0.0556 | 0.9602 ± 0.0331 | 0.8183 ± 0.0638 |
| Luna | label | 0.8916 ± 0.0465 | 0.6873 ± 0.0738 | 0.2737 ± 0.0634 | 0.6703 ± 0.0542 | 0.9825 ± 0.0166 | 0.8916 ± 0.0465 |
| Luna | evidence | 0.8363 ± 0.0717 | 0.5184 ± 0.1030 | 0.3258 ± 0.0727 | 0.5476 ± 0.0565 | 0.9728 ± 0.0238 | 0.8363 ± 0.0717 |
| Luna | false-label | 0.7625 ± 0.0593 | 0.4285 ± 0.0911 | 0.4576 ± 0.0606 | 0.6058 ± 0.0532 | 0.9682 ± 0.0173 | 0.7625 ± 0.0593 |

## C. Numeric support for Table 3

Raw secondary p values and descriptive intervals do not create a confirmatory rejection rule. Effect sizes (paired SD, d_z), exact seed means and support counts for these and all registered secondary contrasts are in JSON. H2 fidelity and true-driver citation are the same outcome. Opposite/false citation always selects the opposite CURRENT driver, independently of the persisted label's present correctness. H1/H3/H4 primary rows are in the headline list above.

| Model | Secondary contrast | Δ [95% CI] | Raw p | Seeds | Common n |
|---|---|---|---:|---:|---:|
| DeepSeek | H2_fidelity_label_minus_naive | 0.0638 [0.0429, 0.0858] | 2.0025e-05 | 20 | 2400 |
| DeepSeek | H2_precision_label_minus_naive | -0.0102 [-0.0416, 0.0212] | 0.54741 | 20 | 1205 |
| DeepSeek | H2_precision_evidence_minus_label | -0.0038 [-0.0364, 0.0287] | 0.83124 | 20 | 1205 |
| DeepSeek | H4_fidelity_false-label_minus_label | -0.0496 [-0.0704, -0.0283] | 0.00026576 | 20 | 2400 |
| DeepSeek | H4_false_citation_false-label_minus_naive | 0.1058 [0.0792, 0.1337] | 4.3863e-07 | 20 | 2400 |
| DeepSeek | H5_precision_evidence_minus_punitive | 0.0328 [0.0023, 0.0654] | 0.061561 | 20 | 1202 |
| DeepSeek | H5_precision_punitive_minus_naive | -0.0468 [-0.0621, -0.0326] | 9.9805e-06 | 20 | 1204 |
| DeepSeek | H1_dependence_evidence_minus_punitive | -0.0805 [-0.1214, -0.0359] | 0.0018223 | 20 | 1207 |
| DeepSeek | H5_dependence_punitive_minus_naive | 0.0181 [-0.0031, 0.0392] | 0.11409 | 20 | 1207 |
| Haiku | H2_fidelity_label_minus_naive | 0.0776 [0.0418, 0.1151] | 0.0035499 | 10 | 1199 |
| Haiku | H2_precision_label_minus_naive | 0.0834 [0.0237, 0.1337] | 0.019607 | 10 | 565 |
| Haiku | H2_precision_evidence_minus_label | -0.0581 [-0.1132, -0.0002] | 0.086479 | 10 | 562 |
| Haiku | H4_fidelity_false-label_minus_label | -0.1802 [-0.2221, -0.1367] | 2.9248e-05 | 10 | 1199 |
| Haiku | H4_false_citation_false-label_minus_naive | 0.1208 [0.0567, 0.1808] | 0.0058643 | 10 | 1200 |
| Haiku | H5_precision_evidence_minus_punitive | -0.0121 [-0.0583, 0.0357] | 0.64433 | 10 | 555 |
| Haiku | H5_precision_punitive_minus_naive | 0.0338 [0.0046, 0.0602] | 0.051227 | 10 | 562 |
| Haiku | H1_dependence_evidence_minus_punitive | -0.0454 [-0.0851, 0.0020] | 0.084689 | 10 | 591 |
| Haiku | H5_dependence_punitive_minus_naive | 0.0408 [-0.0015, 0.0803] | 0.092822 | 10 | 596 |
| Luna | H2_fidelity_label_minus_naive | 0.0726 [0.0492, 0.1009] | 0.00060941 | 10 | 1199 |
| Luna | H2_precision_label_minus_naive | 0.0041 [-0.0457, 0.0579] | 0.88715 | 10 | 583 |
| Luna | H2_precision_evidence_minus_label | -0.1225 [-0.1634, -0.0772] | 0.00052023 | 10 | 587 |
| Luna | H4_fidelity_false-label_minus_label | -0.1285 [-0.1733, -0.0808] | 0.00063091 | 10 | 1199 |
| Luna | H4_false_citation_false-label_minus_naive | 0.1717 [0.1225, 0.2208] | 0.00011072 | 10 | 1200 |
| Luna | H5_precision_evidence_minus_punitive | -0.1027 [-0.1484, -0.0585] | 0.0023168 | 10 | 579 |
| Luna | H5_precision_punitive_minus_naive | -0.0176 [-0.0508, 0.0144] | 0.34249 | 10 | 580 |
| Luna | H1_dependence_evidence_minus_punitive | -0.0770 [-0.1488, -0.0030] | 0.07941 | 10 | 593 |
| Luna | H5_dependence_punitive_minus_naive | -0.0170 [-0.0462, 0.0134] | 0.31194 | 10 | 594 |

CSD components below use exactly the corresponding primary CSD support; citation-only secondary contrasts above can use more valid bases.

| Model | CSD | Component change | Δ [95% CI] | Raw p |
|---|---|---|---|---:|
| DeepSeek | H3_sci_label | citation_delta | 0.0655 [0.0437, 0.0863] | 1.1857e-05 |
| DeepSeek | H3_sci_label | dependence_delta | 0.1044 [0.0671, 0.1424] | 3.8297e-05 |
| DeepSeek | H4_sci_false-label | citation_delta | 0.1192 [0.0907, 0.1501] | 3.1533e-07 |
| DeepSeek | H4_sci_false-label | dependence_delta | 0.2533 [0.2170, 0.2893] | 5.6367e-11 |
| Haiku | H3_sci_label | citation_delta | 0.0962 [0.0503, 0.1459] | 0.0046735 |
| Haiku | H3_sci_label | dependence_delta | 0.1316 [0.0685, 0.1892] | 0.0026608 |
| Haiku | H4_sci_false-label | citation_delta | 0.1466 [0.0843, 0.2096] | 0.0019097 |
| Haiku | H4_sci_false-label | dependence_delta | 0.2038 [0.1630, 0.2377] | 3.7293e-06 |
| Luna | H3_sci_label | citation_delta | 0.0455 [0.0130, 0.0797] | 0.032689 |
| Luna | H3_sci_label | dependence_delta | 0.0788 [0.0347, 0.1215] | 0.0086055 |
| Luna | H4_sci_false-label | citation_delta | 0.1792 [0.1126, 0.2399] | 0.00053754 |
| Luna | H4_sci_false-label | dependence_delta | 0.1388 [0.1014, 0.1737] | 5.6965e-05 |

## D. Regime split

Rates and discrimination estimates below weight seeds equally; n counts complete decisions. The JSON also reports pooled-decision rates and pooled discrimination. All-tick naive discrimination reproduces the published instrument diagnostic; the full primary-window table includes every condition and both regimes.

| Model | Window | Condition | Regime | Driver rate | Non-driver rate | Discrimination [95% CI] | Seeds | Decisions |
|---|---|---|---|---:|---:|---|---:|---:|
| DeepSeek | overall | naive | news | 0.4015 | 0.5205 | -0.1190 [-0.1970, -0.0438] | 20 | 1219 |
| DeepSeek | overall | naive | momentum | 0.7261 | 0.2037 | 0.5224 [0.4471, 0.5918] | 20 | 1202 |
| DeepSeek | primary | naive | news | 0.4205 | 0.4955 | -0.0750 [-0.1645, 0.0187] | 20 | 603 |
| DeepSeek | primary | naive | momentum | 0.7760 | 0.1648 | 0.6112 [0.5156, 0.6971] | 20 | 604 |
| DeepSeek | primary | punitive | news | 0.4935 | 0.4362 | 0.0573 [-0.0556, 0.1702] | 20 | 603 |
| DeepSeek | primary | punitive | momentum | 0.7389 | 0.2006 | 0.5382 [0.4462, 0.6292] | 20 | 604 |
| DeepSeek | primary | label | news | 0.6199 | 0.3530 | 0.2669 [0.1678, 0.3553] | 20 | 603 |
| DeepSeek | primary | label | momentum | 0.7778 | 0.2179 | 0.5598 [0.4391, 0.6702] | 20 | 604 |
| DeepSeek | primary | evidence | news | 0.3484 | 0.5700 | -0.2216 [-0.3597, -0.0777] | 20 | 603 |
| DeepSeek | primary | evidence | momentum | 0.7267 | 0.2177 | 0.5090 [0.3719, 0.6381] | 20 | 604 |
| DeepSeek | primary | false-label | news | 0.3510 | 0.6470 | -0.2960 [-0.3725, -0.2147] | 20 | 603 |
| DeepSeek | primary | false-label | momentum | 0.4528 | 0.5183 | -0.0655 [-0.2048, 0.0768] | 20 | 604 |
| Haiku | overall | naive | news | 0.3984 | 0.3996 | -0.0011 [-0.1007, 0.0999] | 10 | 607 |
| Haiku | overall | naive | momentum | 0.5953 | 0.2253 | 0.3700 [0.2792, 0.4589] | 10 | 591 |
| Haiku | primary | naive | news | 0.4327 | 0.3998 | 0.0330 [-0.0770, 0.1586] | 10 | 296 |
| Haiku | primary | naive | momentum | 0.6414 | 0.2068 | 0.4346 [0.3152, 0.5419] | 10 | 300 |
| Haiku | primary | punitive | news | 0.4947 | 0.3702 | 0.1245 [0.0086, 0.2451] | 10 | 296 |
| Haiku | primary | punitive | momentum | 0.6629 | 0.2212 | 0.4418 [0.3088, 0.5564] | 10 | 300 |
| Haiku | primary | label | news | 0.6173 | 0.3368 | 0.2806 [0.1856, 0.3710] | 10 | 296 |
| Haiku | primary | label | momentum | 0.7153 | 0.2107 | 0.5046 [0.3786, 0.6173] | 10 | 298 |
| Haiku | primary | evidence | news | 0.4751 | 0.4027 | 0.0724 [-0.0664, 0.2170] | 10 | 291 |
| Haiku | primary | evidence | momentum | 0.5842 | 0.2472 | 0.3370 [0.1241, 0.5387] | 10 | 300 |
| Haiku | primary | false-label | news | 0.3520 | 0.5805 | -0.2285 [-0.3116, -0.1304] | 10 | 296 |
| Haiku | primary | false-label | momentum | 0.4602 | 0.4326 | 0.0276 [-0.1759, 0.2338] | 10 | 299 |
| Luna | overall | naive | news | 0.5474 | 0.3668 | 0.1806 [0.0908, 0.2630] | 10 | 606 |
| Luna | overall | naive | momentum | 0.5542 | 0.3411 | 0.2131 [0.0701, 0.3413] | 10 | 590 |
| Luna | primary | naive | news | 0.6118 | 0.3479 | 0.2639 [0.1575, 0.3755] | 10 | 295 |
| Luna | primary | naive | momentum | 0.6084 | 0.2927 | 0.3158 [0.1940, 0.4347] | 10 | 299 |
| Luna | primary | punitive | news | 0.5882 | 0.3717 | 0.2166 [0.0685, 0.3739] | 10 | 296 |
| Luna | primary | punitive | momentum | 0.5991 | 0.2929 | 0.3062 [0.1911, 0.4004] | 10 | 300 |
| Luna | primary | label | news | 0.5991 | 0.3515 | 0.2476 [0.1755, 0.3319] | 10 | 293 |
| Luna | primary | label | momentum | 0.7722 | 0.2018 | 0.5704 [0.4393, 0.6970] | 10 | 300 |
| Luna | primary | evidence | news | 0.5791 | 0.3179 | 0.2613 [0.1208, 0.4088] | 10 | 294 |
| Luna | primary | evidence | momentum | 0.4668 | 0.3363 | 0.1305 [-0.0487, 0.3122] | 10 | 299 |
| Luna | primary | false-label | news | 0.3998 | 0.5366 | -0.1368 [-0.2502, -0.0340] | 10 | 296 |
| Luna | primary | false-label | momentum | 0.4568 | 0.3825 | 0.0743 [-0.0873, 0.2202] | 10 | 300 |

| Model | Regime | Contrast | Δ [95% CI] | Raw p | Seeds | Common n |
|---|---|---|---|---:|---:|---:|
| DeepSeek | news | P1 | 0.0082 [-0.0319, 0.0494] | 0.70641 | 20 | 602 |
| DeepSeek | news | P2 | -0.0721 [-0.1401, -0.0050] | 0.05771 | 20 | 603 |
| DeepSeek | news | P3 | -0.1004 [-0.1727, -0.0238] | 0.017998 | 20 | 603 |
| DeepSeek | news | P4 | -0.1162 [-0.1771, -0.0545] | 0.0016276 | 20 | 603 |
| DeepSeek | momentum | P1 | -0.0348 [-0.0729, 0.0023] | 0.098507 | 20 | 601 |
| DeepSeek | momentum | P2 | -0.0493 [-0.0993, -0.0045] | 0.061413 | 20 | 604 |
| DeepSeek | momentum | P3 | 0.0271 [-0.0376, 0.0912] | 0.43203 | 20 | 604 |
| DeepSeek | momentum | P4 | -0.1503 [-0.2189, -0.0846] | 0.00043884 | 20 | 604 |
| Haiku | news | P1 | 0.0415 [-0.0201, 0.1020] | 0.24154 | 10 | 274 |
| Haiku | news | P2 | 0.0457 [-0.0055, 0.1074] | 0.16963 | 10 | 291 |
| Haiku | news | P3 | -0.0256 [-0.0852, 0.0430] | 0.47308 | 10 | 296 |
| Haiku | news | P4 | -0.0350 [-0.0976, 0.0312] | 0.33764 | 10 | 296 |
| Haiku | momentum | P1 | -0.0115 [-0.0793, 0.0513] | 0.74955 | 10 | 281 |
| Haiku | momentum | P2 | -0.0572 [-0.1577, 0.0405] | 0.31339 | 10 | 300 |
| Haiku | momentum | P3 | -0.0462 [-0.1338, 0.0261] | 0.31412 | 10 | 298 |
| Haiku | momentum | P4 | -0.0766 [-0.1550, -0.0023] | 0.099844 | 10 | 299 |
| Luna | news | P1 | -0.1076 [-0.1608, -0.0572] | 0.0036586 | 10 | 292 |
| Luna | news | P2 | -0.0309 [-0.1269, 0.0638] | 0.55636 | 10 | 293 |
| Luna | news | P3 | 0.0730 [-0.0021, 0.1704] | 0.14932 | 10 | 292 |
| Luna | news | P4 | -0.0765 [-0.1259, -0.0249] | 0.020361 | 10 | 295 |
| Luna | momentum | P1 | -0.1272 [-0.1720, -0.0826] | 0.00046837 | 10 | 290 |
| Luna | momentum | P2 | -0.1426 [-0.2063, -0.0833] | 0.0019373 | 10 | 298 |
| Luna | momentum | P3 | -0.1390 [-0.2306, -0.0468] | 0.020231 | 10 | 299 |
| Luna | momentum | P4 | 0.1589 [0.0762, 0.2519] | 0.0082331 | 10 | 299 |

## E. Identical-prompt noise and additive sensitivity

Registered full 40x6 Bernoulli(.20) mask from default_rng(seed*1000+29), intersect CF mask. Implemented RNG draws only at CF-selected coordinates, after base response regardless of validity. One selected invalid Haiku evidence base still received a null call with undefined flip. Same seed and .20 probability, different coordinate mask; no response-dependent selection. See results/deviations.md and results/confirmatory_results.md for the public deviation record.

The two recipes share seed and probability but map RNG draws to different decisions. Every actual mask is asserted against the implemented scalar recipe, and no run matches the registered full-mask recipe. The sole invalid-base null call is Haiku evidence seed 203, tick 3, agent 4; its flip is undefined and excluded. Valid-base null missingness and selected counts are retained in JSON. Null-rate intervals there are descriptive Wilson intervals for pooled responses plus seed-bootstrap intervals for equal-seed rates. n below is the number of valid observed nulls.

| Model | Condition | Regime | Overall null flips/n (rate) | Primary null flips/n (rate) | Overall null selections / CF selected |
|---|---|---|---|---|---|
| DeepSeek | naive | news | 11/228 (0.0482) | 9/112 (0.0804) | 228/1219 (18.70%) |
| DeepSeek | naive | momentum | 10/222 (0.0450) | 2/113 (0.0177) | 222/1202 (18.47%) |
| DeepSeek | punitive | news | 9/228 (0.0395) | 6/112 (0.0536) | 228/1219 (18.70%) |
| DeepSeek | punitive | momentum | 11/222 (0.0495) | 4/113 (0.0354) | 222/1202 (18.47%) |
| DeepSeek | label | news | 6/228 (0.0263) | 3/112 (0.0268) | 228/1219 (18.70%) |
| DeepSeek | label | momentum | 4/222 (0.0180) | 1/113 (0.0088) | 222/1202 (18.47%) |
| DeepSeek | evidence | news | 16/228 (0.0702) | 7/112 (0.0625) | 228/1219 (18.70%) |
| DeepSeek | evidence | momentum | 6/222 (0.0270) | 2/113 (0.0177) | 222/1202 (18.47%) |
| DeepSeek | false-label | news | 5/228 (0.0219) | 2/112 (0.0179) | 228/1219 (18.70%) |
| DeepSeek | false-label | momentum | 3/222 (0.0135) | 2/113 (0.0177) | 222/1202 (18.47%) |
| Haiku | naive | news | 2/110 (0.0182) | 1/54 (0.0185) | 110/607 (18.12%) |
| Haiku | naive | momentum | 3/112 (0.0268) | 1/57 (0.0175) | 112/592 (18.92%) |
| Haiku | punitive | news | 10/110 (0.0909) | 5/54 (0.0926) | 110/607 (18.12%) |
| Haiku | punitive | momentum | 4/112 (0.0357) | 1/57 (0.0175) | 112/592 (18.92%) |
| Haiku | label | news | 2/110 (0.0182) | 2/54 (0.0370) | 110/607 (18.12%) |
| Haiku | label | momentum | 7/112 (0.0625) | 3/57 (0.0526) | 112/592 (18.92%) |
| Haiku | evidence | news | 5/110 (0.0455) | 1/54 (0.0185) | 110/607 (18.12%) |
| Haiku | evidence | momentum | 8/111 (0.0721) | 4/57 (0.0702) | 112/592 (18.92%) |
| Haiku | false-label | news | 8/110 (0.0727) | 4/54 (0.0741) | 110/607 (18.12%) |
| Haiku | false-label | momentum | 3/112 (0.0268) | 1/57 (0.0175) | 112/592 (18.92%) |
| Luna | naive | news | 6/110 (0.0545) | 3/54 (0.0556) | 110/607 (18.12%) |
| Luna | naive | momentum | 4/112 (0.0357) | 3/57 (0.0526) | 112/592 (18.92%) |
| Luna | punitive | news | 15/110 (0.1364) | 7/54 (0.1296) | 110/607 (18.12%) |
| Luna | punitive | momentum | 4/112 (0.0357) | 2/57 (0.0351) | 112/592 (18.92%) |
| Luna | label | news | 5/110 (0.0455) | 2/54 (0.0370) | 110/607 (18.12%) |
| Luna | label | momentum | 2/112 (0.0179) | 1/57 (0.0175) | 112/592 (18.92%) |
| Luna | evidence | news | 10/110 (0.0909) | 7/54 (0.1296) | 110/607 (18.12%) |
| Luna | evidence | momentum | 6/112 (0.0536) | 3/57 (0.0526) | 112/592 (18.92%) |
| Luna | false-label | news | 3/110 (0.0273) | 1/54 (0.0185) | 110/607 (18.12%) |
| Luna | false-label | momentum | 6/112 (0.0536) | 4/57 (0.0702) | 112/592 (18.92%) |

Realized null sampling rates, all conditions and all ticks combined:

- DeepSeek: 2250/12105 (18.59%) of CF-selected decisions; 2250/24000 (9.38%) of assigned decisions.
- Haiku: 1110/5995 (18.52%) of CF-selected decisions; 1110/12000 (9.25%) of assigned decisions.
- Luna: 1110/5995 (18.52%) of CF-selected decisions; 1110/12000 (9.25%) of assigned decisions.

Within-seed all-tick condition null rate subtracted from dependence and added to citation-minus-dependence, no clipping; model-condition fallback only for a seed with no observed null. Seed-bootstrap resamples contrasts and their estimated null rates together, with no additional within-cell null resampling. This additive sensitivity does not recover latent feature effects or redefine individual precision/recall.

| Model | Adjusted contrast | Δ [95% CI] | Raw p | Seeds | Fallback cells used |
|---|---|---|---:|---:|---:|
| DeepSeek | H1_dependence_evidence_minus_naive | -0.0627 [-0.1046, -0.0202] | 0.0099727 | 20 | 0 |
| DeepSeek | H3_sci_label | -0.0653 [-0.1192, -0.0162] | 0.024973 | 20 | 0 |
| DeepSeek | H4_sci_false-label | -0.1631 [-0.2093, -0.1158] | 2.439e-06 | 20 | 0 |
| Haiku | H1_dependence_evidence_minus_naive | -0.0394 [-0.1089, 0.0441] | 0.36167 | 10 | 0 |
| Haiku | H3_sci_label | -0.0156 [-0.0919, 0.0622] | 0.71321 | 10 | 0 |
| Haiku | H4_sci_false-label | -0.0324 [-0.0998, 0.0309] | 0.38566 | 10 | 0 |
| Luna | H1_dependence_evidence_minus_naive | -0.1212 [-0.1902, -0.0376] | 0.015913 | 10 | 0 |
| Luna | H3_sci_label | -0.0453 [-0.1199, 0.0302] | 0.29146 | 10 | 0 |
| Luna | H4_sci_false-label | 0.0348 [-0.0311, 0.0883] | 0.3085 | 10 | 0 |

Condition noise differences use paired seed rates on common valid null coordinates. All ten condition pairs per model, and pooled/news/momentum tests in both windows, are in `E_null_condition_tests`. All-tick omnibus and contrasts against naive are shown below; these tests are exploratory.

| Model | Test, all ticks pooled | Δ [95% CI] or statistic | Raw p |
|---|---|---|---:|
| DeepSeek | Friedman, 5 conditions | 10.7681 | 0.029297 |
| DeepSeek | naive_minus_punitive | 0.0046 [-0.0239, 0.0355] | 0.76853 |
| DeepSeek | naive_minus_label | 0.0264 [-0.0015, 0.0575] | 0.10286 |
| DeepSeek | naive_minus_evidence | -0.0004 [-0.0246, 0.0274] | 0.97928 |
| DeepSeek | naive_minus_false-label | 0.0289 [0.0092, 0.0525] | 0.020947 |
| Haiku | Friedman, 5 conditions | 6.1628 | 0.187316 |
| Haiku | naive_minus_punitive | -0.0402 [-0.0660, -0.0076] | 0.031727 |
| Haiku | naive_minus_label | -0.0198 [-0.0522, 0.0114] | 0.2849 |
| Haiku | naive_minus_evidence | -0.0332 [-0.0692, 0.0067] | 0.14219 |
| Haiku | naive_minus_false-label | -0.0248 [-0.0625, 0.0152] | 0.26762 |
| Luna | Friedman, 5 conditions | 3.4253 | 0.489329 |
| Luna | naive_minus_punitive | -0.0452 [-0.0932, 0.0013] | 0.10737 |
| Luna | naive_minus_label | 0.0120 [-0.0221, 0.0444] | 0.52092 |
| Luna | naive_minus_evidence | -0.0303 [-0.0698, 0.0057] | 0.17084 |
| Luna | naive_minus_false-label | 0.0056 [-0.0360, 0.0432] | 0.80151 |

## F. Persisted labels and post-treatment subgroups

Correct/stale describes whether the persisted pre-action label equals the current driver; the label condition becomes false when stale, whereas false-label becomes accidentally true. Shares below use all assigned primary decisions (exposure itself is logged even for invalid bases). No washout or stale-label exclusion is applied to original primaries.

| Model | Condition | Current true label | Currently false label | No feedback yet |
|---|---|---|---|---|
| DeepSeek | label | 1644/2400 (68.50%) | 756/2400 (31.50%) | 0/2400 (0.00%) |
| DeepSeek | false-label | 756/2400 (31.50%) | 1644/2400 (68.50%) | 0/2400 (0.00%) |
| Haiku | label | 828/1200 (69.00%) | 372/1200 (31.00%) | 0/1200 (0.00%) |
| Haiku | false-label | 372/1200 (31.00%) | 828/1200 (69.00%) | 0/1200 (0.00%) |
| Luna | label | 828/1200 (69.00%) | 372/1200 (31.00%) | 0/1200 (0.00%) |
| Luna | false-label | 372/1200 (31.00%) | 828/1200 (69.00%) | 0/1200 (0.00%) |

Subgroup CSD retains the opposite-current-driver selector of P4 for false-label, even when the actual false-label label is currently true. For label the table uses the P3 current-true-driver selector. Actual-label CSD and current/opposite citation and dependence in every subgroup are also reported in JSON. These are selected descriptive comparisons; the subgroup is defined from the target's post-treatment exposure.

| Model | Condition | Label currently | Adopt persisted label | Flip persisted label | CSD P3(label)/P4(false-label) [95% CI] | Raw p | Common n |
|---|---|---|---:|---:|---|---:|---:|
| DeepSeek | label | correct | 1.0000 | 0.9386 | -0.2169 [-0.2669, -0.1653] | 1.2893e-07 | 837 |
| DeepSeek | label | stale | 0.9907 | 0.8084 | 0.3325 [0.2531, 0.4138] | 2.3535e-07 | 370 |
| DeepSeek | label | no_label | NA | NA | NA [NA, NA] | 1 | 0 |
| DeepSeek | false-label | correct | 1.0000 | 0.9618 | 0.2983 [0.2295, 0.3630] | 6.7251e-08 | 370 |
| DeepSeek | false-label | stale | 0.9946 | 0.8302 | -0.3284 [-0.3928, -0.2687] | 4.3038e-09 | 837 |
| DeepSeek | false-label | no_label | NA | NA | NA [NA, NA] | 1 | 0 |
| Haiku | label | correct | 0.9122 | 0.8311 | -0.1029 [-0.1676, -0.0317] | 0.020546 | 417 |
| Haiku | label | stale | 0.7784 | 0.6188 | 0.1384 [0.0525, 0.2241] | 0.014484 | 177 |
| Haiku | label | no_label | NA | NA | NA [NA, NA] | 1 | 0 |
| Haiku | false-label | correct | 0.9028 | 0.8726 | 0.0624 [-0.0416, 0.1712] | 0.30419 | 177 |
| Haiku | false-label | stale | 0.8314 | 0.6606 | -0.0940 [-0.1600, -0.0265] | 0.028993 | 418 |
| Haiku | false-label | no_label | NA | NA | NA [NA, NA] | 1 | 0 |
| Luna | label | correct | 0.9773 | 0.8433 | -0.1234 [-0.2010, -0.0427] | 0.017598 | 415 |
| Luna | label | stale | 0.9456 | 0.5619 | 0.1786 [0.1021, 0.2574] | 0.002005 | 176 |
| Luna | label | no_label | NA | NA | NA [NA, NA] | 1 | 0 |
| Luna | false-label | correct | 0.9819 | 0.8437 | 0.0948 [0.0322, 0.1660] | 0.029071 | 176 |
| Luna | false-label | stale | 0.9568 | 0.6023 | 0.0151 [-0.0519, 0.0794] | 0.679 | 418 |
| Luna | false-label | no_label | NA | NA | NA [NA, NA] | 1 | 0 |

## G. Hedging and specificity

exclusive_true_within_probes=1[C={g}] (distractor may also be cited); only_true_reason=1[R={g}]. true_share_of_probed_citations=1[g in C]/|C| defined only when C nonempty; both drivers score .5. unconditional_true_minus_opposite_citation=1[g in R]-1[opposite(g) in R]; both or neither score zero.

Citing both drivers guarantees environmental audit PASS without identifying a specific driver. These rates use all valid primary base decisions and equal seed weights; counts, SD, CIs and all-tick rates are in JSON.

| Model | Condition | Both drivers | Exclusive true within probes | Only true reason | True share of probed citations | True − opposite citation |
|---|---|---:|---:|---:|---:|---:|
| DeepSeek | naive | 0.7200 | 0.1742 | 0.0000 | 0.5350 | 0.0700 |
| DeepSeek | punitive | 0.8238 | 0.1083 | 0.0000 | 0.5208 | 0.0417 |
| DeepSeek | label | 0.8229 | 0.1350 | 0.0383 | 0.5465 | 0.0929 |
| DeepSeek | evidence | 0.6800 | 0.1733 | 0.0000 | 0.5138 | 0.0275 |
| DeepSeek | false-label | 0.8383 | 0.0700 | 0.0175 | 0.4892 | -0.0217 |
| Haiku | naive | 0.3150 | 0.4108 | 0.0100 | 0.5888 | 0.1717 |
| Haiku | punitive | 0.2833 | 0.4267 | 0.0467 | 0.5868 | 0.1683 |
| Haiku | label | 0.3177 | 0.4855 | 0.2094 | 0.6508 | 0.2986 |
| Haiku | evidence | 0.2980 | 0.3852 | 0.0525 | 0.5532 | 0.1026 |
| Haiku | false-label | 0.3042 | 0.3192 | 0.1075 | 0.4740 | -0.0517 |
| Luna | naive | 0.4708 | 0.3475 | 0.0683 | 0.5887 | 0.1758 |
| Luna | punitive | 0.4750 | 0.3433 | 0.0642 | 0.5893 | 0.1758 |
| Luna | label | 0.5721 | 0.3194 | 0.1368 | 0.6060 | 0.2118 |
| Luna | evidence | 0.6093 | 0.2271 | 0.0300 | 0.5339 | 0.0676 |
| Luna | false-label | 0.5775 | 0.1850 | 0.0742 | 0.4741 | -0.0517 |

## H. Direction of the observed re-asks

BUY=+1, SELL=-1; original feature x, perturbed feature -x. New action reconstructed exactly from binary base action and logged flipped Boolean. Zero-valued features excluded only from sign alignment. Expected driver sign follows +0.02*x fundamental return, not the whole endogenous return.

Conditional-on-flip alignment is mechanically equivalent to baseline sign alignment under binary actions and sign reversal; it does not independently validate causal use. Inactive feature sign is a descriptive benchmark without fundamental-return effect. Tests against 0.5 are post hoc seed-level diagnostics with non-simultaneous CIs.

23970 valid primary feature re-ask records were verified against logged perturbed values. The table shows driver probes; non-driver sign benchmarks, zero-feature counts and transition tables are in JSON. No claim about economic optimality or full-return prediction follows from matching the fundamental component's sign.

| Model | Condition | Regime | Driver probes | Flips | New action follows flipped sign [seed 95% CI] | Among flips, follows sign (pooled) |
|---|---|---|---:|---:|---|---|
| Haiku | evidence | momentum | 300 | 177 | 0.7302 [0.6327, 0.8152] | 177/177 (100.00%) |
| Haiku | evidence | news | 294 | 139 | 0.7599 [0.6755, 0.8337] | 138/139 (99.28%) |
| Haiku | label | momentum | 299 | 214 | 0.8714 [0.8155, 0.9213] | 214/214 (100.00%) |
| Haiku | label | news | 296 | 182 | 0.8109 [0.7538, 0.8681] | 182/182 (100.00%) |
| Haiku | naive | momentum | 300 | 193 | 0.7745 [0.6767, 0.8465] | 192/193 (99.48%) |
| Haiku | naive | news | 296 | 127 | 0.7157 [0.6523, 0.7802] | 126/127 (99.21%) |
| Haiku | false-label | momentum | 299 | 139 | 0.6450 [0.5307, 0.7571] | 138/139 (99.28%) |
| Haiku | false-label | news | 296 | 103 | 0.6853 [0.5915, 0.7756] | 102/103 (99.03%) |
| Haiku | punitive | momentum | 300 | 199 | 0.7884 [0.7107, 0.8484] | 199/199 (100.00%) |
| Haiku | punitive | news | 296 | 144 | 0.7189 [0.6723, 0.7686] | 141/144 (97.92%) |
| DeepSeek | evidence | momentum | 604 | 437 | 0.8570 [0.8006, 0.9096] | 437/437 (100.00%) |
| DeepSeek | evidence | news | 603 | 205 | 0.6734 [0.6035, 0.7382] | 204/205 (99.51%) |
| DeepSeek | label | momentum | 604 | 470 | 0.9057 [0.8786, 0.9321] | 469/470 (99.79%) |
| DeepSeek | label | news | 603 | 376 | 0.7972 [0.7582, 0.8355] | 375/376 (99.73%) |
| DeepSeek | naive | momentum | 604 | 466 | 0.8769 [0.8306, 0.9196] | 466/466 (100.00%) |
| DeepSeek | naive | news | 603 | 253 | 0.7019 [0.6534, 0.7491] | 252/253 (99.60%) |
| DeepSeek | false-label | momentum | 604 | 273 | 0.6933 [0.6234, 0.7585] | 273/273 (100.00%) |
| DeepSeek | false-label | news | 603 | 212 | 0.6804 [0.6190, 0.7382] | 212/212 (100.00%) |
| DeepSeek | punitive | momentum | 604 | 445 | 0.8647 [0.8177, 0.9100] | 445/445 (100.00%) |
| DeepSeek | punitive | news | 603 | 297 | 0.7448 [0.6934, 0.7953] | 297/297 (100.00%) |
| Luna | evidence | momentum | 300 | 142 | 0.6479 [0.5539, 0.7407] | 140/142 (98.59%) |
| Luna | evidence | news | 294 | 167 | 0.7800 [0.7056, 0.8483] | 162/167 (97.01%) |
| Luna | label | momentum | 300 | 232 | 0.8859 [0.8458, 0.9251] | 232/232 (100.00%) |
| Luna | label | news | 294 | 177 | 0.8001 [0.7594, 0.8357] | 176/177 (99.44%) |
| Luna | naive | momentum | 300 | 182 | 0.7173 [0.6750, 0.7581] | 177/182 (97.25%) |
| Luna | naive | news | 296 | 182 | 0.7833 [0.7413, 0.8257] | 177/182 (97.25%) |
| Luna | false-label | momentum | 300 | 138 | 0.6160 [0.5195, 0.7110] | 134/138 (97.10%) |
| Luna | false-label | news | 296 | 119 | 0.6591 [0.5779, 0.7345] | 116/119 (97.48%) |
| Luna | punitive | momentum | 300 | 180 | 0.7273 [0.6706, 0.7823] | 176/180 (97.78%) |
| Luna | punitive | news | 296 | 175 | 0.7668 [0.6945, 0.8371] | 173/175 (98.86%) |

## I. Placebo verdict/label conflict

revealed_label/feedback in decision is persisted pre-action exposure; audit_event.revealed_label is generated after that action. Audits fail iff current true driver is absent; citing a false label alone fails if audited, citing both drivers passes. Observed associations are not causal effects.

| Model | Valid decisions | Persisted false label cited | Audited such citations | Failed and fined | Fine rate among audited citations | Failed/fined share of all valid decisions |
|---|---:|---:|---:|---:|---|---|
| Haiku | 1200 | 688 | 186 | 111 | 111/186 (59.68%) | 111/1200 (9.25%) |
| DeepSeek | 2400 | 1635 | 487 | 61 | 61/487 (12.53%) | 61/2400 (2.54%) |
| Luna | 1200 | 792 | 216 | 70 | 70/216 (32.41%) | 70/1200 (5.83%) |

## J. Why Haiku P4 has a negative bootstrap interval and p > .05

Haiku P4 Δ=-0.0571824; percentile bootstrap CI [-0.1045458, -0.0038759]. Paired t=-2.0857341, df=9, raw p=0.0666428, Holm p=0.2665711. Student-t 95% CI [-0.1192015, 0.0048368]. Seed-difference skewness=0.7738.

The descriptive percentile-bootstrap interval is not the inversion of the paired Student t test. With only ten seed differences, resampling their asymmetric empirical distribution can exclude zero while the wider t interval includes it. The registered inference uses the two-sided t p with Holm; the bootstrap interval makes no confirmatory rejection. Neither result is substituted for the other.

Seed differences: -0.066667, -0.161290, -0.127273, 0.076923, -0.137931, -0.104478, -0.068966, 0.000000, -0.071429, 0.089286.

## K. Actual evidence-window crossing and endogenous price impact

Nominal EVIDENCE_WINDOW=8 caps statistics, but caller supplies only _history_for(...)[-HISTORY_K:] (HISTORY_K=4) plus just-completed tick. Actual tables contain min(t+1,5) completed pairs, never 8. Every persisted table regenerated and matched byte-for-byte.

Verified 8721 persisted feedback instances. All primary audit tables have n=5. Audits on tick 39 are generated after the final decision and have no later prompt exposure; generation and exposure denominators are therefore distinct. Nominal eight-tick counts below use the same observed audit ticks and are a counterfactual recipe comparison, not a description of delivered tables.

| Model | Window | Actual mixed / generated | Nominal 8 mixed / same audits | Actual mixed / exposed prompts | Exposed windows ending in old regime |
|---|---|---|---|---|---|
| Haiku | overall | 218/696 (31.32%) | 361/696 (51.87%) | 763/2184 (34.94%) | 593/2184 (27.15%) |
| Haiku | primary | 150/344 (43.60%) | 249/344 (72.38%) | 549/1200 (45.75%) | 372/1200 (31.00%) |
| DeepSeek | overall | 433/1417 (30.56%) | 745/1417 (52.58%) | 1442/4353 (33.13%) | 1150/4353 (26.42%) |
| DeepSeek | primary | 294/718 (40.95%) | 507/718 (70.61%) | 996/2400 (41.50%) | 756/2400 (31.50%) |
| Luna | overall | 218/696 (31.32%) | 361/696 (51.87%) | 763/2184 (34.94%) | 593/2184 (27.15%) |
| Luna | primary | 150/344 (43.60%) | 249/344 (72.38%) | 549/1200 (45.75%) | 372/1200 (31.00%) |

Pearson corr(x_f,r), r=0.02*x_driver+0.03*I+epsilon; I=sum(signed requested order sizes)/(6*5). Cash/inventory settlement constraints and audit haircuts do not change requested-order imbalance. Returns are pre-price-floor Market.step values. Covariance numerator decomposes additively; normalization uses SD(r), so subtracting an impact correlation is not deconvolution.

An agent's own requested order contributes 0.03*s*q/30=0.001*s*q to the reported raw return, up to ±0.01. Correlations include this component without residualization. Order signs/sizes depend on feedback and features, so the correlation table can reflect the agents' own behavior. Spread/volume/orderflow/sentiment also enter the reported table. Cov(x,r)=0.02 Cov(x,x_driver)+0.03 Cov(x,I)+Cov(x,epsilon); dividing by sd(x)sd(r) gives its Pearson numerator decomposition.

Same actual table observations after subtracting 0.03*I from each realized return: fixed-path sensitivity, not an alternative market simulation or causal mediation estimate.

| Model | Primary mean absolute impact | Impact SD | Fundamental SD | Return SD | Mean absolute table-correlation change after removing impact |
|---|---:|---:|---:|---:|---:|
| Haiku | 0.0187 | 0.0197 | 0.0252 | 0.0420 | 0.1543 |
| DeepSeek | 0.0291 | 0.0305 | 0.0239 | 0.0501 | 0.2021 |
| Luna | 0.0189 | 0.0203 | 0.0252 | 0.0428 | 0.1474 |

Implementation-deviation disclosure:

> An implementation check established that the evidence builder received the four-tick display history plus the just-completed audited tick. Its registered eight-tick cap therefore operated on at most five observations. All primary-window audit tables used five observations; no eight-observation table was delivered. We retain the original data and confirmatory estimands and report this as an implementation deviation. The evidence-package estimates describe the implemented five-tick correlation feedback, and do not estimate an eight-tick intervention.

## L. Reproducibility facts

The literal full prompt definitions, response schema, persona mandates, per-condition sentences, feedback templates and exact six-feature DGP equations are in [prompt_and_dgp.md](prompt_and_dgp.md). Full payloads without messages, seed recipes, source hashes, confirmatory/exploratory software versions, retry/error counts, historical preregistration commits and collection timestamps are in `L_reproducibility`.

| Model | Provider / served route | Endpoint | Temperature | Collection ledger first UTC | Last UTC |
|---|---|---|---|---|---|
| deepseek-v4-flash | deepseek / direct | https://api.deepseek.com/chat/completions | 0 | 2026-10-27T12:45:03.673835+00:00 | 2026-10-27T16:11:56.841681+00:00 |
| anthropic/claude-haiku-5.5 | openrouter / ['anthropic'] | https://openrouter.ai/api/v1/chat/completions | omitted, provider default unrecorded | 2026-10-27T12:45:03.828004+00:00 | 2026-10-27T16:05:37.860518+00:00 |
| openai/gpt-6-luna | openrouter / ['openai'] | https://openrouter.ai/api/v1/chat/completions | omitted, provider default unrecorded | 2026-10-27T12:45:04.053069+00:00 | 2026-10-27T16:32:46.910858+00:00 |

Preregistration document date: 2026-10-26; initial committed registration: 95bd99b0c95ba6a0ef2e3a115f59391ffa4ebbd9 (2026-10-27T09:34:20+01:00). Amendment 1: 4268a9806981273cbf3aeaa42f54a7bc25136ecc; approval: c1833938a0266c015df875c6f6f9998ed9387a8b; Amendment 2 (budget/operations, 2026-10-27): 72d05151df3fd1944fb009dda7506707ff455c82. Renewed freeze marker commit: 9345e7d9854271cad336195b8f9ce624a14607c1. The original document's retained DRAFT header causes the confirmatory analyzer's metadata to say draft; the hash and recorded approval/freeze in FROZEN.json determine freeze provenance.

Current environment: python 3.12.2, numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, matplotlib 3.11.2, statsmodels 0.15.0, httpx 0.28.1, pytest 9.1.1.

## Not computable / interpretation limits

- Internal reasoning, necessary causal feature use, economic optimality and a calibrated latent explanation/behavior gap are not identified by binary sign-flip re-asks.
- A selected missing/invalid CF flip records no action; logs alone cannot always separate invalid JSON from a failed call. Neither is imputed.
- Provider internal sampling defaults, immutable model checkpoint and historical server software are not recorded; no numeric default temperature is inferred.
- Full raw API responses, raw output strings, returned immutable model IDs/versions and actual provider default sampling parameters are not persisted in confirm JSONL/ledger. Requested IDs and successful provider pins are available; numeric temperature/top_p for Haiku/Luna are not.
- Original collection environment versions beyond preregistered versions and original-analysis metadata are not independently archived.
- Source comment identifies the DeepSeek alias as V4.1 Flash, but ledger preserves requested alias only, not a response-verified backend version.
- Some Luna ledger entries have no served_by identity and usage missing; logs do not establish the backend/version for those requests.

## Offline reproduction

Run `python -m pytest -q tests/v2/test_exploratory_analyses.py` and `python -m pytest -q` for the focused checks and full public suite. Release validation is recorded in [VERIFICATION.md](../../../../VERIFICATION.md).

Reproduce offline with `python src/v2/exploratory_analyses.py`. The script asserts exact primary and registered-secondary reproduction and deterministic masks before writing. No volatile execution time is embedded in generated outputs. Public packaging changes documentation, source hashes and path provenance while preserving the scientific estimates and historical collection facts.
