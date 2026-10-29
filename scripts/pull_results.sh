#!/usr/bin/env bash
# Copy one run's results from the VM (Drive or local results root) to results/runs/<run_id>/.
# Usage: scripts/pull_results.sh <run_id>
source "$(dirname "$0")/_common.sh"

[[ $# -eq 1 ]] || die "usage: $0 <run_id>"
RUN_ID="$1"

vm_py 300 <<PY
import subprocess
subprocess.run(["tar", "-czf", "/content/results_$RUN_ID.tgz", "-C", "$VM_RESULTS_ROOT", "$RUN_ID"], check=True)
print("packed")
PY
mkdir -p "$REPO_ROOT/results/runs"
tmp=$(mktemp "${TMPDIR:-/tmp}/indobench_res.XXXXXX")
trap 'rm -f "$tmp"' EXIT
colab download -s "$SESSION" "/content/results_$RUN_ID.tgz" "$tmp" </dev/null
tar -xzf "$tmp" -C "$REPO_ROOT/results/runs"
echo "pulled to results/runs/$RUN_ID"
