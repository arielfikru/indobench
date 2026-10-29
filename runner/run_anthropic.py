#!/usr/bin/env python3
"""Run indobench MCQ tasks against Claude models on the Anthropic API (official SDK).

Same prompts and letter extraction as runner/run_api.py (OpenRouter); see its docstring for why this
is a reference point rather than a like-for-like comparison with the vllm loglikelihood runs.

Per-model settings follow the Claude 5.5 API rules (no sampling parameters, no prefill):
  claude-haiku-5.5   thinking disabled
  claude-sonnet-5.5  thinking between_tools (no tools here, so no thinking)
  claude-opus-5.5    thinking cannot be disabled; effort low, thinking tokens are billed and logged
max_tokens leaves room for an explanation before the letter (16 cut off ~10% of answers in the smoke test).

Modes:
  sync (default)  concurrent requests, resumable per doc_id; use for smoke tests
  --batch         one Message Batch per model (50% price); re-run the same command to poll / collect

Key: ANTHROPIC_API_KEY, or --key-file (scripts/save_anthropic_key.sh writes one from the clipboard).

Usage:
  python runner/run_anthropic.py --run-id api-claude --models haiku,sonnet,opus --limit 5
  python runner/run_anthropic.py --run-id api-claude --models haiku --batch
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_api import REPO, build_items, extract, load_tasks, log  # noqa: E402

PRESETS = {
    "haiku": {"key": "claude-haiku-5.5", "model": "claude-haiku-5-5", "max_tokens": 512,
              "extra": {"thinking": {"type": "disabled"}}, "price": (0.10, 0.50)},
    "sonnet": {"key": "claude-sonnet-5.5", "model": "claude-sonnet-5-5", "max_tokens": 512,
               "extra": {"thinking": {"type": "between_tools"}, "output_config": {"effort": "high"}},
               "price": (2.0, 10.0)},
    "opus": {"key": "claude-opus-5.5", "model": "claude-opus-5-5", "max_tokens": 4096,
             "extra": {"output_config": {"effort": "low"}}, "price": (4.0, 20.0)},
}


def params(preset: dict, prompt: str) -> dict:
    return {"model": preset["model"], "max_tokens": preset["max_tokens"],
            "messages": [{"role": "user", "content": prompt}], **preset["extra"]}


def cost(preset: dict, usage: dict, batch: bool) -> float:
    pin, pout = preset["price"]
    c = (usage.get("input_tokens", 0) * pin + usage.get("output_tokens", 0) * pout) / 1e6
    return c / 2 if batch else c


def row_from_message(it: dict, msg, preset: dict, batch: bool) -> dict:
    text = next((b.text for b in msg.content if b.type == "text"), "")
    pred = extract(text, it["choices"])
    usage = {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}
    return {"doc_id": it["doc_id"], "target": str(it["gold"]), "resps": text, "pred": pred,
            "acc": float(pred == it["gold"]), "unparsed": pred is None, "stop_reason": msg.stop_reason,
            "usage": usage, "cost": cost(preset, usage, batch)}


def sample_path(out_dir: Path, task_name: str) -> Path:
    existing = sorted(out_dir.glob(f"samples_{task_name}_*.jsonl"))
    return existing[-1] if existing else out_dir / f"samples_{task_name}_{dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')}.jsonl"


def finish_task(out_dir: Path, task_name: str, path: Path) -> dict:
    rows = [json.loads(line) for line in path.open()]
    summary = {"task": task_name, "n": len(rows), "acc": sum(r["acc"] for r in rows) / len(rows),
               "unparsed": sum(r["unparsed"] for r in rows),
               "input_tokens": sum(r["usage"]["input_tokens"] for r in rows),
               "output_tokens": sum(r["usage"]["output_tokens"] for r in rows),
               "cost": sum(r["cost"] for r in rows)}
    (out_dir / f"DONE_{task_name}.json").write_text(json.dumps(summary, indent=2))
    log(f"  {task_name}: acc {summary['acc']:.3f}  unparsed {summary['unparsed']}/{summary['n']}  "
        f"out tok/item {summary['output_tokens'] / summary['n']:.0f}  ${summary['cost']:.3f}")
    return summary


def todo_items(model_dir: Path, tasks, limit) -> dict[tuple[str, str], tuple[Path, list[dict]]]:
    out = {}
    for bench_key, task_name in tasks:
        out_dir = model_dir / bench_key
        out_dir.mkdir(parents=True, exist_ok=True)
        if (out_dir / f"DONE_{task_name}.json").exists():
            continue
        path = sample_path(out_dir, task_name)
        done = {json.loads(line)["doc_id"] for line in path.open()} if path.exists() else set()
        out[(bench_key, task_name)] = (path, [it for it in build_items(task_name, limit) if it["doc_id"] not in done])
    return out


def run_sync(client, preset: dict, model_dir: Path, tasks, args) -> None:
    for (bench_key, task_name), (path, todo) in todo_items(model_dir, tasks, args.limit).items():
        log(f"{preset['key']} {task_name}: {len(todo)} to do")
        with path.open("a") as f, ThreadPoolExecutor(args.concurrency) as pool:
            futs = {pool.submit(client.messages.create, **params(preset, it["prompt"])): it for it in todo}
            for fut in as_completed(futs):
                f.write(json.dumps(row_from_message(futs[fut], fut.result(), preset, False), ensure_ascii=False) + "\n")
                f.flush()
        finish_task(model_dir / bench_key, task_name, path)


def run_batch(client, preset: dict, model_dir: Path, tasks, args) -> None:
    state_file = model_dir / "batch.json"
    work = todo_items(model_dir, tasks, args.limit)
    index = {f"{task_name}-{it['doc_id']}": (bench_key, task_name, it)
             for (bench_key, task_name), (_, todo) in work.items() for it in todo}
    if not index:
        log(f"{preset['key']}: nothing to do")
        return
    if state_file.exists():
        batch_id = json.loads(state_file.read_text())["batch_id"]
    else:
        reqs = [{"custom_id": cid, "params": params(preset, it["prompt"])} for cid, (_, _, it) in index.items()]
        batch_id = client.messages.batches.create(requests=reqs).id
        state_file.write_text(json.dumps({"batch_id": batch_id, "n": len(reqs),
                                          "created": dt.datetime.now(dt.timezone.utc).isoformat()}))
        log(f"{preset['key']}: batch {batch_id} created with {len(reqs)} requests")
    while True:
        b = client.messages.batches.retrieve(batch_id)
        if b.processing_status == "ended":
            break
        if not args.wait:
            log(f"{preset['key']}: batch {batch_id} {b.processing_status}, {b.request_counts.processing} processing; re-run to collect")
            return
        log(f"{preset['key']}: {b.request_counts.processing} processing, {b.request_counts.succeeded} succeeded")
        time.sleep(60)
    files, errors = {}, 0
    for res in client.messages.batches.results(batch_id):
        if res.custom_id not in index:
            continue
        bench_key, task_name, it = index[res.custom_id]
        if res.result.type != "succeeded":
            errors += 1
            continue
        path = work[(bench_key, task_name)][0]
        f = files.get(path) or files.setdefault(path, path.open("a"))
        f.write(json.dumps(row_from_message(it, res.result.message, preset, True), ensure_ascii=False) + "\n")
    for f in files.values():
        f.close()
    state_file.unlink()
    if errors:
        log(f"{preset['key']}: {errors} requests errored; re-run --batch to retry them")
        return
    for (bench_key, task_name), (path, _) in work.items():
        finish_task(model_dir / bench_key, task_name, path)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--models", default="haiku", help=f"comma-separated: {','.join(PRESETS)}")
    p.add_argument("--tasks", help="comma-separated benchmark keys or lm_eval task names")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch", action="store_true", help="use the Message Batches API (50%% price)")
    p.add_argument("--wait", action="store_true", help="with --batch: poll until the batch ends")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--results-root", type=Path, default=REPO / "results/runs")
    p.add_argument("--key-file", type=Path, help="file holding the Anthropic key (default: ANTHROPIC_API_KEY)")
    args = p.parse_args()

    import anthropic

    key = args.key_file.read_text().strip() if args.key_file else os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        sys.exit("no key: set ANTHROPIC_API_KEY or pass --key-file")
    client = anthropic.Anthropic(api_key=key, max_retries=8)
    tasks = load_tasks(set(args.tasks.split(",")) if args.tasks else None)
    for name in args.models.split(","):
        preset = PRESETS[name]
        model_dir = args.results_root / args.run_id / preset["key"]
        model_dir.mkdir(parents=True, exist_ok=True)
        (model_dir / "manifest.json").write_text(json.dumps(
            {"model_key": preset["key"], "api": "anthropic", "api_model": preset["model"],
             "request": {k: v for k, v in params(preset, "").items() if k != "messages"},
             "mode": "generative letter answer, regex-extracted", "batch": args.batch, "limit": args.limit,
             "updated": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=2))
        (run_batch if args.batch else run_sync)(client, preset, model_dir, tasks, args)
    log("SEMUA SELESAI")


if __name__ == "__main__":
    main()
