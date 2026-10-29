"""Render the headline results table as a PNG for the README.

Reads results/summary.csv and results/best_per_task.csv (both written by analysis/summarize.py) and
writes results/results_table.png; does the same for results/claude/ -> results/claude_table.png, with the
best open model as a muted reference column. Bold = highest score. Shaded = highest score and every model not
significantly below it (paired bootstrap, Holm-corrected within the task); blue in a highlighted
column, grey otherwise. Regional (GoTo) models are outlined. +/- is the 95% bootstrap CI half-width.

Usage: uv run --with matplotlib python analysis/results_table.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

REPO = Path(__file__).resolve().parent.parent

OPEN_MODELS = [  # (key in summary.csv, header, highlighted)
    ("qwen3.8-27b", "Qwen3.8\n27B", False),
    ("gotoai-gemma3-27b-it", "GoTo\nGemma 3 27B", True),
    ("gemma3-27b-it", "Gemma 3\n27B", False),
    ("gemma4-12b-it", "Gemma 4\n12B", False),
    ("sahabatai-gemma2-9b-it", "Sahabat-AI\n9B", True),
    ("gemma2-9b-it", "Gemma 2\n9B", False),
]
CLAUDE_MODELS = [
    ("claude-haiku-5.5", "Haiku 5.5", False),
    ("claude-sonnet-5.5", "Sonnet 5.5", False),
    ("claude-opus-5.5", "Opus 5.5", False),
]
REFERENCE = ("qwen3.8-27b", "Qwen3.8 27B\n(best open)")
# Batch-price cost for all 21,301 items, from the DONE_*.json files of run api-claude (raw runs not in repo).
CLAUDE_COST = {"claude-haiku-5.5": "$0.31", "claude-sonnet-5.5": "$7.43", "claude-opus-5.5": "$21.70"}
ROWS = [  # (category, benchmark, note, task in summary.csv)
    ("School exams", "IndoMMLU", "incl. local languages", "indommlu_t0"),
    ("Translated MMLU", "Global-MMLU ID", "culturally agnostic", "global_mmlu_full_id_ca_t0"),
    # CS questions are mostly about Western culture (Global-MMLU paper), not Indonesian culture.
    ("Translated MMLU", "Global-MMLU ID", "culturally sensitive", "global_mmlu_full_id_cs_t0"),
    ("Indonesian culture", "IndoCulture", "per province", "indoculture_t0"),
    ("Causal reasoning", "COPAL-ID", "standard", "copal_id_standard_t0"),
    ("Causal reasoning", "COPAL-ID", "colloquial", "copal_id_colloquial_t0"),
]

INK, MUTED, RULE = "#1f1f1f", "#5f6368", "#c4c7c5"
BLUE_FILL, BLUE_LINE, GREY_FILL = "#a8d4fb", "#3b82f6", "#e3e5e8"

# Layout in figure-fraction-like data units: x in [0, 1], y grows downward in row units.
X_CAT, X_TASK, X_NOTE_RIGHT = 0.015, 0.125, 0.395
X_COL0, COL_W = 0.41, 0.0975
HEADER_H, ROW_H = 1.35, 1.0


def load_scores(path: Path) -> dict[tuple[str, str], tuple[float, float]]:
    """(model, task) -> (score %, CI half-width %)."""
    with path.open() as f:
        return {(r["model"], r["task"]): (float(r["score"]) * 100,
                                          (float(r["ci_hi"]) - float(r["ci_lo"])) * 50)
                for r in csv.DictReader(f)}


def load_ties(path: Path) -> set[tuple[str, str]]:
    with path.open() as f:
        return {(r["model"], r["task"]) for r in csv.DictReader(f) if r["tied_with_best"] == "true"}


def render(models, scores, ties, out: Path, caption: str, reference=None, cost=None) -> None:
    """reference: (model key, header) drawn as a muted last column, outside bold/tie marking.
    cost: model key -> text for an extra bottom row."""
    cols = models + ([(reference[0], reference[1], False)] if reference else [])
    n_rows = len(ROWS) + (1 if cost else 0)
    total_h = HEADER_H + n_rows * ROW_H + 0.75
    right = X_COL0 + len(cols) * COL_W + X_CAT  # figure width follows the column count
    fig = plt.figure(figsize=(19 * right, 1.0 + total_h * 0.82), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, right)
    ax.set_ylim(total_h, 0)
    ax.axis("off")
    plt.rcParams["font.family"] = ["Helvetica Neue", "Arial", "DejaVu Sans"]

    def col_x(i: int) -> float:
        return X_COL0 + i * COL_W

    body_top, body_bottom = HEADER_H, HEADER_H + n_rows * ROW_H

    # Header
    ax.text(X_TASK, HEADER_H - 0.3, "Benchmark", fontsize=17, color=INK, va="center")
    for i, (_, header, _) in enumerate(cols):
        ax.text(col_x(i) + COL_W / 2, HEADER_H / 2 + 0.05, header, fontsize=17,
                color=MUTED if reference and i == len(models) else INK,
                ha="center", va="center", linespacing=1.25)
    ax.plot([X_CAT, right - X_CAT], [body_top, body_top], color=RULE, lw=1)

    # Rows
    prev_cat = None
    for r, (cat, bench, note, task) in enumerate(ROWS):
        top = body_top + r * ROW_H
        mid = top + ROW_H / 2
        if cat != prev_cat:
            if prev_cat is not None:
                ax.plot([X_CAT, right - X_CAT], [top, top], color=RULE, lw=1)
            ax.text(X_CAT, top + 0.32, cat, fontsize=15, color=MUTED, va="center")
        else:
            ax.plot([X_TASK, right - X_CAT], [top, top], color=RULE, lw=0.8)
        prev_cat = cat
        ax.text(X_TASK, mid, bench, fontsize=17, color=INK, va="center")
        ax.text(X_NOTE_RIGHT, mid, note, fontsize=14, color=MUTED, va="center", ha="right")

        vals = [scores.get((m, task)) for m, _, _ in cols]
        top_score = max(round(v[0], 1) for v in vals[:len(models)] if v is not None)
        for i, ((m, _, hl), v) in enumerate(zip(cols, vals)):
            if i >= len(models):  # reference column: plain muted score
                if v is not None:
                    ax.text(col_x(i) + COL_W / 2, mid, f"{v[0]:.1f}%", fontsize=19, color=MUTED,
                            ha="center", va="center")
                continue
            if (m, task) in ties:
                ax.add_patch(Rectangle((col_x(i), top), COL_W, ROW_H, lw=0,
                                       facecolor=BLUE_FILL if hl else GREY_FILL, zorder=0))
            if v is None:
                ax.text(col_x(i) + COL_W / 2, mid, "—", fontsize=19, color=INK, ha="center", va="center")
                continue
            ax.text(col_x(i) + COL_W / 2, mid - 0.09, f"{v[0]:.1f}%", fontsize=19, color=INK, ha="center",
                    va="center", fontweight="bold" if round(v[0], 1) == top_score else "normal")
            ax.text(col_x(i) + COL_W / 2, mid + 0.25, f"±{v[1]:.1f}", fontsize=11.5, color=MUTED,
                    ha="center", va="center")
    if cost:
        top = body_top + len(ROWS) * ROW_H
        ax.plot([X_CAT, right - X_CAT], [top, top], color=RULE, lw=1)
        ax.text(X_CAT, top + 0.32, "Cost", fontsize=15, color=MUTED, va="center")
        ax.text(X_TASK, top + ROW_H / 2, "All 21,301 items", fontsize=17, color=INK, va="center")
        ax.text(X_NOTE_RIGHT, top + ROW_H / 2, "batch price", fontsize=14, color=MUTED, va="center", ha="right")
        for i, (m, _, _) in enumerate(models):
            ax.text(col_x(i) + COL_W / 2, top + ROW_H / 2, cost.get(m, "—"), fontsize=19, color=INK,
                    ha="center", va="center")
    ax.plot([X_CAT, right - X_CAT], [body_bottom, body_bottom], color=RULE, lw=1)

    # Outline highlighted (regional) columns over header + body
    for i, (_, _, hl) in enumerate(models):
        if hl:
            ax.add_patch(Rectangle((col_x(i) + 0.002, 0.08), COL_W - 0.004, body_bottom - 0.08,
                                   fill=False, edgecolor=BLUE_LINE, lw=2.6, zorder=5))

    ax.text(X_CAT, body_bottom + 0.42, caption, fontsize=13.5, color=MUTED, va="center")

    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"wrote {out.relative_to(REPO)}")


def main() -> None:
    res = REPO / "results"
    open_scores = load_scores(res / "summary.csv")
    render(OPEN_MODELS, open_scores, load_ties(res / "best_per_task.csv"), res / "results_table.png",
           "Accuracy, zero-shot. Bold: highest. Shaded: highest and models not significantly below it "
           "(paired bootstrap, Holm per task). ±: 95% CI over items. GoTo models outlined. Details: results/summary.md")
    render(CLAUDE_MODELS, {**load_scores(res / "claude/summary.csv"), **open_scores},
           load_ties(res / "claude/best_per_task.csv"), res / "claude_table.png",
           "Accuracy, zero-shot, generative (letter taken from the answer). Bold: highest. Shaded: not "
           "significantly below it (Holm). ±: 95% item CI. Grey column: loglikelihood, reference only.",
           reference=REFERENCE, cost=CLAUDE_COST)


if __name__ == "__main__":
    main()
