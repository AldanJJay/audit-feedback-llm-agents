# Public release verification — 2026-10-29

The release was assembled in a separate directory from read-only development inputs, without model API calls. Only this new public repository was written. The original v13 manuscript PDF, six preregistration documents, all raw run records, and numerical findings were preserved.

## 1. Fresh Python environment and tests

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt pytest==9.1.1 statsmodels==0.15.0
.venv/bin/python -m pytest tests/v2 -q
.venv/bin/python -m pip check
```

Result: **121 passed**, with no dependency conflicts. Python 3.12.2; numpy 2.5.4; scipy 1.18.1; pandas 3.1.0; matplotlib 3.11.2; httpx 0.28.1; statsmodels 0.15.0; pytest 9.1.1. The requirements file pins those versions. Tests use mock HTTP transports and synthetic observations; they do not call model APIs.

One development-only test of the reviewer gzip transport was removed because it imports `tools/review/`, which is explicitly outside the public release. Its import and unused gzip import were also removed. All remaining study tests are included. The test environment and generated caches are removed from the final release folder after verification.

## 2. Exact offline scientific reproduction

```sh
.venv/bin/python scripts/reproduce_analysis.py
```

Result: **PASS: all scientific outputs and non-exempt metadata match exactly**, using all 200 completed confirmatory runs. This compares the entire parsed result object, not just the primary table: manifests, run summaries, primary and secondary statistics, mixed models, validity checks, null monitoring, coverage, and missingness all match. The script also writes the generated JSON, report and figures into a temporary directory and removes that directory after checking.

Differences are limited to repository-root prefixes in paths and three execution-provenance fields: `executed_utc`, `analysis_code_sha256`, and `code_revision`. The committed results retain their historical execution time, development analysis checksum `1684d12aa9199a72bc706039c1fd3630b58237fbbb5e7da736deacdb14bcb1e8`, and development source revision `4424f84b6248a13b18ab595f9dc9807b700fe7c6`. The public analysis source checksum is `70e51cb1f84db9c6048ec67f6d3ddc6aa0474ec3ea8a17a86a080fa5d735b364`; its differences are portable preregistration lookups and public-facing docstrings/headings. The comparison script reports these provenance differences explicitly and requires exact equality for every other value.

The rebuilt exploratory input archive passed ZIP CRC verification, all manifest SHA-256 checks, and byte-for-byte comparison against its current public input files. Its frozen plan and marker remain the unchanged originals. Its manifest explains the public repackaging; the adjacent historical validation record identifies its development-only provenance. No exploratory numerical estimates were changed.

All 470 other included data files remain byte-identical to their development originals. Cost accounting is unchanged in all **126,877** main-ledger rows and **4** review-ledger rows: model, provider, cost and tag match row by row. The ledgers contain accounting fields only.

## 3. Paper compilation

From `paper/latex/`:

```sh
latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape main.tex
```

Result: **PASS**, 23 pages; no unresolved references or citations and no overfull boxes. A harmless epstopdf warning states that shell escape is disabled; the bundled PDF logo assets supply the required graphics. Only referenced manuscript figures/tables, the README design PNG, references and Definitions are included. Generated build files are excluded and removed after verification.

`paper/audit_feedback_llm_agents.pdf` is byte-identical to the supplied `manuscript_v13.pdf`. The public LaTeX source has portable live repository links/paths and cleaned preparation prose, while preserving the historical data-availability statement. Its compiled PDF therefore differs from the separately preserved original preprint.

## 4. Preregistration integrity

All six files are byte-identical to their development sources. SHA-256:

| File | SHA-256 |
|---|---|
| preregistration.md | dd8eaf872b37593433b3168725962937394d1b5d1c4ef005fe415534c37235a1 |
| FROZEN.json | 95a0dd85b8fcd56ecf516dbbf9780c52f16d9a6a4b2e461f07eb9d6f4278952c |
| amendment_1_evidence.md | 570cb4440778331a5b8c8a5d0110bc4e4cec6627fcb5d29433e98fd66a6cd842 |
| calibration_report.md | 5b02362e21c0caa6fa553de6a70108b3c22b806cebcaeaf748904e7f717a9dcf |
| noise_report.md | a4f42abb4ab589a5d8517d9302424180e315ea33f76876ae09537c72c6444d72 |
| research-contract-v2.yaml | c21e8e4d6410e9d3c62f88a910a24bb9e97f09171e54ccf0968b6952075fed1d |

The plan checksum **matches `FROZEN.json`'s `prereg_sha256`**. The frozen marker's commit identifies the development repository; the collection ancestor guard is preserved and refuses a confirmatory run against this fresh public history.

## 5. Credential, path and codename scans

Scanned the release files, extracted PDF text, and every decompressed member of the exploratory ZIP. Checked provider-key prefixes, GitHub-token prefixes, labeled hexadecimal Gitea tokens, authorization-header credential literals, credential/environment-file references, local home-directory paths, internal hosts, and email addresses. Results: **zero keys/tokens, zero credential literals, zero local absolute paths, and zero non-author email addresses**. The only email addresses allowed are the manuscript authors' `jay@uji.es` and `berlanga@uji.es`. API environment-variable names are documented configuration, not secrets. Python environment accessors and environmental-fidelity metric names are ordinary identifiers, not environment-file references.

Third-party template contact emails were removed from comments without removing copyright/author notices. The MDPI EPS logo's encoded image data happened to contain 43 email-shaped strings and one codename-shaped string. Those encoded streams were rewrapped using whitespace only; decoding all four ASCII85 streams before and after verified identical image bytes. This removed the accidental textual matches without changing the graphic.

The only internal-host exceptions are the development URLs in the preserved original manuscript PDF (two occurrences) and the explicitly retained historical data-availability statement in `paper/latex/main.tex` (one occurrence). These identify historical provenance. Live public repository references elsewhere point to the intended GitHub URL. No code comment contains IDE/assistant coordination instructions.

The requested case-insensitive `ns-?b[12]` scan outside `preregistration/` has only the explained categories documented in README: `ns-b2-analysis-v1` schema plus its test/result copies; `nsb2:` accounting tags plus their writer/reader/test; historical manuscript repository/branch/path references; and the explanatory README/verification prose itself. The archive's original plan and marker naturally retain the same frozen codenames. No prior study's code, data, or old manuscript is included; `src/market.py` is the explicitly required shared dependency.

## 6. Fresh public Git history

Initialized a separate repository on `main`, with author/committer configured as `Aldan Jay <jay@uji.es>`. The release has exactly one initial commit with message:

```text
Initial public release: audit feedback and LLM agent decisions (preregistered study)
```

No remote is configured and nothing was pushed. The handoff reports the resulting commit ID, clean status, and `git rev-list --count HEAD` result. No development-repository Git commands or writes were performed.

## 7. Inventory and public artifacts

The handoff reports the final tracked-file count, payload bytes, and total on-disk repository size after removal of the temporary virtual environment, caches, build outputs and verification transcripts. The largest payload is the 83,331,275-byte confirmatory result JSON, below GitHub's 100 MiB per-file limit. README, MIT/CC BY notices, author ORCIDs in CITATION.cff, pinned requirements, a Makefile, and the temporary-output reproduction script are included.

## README key-findings table

| Model / contrast | Estimate | Holm p | Interpretation |
|---|---:|---:|---|
| DeepSeek P1: evidence − naive precision | -0.0137 | 0.3683 | Inconclusive; predicted positive |
| DeepSeek P2: evidence − naive true-driver dependence | -0.0624 | 0.0140 | Negative, contrary to prediction |
| DeepSeek P3: label SCI, current true driver | -0.0389 | 0.2727 | Inconclusive; predicted positive |
| DeepSeek P4: placebo SCI, opposite current driver | -0.1341 | 4.179e-05 | Negative, contrary to prediction |
| Haiku replication (P1 / P2 / P3 / P4) | 0.0163 / -0.0059 / -0.0354 / -0.0572 | 1.0000 / 1.0000 / 0.7625 / 0.2666 | No Holm-significant primary contrast |
| Luna replication (P1 / P2 / P3 / P4) | -0.1198 / -0.0909 / -0.0333 / 0.0404 | 0.0007 / 0.0376 / 0.2883 / 0.2544 | Negative evidence effects on precision and true-driver dependence |
