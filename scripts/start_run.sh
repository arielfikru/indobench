#!/usr/bin/env bash
# Start runner/run_matrix.py detached on the VM (nohup + setsid), so it survives a local
# disconnect, a hung `colab exec` and kernel restarts. Refuses to start a second copy.
# Usage: scripts/start_run.sh <run_id> [run_matrix args...]
#   e.g. scripts/start_run.sh smoke-a --models smoke --limit 50
source "$(dirname "$0")/_common.sh"

[[ $# -ge 1 ]] || die "usage: $0 <run_id> [run_matrix args...]"
RUN_ID="$1"; shift
ARGS=$(printf '%q ' --run-id "$RUN_ID" --results-root "$VM_RESULTS_ROOT" "$@")

vm_py 60 <<PY
import subprocess
if subprocess.run(["pgrep", "-f", "runner/run_matrix.py"], capture_output=True).returncode == 0:
    raise SystemExit("ALREADY_RUNNING: a run_matrix process is alive on the VM")
subprocess.run("rm -f /content/indobench_status.json", shell=True)
subprocess.Popen(
    "cd /content/indobench && nohup setsid python3 runner/run_matrix.py $ARGS"
    " >> /content/indobench_nohup.log 2>&1 < /dev/null &",
    shell=True,
)
print("STARTED $RUN_ID")
PY
