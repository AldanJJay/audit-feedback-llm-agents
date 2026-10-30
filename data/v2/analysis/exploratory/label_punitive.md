# Post hoc label-minus-punitive package contrasts

Exploratory (not preregistered), descriptive, non-simultaneous 95% percentile intervals; raw two-sided paired Student t p values, no Holm correction.
Ticks 20–39; equal weights for the 20 DeepSeek seeds and the 10 Haiku/Luna seeds; both arms must have defined values at the same tick/agent coordinate.
The analysis imports the unchanged confirmatory estimators and checks point estimates, intervals, raw p values and effect sizes against the existing confirmatory estimator.
No inference API calls or new experiments were made; frozen confirmatory outputs were not modified.

| Model | Metric | n seed pairs | Common decisions | Delta | 95% CI | dz | Cohen h | Raw p |
|---|---|---:|---:|---:|---|---:|---:|---:|
| deepseek-v4-flash | environmental_fidelity | 20 | 2400 | 0.025833 | [0.010417, 0.040417] | 0.724559 | 0.114086 | 0.00430631 |
| deepseek-v4-flash | process_precision | 20 | 1204 | 0.036213 | [0.007804, 0.065275] | 0.533580 | 0.073014 | 0.02758231 |
| deepseek-v4-flash | dependence_true | 20 | 1207 | 0.086252 | [0.051708, 0.123758] | 1.025719 | 0.182018 | 0.00020123 |
| anthropic/claude-haiku-5.5 | environmental_fidelity | 10 | 1199 | 0.093459 | [0.060126, 0.133333] | 1.484499 | 0.218636 | 0.00112904 |
| anthropic/claude-haiku-5.5 | process_precision | 10 | 569 | 0.044468 | [-0.016502, 0.104775] | 0.432642 | 0.097549 | 0.20445208 |
| anthropic/claude-haiku-5.5 | dependence_true | 10 | 594 | 0.090845 | [0.057888, 0.125588] | 1.581546 | 0.187467 | 0.00073767 |
| openai/gpt-6-luna | environmental_fidelity | 10 | 1199 | 0.072598 | [0.044151, 0.098529] | 1.552596 | 0.207873 | 0.00083634 |
| openai/gpt-6-luna | process_precision | 10 | 581 | 0.019623 | [-0.031525, 0.074967] | 0.217405 | 0.041442 | 0.50909868 |
| openai/gpt-6-luna | dependence_true | 10 | 593 | 0.093863 | [0.027440, 0.158196] | 0.841211 | 0.195988 | 0.02603975 |

Sensitivity is the frequency of binary action changes after a sign flip. Process precision is restricted to complete probes with nonempty citations; environmental fidelity uses valid original responses, so its support can be larger.
These package contrasts do not identify an isolated label mechanism because the design was not factorial.
The artifact records all per-seed paired means, matched coordinates, support counts and source hashes; RNG 20261026 is reset for each 10,000-draw bootstrap as in the confirmatory estimator.
