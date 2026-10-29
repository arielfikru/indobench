#!/usr/bin/env bash
# Poll the detached run every INTERVAL seconds. Exits 0 when the run finished cleanly,
# 1 when it finished with failed models, 2 on FATAL / dead runner / VM unreachable.
# With --stop, stops the Colab session on exit (so the VM never idles).
# Never run other `colab exec` calls on the same session while this is polling.
# Usage: scripts/watch.sh [--stop] [--interval 60]
source "$(dirname "$0")/_common.sh"

STOP=0; INTERVAL=60
while [[ $# -gt 0 ]]; do
  case "$1" in
    --stop) STOP=1; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) die "unknown arg $1" ;;
  esac
done

finish() {
  local code=$1
  if [[ $STOP == 1 ]]; then "$REPO_ROOT/scripts/teardown.sh"; fi
  exit "$code"
}

fails=0
while true; do
  out=$(vm_py 60 <<'PY' 2>&1 || true
import json, os, subprocess
alive = subprocess.run(["pgrep", "-f", "runner/run_matrix.py"], capture_output=True).returncode == 0
path = "/content/indobench_status.json"
st = json.load(open(path)) if os.path.exists(path) else {}
state = st.get("state")
if alive:
    verdict = "RUNNING"
elif state == "done":
    verdict = "DONE"
elif state == "done_with_errors":
    verdict = "DONE_WITH_ERRORS"
elif state == "fatal":
    verdict = "FATAL"
else:
    verdict = "DEAD"
print(f"VERDICT {verdict} | model {st.get('current_model')} | done {st.get('done')} | failed {st.get('failed')}")
print(subprocess.run("tail -n 2 /content/indobench_run.log; tail -n 2 /content/indobench_nohup.log",
                     shell=True, capture_output=True, text=True).stdout)
PY
)
  echo "[$(date '+%H:%M:%S')] $(echo "$out" | head -8)"
  verdict=$(echo "$out" | grep -ao '^VERDICT [A-Z_]*' | awk '{print $2}' || true)
  case "$verdict" in
    RUNNING) fails=0 ;;
    DONE) finish 0 ;;
    DONE_WITH_ERRORS) finish 1 ;;
    FATAL|DEAD) finish 2 ;;
    *)
      fails=$((fails + 1))
      [[ $fails -ge 5 ]] && { echo "5 failed polls in a row" >&2; finish 2; }
      ;;
  esac
  sleep "$INTERVAL"
done
