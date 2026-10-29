#!/usr/bin/env bash
# Stop the Colab session and show what is still running (an idle VM still burns CU).
source "$(dirname "$0")/_common.sh"

colab stop -s "$SESSION" </dev/null || true
echo "== remaining sessions"; colab sessions </dev/null || true
echo "== usage"; colab usage </dev/null || true
