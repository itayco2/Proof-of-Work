# The runbook. Everything here is free: no API key, no account, no model.
PY := ./.venv/bin/python
# The first interpreter on this machine that is 3.10 or newer. macOS ships python3 as 3.9.
PYTHON ?= $(shell for p in python3.13 python3.12 python3.11 python3.10 python3; do \
  if command -v $$p >/dev/null 2>&1 && $$p -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then echo $$p; break; fi; done)

.PHONY: help setup gate test links icons clean

help:
	@grep -E '^[a-z0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-8s %s\n", $$1, $$2}'

setup:  ## create .venv and install the test tier (pytest only)
	@if [ -z "$(PYTHON)" ]; then echo "No Python 3.10 or newer found. Install one:  brew install python@3.12"; exit 1; fi
	$(PYTHON) -m venv .venv && $(PY) -m pip install -q --upgrade pip && $(PY) -m pip install -q -r requirements-test.txt
	@echo "done. Next:  make gate"

gate:  ## THE GATE: the fast tier plus every external link, under a minute
	$(PY) scripts/gate.py

test:  ## the fast tier only: every guide and prompt against its contract, under a second
	$(PY) -m pytest -q tests

links:  ## the live link check only (CI runs it weekly)
	$(PY) scripts/gate.py --links-only

icons:  ## rebuild the 128 px thumbnails and the banner from the five illustrations (needs CHROME_BIN)
	$(PY) scripts/make_icons.py

clean:  ## remove caches
	rm -rf .pytest_cache tests/__pycache__ scripts/__pycache__
