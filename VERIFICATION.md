# Public release verification — 2026-10-30

This update packages the final 15-page manuscript and its exploratory analyses. Validation used the existing Python 3.12.2 environment with the exact versions pinned in requirements.txt, CPU only, without provider requests. No commit or push was made during preparation.

## Offline tests and confirmatory reproduction

From the repository root, after installing requirements.txt into a local virtual environment:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest -q tests/v2/test_exploratory_analyses.py
.venv/bin/python scripts/reproduce_analysis.py
```

Results: **131 passed in 35.20s** for the full suite, and **10 passed in 1.39s** for the focused exploratory checks. There are no pre-existing public-suite failures. Tests use mock providers and synthetic observations.

The confirmatory comparison reports **PASS: all scientific outputs and non-exempt metadata match exactly**, across all 200 completed runs. It normalizes repository-root prefixes and reports only the three expected execution-provenance differences: execution timestamp, analysis-source SHA-256 and Git revision. Every other parsed result field matches the recorded public confirmatory output. Temporary reproduction outputs are removed by the script.

Environment: Python 3.12.2, numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, matplotlib 3.11.2, statsmodels 0.15.0, httpx 0.28.1 and pytest 9.1.1.

## Exploratory and manuscript inputs

```sh
.venv/bin/python src/v2/exploratory_analyses.py
.venv/bin/python paper/latex/summarize_audit_traffic.py
.venv/bin/python paper/latex/analyze_label_punitive.py
.venv/bin/python paper/latex/generate_tables.py
.venv/bin/python paper/latex/generate_figures.py
pdftoppm -png -singlefile -r 150 paper/latex/figures/fig1_design.pdf paper/latex/figures/fig1_design
```

All commands pass offline. Consecutive exploratory runs reproduce all three main deliverables **byte for byte**:

| File in data/v2/analysis/exploratory/ | SHA-256 |
|---|---|
| results.json | `cac41b406e7a5576a3884b80cd30e2709f8985c31c6b009f2649de42091a1a50` |
| report.md | `a2d4831f5046aabae1b486b5bc036b3efac108e5c71db9137f3a2dff1fe9c7bc` |
| prompt_and_dgp.md | `2d9671a817b6e554222dea5cb6e3846326755e6cc692c96f0f7a707b3a18f0f9` |

Every scientific result and historical collection diagnostic matches the final-paper development outputs exactly. Differences are public paths, source and input-file hashes, a portable deviation pointer, and validation prose. The historical preregistration commit list is preserved as development provenance rather than inferred from public Git history. All non-metadata values in the workload and label-minus-punitive JSON match the final-paper inputs exactly.

All six generated table inputs and both figure PDFs reproduce the final manuscript inputs **byte for byte**. Only referenced figure PDFs and the regenerated README design PNG are retained; the obsolete figure with the former metric name is removed. The optional decomposition preview PNG is not generated in this release.

Earlier public packaging had omitted safe diagnostic fields from the accounting ledger. This update restores six `provider_mismatch` flags, five `usage_missing` flags and two HTTP `status_code` values across eight rows, solely from the recorded source. No error bodies, provider responses or credential material are added. All 126,877 rows retain their original order, timestamps, models, providers, tags, token counts and charged costs; these diagnostic flags allow exact recovery of the final-paper missing-usage and HTTP-error summaries.

## Final paper

```sh
make paper
# Equivalent, from paper/latex/:
latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape main.tex
```

Result: **15 pages, zero undefined references/citations, zero overfull boxes**. The sole package warning is epstopdf noting that shell escape is disabled; bundled PDF logos supply the graphics. The supplied PDF is byte-identical to the final manuscript PDF. Extracted text from the in-place compiled PDF and supplied PDF is byte-identical using `pdftotext -layout`; PDF bytes can differ because of build metadata and the equivalent public-safe logo asset.

Supplied final PDF SHA-256: `ed8c789ebb770ab7ca5168f25efbf0d24b5b564dade86fa7a0c90c85cf3d5854`.

LaTeX build artifacts, caches, temporary comparison output and local verification logs are ignored by .gitignore. No build artifacts are among the changed/untracked release files. Existing public-safe template comments and equivalent logo streams are preserved, including the original third-party notices.

## Frozen preregistration

The same six documents remain byte-identical to the previous public release; none was edited. The plan checksum matches `prereg_sha256` in FROZEN.json.

| File | SHA-256 |
|---|---|
| FROZEN.json | `95a0dd85b8fcd56ecf516dbbf9780c52f16d9a6a4b2e461f07eb9d6f4278952c` |
| amendment_1_evidence.md | `570cb4440778331a5b8c8a5d0110bc4e4cec6627fcb5d29433e98fd66a6cd842` |
| calibration_report.md | `5b02362e21c0caa6fa553de6a70108b3c22b806cebcaeaf748904e7f717a9dcf` |
| noise_report.md | `a4f42abb4ab589a5d8517d9302424180e315ea33f76876ae09537c72c6444d72` |
| preregistration.md | `dd8eaf872b37593433b3168725962937394d1b5d1c4ef005fe415534c37235a1` |
| research-contract-v2.yaml | `c21e8e4d6410e9d3c62f88a910a24bb9e97f09171e54ccf0968b6952075fed1d` |

The freeze commit identifies the development repository. The collection ancestor guard remains unchanged and refuses confirmatory collection in this fresh public history. Deviations are disclosed separately in [results/deviations.md](results/deviations.md).

## Public documentation and scans

The README uses the final paper's sign-flip sensitivity, citation–sensitivity difference and false-label terminology, corrected model-level conclusions, regime-specific instrument limitations and measured audit-sidecar workload. One traceability sentence maps the older registered names. CITATION.cff retains the manuscript title and author metadata, with release version 1.1.0 and date 2026-10-30.

All **15 local README links** resolve to existing files. `git diff --check` passes. The complete added/modified-file scan, including binary bytes and extracted PDF text, finds **zero credential-prefix/header, absolute home-path, internal-assistant, internal review-text or checkout-workflow matches** against the requested release patterns. No internal assessment files, submission archive or cover letter are included. Historical frozen documents remain untouched.
