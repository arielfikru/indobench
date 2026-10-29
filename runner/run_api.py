#!/usr/bin/env python3
"""Run indobench MCQ tasks against a chat API (OpenRouter) as a closed-model comparator.

Same prompts as the open models (lm_eval doc_to_text of the *_t0 tasks), but generative: the model
answers with a letter, which is extracted with a regex. No log-likelihoods and no answer prefill
(Claude Haiku 5.5 rejects assistant prefill), so scores are a reference point, not a strict
like-for-like comparison with the vllm loglikelihood runs.

Writes the same layout analysis/summarize.py reads:
  <results-root>/<run_id>/<model_key>/<task_key>/samples_<task>_<ts>.jsonl  (doc_id, target, acc, ...)
Resumable: finished doc_ids in an existing partial file are skipped.

Key: OPENROUTER_API_KEY, or a file passed with --key-file (e.g. an OpenRouter key with your own
Anthropic key attached as BYOK). Never logged or written.

Usage:
  python runner/run_api.py --run-id api-haiku --limit 5           # smoke
  python runner/run_api.py --run-id api-haiku                     # full suite
  python runner/run_api.py --run-id api-haiku --dry-run --limit 2 # print prompts, no API calls
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
API_URL = "https://openrouter.ai/api/v1/chat/completions"
LETTER_RE = re.compile(r"^\W*(?:jawaban\W*)?\(?([A-Z])\b", re.IGNORECASE)
# Fallbacks when a model explains first: "Jawaban(nya) (yang paling tepat) (adalah): B", "**B**",
# or a letter alone on the last line. The last match wins.
ANSWER_RE = re.compile(
    r"(?:jawaban(?:nya)?(?:\s+yang\s+(?:paling\s+)?tepat)?(?:\s+adalah)?\s*[:\uff1a]?\s*\**\(?|\*\*\(?)([A-Z])(?![A-Za-z])",
    re.IGNORECASE)
LAST_LINE_RE = re.compile(r"(?:^|\n)\W*([A-Z])\W*$")


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def load_tasks(task_filter: set[str] | None) -> list[tuple[str, str]]:
    cfg = yaml.safe_load((REPO / "configs/tasks.yaml").read_text())
    out = []
    for b in cfg["benchmarks"]:
        for t in b["lm_eval_tasks"]:
            if task_filter is None or b["key"] in task_filter or t in task_filter:
                out.append((b["key"], t))
    return out


def build_items(task_name: str, limit: int | None) -> list[dict]:
    from lm_eval.tasks import TaskManager

    tm = TaskManager(include_path=str(REPO / "tasks"))
    task = tm.load_task_or_group([task_name])[task_name]
    docs = list(task.test_docs())
    items = []
    for doc_id, doc in enumerate(docs[:limit] if limit else docs):
        choices = task.doc_to_choice(doc)
        target = task.doc_to_target(doc)
        gold = target if isinstance(target, int) else choices.index(str(target))
        items.append({"doc_id": doc_id, "prompt": task.doc_to_text(doc), "choices": choices, "gold": gold})
    return items


def call_api(key: str, model: str, prompt: str, max_tokens: int, reasoning: dict | None) -> dict:
    # No temperature/top_p: Claude 5.x models return a 400 on non-default sampling parameters.
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    if reasoning is not None:
        body["reasoning"] = reasoning
    req = urllib.request.Request(API_URL, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 529) and attempt < 5:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 5:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("unreachable")


def extract(text: str, choices: list[str]) -> int | None:
    text = text or ""
    m = LETTER_RE.match(text)
    if m and m[1].upper() in choices:
        return choices.index(m[1].upper())
    hits = [h.upper() for h in ANSWER_RE.findall(text) if h.upper() in choices]
    m = LAST_LINE_RE.search(text.strip())
    if m and m[1] in choices:
        hits.append(m[1])
    return choices.index(hits[-1]) if hits else None


def run_task(args, key: str, model_dir: Path, bench_key: str, task_name: str, usage: dict) -> None:
    out_dir = model_dir / bench_key
    out_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / f"DONE_{task_name}.json").exists():
        log(f"skip {task_name} (done)")
        return
    items = build_items(task_name, args.limit)
    existing = sorted(out_dir.glob(f"samples_{task_name}_*.jsonl"))
    path = existing[-1] if existing else out_dir / f"samples_{task_name}_{dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')}.jsonl"
    done = {json.loads(line)["doc_id"] for line in path.open()} if path.exists() else set()
    todo = [it for it in items if it["doc_id"] not in done]
    log(f"{task_name}: {len(items)} items, {len(todo)} to do")
    if args.dry_run:
        for it in todo[:2]:
            print("---", it["doc_id"], "gold", it["choices"][it["gold"]], "\n" + it["prompt"])
        return
    lock = threading.Lock()
    reasoning = json.loads(args.reasoning) if args.reasoning else None

    def one(it: dict) -> dict:
        resp = call_api(key, args.api_model, it["prompt"], args.max_tokens, reasoning)
        text = (resp.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        pred = extract(text, it["choices"])
        return {"doc_id": it["doc_id"], "target": str(it["gold"]), "resps": text, "pred": pred,
                "acc": float(pred == it["gold"]), "unparsed": pred is None,
                "usage": resp.get("usage", {}), "provider": resp.get("provider")}

    with path.open("a") as f, ThreadPoolExecutor(args.concurrency) as pool:
        futs = [pool.submit(one, it) for it in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            row = fut.result()
            with lock:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                u = row["usage"] or {}
                usage["prompt_tokens"] += u.get("prompt_tokens", 0)
                usage["completion_tokens"] += u.get("completion_tokens", 0)
                usage["cost"] += float(u.get("cost") or 0)
            if i % 500 == 0:
                log(f"  {task_name}: {i}/{len(todo)}  cost so far ${usage['cost']:.3f}")
    rows = [json.loads(line) for line in path.open()]
    acc = sum(r["acc"] for r in rows) / len(rows)
    unparsed = sum(r["unparsed"] for r in rows)
    (out_dir / f"DONE_{task_name}.json").write_text(json.dumps(
        {"task": task_name, "n": len(rows), "acc": acc, "unparsed": unparsed}, indent=2))
    log(f"{task_name}: acc {acc:.3f}  unparsed {unparsed}/{len(rows)}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--model-key", default="claude-haiku-5.5")
    p.add_argument("--api-model", default="anthropic/claude-haiku-5.5", help="OpenRouter model slug")
    p.add_argument("--reasoning", default='{"enabled": false}',
                   help="OpenRouter reasoning object as JSON ('' to omit); thinking off to match the open models")
    p.add_argument("--max-tokens", type=int, default=16)
    p.add_argument("--tasks", help="comma-separated benchmark keys or lm_eval task names")
    p.add_argument("--limit", type=int)
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--results-root", type=Path, default=REPO / "results/runs")
    p.add_argument("--key-file", type=Path, help="file holding the OpenRouter key (default: OPENROUTER_API_KEY)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    key = args.key_file.read_text().strip() if args.key_file else os.environ.get("OPENROUTER_API_KEY", "")
    if not key and not args.dry_run:
        sys.exit("no key: set OPENROUTER_API_KEY or pass --key-file")
    model_dir = args.results_root / args.run_id / args.model_key
    model_dir.mkdir(parents=True, exist_ok=True)
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    task_filter = set(args.tasks.split(",")) if args.tasks else None
    for bench_key, task_name in load_tasks(task_filter):
        run_task(args, key, model_dir, bench_key, task_name, usage)
    if not args.dry_run:
        manifest = {"model_key": args.model_key, "api": "openrouter", "api_model": args.api_model,
                    "reasoning": args.reasoning, "max_tokens": args.max_tokens, "limit": args.limit,
                    "mode": "generative letter answer, regex-extracted", "started": started,
                    "finished": dt.datetime.now(dt.timezone.utc).isoformat(), "usage_this_invocation": usage}
        (model_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        log(f"SEMUA SELESAI  cost this invocation ${usage['cost']:.3f}")


if __name__ == "__main__":
    main()
