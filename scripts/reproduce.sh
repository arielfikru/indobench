#!/usr/bin/env bash
# Rebuild every published table and figure from the per-item predictions in results/predictions/.
# Needs only uv; no GPU, no API key, no dataset download. Usage: scripts/reproduce.sh
set -euo pipefail
cd "$(dirname "$0")/.."
py() { uv run -q --with numpy --with pyyaml "$@"; }
py --with pytest python -m pytest -q analysis
py python analysis/summarize.py --predictions results/predictions/full-m4 --run-id full-m4 --out results/
py python analysis/summarize.py --predictions results/predictions/api-claude --run-id api-claude --out results/claude/
py --with matplotlib python analysis/results_table.py
git status --short results/ || true
echo "done; an empty git status above means the published results reproduce exactly"
