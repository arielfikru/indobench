#!/usr/bin/env python3
"""Ekspor prediksi per soal ke results/predictions/<run-id>/<model>/<task>.csv.gz.

Hanya id, hash, label, prediksi, dan nama subject/provinsi yang ditulis. Teks soal, opsi, dan
konteks TIDAK ditulis, karena beberapa dataset berlisensi CC BY-NC-SA dan tidak boleh didistribusikan ulang.

Sumber: file samples_*.jsonl terbaru per model dan task di results/runs/<run-id> (lihat summarize.py).
Kolom: doc_id, doc_hash, target, pred, correct, n_choices, cluster.

Contoh (dari root repo):
    uv run --with numpy --with pyyaml python analysis/export_predictions.py
    uv run --with numpy --with pyyaml python analysis/summarize.py --predictions results/predictions/full-m4 --run-id full-m4 --out /tmp/x1/
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from pathlib import Path

from summarize import REPO, find_latest_samples, load_samples, visible_dirs

COLUMNS = ["doc_id", "doc_hash", "target", "pred", "correct", "n_choices", "cluster"]
DEFAULT_RUNS = ("full-m4", "api-claude")
# API runs log no dataset row, so cluster and n_choices come from this lm_eval run (same docs, same doc_id).
REF_RUN = "full-m4"


def read_rows(path: Path) -> list[dict]:
    """Baris mentah dengan seleksi yang sama seperti load_samples: filter 'none', doc_id pertama saja, urutan file."""
    with path.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if any(r.get("filter") == "none" for r in rows):
        rows = [r for r in rows if r.get("filter", "none") == "none"]
    seen: set = set()
    out: list[dict] = []
    for r in rows:
        if r["doc_id"] in seen:
            continue
        seen.add(r["doc_id"])
        out.append(r)
    return out


def predicted_index(row: dict) -> int | None:
    """Indeks pilihan. lm_eval: argmax loglikelihood (seri -> indeks kecil, seperti np.argmax). Claude: pred tersimpan."""
    if "filtered_resps" in row:
        lls = [float(x[0]) for x in row["filtered_resps"]]
        return max(range(len(lls)), key=lambda i: (lls[i], -i)) if lls else None
    return row.get("pred")


def cluster_of(task: str, row: dict) -> str:
    """subject untuk indommlu dan global_mmlu, province untuk indoculture. Kosong untuk task lain atau bila field hilang."""
    doc = row.get("doc")
    if not isinstance(doc, dict):
        return ""
    if task.startswith(("indommlu", "global_mmlu")):
        field = "subject"
    elif task.startswith("indoculture"):
        field = "province"
    else:
        return ""
    value = doc.get(field)
    return "" if value is None else str(value)


def gold_index(target: str) -> int | None:
    """Hanya untuk cek internal: target huruf (A, B, ...) atau indeks angka ke indeks."""
    if target.isdigit():
        return int(target)
    if len(target) == 1 and target.isalpha():
        return ord(target.upper()) - ord("A")
    return None


def reference_rows(results_root: Path, task: str) -> dict[int, tuple[int | None, str, int]]:
    """doc_id -> (indeks kunci, cluster, n_choices) dari model pertama di REF_RUN yang punya task ini."""
    for model_dir in visible_dirs(results_root / REF_RUN):
        for task_dir in visible_dirs(model_dir):
            path = find_latest_samples(task_dir).get(task)
            if path:
                return {r["doc_id"]: (gold_index(str(r.get("target"))), cluster_of(task, r), len(r["filtered_resps"]))
                        for r in read_rows(path)}
    raise RuntimeError(f"task {task} tidak ada di run {REF_RUN}")


def export_task(path: Path, task: str, out_path: Path,
                ref: dict[int, tuple[int | None, str, int]] | None = None) -> dict[str, int]:
    """Tulis satu file CSV gzip. Mengembalikan statistik kecil untuk ringkasan konsol."""
    # Nilai correct diambil lewat load_samples (metrik acc) supaya sama persis dengan yang dipakai summarize.py.
    samples, err = load_samples(path, "acc")
    if samples is None:
        raise RuntimeError(f"{path}: {err}")
    rows = read_rows(path)
    if {r["doc_id"] for r in rows} != set(samples.values):
        raise RuntimeError(f"{path}: daftar doc_id tidak sama dengan load_samples")

    stats = {"rows": 0, "unparsed": 0, "pred_acc_mismatch": 0}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        with io.TextIOWrapper(gz, encoding="utf-8", newline="") as text:
            writer = csv.writer(text, lineterminator="\n")
            writer.writerow(COLUMNS)
            for r in rows:
                doc_id = r["doc_id"]
                correct = samples.values[doc_id]
                if correct not in (0.0, 1.0):
                    raise RuntimeError(f"{path}: nilai acc bukan 0/1 untuk doc_id {doc_id}")
                pred = predicted_index(r)
                n_choices = len(r["filtered_resps"]) if "filtered_resps" in r else ""
                cluster = cluster_of(task, r)
                if ref is not None:
                    ref_gold, cluster, n_choices = ref[doc_id]
                    if ref_gold != gold_index(str(r.get("target"))):
                        raise RuntimeError(f"{path}: kunci doc_id {doc_id} beda dengan {REF_RUN}")
                if pred is None:
                    stats["unparsed"] += 1
                else:
                    gold = gold_index(str(r.get("target")))
                    if gold is not None and (pred == gold) != bool(correct):
                        stats["pred_acc_mismatch"] += 1
                writer.writerow([
                    doc_id,
                    r.get("doc_hash") or "",
                    r.get("target") if r.get("target") is not None else "",
                    "" if pred is None else pred,
                    int(correct),
                    n_choices,
                    cluster,
                ])
                stats["rows"] += 1
    return stats


def export_run(results_root: Path, run_id: str, out_root: Path) -> None:
    run_dir = results_root / run_id
    if not run_dir.is_dir():
        raise SystemExit(f"run `{run_id}` tidak ditemukan di `{run_dir}`")
    for model_dir in visible_dirs(run_dir):
        for task_dir in visible_dirs(model_dir):
            for task, path in sorted(find_latest_samples(task_dir).items()):
                out_path = out_root / run_id / model_dir.name / f"{task}.csv.gz"
                rows = read_rows(path)
                ref = reference_rows(results_root, task) if rows and "doc" not in rows[0] else None
                st = export_task(path, task, out_path, ref)
                print(f"{run_id}/{model_dir.name}/{task}: {st['rows']} baris, "
                      f"unparsed {st['unparsed']}, pred vs acc tidak cocok {st['pred_acc_mismatch']}")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, default=REPO / "results/runs")
    p.add_argument("--out", type=Path, default=REPO / "results/predictions")
    p.add_argument("--runs", nargs="+", default=list(DEFAULT_RUNS))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    for run_id in args.runs:
        export_run(args.results, run_id, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
