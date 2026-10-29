"""Diagnose COPAL-ID scores from existing sample logs (no new GPU run).

Checks two suspected artifacts of lm_eval's copal_id task (0.4.13):
1. Truncated premise: utils.doc_to_text drops the last character (`premise.strip()[:-1]`),
   assuming a trailing period. Premises without one lose a real letter ("angkot" -> "angko").
2. Length bias: `acc` compares summed log-likelihoods, which favours shorter choices.
   acc_norm here = per-character log-likelihood (same idea as lm_eval's acc_norm).

Usage: python analysis/copal_check.py --run-dir results/runs/full-m4
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open()]


def stats(rows: list[dict]) -> dict:
    n = len(rows)
    trunc = [r for r in rows if not r["doc"]["premise"].strip().endswith(".")]
    acc = sum(r["acc"] for r in rows) / n
    norm_hits = short_picks = short_correct = 0
    for r in rows:
        lls = [float(x[0]) for x in r["filtered_resps"]]
        conts = [r["arguments"][f"gen_args_{i}"]["arg_1"] for i in range(len(lls))]
        norm = [ll / max(len(c), 1) for ll, c in zip(lls, conts)]
        gold = int(r["target"])
        norm_hits += max(range(len(norm)), key=norm.__getitem__) == gold
        pred = max(range(len(lls)), key=lls.__getitem__)
        shortest = min(range(len(conts)), key=lambda i: len(conts[i]))
        short_picks += pred == shortest
        short_correct += shortest == gold
    acc_trunc = sum(r["acc"] for r in trunc) / len(trunc) if trunc else float("nan")
    rest = [r for r in rows if r not in trunc]
    acc_rest = sum(r["acc"] for r in rest) / len(rest) if rest else float("nan")
    return {
        "n": n,
        "acc": acc,
        "acc_norm_char": norm_hits / n,
        "premise_truncated_pct": len(trunc) / n,
        "acc_truncated": acc_trunc,
        "acc_intact": acc_rest,
        "picks_shorter_pct": short_picks / n,
        "gold_is_shorter_pct": short_correct / n,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, required=True)
    args = p.parse_args()
    cols = ["n", "acc", "acc_norm_char", "premise_truncated_pct", "acc_truncated", "acc_intact",
            "picks_shorter_pct", "gold_is_shorter_pct"]
    print("| model | split | " + " | ".join(cols) + " |")
    print("|" + "---|" * (len(cols) + 2))
    for f in sorted(args.run_dir.glob("*/copal_id/samples_copal_id_*.jsonl")):
        model = f.parts[-3]
        split = "colloquial" if "colloquial" in f.name else "standard"
        s = stats(load(f))
        vals = [str(s["n"])] + [f"{s[c]:.3f}" for c in cols[1:]]
        print(f"| {model} | {split} | " + " | ".join(vals) + " |")


if __name__ == "__main__":
    main()
