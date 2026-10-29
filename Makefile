PYTHON ?= .venv/bin/python

.PHONY: reproduce test paper
reproduce:
	$(PYTHON) scripts/reproduce_analysis.py

test:
	$(PYTHON) -m pytest tests/v2 -q

paper:
	cd paper/latex && latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape main.tex
