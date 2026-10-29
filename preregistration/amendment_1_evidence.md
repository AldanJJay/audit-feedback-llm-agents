# Amendment 1 evidence — 2026-10-27

This is the development-evidence record for Amendment 1 in
`docs/ns-b2/preregistration.md` and the `amendments` entry in
`research-contract-v2.yaml`. It contains no confirmatory result. The original
preregistration and contract remain intact above their appended amendments;
PI answers, T12 verification, and the coordinator's freeze marker are pending.

## Instrument failure, calibration, and noise

| Finding | Evidence path and location | Development result |
|---|---|---|
| Original extreme fails its registered ceiling gate | `data/v2/analysis/pilot/report.md`, "Pilot validity gate"; `data/v2/analysis/pilot/results.json`, `pilot_validity` | DeepSeek naive true driver 109/114 = 0.956, above the original 0.95 ceiling. |
| Extreme can flip the non-driver almost as often as the driver | Same report, naive momentum-regime rows | DeepSeek true/non-driver 0.927/0.945; Luna 0.891/0.982. These are regime diagnostics, not additional original gates. |
| Fixed calibration rule selects sign reversal | `docs/ns-b2/calibration_report.md`, "Fixed selection rule" | Every model's naive true-driver rate must be in [0.10, 0.90]; maximize minimum discrimination, require at least 0.15, use fixed 0.02 ties and perturbation ordering. `sign_flip` minimum discrimination is 0.184. |
| Sign reversal exceeds the null floor | `docs/ns-b2/noise_report.md`, "Rates", "Two-call sensitivity check", and "Answers to the calibration questions" | Naive pooled null rates 0.043/0.041/0.053 for DeepSeek/Haiku/Luna; noise-adjusted eligibility holds and minimum discrimination is 0.197. |
| Noise varies across conditions | Same noise report | Label null rates 0.009/0.064/0.033; estimate separately per model × condition in confirmation. |
| Pilot stopped by PI | Git commit `bef0c18e5237eb5338525f6f71b0c27ab2b224a1`, message and retained pilot data | Incomplete pilot blocks are documented, not silently completed or replaced. |
| PI/coordinator saw descriptive label rates | Calibration report, "Label-condition rates for the selected variant"; noise report, "Rates" | Calibration true-driver sign-flip rates are higher in label than naive for all three required models; label uses seed 100, naive pools 100–101. This exposure is disclosed, not treated as a confirmatory comparison. |

Calibration's rule was fixed before calibration data, as recorded in the
calibration report and task specification; the git commit below records the
implementation, report, and artifacts together, rather than separately proving
the time the rule was fixed. Its naive pooled sign-flip results are:

| Model | True-driver rate | Non-driver rate | Discrimination | Noise-run net true | Noise-run net non-driver | Noise-run discrimination |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek | 0.539 | 0.355 | 0.184 | 0.527 | 0.295 | 0.232 |
| Haiku | 0.500 | 0.285 | 0.215 | 0.437 | 0.240 | 0.197 |
| Luna | 0.496 | 0.250 | 0.246 | 0.447 | 0.241 | 0.206 |

Calibration and noise are separate development runs on the same dev seeds;
their rates need not be identical. Subtracting a common model × condition null
rate from true and non-driver rates cancels in their difference, so the net
discrimination is algebraically unchanged within the noise runs. It does not
establish a noise-free internal causal mechanism. Null non-overlap comparisons
and the two-call sensitivity are descriptive development checks.

The retained model directories are:

- `data/v2/deepseek-v4-flash/`
- `data/v2/anthropic-claude-haiku-5.5/`
- `data/v2/openai-gpt-6-luna/`

Each contains `calib/naive_seed_100.jsonl`, `calib/naive_seed_101.jsonl`,
`calib/label_seed_100.jsonl`, the analogous three files under `noise/`, and their
`.summary.json` companions. Original `pilot/` and `smoke/` artifacts remain;
incomplete blocks are listed in the pilot analysis. DeepSeek duplicate-run
artifacts remain under `data/v2/deepseek-v4-flash/noise_quarantine/` and are
excluded from noise analysis. The noise report discloses the extra-null-call
implementation error and the overlapping-process incident. All their costs
remain in the provider ledger. No development artifacts enter confirmation.

## Endpoint behavior and payload fidelity

`src/v2/models.py` records the **2026-10-27** endpoint checks, provider pins,
and temperature support flags. On that date, no endpoint in the
[Haiku listing](https://openrouter.ai/api/v1/models/anthropic/claude-haiku-5.5/endpoints)
or [Luna listing](https://openrouter.ai/api/v1/models/openai/gpt-6-luna/endpoints)
listed `temperature` among `supported_parameters`. This was rechecked while
authoring this record. The counts were ten listed Haiku endpoints and seven
listed Luna endpoints, including regional/service-tier entries. Their sampling
therefore uses provider defaults, with temperature omitted.

`src/v2/llm.py`, `src/v2/models.py`, and `tests/v2/test_llm.py` implement/document
Anthropic/OpenAI/Alibaba pins for Haiku/Luna/Qwen, disabled fallback, denied data
collection, returned `served_by`, and charged provider-mismatch failure. Git
commit `717c23e` records this transport correction; `data/v2/ledger.jsonl` has
four `t9-verify` calls, including the provider-mismatch development check.
The noise report verifies the pinned providers in the noise-tagged responses.
DeepSeek stays on its direct API at temperature 0; its legacy model alias and
the conservative peak-price snapshot are recorded in `src/v2/models.py`.

`docs/ns-b2/opencode_probe_report.md` records the free OpenCode CLI **no-go**.
The direct comparisons in `tools/opencode_probe/captures/payload_comparison.json`
all fail exact messages: runtime system additions and quoted user text change
the payload, and an additional request generates a title. Raw decision requests
are `tools/opencode_probe/captures/{naive,label,evidence}_request_2.json`;
the corresponding `_request_1.json` files show title generation.
`tools/opencode_probe/captures/real_model_runs.json` records authentication-only
failures for the attempted free model; these cannot establish model latency,
determinism, or temperature compliance.

## Ledger snapshot and measured projection

Source: `data/v2/ledger.jsonl`, **26,231 rows**, latest timestamp
**2026-10-27 12:16:35 UTC**. Snapshot SHA-256:
`fcd0c545c307e0351e70393f4b447b9ecd9cb32b2bf25f6813b3b9e41726d5f2`.
Both provider reservation files were empty objects when checked; no outstanding
reservation is added to this snapshot. Future checks must reload the live ledger.

For each model m, let B_m be usage-bearing ledger rows excluding
`billed_conservatively` and `usage_missing` rows, and let
u_m = sum(cost_usd in B_m) / |B_m|. This measures cost per recorded attempt,
including measured failed-provider calls and development duplicates; invalid
outputs are not free. One unknown-usage DeepSeek `ReadError` charge is excluded
from B_m but retained in spending to date. Dry-run 512-token output estimates
are not ledger measurements and are excluded from u_m. No observed ledger row
has 512 completion tokens at this snapshot.

| Model | Measured attempts | Unit cost | Per 1,000 attempts | Measured spend | All ledger spend |
|---|---:|---:|---:|---:|---:|
| DeepSeek | 10,295 | USD 9.152 × 10⁻⁵ | USD 0.092 | USD 0.942 | USD 0.944 |
| Haiku | 7,931 | USD 1.317 × 10⁻⁴ | USD 0.132 | USD 1.045 | USD 1.045 |
| Luna | 8,003 | USD 7.744 × 10⁻⁵ | USD 0.077 | USD 0.620 | USD 0.620 |
| Qwen, short verification | 1 | USD 8.200 × 10⁻⁶ | USD 0.008 | USD 8.200 × 10⁻⁶ | USD 8.200 × 10⁻⁶ |

Use full precision from the ledger rather than the rounded table entries.
The DeepSeek unknown-usage reservation is USD 0.001 at three decimal places;
rounding explains why rounded component spends need not add exactly.
Its observed cache-hit and cache-miss counts enter the ledger's peak-price
calculation. Confirmation cost is projected from these actual recorded usage
costs, not from a hypothetical 512-token completion on every call.

Expected calls per condition × seed block are
240 + 2 × (240 × 0.50) + 1 × (240 × 0.50 × 0.20) = **504**.
This is an expectation under the registered Bernoulli masks, not a quota or an
instruction to top up the sample. Real mask counts, token lengths, missingness,
and transport retries can change cost; a block has at most 960 requested calls
without retries if every CF and null mask entry is selected.

| Model | Blocks | Base / CF / null calls | Base cost | CF cost | Null cost | Total confirmation |
|---|---:|---|---:|---:|---:|---:|
| DeepSeek | 100 | 24,000 / 24,000 / 2,400 | USD 2.196 | USD 2.196 | USD 0.220 | USD 4.612 |
| Haiku | 50 | 12,000 / 12,000 / 1,200 | USD 1.580 | USD 1.580 | USD 0.158 | USD 3.319 |
| Luna | 50 | 12,000 / 12,000 / 1,200 | USD 0.929 | USD 0.929 | USD 0.093 | USD 1.951 |

Required confirmation expects 100,800 calls in total. Required OpenRouter
confirmation is USD 5.270. A dev-evidence-only unit-rate check using just `calib`
and `noise` ledger tags projects USD 4.496 DeepSeek, USD 3.294 Haiku, and
USD 1.955 Luna; the primary all-measured projection above also retains original
pilot/smoke and verification costs in its rate estimate and spending totals.

| Provider | Spent | Cap | Current headroom | Confirmation | Spent + confirmation | Projected headroom |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek | USD 0.944 | USD 8.000 | USD 7.056 | USD 4.612 | USD 5.556 | USD 2.444 |
| OpenRouter | USD 1.664 | USD 8.000 | USD 6.336 | USD 5.270 | USD 6.935 | USD 1.065 |

The coordinator's planning instruction reserves **USD 0.600 OpenRouter for
adversarial review**, leaving **USD 0.465** after required confirmation. Optional
exploratory Qwen is removed on cost feasibility. Its single 39-input/5-output
token verification is not representative; a sizing proxy applies Qwen's recorded
token prices to Luna's observed average study traffic, giving **USD 2.751** for
25,200 calls. This proxy is not a Qwen observation or a selected model substitution.

## DeepSeek risk scenario and PI contingency

Measured DeepSeek averages are about 674.896 input and 19.506 output tokens per
usage-bearing attempt. The ledger includes 4,704,896 cache-hit tokens and
2,243,117 cache-miss tokens for those attempts. At the recorded peak prices,
repricing **all** input tokens as misses gives a no-cache scenario of **USD
11.384** for 50,400 calls, **USD 12.328** with spending to date, **USD 4.328**
above the cap. The observed cache-inclusive **USD 4.612** remains the primary
projection; the no-cache scenario is a risk, not the expected bill or a strict
upper bound on future costs.

[DeepSeek's official pricing](https://api-docs.deepseek.com/quick_start/pricing/),
checked **2026-10-27**, states peak rates per million tokens of USD 0.006 cached
input, USD 0.300 uncached input, and USD 1.200 output, with off-peak rates half
as large. Peak periods are Monday–Friday 01:00–04:00 and 06:00–10:00 UTC,
excluding Chinese public holidays. The same observed-token no-cache scenario
at off-peak prices is **USD 5.692**, or **USD 6.636** with spending to date.
These calculations retain observed completion lengths and do not assume 512
output tokens. The ledger implementation conservatively uses its peak snapshot;
half-price billing must not be assumed to reduce the enforced ledger unless the
coordinator verifies its accounting before any PI-approved timing change.

Ask the PI to pre-approve a pause for disposition if cumulative DeepSeek ledger
spending reaches **USD 7.000** during confirmation. Off-peak execution or routing
through OpenRouter `deepseek/deepseek-v4.1-flash` with **both provider and
quantization pinned** are the only budget contingency options. No option is
chosen here. The coordinator must obtain the PI's choice, rerun the feasibility
gate with remaining required blocks and review reserve, and document any
post-freeze change as Amendment 2 before execution. A different route cannot be
silently pooled with the original route; the original cohort-disclosure rules
still apply. The code's project-wide USD 8/provider reservation cap remains
binding even if a projection is optimistic.

## Read-only calculation to reproduce the projection

Run from the repository root with the existing environment. This reads the
ledger and model snapshot, makes no API calls, and writes no output files.

```bash
.venv/bin/python - <<'PY'
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from src.v2.models import MODELS

path = Path('data/v2/ledger.jsonl')
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
print('rows', len(rows), 'sha256', hashlib.sha256(path.read_bytes()).hexdigest())
print('latest', max(row['timestamp'] for row in rows))
spent = defaultdict(Decimal)
projected = defaultdict(Decimal)
for row in rows:
    spent[row['provider']] += Decimal(str(row['cost_usd']))
for model, spec in MODELS.items():
    measured = [row for row in rows if row['model'] == model
                and not row.get('billed_conservatively')
                and not row.get('usage_missing')
                and row['prompt_tokens'] + row['completion_tokens'] > 0]
    cost = sum((Decimal(str(row['cost_usd'])) for row in measured), Decimal(0))
    unit = cost / len(measured)
    print(model, 'measured calls', len(measured), f'measured USD {cost:.3f}',
          f'USD/call {unit:.3E}', f'USD/1000 calls {unit * 1000:.3f}')
    if model == 'qwen/qwen3.8-flash':
        continue
    calls = 50400 if spec.provider == 'deepseek' else 25200
    projection = unit * calls
    projected[spec.provider] += projection
    print('confirmation calls', calls, f'USD {projection:.3f}')
    if spec.provider == 'deepseek':
        prompt = Decimal(sum(row['prompt_tokens'] for row in measured)) / len(measured)
        completion = Decimal(sum(row['completion_tokens'] for row in measured)) / len(measured)
        no_cache = (prompt * Decimal('0.30') + completion * Decimal('1.20')) * calls / 1000000
        print(f'peak no-cache risk USD {no_cache:.3f}',
              f'off-peak no-cache scenario USD {no_cache / 2:.3f}')
for provider in ('deepseek', 'openrouter'):
    headroom = Decimal(8) - spent[provider] - projected[provider]
    print(provider, f'spent USD {spent[provider]:.3f}',
          f'confirmation USD {projected[provider]:.3f}',
          f'headroom after confirmation USD {headroom:.3f}')
print(f'OpenRouter headroom after review reserve USD {Decimal(8) - spent["openrouter"] - projected["openrouter"] - Decimal("0.600"):.3f}')
luna = [row for row in rows if row['model'] == 'openai/gpt-6-luna'
        and not row.get('billed_conservatively') and not row.get('usage_missing')
        and row['prompt_tokens'] + row['completion_tokens'] > 0]
qwen_proxy = sum((Decimal(row['prompt_tokens']) * Decimal('0.15')
                  + Decimal(row['completion_tokens']) * Decimal('0.47')
                  for row in luna), Decimal(0)) / len(luna) * 25200 / 1000000
print(f'Qwen sizing proxy USD {qwen_proxy:.3f}')
PY
```

## Chronology and execution evidence still required

`git log -12 --date=iso-strict --format='%h %ad %s'` and the individual commit
messages establish this retained development chronology (2026-10-27 unless noted):

| Commit | Evidence recorded |
|---|---|
| `95bd99b` | Original draft preregistration, contract, and canonical prompts. |
| `4d40eb9` | v2 runner and real DeepSeek smoke. |
| `7250bd3`, `994de1d` | Analysis pipeline and generic CF validity diagnostic. |
| `894a841` | OpenCode payload/transport no-go. |
| `54ceea1` | Calibration rule, dev runs, report, and sign-flip selection. |
| `717c23e` | Provider pinning, served-provider logging, temperature exceptions. |
| `a0f4866` | Noise runs, report, deviations, and quarantine records. |
| `bef0c18` | Stopped pilot and its original-extreme validity analysis retained. |

Amendment 1 requires the **T12 hardened runner** before confirmation: exclusive
block locks, bounded parallelism, and a confirm guard validating the freeze
marker and plan hash. Its implementation evidence is `src/v2/simulate.py` plus
runner tests under `tests/v2/`; T12 completion is not asserted by this document.
Only the coordinator resumes interrupted blocks, with no automatic relaunches.

After the PI answers the eight yes/no questions in Amendment 1 item 8 and the
gates pass, the coordinator commits the approved plan and creates
`docs/ns-b2/FROZEN.json` with `commit`, `prereg_sha256`, `pi_name`,
and `date`. This worker does not create the marker. Post-freeze changes require
Amendment 2, PI approval, and renewed freeze. Hypotheses, directions, primary
family, windows, alpha 0.05, Holm, and other inferential thresholds remain unchanged.

The open questions cover instrument/validity approval, null monitoring with
uncorrected primary tests, temperature/routing and transport acceptance,
development exposure and separation, measured budget/review reserve/Qwen removal,
the USD 7.000 PI contingency, retained original design details, and T12/freeze
authorization. Each recommends Yes; none is treated as already answered.

## Document validation

- `python3 -c "import yaml; yaml.safe_load(open('research-contract-v2.yaml'))"`
  parsed the amended contract successfully.
- `.venv/bin/python -m pytest tests/v2/test_conditions.py::test_preregistration_quotes_current_prompt_text -q`
  returned **1 passed**; the verbatim prompt appendix is unchanged.
- `git diff --check` passed. Byte-prefix comparisons against `git show HEAD:`
  verified that the complete original preregistration and contract are unchanged.
- The calculation above reproduced USD 4.612 DeepSeek and USD 5.270 OpenRouter
  confirmation costs. Explicit evidence paths exist, eight amendment items and
  eight numbered PI questions are present, and no `FROZEN.json` was created.
