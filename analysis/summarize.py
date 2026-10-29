#!/usr/bin/env python3
"""Ringkas hasil lm-eval per model dan task ke results/summary.csv dan results/summary.md.

Contoh (dari root repo):
    python analysis/summarize.py --results results/runs --run-id <id> [--compare-run <id2>] --metric acc --out results/
    python analysis/summarize.py --predictions results/predictions/<id> --run-id <id> --out results/
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from stats import (
    bootstrap_ci,
    cluster_bootstrap_ci,
    holm,
    paired_bootstrap_delta,
    paired_cluster_bootstrap_delta,
    stderr,
    unpaired_bootstrap_delta,
)

REPO = Path(__file__).resolve().parent.parent
SAMPLES_RE = re.compile(r"^samples_(?P<task>.+)_(?P<ts>\d{4}-\d{2}-\d{2}T[\d.-]+)\.jsonl$")
N_BOOT = 10000
SEED = 0
SANITY_MIN_PARAMS_B = 20.0
SANITY_MARGIN = 0.05
META_KEYS = ("n_options", "random_baseline")
META_NAME_KEYS = ("lm_eval_task", "task", "name", "key")


@dataclass
class Samples:
    values: dict[Any, float]
    targets: dict[Any, str]
    n_choices: int | None
    clusters: dict[Any, str] | None = None  # doc_id -> cluster label; None when the task is not clustered


@dataclass
class PairResult:
    n: int
    delta: float
    lo: float
    hi: float
    p: float


RunData = dict[str, dict[str, Samples]]


def f3(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x:.3f}"


def ci_text(lo: float, hi: float) -> str:
    return f"[{f3(lo)}, {f3(hi)}]"


def verdict(lo: float, hi: float) -> str:
    return "bermakna" if (lo > 0 or hi < 0) else "tidak bermakna"


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return lines


def load_yaml(path: Path, notes: list[str]) -> dict[str, Any]:
    if not path.is_file():
        notes.append(f"`{path.name}` tidak ditemukan, bagian terkait dilewati")
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_samples(path: Path, metric: str) -> tuple[Samples | None, str | None]:
    with path.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if any(r.get("filter") == "none" for r in rows):
        rows = [r for r in rows if r.get("filter", "none") == "none"]
    values: dict[Any, float] = {}
    targets: dict[Any, str] = {}
    n_choices: int | None = None
    for r in rows:
        doc_id = r["doc_id"]
        if doc_id in values:
            continue
        if metric not in r:
            return None, f"metrik `{metric}` tidak ada di {path.name}"
        values[doc_id] = float(r[metric])
        targets[doc_id] = str(r.get("target"))
        # lm_eval: resps is one list per choice; API runs store the response text there instead.
        if n_choices is None and isinstance(r.get("resps"), list) and len(r["resps"]) > 1:
            n_choices = len(r["resps"])
    return Samples(values, targets, n_choices), None


def find_latest_samples(task_dir: Path) -> dict[str, Path]:
    """Map lm_eval task name to its samples file with the latest timestamp (recursive)."""
    latest: dict[str, tuple[str, Path]] = {}
    for path in task_dir.rglob("samples_*.jsonl"):
        m = SAMPLES_RE.match(path.name)
        if m is None:
            continue
        task, ts = m["task"], m["ts"]
        if task not in latest or ts > latest[task][0]:
            latest[task] = (ts, path)
    return {task: path for task, (_, path) in latest.items()}


def visible_dirs(path: Path) -> list[Path]:
    return sorted(p for p in path.iterdir() if p.is_dir() and not p.name.startswith("."))


def load_run(results_root: Path, run_id: str, metric: str, notes: list[str]) -> RunData:
    run_dir = results_root / run_id
    if not run_dir.is_dir():
        notes.append(f"run `{run_id}` tidak ditemukan di `{run_dir}`")
        return {}
    data: RunData = {}
    for model_dir in visible_dirs(run_dir):
        tasks: dict[str, Samples] = {}
        for task_dir in visible_dirs(model_dir):
            for task, path in find_latest_samples(task_dir).items():
                samples, err = load_samples(path, metric)
                if samples is None:
                    notes.append(f"`{model_dir.name}/{task}`: {err}")
                    continue
                tasks[task] = samples
        if not tasks:
            notes.append(f"`{model_dir.name}` di run `{run_id}` tidak punya samples")
        data[model_dir.name] = tasks
    return data


def load_predictions(pred_dir: Path, notes: list[str]) -> RunData:
    """Muat run dari CSV hasil export_predictions.py: results/predictions/<run-id>/<model>/<task>.csv.gz."""
    if not pred_dir.is_dir():
        notes.append(f"folder prediksi `{pred_dir}` tidak ditemukan")
        return {}
    data: RunData = {}
    for model_dir in visible_dirs(pred_dir):
        tasks = {p.name.removesuffix(".csv.gz"): load_prediction_csv(p) for p in sorted(model_dir.glob("*.csv.gz"))}
        if not tasks:
            notes.append(f"`{model_dir.name}` di `{pred_dir}` tidak punya prediksi")
        data[model_dir.name] = tasks
    return data


def load_prediction_csv(path: Path) -> Samples:
    """Kolom correct sama dengan metrik acc di samples jsonl, jadi hanya acc yang didukung."""
    values: dict[Any, float] = {}
    targets: dict[Any, str] = {}
    clusters: dict[Any, str] = {}
    empty_clusters = 0
    n_choices: int | None = None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            doc_id = int(row["doc_id"])
            values[doc_id] = float(row["correct"])
            targets[doc_id] = row["target"]
            if row.get("cluster"):
                clusters[doc_id] = row["cluster"]
            else:
                empty_clusters += 1
            if n_choices is None and row["n_choices"]:
                n_choices = int(row["n_choices"])
    if clusters and empty_clusters:
        raise ValueError(f"{path.name}: kolom cluster terisi sebagian ({len(clusters)} terisi, {empty_clusters} kosong)")
    return Samples(values, targets, n_choices, clusters or None)


def collect_task_meta(node: Any, out: dict[str, dict[str, Any]]) -> None:
    """Loosely find per-task metadata (n_options / random_baseline) anywhere in tasks.yaml."""
    if isinstance(node, dict):
        if any(k in node for k in META_KEYS):
            name = next((node[k] for k in META_NAME_KEYS if isinstance(node.get(k), str)), None)
            if name:
                out.setdefault(name, node)
            for task in node.get("lm_eval_tasks") or []:  # benchmark entries list their lm_eval tasks
                out.setdefault(task, node)
        for key, value in node.items():
            if isinstance(key, str) and isinstance(value, dict) and any(k in value for k in META_KEYS):
                out.setdefault(key, value)
            collect_task_meta(value, out)
    elif isinstance(node, list):
        for item in node:
            collect_task_meta(item, out)


def random_baseline(task: str, samples: Samples, meta: dict[str, dict[str, Any]]) -> float | None:
    m = meta.get(task, {})
    if isinstance(m.get("random_baseline"), (int, float)):
        return float(m["random_baseline"])
    n_options = m.get("n_options") or samples.n_choices
    return 1.0 / n_options if n_options else None


def mean_of(s: Samples) -> float:
    return float(np.mean(list(s.values.values()))) if s.values else float("nan")


def aligned(a: Samples, b: Samples) -> tuple[np.ndarray, np.ndarray]:
    common = sorted(set(a.values) & set(b.values), key=str)
    return (np.array([a.values[k] for k in common], dtype=float),
            np.array([b.values[k] for k in common], dtype=float))


def paired_result(a: Samples, b: Samples) -> PairResult | None:
    xa, xb = aligned(a, b)
    if xa.size == 0:
        return None
    delta, lo, hi, p = paired_bootstrap_delta(xa, xb, n=N_BOOT, seed=SEED)
    return PairResult(xa.size, delta, lo, hi, p)


def is_parallel(a: Samples, b: Samples) -> bool:
    """Same doc_id set and same gold label per doc_id."""
    return bool(a.values) and set(a.values) == set(b.values) and all(
        a.targets[k] == b.targets[k] for k in a.values
    )


def section_scores(run: RunData, meta: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    table = []
    for model, tasks in run.items():
        for task, s in sorted(tasks.items()):
            vals = np.array([s.values[k] for k in sorted(s.values, key=str)], dtype=float)
            score, lo, hi = bootstrap_ci(vals, n=N_BOOT, seed=SEED)
            rb = random_baseline(task, s, meta)
            above = None if rb is None else lo > rb
            se = stderr(vals)
            rows.append({
                "model": model, "task": task, "score": score, "stderr": se,
                "ci_lo": lo, "ci_hi": hi, "n": vals.size,
                "random_baseline": rb, "above_random": above,
            })
            table.append([model, task, str(vals.size), f"{f3(score)} {ci_text(lo, hi)}",
                          f3(se), f3(rb), "-" if above is None else ("ya" if above else "tidak")])
    if not table:
        return ["_Dilewati: tidak ada skor untuk ditampilkan._"]
    return md_table(["Model", "Task (lm_eval)", "n", "Skor [95% CI]", "stderr", "Random", "Di atas random"], table)


def section_pairs(run: RunData, models: dict[str, Any]) -> list[str]:
    table, notes = [], []
    for key, cfg in models.items():
        pair = (cfg or {}).get("pair") or {}
        if pair.get("role") != "derived":
            continue
        base = pair.get("base")
        if key not in run or base not in run:
            notes.append(f"`{key}` vs `{base}`: salah satu model tidak ada di run")
            continue
        common = sorted(set(run[key]) & set(run[base]))
        if not common:
            notes.append(f"`{key}` vs `{base}`: tidak ada task yang sama")
        for task in common:
            r = paired_result(run[key][task], run[base][task])
            if r is None:
                notes.append(f"`{key}` vs `{base}` / {task}: tidak ada doc_id yang sama")
                continue
            table.append([key, base, task, str(r.n), f"{r.delta:+.3f}", ci_text(r.lo, r.hi),
                          f"{r.p:.4f}", verdict(r.lo, r.hi)])
    lines = md_table(["Derived", "Base", "Task", "n (doc_id irisan)", "Delta (derived - base)",
                      "CI 95%", "p", "Status"], table) if table else []
    if not table:
        lines.append("_Dilewati: tidak ada pasangan derived-base yang lengkap di run ini._")
    return lines + [f"_Dilewati: {n}_" for n in notes]


def section_regional(run: RunData, cfg: dict[str, Any]) -> list[str]:
    regional = cfg.get("regional") or []
    latest = cfg.get("latest") or []
    if not regional or not latest:
        return ["_Dilewati: `comparisons.regional_vs_latest` kosong di models.yaml._"]
    table, notes = [], []
    for reg in regional:
        for lat in latest:
            if reg not in run or lat not in run:
                notes.append(f"`{reg}` vs `{lat}`: salah satu model tidak ada di run")
                continue
            for task in sorted(set(run[reg]) & set(run[lat])):
                r = paired_result(run[reg][task], run[lat][task])
                if r is None:
                    continue
                table.append([reg, lat, task, str(r.n), f"{r.delta:+.3f}", ci_text(r.lo, r.hi),
                              f"{r.p:.4f}", verdict(r.lo, r.hi)])
    lines = md_table(["Regional", "Terbaru", "Task", "n (doc_id irisan)", "Delta (regional - terbaru)",
                      "CI 95%", "p", "Status"], table) if table else []
    if not table:
        lines.append("_Dilewati: tidak ada pasangan regional-terbaru yang bisa dibandingkan._")
    return lines + [f"_Dilewati: {n}_" for n in notes]


def standard_colloquial_stems(tasks: dict[str, Samples]) -> list[tuple[str, str]]:
    out = []
    for task in sorted(tasks):
        m = re.match(r"^(.+)_standard(_t\d+)?$", task)
        if m and f"{m[1]}_colloquial{m[2] or ''}" in tasks:
            out.append((task, f"{m[1]}_colloquial{m[2] or ''}"))
    return out


def section_copa_gap(run: RunData) -> list[str]:
    table = []
    for model, tasks in run.items():
        for std, col in standard_colloquial_stems(tasks):
            a, b = tasks[std], tasks[col]
            if is_parallel(a, b):
                r = paired_result(a, b)
                how = "paired (doc_id sejajar)"
                delta, lo, hi, p = r.delta, r.lo, r.hi, r.p
                n = r.n
            else:
                xa = np.array(list(a.values.values()), dtype=float)
                xb = np.array(list(b.values.values()), dtype=float)
                delta, lo, hi, p = unpaired_bootstrap_delta(xa, xb, n=N_BOOT, seed=SEED)
                n = f"{xa.size}/{xb.size}"
                how = "UNPAIRED (doc_id tidak sejajar)"
            table.append([model, std, col, str(n), f"{delta:+.3f}", ci_text(lo, hi), f"{p:.4f}",
                          verdict(lo, hi), how])
    if not table:
        return ["_Dilewati: tidak ada pasangan `*_standard` / `*_colloquial` di run ini._"]
    return md_table(["Model", "Baku", "Kolokial", "n", "Gap (baku - kolokial)", "CI 95%", "p",
                     "Status", "Metode"], table)


def section_mmlu_gap(run: RunData) -> list[str]:
    table = []
    for model, tasks in run.items():
        for task in sorted(tasks):
            ca = re.sub(r"_cs(_t\d+)?$", r"_ca\1", task)  # global_mmlu_full_id_cs_t0 -> ..._ca_t0
            if ca == task or ca not in tasks:
                continue
            a, b = tasks[task], tasks[ca]
            xa = np.array(list(a.values.values()), dtype=float)
            xb = np.array(list(b.values.values()), dtype=float)
            delta, lo, hi, p = unpaired_bootstrap_delta(xa, xb, n=N_BOOT, seed=SEED)
            table.append([model, task, ca, f"{xa.size}/{xb.size}", f"{delta:+.3f}",
                          ci_text(lo, hi), f"{p:.4f}", verdict(lo, hi)])
    if not table:
        return ["_Dilewati: tidak ada pasangan task `*_cs` / `*_ca` di run ini ._"]
    return md_table(["Model", "CS", "CA", "n (CS/CA)", "Gap (CS - CA)", "CI 95%", "p", "Status"], table)


def section_sanity(run: RunData, models: dict[str, Any], meta: dict[str, dict[str, Any]]) -> list[str]:
    flags, notes = [], []
    for model, tasks in run.items():
        if model not in models:
            notes.append(f"`{model}` tidak ada di models.yaml, cek params dilewati")
            continue
        params = (models[model] or {}).get("params_b")
        if params is None or params < SANITY_MIN_PARAMS_B:
            continue
        for task, s in sorted(tasks.items()):
            rb = random_baseline(task, s, meta)
            if rb is None:
                continue
            score = mean_of(s)
            if abs(score - rb) <= SANITY_MARGIN:
                flags.append(f"- `{model}` / `{task}`: skor {f3(score)} vs random {f3(rb)} "
                             f"(selisih {score - rb:+.3f}), periksa setup evaluasi")
    lines = flags if flags else ["Tidak ada model >= 20B yang skornya dalam 5 poin dari random."]
    return lines + [f"_Dilewati: {n}_" for n in notes]


def section_noise(run: RunData, cmp_run: RunData) -> list[str]:
    table = []
    for model in sorted(set(run) & set(cmp_run)):
        for task in sorted(set(run[model]) & set(cmp_run[model])):
            a, b = run[model][task], cmp_run[model][task]
            r = paired_result(a, b)
            if r is None:
                continue
            table.append([model, task, str(r.n), f3(mean_of(a)), f3(mean_of(b)), f"{r.delta:+.3f}",
                          ci_text(r.lo, r.hi), f"{r.p:.4f}", verdict(r.lo, r.hi)])
    if not table:
        return ["_Dilewati: tidak ada model/task yang sama di kedua run._"]
    return md_table(["Model", "Task", "n", "Skor run1", "Skor run2", "Delta (run1 - run2)", "CI 95%",
                     "p", "Status"], table)


def section_tokenizer(path: Path) -> list[str]:
    if not path.is_file():
        return [f"_Dilewati: `{path.name}` tidak ditemukan._"]
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = [r for r in reader if r]
    if len(rows) < 2:
        return [f"_Dilewati: `{path.name}` kosong._"]
    return md_table(rows[0], rows[1:])


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["model", "task", "score", "stderr", "ci_lo", "ci_hi", "n", "random_baseline", "above_random"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            out = {k: r[k] for k in fields}
            for k in ("score", "stderr", "ci_lo", "ci_hi", "random_baseline"):
                out[k] = "" if out[k] is None else f"{out[k]:.6f}"
            out["above_random"] = "" if r["above_random"] is None else str(r["above_random"]).lower()
            writer.writerow(out)


def section_best(run: RunData, best_rows: list[dict[str, Any]]) -> list[str]:
    """Every model vs the best model on each task (paired bootstrap), Holm-corrected within the task.

    A model is "tied with best" when its deficit is not significant after correction. Feeds the
    shading in results/results_table.png.
    """
    tasks = sorted({t for per_model in run.values() for t in per_model})
    lines = md_table(["Task", "Terbaik", "Model", "Delta vs terbaik", "CI 95%", "p", "p Holm sig.", "Status"], [])
    for task in tasks:
        have = {m: per_model[task] for m, per_model in run.items() if task in per_model}
        if len(have) < 2:
            continue
        best = max(have, key=lambda m: mean_of(have[m]))
        others = [m for m in sorted(have) if m != best]
        results = {m: paired_result(have[m], have[best]) for m in others}
        valid = [m for m in others if results[m] is not None]
        reject = dict(zip(valid, holm([results[m].p for m in valid])))
        best_rows.append({"task": task, "model": best, "best": best, "delta": 0.0, "ci_lo": 0.0, "ci_hi": 0.0,
                          "p": 1.0, "holm_significant": False, "tied_with_best": True})
        for m in valid:
            r = results[m]
            tied = not reject[m]
            best_rows.append({"task": task, "model": m, "best": best, "delta": r.delta, "ci_lo": r.lo,
                              "ci_hi": r.hi, "p": r.p, "holm_significant": reject[m], "tied_with_best": tied})
            lines.append(f"| {task} | {best} | {m} | {r.delta:+.3f} | {ci_text(r.lo, r.hi)} | {r.p:.4f} | "
                         f"{'ya' if reject[m] else 'tidak'} | {'seri dengan terbaik' if tied else 'di bawah terbaik'} |")
    return lines


def aligned_clustered(a: Samples, b: Samples) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Like aligned(), plus the cluster label of each aligned doc_id (taken from a; b must agree)."""
    common = sorted(set(a.values) & set(b.values), key=str)
    cl_a = a.clusters or {}
    cl_b = b.clusters or {}
    if any(cl_a.get(k) != cl_b.get(k) for k in common):
        raise ValueError("label cluster a dan b tidak sama untuk doc_id yang sama")
    return (np.array([a.values[k] for k in common], dtype=float),
            np.array([b.values[k] for k in common], dtype=float),
            np.array([cl_a[k] for k in common], dtype=object))


def ratio_text(r: float) -> str:
    return "-" if math.isnan(r) else f"{r:.2f}x"


CLUSTERED_FIELDS = ["kind", "model", "ref", "task", "n_items", "n_clusters", "delta", "iid_lo", "iid_hi",
                    "cl_lo", "cl_hi", "width_ratio", "p_iid", "p_cluster", "verdict_iid", "verdict_cluster",
                    "changed"]


def section_clustered(run: RunData, models: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    """Item-level CI vs cluster-bootstrap CI for clustered tasks only (IndoMMLU, Global-MMLU, IndoCulture).

    Rows (kind): "ci" per model x task, "pair" for the derived-base comparisons in models.yaml,
    "best" for every model vs the best model on the task (Holm within the task, as in section_best).
    """
    lines: list[str] = []

    # (a) CI per model x clustered task.
    table = []
    for model, tasks in run.items():
        for task, s in sorted(tasks.items()):
            if not s.clusters:
                continue
            keys = sorted(s.values, key=str)
            vals = np.array([s.values[k] for k in keys], dtype=float)
            cl = np.array([s.clusters[k] for k in keys], dtype=object)
            score, lo_i, hi_i = bootstrap_ci(vals, n=N_BOOT, seed=SEED)
            _, lo_c, hi_c = cluster_bootstrap_ci(vals, cl, n_boot=N_BOOT, seed=SEED)
            n_cl = len(set(cl.tolist()))
            ratio = (hi_c - lo_c) / (hi_i - lo_i)
            rows.append({"kind": "ci", "model": model, "ref": "", "task": task, "n_items": vals.size,
                         "n_clusters": n_cl, "delta": score, "iid_lo": lo_i, "iid_hi": hi_i, "cl_lo": lo_c,
                         "cl_hi": hi_c, "width_ratio": ratio, "p_iid": None, "p_cluster": None,
                         "verdict_iid": "", "verdict_cluster": "", "changed": ""})
            table.append([model, task, str(vals.size), str(n_cl), f"{f3(score)} {ci_text(lo_i, hi_i)}",
                          f"{ci_text(lo_c, hi_c)}", ratio_text(ratio)])
    lines += ["**a. Skor dengan CI iid vs CI berkelompok**", ""]
    lines += md_table(["Model", "Task", "n item", "n klaster", "Skor [CI iid]", "CI berkelompok",
                       "Rasio lebar (berkelompok / iid)"], table) if table else ["_Dilewati: tidak ada task berkluster._"]
    lines.append("")

    # (b1) CPT pairs from models.yaml, clustered tasks only.
    table, notes = [], []
    for key, cfg in models.items():
        pair = (cfg or {}).get("pair") or {}
        if pair.get("role") != "derived":
            continue
        base = pair.get("base")
        if key not in run or base not in run:
            continue
        for task in sorted(set(run[key]) & set(run[base])):
            a, b = run[key][task], run[base][task]
            if not (a.clusters and b.clusters):
                continue
            xa, xb, cl = aligned_clustered(a, b)
            if xa.size == 0:
                notes.append(f"`{key}` vs `{base}` / {task}: tidak ada doc_id yang sama")
                continue
            delta, lo_i, hi_i, p_i = paired_bootstrap_delta(xa, xb, n=N_BOOT, seed=SEED)
            _, lo_c, hi_c, p_c = paired_cluster_bootstrap_delta(xa, xb, cl, n_boot=N_BOOT, seed=SEED)
            v_i, v_c = verdict(lo_i, hi_i), verdict(lo_c, hi_c)
            changed = v_i != v_c
            n_cl = len(set(cl.tolist()))
            rows.append({"kind": "pair", "model": key, "ref": base, "task": task, "n_items": xa.size,
                         "n_clusters": n_cl, "delta": delta, "iid_lo": lo_i, "iid_hi": hi_i, "cl_lo": lo_c,
                         "cl_hi": hi_c, "width_ratio": (hi_c - lo_c) / (hi_i - lo_i), "p_iid": p_i,
                         "p_cluster": p_c, "verdict_iid": v_i, "verdict_cluster": v_c,
                         "changed": "ya" if changed else "tidak"})
            table.append([key, base, task, str(n_cl), f"{delta:+.3f}", ci_text(lo_i, hi_i),
                          ci_text(lo_c, hi_c), f"{p_c:.4f}", v_i, v_c, "ya" if changed else "tidak"])
    lines += ["**b1. Selisih pasangan derived - base (task berkluster)**", ""]
    lines += md_table(["Derived", "Base", "Task", "n klaster", "Delta", "CI iid", "CI berkelompok", "p berkelompok",
                       "Status iid", "Status berkelompok", "Berubah"], table) if table \
        else ["_Dilewati: tidak ada pasangan derived-base berkluster di run ini._"]
    lines += [f"_Dilewati: {n}_" for n in notes]
    lines.append("")

    # (b2) best-per-task on clustered tasks, Holm within the task, same logic as section_best.
    table = []
    tasks = sorted({t for per_model in run.values() for t in per_model})
    for task in tasks:
        have = {m: per_model[task] for m, per_model in run.items() if task in per_model}
        if len(have) < 2 or not all(s.clusters for s in have.values()):
            continue
        best = max(have, key=lambda m: mean_of(have[m]))
        others = [m for m in sorted(have) if m != best]
        iid, cl_res, n_cl = {}, {}, {}
        for m in others:
            xa, xb, cl = aligned_clustered(have[m], have[best])
            if xa.size == 0:
                continue
            iid[m] = paired_bootstrap_delta(xa, xb, n=N_BOOT, seed=SEED)
            cl_res[m] = paired_cluster_bootstrap_delta(xa, xb, cl, n_boot=N_BOOT, seed=SEED)
            n_cl[m] = len(set(cl.tolist()))
        valid = [m for m in others if m in iid]
        rej_i = dict(zip(valid, holm([iid[m][3] for m in valid])))
        rej_c = dict(zip(valid, holm([cl_res[m][3] for m in valid])))
        for m in valid:
            d, lo_i, hi_i, p_i = iid[m]
            _, lo_c, hi_c, p_c = cl_res[m]
            v_i = "seri dengan terbaik" if not rej_i[m] else "di bawah terbaik"
            v_c = "seri dengan terbaik" if not rej_c[m] else "di bawah terbaik"
            changed = v_i != v_c
            rows.append({"kind": "best", "model": m, "ref": best, "task": task, "n_items": len(have[m].values),
                         "n_clusters": n_cl[m], "delta": d, "iid_lo": lo_i, "iid_hi": hi_i, "cl_lo": lo_c,
                         "cl_hi": hi_c, "width_ratio": (hi_c - lo_c) / (hi_i - lo_i), "p_iid": p_i,
                         "p_cluster": p_c, "verdict_iid": v_i, "verdict_cluster": v_c,
                         "changed": "ya" if changed else "tidak"})
            table.append([task, best, m, f"{d:+.3f}", ci_text(lo_i, hi_i), ci_text(lo_c, hi_c), f"{p_c:.4f}",
                          "ya" if rej_c[m] else "tidak", v_i, v_c, "ya" if changed else "tidak"])
    lines += ["**b2. Semua model vs terbaik per task (task berkluster, Holm per task)**", ""]
    lines += md_table(["Task", "Terbaik", "Model", "Delta vs terbaik", "CI iid", "CI berkelompok", "p berkelompok",
                       "Holm sig. berkelompok", "Status iid", "Status berkelompok", "Berubah"], table) if table \
        else ["_Dilewati: tidak ada task berkluster dengan minimal dua model._"]
    return lines


def build_markdown(args: argparse.Namespace, run: RunData, cmp_run: RunData | None, models: dict[str, Any],
                   cfg_compare: dict[str, Any], meta: dict[str, dict[str, Any]], rows: list[dict[str, Any]],
                   notes: list[str], best_rows: list[dict[str, Any]], cl_rows: list[dict[str, Any]]) -> str:
    header = [f"# Ringkasan indobench: run `{args.run_id}`", "",
              f"- Metrik: `{args.metric}`", f"- Model di run: {len(run)}",
              f"- Compare run: `{args.compare_run}`" if args.compare_run else "- Compare run: -", ""]
    body: list[str] = []

    def add(title: str, lines: list[str]) -> None:
        body.extend([f"## {title}", ""] + lines + [""])

    add("a. Skor per model dan task", section_scores(run, meta, rows))
    add("b. Selisih pasangan (derived - base)", section_pairs(run, models))
    add("c. Regional vs terbaru", section_regional(run, cfg_compare))
    add("d. Gap baku vs kolokial (COPA-ID)", section_copa_gap(run))
    add("e. Gap Global-MMLU CS vs CA", section_mmlu_gap(run))
    add("f. Sanity: model >= 20B dekat random", section_sanity(run, models, meta))
    add("i. Semua model vs terbaik per task (paired bootstrap, koreksi Holm per task)", section_best(run, best_rows))
    add("j. CI berkelompok (cluster bootstrap, task berkluster saja)", section_clustered(run, models, cl_rows))
    if cmp_run is not None:
        add("g. Noise floor antar-run", section_noise(run, cmp_run))
    add("h. Fertilitas tokenizer", section_tokenizer(args.out_dir / "tokenizer_fertility.csv"))
    if notes:
        add("Catatan", [f"- {n}" for n in notes])
    return "\n".join(header + body)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, default=Path("results/runs"))
    p.add_argument("--run-id", required=True)
    p.add_argument("--compare-run")
    p.add_argument("--metric", default="acc")
    p.add_argument("--out", dest="out_dir", type=Path, default=Path("results"))
    p.add_argument("--models", type=Path, default=REPO / "configs/models.yaml")
    p.add_argument("--tasks", type=Path, default=REPO / "configs/tasks.yaml")
    # Muat run dari CSV prediksi (results/predictions/<run-id>) alih-alih samples jsonl di --results.
    p.add_argument("--predictions", type=Path)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    notes: list[str] = []
    cfg = load_yaml(args.models, notes)
    models = cfg.get("models") or {}
    cfg_compare = (cfg.get("comparisons") or {}).get("regional_vs_latest") or {}
    meta: dict[str, dict[str, Any]] = {}
    collect_task_meta(load_yaml(args.tasks, notes), meta)

    if args.predictions is not None:
        if args.metric != "acc":
            notes.append(f"`--predictions` hanya membawa metrik acc, `--metric {args.metric}` diabaikan")
        run = load_predictions(args.predictions, notes)
    else:
        run = load_run(args.results, args.run_id, args.metric, notes)
    cmp_run = load_run(args.results, args.compare_run, args.metric, notes) if args.compare_run else None
    for key in run:
        if models and key not in models:
            notes.append(f"model `{key}` di run tidak ada di models.yaml (tanpa info pair/params)")

    rows: list[dict[str, Any]] = []
    best_rows: list[dict[str, Any]] = []
    cl_rows: list[dict[str, Any]] = []
    md = build_markdown(args, run, cmp_run, models, cfg_compare, meta, rows, notes, best_rows, cl_rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "summary.csv", rows)
    (args.out_dir / "summary.md").write_text(md + "\n", encoding="utf-8")
    with (args.out_dir / "best_per_task.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["task", "model", "best", "delta", "ci_lo", "ci_hi", "p",
                                          "holm_significant", "tied_with_best"])
        w.writeheader()
        for r in best_rows:
            w.writerow({**r, **{k: f"{r[k]:.6f}" for k in ("delta", "ci_lo", "ci_hi", "p")},
                        "holm_significant": str(r["holm_significant"]).lower(),
                        "tied_with_best": str(r["tied_with_best"]).lower()})
    with (args.out_dir / "clustered.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CLUSTERED_FIELDS)
        w.writeheader()
        for r in cl_rows:
            out = dict(r)
            for k in ("delta", "iid_lo", "iid_hi", "cl_lo", "cl_hi", "width_ratio", "p_iid", "p_cluster"):
                out[k] = "" if r[k] is None else f"{r[k]:.6f}"
            w.writerow(out)
    print(f"Ditulis: {args.out_dir / 'summary.csv'} ({len(rows)} baris), {args.out_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
