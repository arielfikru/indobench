#!/usr/bin/env bash
# Upload the code the VM needs (configs, tasks, runner, requirements) to /content/indobench.
# Results on the VM are never touched.
source "$(dirname "$0")/_common.sh"

tarball=$(mktemp "${TMPDIR:-/tmp}/indobench_code.XXXXXX")
trap 'rm -f "$tarball"' EXIT
COPYFILE_DISABLE=1 tar --no-xattrs -czf "$tarball" -C "$REPO_ROOT" configs tasks runner requirements.txt
colab upload -s "$SESSION" "$tarball" /content/indobench_code.tgz </dev/null
vm_py 120 <<'PY'
import shutil, subprocess
for d in ("configs", "tasks", "runner"):
    shutil.rmtree(f"/content/indobench/{d}", ignore_errors=True)
subprocess.run(["mkdir", "-p", "/content/indobench"], check=True)
subprocess.run(["tar", "-xzf", "/content/indobench_code.tgz", "-C", "/content/indobench"], check=True)
print("code synced:", sorted(__import__("os").listdir("/content/indobench")))
PY
