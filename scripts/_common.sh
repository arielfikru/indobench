# Shared helpers for the scripts in this folder. Source, don't run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION="${INDOBENCH_SESSION:-indobench}"
VM_REPO=/content/indobench
VM_RESULTS_ROOT="${INDOBENCH_RESULTS_ROOT:-/content/drive/MyDrive/indobench/results/runs}"

# Run Python on the VM with a hard local wall clock, so one hung call can't stall a loop.
# Usage: vm_py <timeout_s> <<'PY' ... PY
vm_py() {
  local t="$1"
  perl -e 'alarm shift; exec @ARGV' "$((t + 30))" colab exec -s "$SESSION" --timeout "$t"
}

die() { echo "ERROR: $*" >&2; exit 1; }
