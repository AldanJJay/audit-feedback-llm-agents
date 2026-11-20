# Public release verification — 2026-11-20

This update adds post hoc diagnostics and a separately collected latency benchmark. The existing paper, preregistration, raw study data and generated outputs are preserved. Validation used Python 3.12.2 and the exact versions pinned in requirements.txt, CPU only, without provider requests. The full offline suite passes **170 tests in 45.74s**, compared with the unchanged baseline of **131 tests in 30.60s**; there are no pre-existing failures. No commit, push or tag change was made during preparation.

## Post hoc analyses

These additional diagnostics were not preregistered: regime-specific contrasts, citation specificity, label truth/adoption, evidence informativeness, perturbation/proxy strata, paired-seed power, market components, and citation ceilings. Regenerate offline:

```sh
.venv/bin/python src/v2/posthoc_analyses.py
# Or: make posthoc
```

The script writes `data/v2/analysis/posthoc_analyses/results.json` and `report.md`, asserts exact registered primary reproduction, and uses deterministic resampling. All scientific JSON fields and the scientific report body match development exactly. Full byte identity to development is affected by the descriptive public name, the source checksum, the checksum of the already public-packaged confirmatory output, and public validation prose. No existing input or output is rewritten. Repeated public regeneration produces identical bytes.

| Artifact | SHA-256 |
|---|---|
| results.json | `dfa33d8f878985dcd3a32c985537f730c9acc94d2cd6a9625bd5abda5b801472` |
| report.md | `2b0f5d0a8ee4b39312677cebee78ee3625127c248b45eef4d5fba6683836e178` |

The logging defect disclosed on 20 November 2026 is documented in [results/deviations.md](results/deviations.md). The per-row diagnostic `audit_selected` value is wrong; audits, fines and labels used the correct per-agent flag, and reported analyses do not use that diagnostic field.

## Latency benchmark

The post-collection benchmark ran on **19 November 2026**, from one client host, over approximately **17 minutes**: **1,260 requests**, approximately **USD 0.14**, and a separate `data/v2/latency_ledger.jsonl`. It was not preregistered. Full-run statistics exclude pilot rows. Re-summarize offline:

```sh
.venv/bin/python -m src.v2.latency_benchmark --summarize-only
# Or: make latency-summary
```

Only the new benchmark summary and report are overwritten. Input hash keys are repository-relative and resolve to their recorded SHA-256 values. Every measurement and cost statistic matches the development summary. Requests, pilot/full stage records and the separate ledger are byte-identical to collection outputs. The approval record identifies the study maintainer without a terminal identifier; historical collection validation keeps its original code hashes explicitly labeled and points to this release's current tests. Repeated offline summaries are byte-identical. Single-host chronology, disjoint prompts and the short measurement window limit concurrency and tail-latency conclusions.

Provider credentials are read exclusively from the documented `DEEPSEEK_API_KEY` and `OPENROUTER_API_KEY` environment variables. The public client no longer reads a credential-file fallback. No new statistical dependency or other change to existing modules was needed.

The 39 additional tests cover the post hoc calculations and benchmark, including offline summarization, prompt replay, timing intervals, scheduling, retries, routing, budgets and environment-only credential lookup. All **538 protected existing tracked files** retain their baseline SHA-256, including the complete paper, six frozen documents, existing data and all existing outputs. All local README links resolve; the requested forbidden-content scan over every added/modified file has zero hits, and `git diff --check` passes. Citation metadata advances to version 1.2.0, dated 20 November 2026, following the prior release convention.

## Previous release verification — 30 October 2026

The remaining sections record the preceding manuscript release and its historical checks. The 170-test result above is the current full-suite validation.

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
