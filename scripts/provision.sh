#!/usr/bin/env bash
# Provision a Colab GPU VM for indobench: create session, check VRAM, upload token + repo,
# install deps, verify vllm with one tiny generate.
# Usage: scripts/provision.sh [--gpu G4|A100] [--yes] [--skip-verify]
# Session name: $INDOBENCH_SESSION (default: indobench).
source "$(dirname "$0")/_common.sh"

GPU=G4; YES=0; VERIFY=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gpu) GPU="$2"; shift 2 ;;
    --yes) YES=1; shift ;;
    --skip-verify) VERIFY=0; shift ;;
    *) die "unknown arg $1" ;;
  esac
done
[[ "$GPU" == G4 || "$GPU" == A100 ]] || die "--gpu must be G4 or A100 (unknown names silently fall back to A100)"
MIN_VRAM_MIB=79000   # 27-31B BF16 needs the 80/96 GB cards

echo "== colab usage"; colab usage </dev/null
if [[ $YES != 1 ]]; then
  read -r -p "Create $GPU session '$SESSION'? [y/N] " ans
  [[ "$ans" == y || "$ans" == Y ]] || exit 1
fi

echo "== colab new $SESSION ($GPU)"
colab new -s "$SESSION" --gpu "$GPU" --high-mem </dev/null || colab new -s "$SESSION" --gpu "$GPU" </dev/null

echo "== VRAM check"
gpu_line=$(vm_py 60 <<'PY' | grep -a '^GPU|' || true
import subprocess
out = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader,nounits"]).decode()
print("GPU|" + out.strip().splitlines()[0])
PY
)
echo "$gpu_line"
vram=$(echo "$gpu_line" | awk -F', *' '{print $NF}')
if [[ -z "$vram" || "$vram" -lt $MIN_VRAM_MIB ]]; then
  echo "VRAM ${vram:-unknown} MiB < $MIN_VRAM_MIB: stopping session." >&2
  colab stop -s "$SESSION" </dev/null
  exit 3
fi
driver_major=$(echo "$gpu_line" | awk -F', *' '{print $2}' | cut -d. -f1)
if [[ -z "$driver_major" || "$driver_major" -lt 580 ]]; then
  echo "WARNING: driver ${driver_major:-unknown} may not support CUDA 13.0 (vllm 0.32 wheel needs >= 580)." >&2
fi

echo "== HF token (file upload, never printed or passed via exec/--env)"
vm_py 60 <<'PY' >/dev/null
import os; os.makedirs("/root/.cache/huggingface", mode=0o700, exist_ok=True)
PY
tok_file=$(umask 077; mktemp "${TMPDIR:-/tmp}/indobench_hf.XXXXXX")
trap 'rm -f "$tok_file"' EXIT
if [[ -n "${HF_TOKEN:-}" ]]; then
  printf '%s' "$HF_TOKEN" > "$tok_file"
else
  security find-generic-password -s huggingface-api-key -w | tr -d '\n' > "$tok_file"
fi
[[ -s "$tok_file" ]] || die "no HF token found (HF_TOKEN env or keychain huggingface-api-key)"
colab upload -s "$SESSION" "$tok_file" /root/.cache/huggingface/token </dev/null
rm -f "$tok_file"

"$REPO_ROOT/scripts/sync_code.sh"

echo "== install requirements"
# The CLI's client can time out while the install keeps running on the VM (seen 2026-10-28),
# so a failure here is checked against what is actually installed.
colab install -s "$SESSION" -r "$REPO_ROOT/requirements.txt" </dev/null || echo "colab install returned an error; checking the VM"
vm_py 60 <<'PY' | grep -a "INSTALLED" || die "vllm/lm_eval not installed on the VM"
import importlib.metadata as md
print("INSTALLED", md.version("vllm"), md.version("lm_eval"), md.version("torch"))
PY
# Prebuilt FlashInfer kernels; without them every model load JIT-compiles for minutes.
vm_py 900 <<'PY' | tail -2
import subprocess
r = subprocess.run(["vllm", "download-kernels"], capture_output=True, text=True)
print(r.stdout[-500:], r.stderr[-500:], "DOWNLOAD_KERNELS_EXIT", r.returncode)
PY

if [[ $VERIFY == 1 ]]; then
  echo "== verify vllm (subprocess, so the kernel never holds GPU memory)"
  vm_py 1500 <<'PY'
import subprocess, sys
r = subprocess.run(["python3", "/content/indobench/runner/verify_env.py"], capture_output=True, text=True)
print(r.stdout[-3000:]); print(r.stderr[-3000:], file=sys.stderr)
print("VERIFY_EXIT", r.returncode)
PY
fi
echo "== provisioned $SESSION"
