#!/usr/bin/env bash
# Save an Anthropic API key from the macOS clipboard to a private file for runner/run_api.py.
# The key is never printed. Usage: copy the key, then run scripts/save_anthropic_key.sh [path]
set -euo pipefail
dest="${1:-${XDG_CONFIG_HOME:-$HOME/.config}/indobench/anthropic.key}"
key=$(pbpaste | tr -d '[:space:]')
if [[ "$key" != sk-ant-* ]]; then
  echo "clipboard does not hold an Anthropic API key (expected prefix sk-ant-); nothing saved" >&2
  exit 1
fi
mkdir -p "$(dirname "$dest")"
( umask 077; printf '%s' "$key" > "$dest" )
chmod 600 "$dest"
echo "saved ${#key}-char key to $dest (mode 600)"
