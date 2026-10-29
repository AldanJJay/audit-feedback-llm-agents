# Counterfactual perturbation calibration on dev seeds

This report calibrates the counterfactual measuring instrument using development data only. It tests no hypothesis and includes no confirmatory data. The selected perturbation, if valid under the fixed rule below, is input for a dated preregistration amendment before confirmatory data are collected.

## Feature scales and perturbations

In `src/market.py`, each feature among news and momentum is drawn as a standard normal driver plus independent N(0, 0.7) noise when its regime is active, and as N(0, 0.7) noise when inactive. Thus the active-regime variance is 1 + 0.7² = 1.49 and the inactive-regime variance is 0.7² = 0.49. The two regimes are pooled equally, so each feature has population variance (1.49 + 0.49) / 2 = 0.99 and scale s_f = sqrt(0.99) = 0.994987. This derivation is for the generating values before the market stores them rounded to three decimal places; the rounding is negligible at the displayed precision.

For base BUY, dir = −1; for base SELL, dir = +1. `zero` replaces the feature with 0; `sign_flip` replaces v with −v; `adverse_1sd` and `adverse_2sd` use v + dir × 1 × s_f and v + dir × 2 × s_f; `extreme_v1` retains the preregistered values of ±6 for news and ±10 for momentum, directed against the base action. Every sampled valid decision received all five variants for both features. The five counterfactual calls for a given feature change only that feature value on the prompt’s final market-features line.

## Run design and spend

Each model ran naive at seeds 100 and 101, and label at seed 100, with six agents, 40 ticks, and the same reproducible 50% counterfactual mask. Each block contains 240 decisions and 1,140 counterfactual rows. All nine blocks have a completion marker.

Calibration spend: DeepSeek 0.366496 USD; OpenRouter 0.876592 USD.

## Flip rates by model, condition, variant, and regime

The true-driver rate is the flip rate for the feature matching the current market regime; the non-driver rate is the other feature. Rates use sampled decisions with a valid base action and boolean counterfactual result. Each rate is shown with its Wilson 95% confidence interval. `n true/non` gives the denominators for the two rates; `pooled` combines both current regimes and, for naive, both dev seeds.

| Model | Condition | Variant | Current regime | True-driver rate [95% CI] | Non-driver rate [95% CI] | Difference | n true/non |
|---|---|---|---|---:|---:|---:|---:|
| `deepseek-v4-flash` | naive | zero | news | 0.252 [0.182, 0.339] | 0.296 [0.220, 0.385] | -0.043 | 115/115 |
| `deepseek-v4-flash` | naive | zero | momentum | 0.292 [0.216, 0.382] | 0.133 [0.082, 0.208] | +0.159 | 113/113 |
| `deepseek-v4-flash` | naive | zero | pooled | 0.272 [0.218, 0.333] | 0.215 [0.167, 0.273] | +0.057 | 228/228 |
| `deepseek-v4-flash` | naive | sign_flip | news | 0.383 [0.299, 0.474] | 0.548 [0.457, 0.636] | -0.165 | 115/115 |
| `deepseek-v4-flash` | naive | sign_flip | momentum | 0.699 [0.609, 0.776] | 0.159 [0.103, 0.238] | +0.540 | 113/113 |
| `deepseek-v4-flash` | naive | sign_flip | pooled | 0.539 [0.475, 0.603] | 0.355 [0.296, 0.419] | +0.184 | 228/228 |
| `deepseek-v4-flash` | naive | adverse_1sd | news | 0.478 [0.389, 0.569] | 0.696 [0.606, 0.772] | -0.217 | 115/115 |
| `deepseek-v4-flash` | naive | adverse_1sd | momentum | 0.487 [0.397, 0.578] | 0.381 [0.296, 0.473] | +0.106 | 113/113 |
| `deepseek-v4-flash` | naive | adverse_1sd | pooled | 0.482 [0.418, 0.547] | 0.539 [0.475, 0.603] | -0.057 | 228/228 |
| `deepseek-v4-flash` | naive | adverse_2sd | news | 0.739 [0.652, 0.811] | 0.826 [0.747, 0.885] | -0.087 | 115/115 |
| `deepseek-v4-flash` | naive | adverse_2sd | momentum | 0.805 [0.723, 0.868] | 0.522 [0.431, 0.612] | +0.283 | 113/113 |
| `deepseek-v4-flash` | naive | adverse_2sd | pooled | 0.772 [0.713, 0.822] | 0.675 [0.612, 0.733] | +0.096 | 228/228 |
| `deepseek-v4-flash` | naive | extreme_v1 | news | 0.948 [0.891, 0.976] | 0.835 [0.756, 0.892] | +0.113 | 115/115 |
| `deepseek-v4-flash` | naive | extreme_v1 | momentum | 0.912 [0.845, 0.951] | 0.903 [0.834, 0.945] | +0.009 | 113/113 |
| `deepseek-v4-flash` | naive | extreme_v1 | pooled | 0.930 [0.889, 0.956] | 0.868 [0.818, 0.906] | +0.061 | 228/228 |
| `deepseek-v4-flash` | label | zero | news | 0.390 [0.276, 0.517] | 0.085 [0.037, 0.184] | +0.305 | 59/59 |
| `deepseek-v4-flash` | label | zero | momentum | 0.345 [0.234, 0.477] | 0.073 [0.029, 0.173] | +0.273 | 55/55 |
| `deepseek-v4-flash` | label | zero | pooled | 0.368 [0.286, 0.460] | 0.079 [0.042, 0.143] | +0.289 | 114/114 |
| `deepseek-v4-flash` | label | sign_flip | news | 0.627 [0.500, 0.739] | 0.203 [0.120, 0.323] | +0.424 | 59/59 |
| `deepseek-v4-flash` | label | sign_flip | momentum | 0.818 [0.697, 0.898] | 0.164 [0.089, 0.283] | +0.655 | 55/55 |
| `deepseek-v4-flash` | label | sign_flip | pooled | 0.719 [0.631, 0.794] | 0.184 [0.124, 0.265] | +0.535 | 114/114 |
| `deepseek-v4-flash` | label | adverse_1sd | news | 0.559 [0.433, 0.678] | 0.322 [0.217, 0.449] | +0.237 | 59/59 |
| `deepseek-v4-flash` | label | adverse_1sd | momentum | 0.400 [0.281, 0.532] | 0.164 [0.089, 0.283] | +0.236 | 55/55 |
| `deepseek-v4-flash` | label | adverse_1sd | pooled | 0.482 [0.393, 0.573] | 0.246 [0.176, 0.332] | +0.237 | 114/114 |
| `deepseek-v4-flash` | label | adverse_2sd | news | 0.661 [0.534, 0.769] | 0.373 [0.261, 0.500] | +0.288 | 59/59 |
| `deepseek-v4-flash` | label | adverse_2sd | momentum | 0.582 [0.450, 0.703] | 0.236 [0.144, 0.363] | +0.345 | 55/55 |
| `deepseek-v4-flash` | label | adverse_2sd | pooled | 0.623 [0.531, 0.706] | 0.307 [0.230, 0.397] | +0.316 | 114/114 |
| `deepseek-v4-flash` | label | extreme_v1 | news | 0.915 [0.816, 0.963] | 0.390 [0.276, 0.517] | +0.525 | 59/59 |
| `deepseek-v4-flash` | label | extreme_v1 | momentum | 0.909 [0.804, 0.961] | 0.327 [0.218, 0.459] | +0.582 | 55/55 |
| `deepseek-v4-flash` | label | extreme_v1 | pooled | 0.912 [0.846, 0.952] | 0.360 [0.277, 0.451] | +0.553 | 114/114 |
| `anthropic/claude-haiku-5.5` | naive | zero | news | 0.261 [0.189, 0.348] | 0.183 [0.123, 0.263] | +0.078 | 115/115 |
| `anthropic/claude-haiku-5.5` | naive | zero | momentum | 0.221 [0.155, 0.306] | 0.133 [0.082, 0.208] | +0.088 | 113/113 |
| `anthropic/claude-haiku-5.5` | naive | zero | pooled | 0.241 [0.190, 0.301] | 0.158 [0.116, 0.211] | +0.083 | 228/228 |
| `anthropic/claude-haiku-5.5` | naive | sign_flip | news | 0.461 [0.373, 0.552] | 0.391 [0.307, 0.483] | +0.070 | 115/115 |
| `anthropic/claude-haiku-5.5` | naive | sign_flip | momentum | 0.540 [0.448, 0.629] | 0.177 [0.118, 0.258] | +0.363 | 113/113 |
| `anthropic/claude-haiku-5.5` | naive | sign_flip | pooled | 0.500 [0.436, 0.564] | 0.285 [0.230, 0.347] | +0.215 | 228/228 |
| `anthropic/claude-haiku-5.5` | naive | adverse_1sd | news | 0.461 [0.373, 0.552] | 0.565 [0.474, 0.652] | -0.104 | 115/115 |
| `anthropic/claude-haiku-5.5` | naive | adverse_1sd | momentum | 0.354 [0.272, 0.446] | 0.283 [0.208, 0.372] | +0.071 | 113/113 |
| `anthropic/claude-haiku-5.5` | naive | adverse_1sd | pooled | 0.408 [0.346, 0.473] | 0.425 [0.363, 0.490] | -0.018 | 228/228 |
| `anthropic/claude-haiku-5.5` | naive | adverse_2sd | news | 0.739 [0.652, 0.811] | 0.600 [0.509, 0.685] | +0.139 | 115/115 |
| `anthropic/claude-haiku-5.5` | naive | adverse_2sd | momentum | 0.575 [0.483, 0.662] | 0.469 [0.380, 0.561] | +0.106 | 113/113 |
| `anthropic/claude-haiku-5.5` | naive | adverse_2sd | pooled | 0.658 [0.594, 0.716] | 0.535 [0.470, 0.599] | +0.123 | 228/228 |
| `anthropic/claude-haiku-5.5` | naive | extreme_v1 | news | 0.809 [0.727, 0.870] | 0.713 [0.625, 0.788] | +0.096 | 115/115 |
| `anthropic/claude-haiku-5.5` | naive | extreme_v1 | momentum | 0.761 [0.675, 0.830] | 0.504 [0.414, 0.595] | +0.257 | 113/113 |
| `anthropic/claude-haiku-5.5` | naive | extreme_v1 | pooled | 0.785 [0.727, 0.833] | 0.610 [0.545, 0.671] | +0.175 | 228/228 |
| `anthropic/claude-haiku-5.5` | label | zero | news | 0.271 [0.174, 0.396] | 0.220 [0.134, 0.341] | +0.051 | 59/59 |
| `anthropic/claude-haiku-5.5` | label | zero | momentum | 0.296 [0.191, 0.428] | 0.073 [0.029, 0.173] | +0.224 | 54/55 |
| `anthropic/claude-haiku-5.5` | label | zero | pooled | 0.283 [0.208, 0.372] | 0.149 [0.095, 0.226] | +0.134 | 113/114 |
| `anthropic/claude-haiku-5.5` | label | sign_flip | news | 0.559 [0.433, 0.678] | 0.237 [0.147, 0.360] | +0.322 | 59/59 |
| `anthropic/claude-haiku-5.5` | label | sign_flip | momentum | 0.800 [0.676, 0.884] | 0.130 [0.064, 0.244] | +0.670 | 55/54 |
| `anthropic/claude-haiku-5.5` | label | sign_flip | pooled | 0.675 [0.585, 0.754] | 0.186 [0.125, 0.267] | +0.490 | 114/113 |
| `anthropic/claude-haiku-5.5` | label | adverse_1sd | news | 0.508 [0.384, 0.632] | 0.254 [0.161, 0.378] | +0.254 | 59/59 |
| `anthropic/claude-haiku-5.5` | label | adverse_1sd | momentum | 0.418 [0.297, 0.550] | 0.164 [0.089, 0.283] | +0.255 | 55/55 |
| `anthropic/claude-haiku-5.5` | label | adverse_1sd | pooled | 0.465 [0.376, 0.556] | 0.211 [0.146, 0.294] | +0.254 | 114/114 |
| `anthropic/claude-haiku-5.5` | label | adverse_2sd | news | 0.695 [0.569, 0.797] | 0.288 [0.188, 0.414] | +0.407 | 59/59 |
| `anthropic/claude-haiku-5.5` | label | adverse_2sd | momentum | 0.691 [0.560, 0.797] | 0.255 [0.158, 0.383] | +0.436 | 55/55 |
| `anthropic/claude-haiku-5.5` | label | adverse_2sd | pooled | 0.693 [0.603, 0.770] | 0.272 [0.199, 0.360] | +0.421 | 114/114 |
| `anthropic/claude-haiku-5.5` | label | extreme_v1 | news | 0.847 [0.735, 0.918] | 0.322 [0.217, 0.449] | +0.525 | 59/59 |
| `anthropic/claude-haiku-5.5` | label | extreme_v1 | momentum | 0.873 [0.760, 0.937] | 0.255 [0.158, 0.383] | +0.618 | 55/55 |
| `anthropic/claude-haiku-5.5` | label | extreme_v1 | pooled | 0.860 [0.784, 0.912] | 0.289 [0.214, 0.379] | +0.570 | 114/114 |
| `openai/gpt-6-luna` | naive | zero | news | 0.304 [0.228, 0.394] | 0.174 [0.115, 0.253] | +0.130 | 115/115 |
| `openai/gpt-6-luna` | naive | zero | momentum | 0.257 [0.185, 0.344] | 0.150 [0.096, 0.228] | +0.106 | 113/113 |
| `openai/gpt-6-luna` | naive | zero | pooled | 0.281 [0.226, 0.342] | 0.162 [0.120, 0.216] | +0.118 | 228/228 |
| `openai/gpt-6-luna` | naive | sign_flip | news | 0.504 [0.414, 0.594] | 0.270 [0.197, 0.357] | +0.235 | 115/115 |
| `openai/gpt-6-luna` | naive | sign_flip | momentum | 0.487 [0.397, 0.578] | 0.230 [0.162, 0.316] | +0.257 | 113/113 |
| `openai/gpt-6-luna` | naive | sign_flip | pooled | 0.496 [0.431, 0.560] | 0.250 [0.198, 0.310] | +0.246 | 228/228 |
| `openai/gpt-6-luna` | naive | adverse_1sd | news | 0.539 [0.448, 0.627] | 0.504 [0.414, 0.594] | +0.035 | 115/115 |
| `openai/gpt-6-luna` | naive | adverse_1sd | momentum | 0.384 [0.299, 0.476] | 0.460 [0.371, 0.552] | -0.076 | 112/113 |
| `openai/gpt-6-luna` | naive | adverse_1sd | pooled | 0.463 [0.399, 0.528] | 0.482 [0.418, 0.547] | -0.020 | 227/228 |
| `openai/gpt-6-luna` | naive | adverse_2sd | news | 0.783 [0.699, 0.848] | 0.687 [0.597, 0.765] | +0.096 | 115/115 |
| `openai/gpt-6-luna` | naive | adverse_2sd | momentum | 0.681 [0.591, 0.760] | 0.770 [0.684, 0.838] | -0.088 | 113/113 |
| `openai/gpt-6-luna` | naive | adverse_2sd | pooled | 0.732 [0.671, 0.786] | 0.728 [0.667, 0.782] | +0.004 | 228/228 |
| `openai/gpt-6-luna` | naive | extreme_v1 | news | 0.965 [0.914, 0.986] | 0.739 [0.652, 0.811] | +0.226 | 115/115 |
| `openai/gpt-6-luna` | naive | extreme_v1 | momentum | 0.956 [0.901, 0.981] | 0.991 [0.952, 0.998] | -0.035 | 113/113 |
| `openai/gpt-6-luna` | naive | extreme_v1 | pooled | 0.961 [0.927, 0.979] | 0.864 [0.813, 0.903] | +0.096 | 228/228 |
| `openai/gpt-6-luna` | label | zero | news | 0.305 [0.203, 0.431] | 0.102 [0.047, 0.205] | +0.203 | 59/59 |
| `openai/gpt-6-luna` | label | zero | momentum | 0.345 [0.234, 0.477] | 0.073 [0.029, 0.173] | +0.273 | 55/55 |
| `openai/gpt-6-luna` | label | zero | pooled | 0.325 [0.246, 0.415] | 0.088 [0.048, 0.154] | +0.237 | 114/114 |
| `openai/gpt-6-luna` | label | sign_flip | news | 0.508 [0.384, 0.632] | 0.237 [0.147, 0.360] | +0.271 | 59/59 |
| `openai/gpt-6-luna` | label | sign_flip | momentum | 0.764 [0.637, 0.856] | 0.164 [0.089, 0.283] | +0.600 | 55/55 |
| `openai/gpt-6-luna` | label | sign_flip | pooled | 0.632 [0.540, 0.714] | 0.202 [0.138, 0.285] | +0.430 | 114/114 |
| `openai/gpt-6-luna` | label | adverse_1sd | news | 0.593 [0.466, 0.709] | 0.237 [0.147, 0.360] | +0.356 | 59/59 |
| `openai/gpt-6-luna` | label | adverse_1sd | momentum | 0.436 [0.314, 0.567] | 0.218 [0.129, 0.344] | +0.218 | 55/55 |
| `openai/gpt-6-luna` | label | adverse_1sd | pooled | 0.518 [0.427, 0.607] | 0.228 [0.161, 0.313] | +0.289 | 114/114 |
| `openai/gpt-6-luna` | label | adverse_2sd | news | 0.661 [0.534, 0.769] | 0.458 [0.337, 0.583] | +0.203 | 59/59 |
| `openai/gpt-6-luna` | label | adverse_2sd | momentum | 0.655 [0.523, 0.766] | 0.418 [0.297, 0.550] | +0.236 | 55/55 |
| `openai/gpt-6-luna` | label | adverse_2sd | pooled | 0.658 [0.567, 0.739] | 0.439 [0.351, 0.530] | +0.219 | 114/114 |
| `openai/gpt-6-luna` | label | extreme_v1 | news | 0.966 [0.885, 0.991] | 0.508 [0.384, 0.632] | +0.458 | 59/59 |
| `openai/gpt-6-luna` | label | extreme_v1 | momentum | 0.927 [0.827, 0.971] | 0.455 [0.330, 0.585] | +0.473 | 55/55 |
| `openai/gpt-6-luna` | label | extreme_v1 | pooled | 0.947 [0.890, 0.976] | 0.482 [0.393, 0.573] | +0.465 | 114/114 |

## Fixed selection rule

Eligibility is based on naive pooled true-driver flip rates: every model must lie in [0.10, 0.90]. For eligible variants, discrimination is the true-driver rate minus the non-driver rate, and the objective is the minimum discrimination across models. Scores within 0.02 of the maximum are treated as ties and resolved by the fixed smaller-perturbation order: zero, sign_flip, adverse_1sd, adverse_2sd, extreme_v1. No variant is recommended if none is eligible or the best minimum discrimination is below 0.15.

- `zero` is eligible; pooled naive true-driver rates are deepseek-v4-flash: 0.272, anthropic/claude-haiku-5.5: 0.241, openai/gpt-6-luna: 0.281; model discriminations are deepseek-v4-flash: +0.057, anthropic/claude-haiku-5.5: +0.083, openai/gpt-6-luna: +0.118; minimum discrimination +0.057.
- `sign_flip` is eligible; pooled naive true-driver rates are deepseek-v4-flash: 0.539, anthropic/claude-haiku-5.5: 0.500, openai/gpt-6-luna: 0.496; model discriminations are deepseek-v4-flash: +0.184, anthropic/claude-haiku-5.5: +0.215, openai/gpt-6-luna: +0.246; minimum discrimination +0.184.
- `adverse_1sd` is eligible; pooled naive true-driver rates are deepseek-v4-flash: 0.482, anthropic/claude-haiku-5.5: 0.408, openai/gpt-6-luna: 0.463; model discriminations are deepseek-v4-flash: -0.057, anthropic/claude-haiku-5.5: -0.018, openai/gpt-6-luna: -0.020; minimum discrimination -0.057.
- `adverse_2sd` is eligible; pooled naive true-driver rates are deepseek-v4-flash: 0.772, anthropic/claude-haiku-5.5: 0.658, openai/gpt-6-luna: 0.732; model discriminations are deepseek-v4-flash: +0.096, anthropic/claude-haiku-5.5: +0.123, openai/gpt-6-luna: +0.004; minimum discrimination +0.004.
- `extreme_v1` is ineligible because at least one model’s pooled naive true-driver rate falls outside [0.10, 0.90].

**Selection result: `sign_flip`.** Its minimum-across-models discrimination is 0.184, above the 0.15 threshold. The selected variant is an instrument-calibration input for a dated amendment; this result is not a hypothesis test.

### Label-condition rates for the selected variant

These descriptive rates show the selected instrument’s behavior in the label condition; they do not determine selection.

| Model | Current regime | True-driver rate [95% CI] | Non-driver rate [95% CI] | Difference | n true/non |
|---|---|---:|---:|---:|---:|
| `deepseek-v4-flash` | news | 0.627 [0.500, 0.739] | 0.203 [0.120, 0.323] | +0.424 | 59/59 |
| `deepseek-v4-flash` | momentum | 0.818 [0.697, 0.898] | 0.164 [0.089, 0.283] | +0.655 | 55/55 |
| `deepseek-v4-flash` | pooled | 0.719 [0.631, 0.794] | 0.184 [0.124, 0.265] | +0.535 | 114/114 |
| `anthropic/claude-haiku-5.5` | news | 0.559 [0.433, 0.678] | 0.237 [0.147, 0.360] | +0.322 | 59/59 |
| `anthropic/claude-haiku-5.5` | momentum | 0.800 [0.676, 0.884] | 0.130 [0.064, 0.244] | +0.670 | 55/54 |
| `anthropic/claude-haiku-5.5` | pooled | 0.675 [0.585, 0.754] | 0.186 [0.125, 0.267] | +0.490 | 114/113 |
| `openai/gpt-6-luna` | news | 0.508 [0.384, 0.632] | 0.237 [0.147, 0.360] | +0.271 | 59/59 |
| `openai/gpt-6-luna` | momentum | 0.764 [0.637, 0.856] | 0.164 [0.089, 0.283] | +0.600 | 55/55 |
| `openai/gpt-6-luna` | pooled | 0.632 [0.540, 0.714] | 0.202 [0.138, 0.285] | +0.430 | 114/114 |

## Interpretation

These are development-seed measurements used to calibrate an instrument before confirmatory data collection. The selection rule was applied as fixed in advance. The PI can use the selected variant and the reported uncertainty as input to a dated preregistration amendment; no confirmatory conclusion follows from these data.
