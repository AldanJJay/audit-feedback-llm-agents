PYTHON ?= .venv/bin/python

.PHONY: reproduce test paper posthoc latency-summary
reproduce:
	$(PYTHON) scripts/reproduce_analysis.py

test:
	$(PYTHON) -m pytest tests/v2 -q

paper:
	cd paper/latex && latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape main.tex

posthoc:
	$(PYTHON) src/v2/posthoc_analyses.py

latency-summary:
	$(PYTHON) -m src.v2.latency_benchmark --summarize-only
