"""Run the model x task matrix on the Colab VM.

Launched detached (nohup setsid) by scripts/start_run.sh, polled by scripts/watch.sh.
The parent process never imports torch/vllm: each model runs in its own lm_eval
subprocess so VRAM is released between models.

Layout of results (default on Drive):
  <results_root>/<run_id>/manifest.json
  <results_root>/<run_id>/<model_key>/<task_key>/{results_*.json, samples_*.jsonl, DONE.json}
  <results_root>/<run_id>/<model_key>/lm_eval.log
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = Path("/content/indobench_status.json")
RUN_LOG = Path("/content/indobench_run.log")
DONE_MARKER = "SEMUA SELESAI"
FATAL_MARKER = "FATAL"
WEIGHT_PATTERNS = ["*.json", "*.safetensors", "*.jinja", "*.model", "*.txt", "*.tiktoken", "tokenizer*"]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


_LOG_FILES: list[Path] = [RUN_LOG]


def log(msg: str) -> None:
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    for path in _LOG_FILES:
        with path.open("a") as f:
            f.write(line + "\n")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return yaml.safe_load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(path)


# ---------- config ----------

def resolve_models(cfg: dict[str, Any], selector: str) -> dict[str, dict[str, Any]]:
    defaults = cfg.get("defaults", {})
    all_models = {k: {**defaults, **v, "key": k} for k, v in cfg["models"].items()}
    if selector == "all":
        return all_models
    if selector == "smoke":
        return {k: m for k, m in all_models.items() if m.get("smoke")}
    keys = [k.strip() for k in selector.split(",") if k.strip()]
    unknown = [k for k in keys if k not in all_models]
    if unknown:
        raise SystemExit(f"unknown model keys: {unknown}")
    return {k: all_models[k] for k in keys}


def resolve_tasks(cfg: dict[str, Any], selector: str) -> list[dict[str, Any]]:
    tasks = [t for t in cfg["benchmarks"] if not t.get("disabled")]
    if selector == "all":
        return tasks
    keys = {k.strip() for k in selector.split(",")}
    chosen = [t for t in tasks if t["key"] in keys]
    if len(chosen) != len(keys):
        raise SystemExit(f"unknown task keys: {keys - {t['key'] for t in chosen}}")
    return chosen


# ---------- environment ----------

def gpu_info() -> dict[str, Any]:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return {"error": out.stderr.strip()}
    name, mem_mib, driver = [s.strip() for s in out.stdout.splitlines()[0].split(",")]
    return {"name": name, "vram_gb": round(int(mem_mib) / 1024, 1), "driver": driver}


def package_versions() -> dict[str, Any]:
    code = (
        "import json, torch, vllm, lm_eval, transformers;"
        "print(json.dumps({'torch': torch.__version__, 'cuda': torch.version.cuda,"
        "'vllm': vllm.__version__, 'lm_eval': lm_eval.__version__,"
        "'transformers': transformers.__version__}))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    if out.returncode != 0:
        return {"error": out.stderr.strip()[-500:]}
    return json.loads(out.stdout.strip().splitlines()[-1])


def free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1e9


# ---------- weights ----------

def cached_repo_dir(hf_cache: Path, repo: str) -> Path:
    return hf_cache / "hub" / ("models--" + repo.replace("/", "--"))


def purge_weights(hf_cache: Path, repo: str) -> None:
    d = cached_repo_dir(hf_cache, repo)
    if d.exists():
        shutil.rmtree(d)
        log(f"purged weights {repo}")
    # huggingface_hub 2.x keeps a second copy of every downloaded file as Xet chunks; deleting only the
    # repo dir left /content/hf_cache at 142 GB after 3 purged models (2026-10-29). Snapshots don't need it.
    xet = hf_cache / "xet"
    if xet.exists():
        shutil.rmtree(xet, ignore_errors=True)
        log("purged xet chunk cache")


def ensure_disk(hf_cache: Path, needed_gb: float, keep_repo: str, models: dict[str, dict]) -> bool:
    if free_gb(hf_cache) >= needed_gb:
        return True
    for m in models.values():
        if m["repo"] != keep_repo:
            purge_weights(hf_cache, m["repo"])
            if free_gb(hf_cache) >= needed_gb:
                return True
    if free_gb(hf_cache) >= needed_gb:
        return True
    # Purging weights was not enough (2026-10-28: 35 GB free after 3 models); log what fills the disk.
    du = subprocess.run("du -xsh /content/* /content/hf_cache/* /content/hf_cache/hub/* /root/.cache/* 2>/dev/null | sort -rh | head -12",
                        shell=True, capture_output=True, text=True).stdout
    log("disk usage after purge:\n" + du)
    return False


def download(model: dict[str, Any]) -> Path:
    from huggingface_hub import snapshot_download

    path = snapshot_download(model["repo"], revision=model["revision"], allow_patterns=WEIGHT_PATTERNS)
    return Path(path)


def chat_template_hash(snapshot: Path) -> str | None:
    jinja = snapshot / "chat_template.jinja"
    if jinja.exists():
        text = jinja.read_text()
    else:
        cfg_path = snapshot / "tokenizer_config.json"
        if not cfg_path.exists():
            return None
        text = json.loads(cfg_path.read_text()).get("chat_template")
        if text is None:
            return None
        if not isinstance(text, str):
            text = json.dumps(text, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


# ---------- lm_eval command ----------

def model_args(model: dict[str, Any], seed: int, snapshot: Path | None = None) -> str:
    # Loading from the local snapshot keeps vllm off the HF API (429 rate limits seen 2026-10-28);
    # repo + revision are still recorded in the manifest.
    source = {"pretrained": str(snapshot)} if snapshot else {"pretrained": model["repo"], "revision": model["revision"]}
    args: dict[str, Any] = {
        **source,
        "dtype": model["dtype"],
        "max_model_len": model["max_model_len"],
        "gpu_memory_utilization": model["gpu_memory_utilization"],
        "seed": seed,
    }
    args.update(model.get("vllm_args") or {})
    if model.get("text_only"):
        args.update(model.get("text_only_args") or {})
    args.update(model.get("thinking_args") or {})
    return ",".join(f"{k}={v}" for k, v in args.items())


def build_command(model: dict[str, Any], lm_tasks: list[str], out_dir: Path, seed: int, limit: int | None,
                  snapshot: Path | None = None) -> list[str]:
    cmd = [
        "lm_eval",
        "--model", "vllm",
        "--model_args", model_args(model, seed, snapshot),
        "--tasks", ",".join(lm_tasks),
        "--include_path", str(REPO_ROOT / "tasks"),
        "--num_fewshot", "0",
        "--batch_size", "auto",
        "--seed", ",".join([str(seed)] * 4),
        "--log_samples",
        "--output_path", str(out_dir),
    ]
    if model.get("apply_chat_template", True):
        cmd.append("--apply_chat_template")
    if limit is not None:
        cmd += ["--limit", str(limit)]
    return cmd


# ---------- results bookkeeping ----------

def done_spec(model: dict[str, Any], task: dict[str, Any], seed: int, limit: int | None) -> dict[str, Any]:
    return {"revision": model["revision"], "lm_eval_tasks": task["lm_eval_tasks"], "seed": seed, "limit": limit}


def is_done(task_dir: Path, spec: dict[str, Any]) -> bool:
    marker = task_dir / "DONE.json"
    if not marker.exists():
        return False
    saved = json.loads(marker.read_text())
    return all(saved.get(k) == v for k, v in spec.items())


def collect_outputs(local_out: Path, task: dict[str, Any], dest: Path) -> int:
    """Copy the latest results json and this task's samples files into dest."""
    dest.mkdir(parents=True, exist_ok=True)
    results = sorted(local_out.rglob("results_*.json"))
    if not results:
        raise RuntimeError(f"no results json under {local_out}")
    shutil.copy2(results[-1], dest / results[-1].name)
    copied = 0
    for name in expand_subtasks(results[-1], task["lm_eval_tasks"]):
        for f in sorted(local_out.rglob(f"samples_{name}_*.jsonl")):
            shutil.copy2(f, dest / f.name)
            copied += 1
    return copied


def expand_subtasks(results_json: Path, names: list[str]) -> set[str]:
    """Task names plus, for lm_eval groups, all their (nested) subtasks."""
    groups = json.loads(results_json.read_text()).get("group_subtasks", {})
    out: set[str] = set()
    stack = list(names)
    while stack:
        name = stack.pop()
        if name not in out:
            out.add(name)
            stack.extend(groups.get(name, []))
    return out


# ---------- main loop ----------

class Runner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.models = resolve_models(load_yaml(REPO_ROOT / "configs/models.yaml"), args.models)
        self.tasks = resolve_tasks(load_yaml(REPO_ROOT / "configs/tasks.yaml"), args.tasks)
        self.limit = args.limit
        self.run_dir = Path(args.results_root) / args.run_id
        self.work_dir = Path(args.work_dir) / args.run_id
        self.hf_cache = Path(args.hf_cache)
        self.manifest_path = self.run_dir / "manifest.json"
        self.status: dict[str, Any] = {"run_id": args.run_id, "state": "running", "done": [], "failed": [], "skipped": []}

    def set_status(self, **kw: Any) -> None:
        self.status.update(kw, updated=now())
        write_json(STATUS_FILE, self.status)

    def load_manifest(self) -> dict[str, Any]:
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text())
        return {"run_id": self.args.run_id, "models": {}, "invocations": []}

    def save_manifest(self, manifest: dict[str, Any]) -> None:
        write_json(self.manifest_path, manifest)

    def run(self) -> int:
        os.environ["HF_HOME"] = str(self.hf_cache)
        # Token is uploaded to ~/.cache/huggingface/token, outside HF_HOME.
        os.environ.setdefault("HF_TOKEN_PATH", str(Path.home() / ".cache/huggingface/token"))
        self.hf_cache.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        _LOG_FILES.append(self.run_dir / "run.log")

        manifest = self.load_manifest()
        manifest["invocations"].append({
            "started": now(),
            "argv": sys.argv,
            "gpu": gpu_info(),
            "packages": package_versions(),
            "seed": self.args.seed,
            "limit": self.limit,
            "system_prompt": None,
        })
        self.save_manifest(manifest)
        log(f"run {self.args.run_id}: {len(self.models)} models x {len(self.tasks)} tasks, limit={self.limit}")

        for key, model in self.models.items():
            self.set_status(current_model=key)
            try:
                self.run_model(key, model, manifest)
            except Exception as e:  # keep going with the next model
                log(f"model {key} failed: {e!r}")
                self.status["failed"].append(key)
                manifest["models"].setdefault(key, {})["error"] = repr(e)
                self.save_manifest(manifest)
                if self.args.stop_on_error:
                    break

        manifest["invocations"][-1]["finished"] = now()
        self.save_manifest(manifest)
        failed = self.status["failed"]
        self.set_status(state="done" if not failed else "done_with_errors", current_model=None)
        log(f"{DONE_MARKER} done={self.status['done']} failed={failed} skipped={self.status['skipped']}")
        return 1 if failed else 0

    def run_model(self, key: str, model: dict[str, Any], manifest: dict[str, Any]) -> None:
        seed = self.args.seed
        pending = [t for t in self.tasks if not is_done(self.run_dir / key / t["key"], done_spec(model, t, seed, self.limit))]
        if not pending:
            log(f"{key}: all tasks done, skip")
            self.status["skipped"].append(key)
            return

        needed = model["bf16_gb"] * 1.1 + self.args.disk_margin_gb
        if not ensure_disk(self.hf_cache, needed, model["repo"], self.models):
            raise RuntimeError(f"not enough disk: need {needed:.0f} GB, free {free_gb(self.hf_cache):.0f} GB")

        log(f"{key}: download {model['repo']}@{model['revision'][:10]} (free {free_gb(self.hf_cache):.0f} GB)")
        t0 = time.time()
        snapshot = download(model)
        log(f"{key}: downloaded in {time.time() - t0:.0f}s")

        lm_tasks = [name for t in pending for name in t["lm_eval_tasks"]]
        local_out = self.work_dir / key
        if local_out.exists():
            shutil.rmtree(local_out)
        cmd = build_command(model, lm_tasks, local_out, seed, self.limit, snapshot)
        entry = {
            "repo": model["repo"],
            "revision": model["revision"],
            "dtype": model["dtype"],
            "max_model_len": model["max_model_len"],
            "chat_template_sha256": chat_template_hash(snapshot),
            "apply_chat_template": model.get("apply_chat_template", True),
            "thinking": model.get("thinking"),
            "thinking_args": model.get("thinking_args"),
            "text_only": model.get("text_only"),
            "seed": seed,
            "limit": self.limit,
            "tasks": [t["key"] for t in pending],
            "command": shlex.join(cmd),
            "started": now(),
        }
        manifest["models"][key] = entry
        self.save_manifest(manifest)

        model_log = self.run_dir / key / "lm_eval.log"
        model_log.parent.mkdir(parents=True, exist_ok=True)
        log(f"{key}: {shlex.join(cmd)}")
        # Not offline: lm_eval still fetches the (pinned) task datasets. Weights are pinned via revision.
        env = {**os.environ, "TOKENIZERS_PARALLELISM": "false"}
        t0 = time.time()
        with model_log.open("w") as f:
            proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=REPO_ROOT,
                                  timeout=self.args.model_timeout_s)
        entry["finished"] = now()
        entry["eval_seconds"] = round(time.time() - t0)
        entry["returncode"] = proc.returncode
        self.save_manifest(manifest)
        if proc.returncode != 0:
            tail = model_log.read_text()[-2000:]
            raise RuntimeError(f"lm_eval exit {proc.returncode}; log tail:\n{tail}")

        for t in pending:
            dest = self.run_dir / key / t["key"]
            n = collect_outputs(local_out, t, dest)
            write_json(dest / "DONE.json", {**done_spec(model, t, seed, self.limit), "samples_files": n, "finished": now()})
        log(f"{key}: done in {entry['eval_seconds']}s ({len(pending)} task groups)")
        self.status["done"].append(key)

        if self.should_purge(key):
            purge_weights(self.hf_cache, model["repo"])

    def should_purge(self, key: str) -> bool:
        if self.args.purge == "always":
            return True
        if self.args.purge == "never":
            return False
        keys = list(self.models)
        rest = keys[keys.index(key) + 1:]
        biggest_next = max((self.models[k]["bf16_gb"] for k in rest), default=0)
        return free_gb(self.hf_cache) < biggest_next * 1.1 + self.args.disk_margin_gb


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-id", required=True)
    p.add_argument("--models", default="smoke", help="'smoke', 'all', or comma-separated keys from configs/models.yaml")
    p.add_argument("--tasks", default="all", help="'all' or comma-separated keys from configs/tasks.yaml")
    p.add_argument("--limit", type=int, default=None, help="max docs per lm_eval task (smoke test: 50)")
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--results-root", default="/content/drive/MyDrive/indobench/results/runs")
    p.add_argument("--work-dir", default="/content/indobench_work")
    p.add_argument("--hf-cache", default="/content/hf_cache")
    p.add_argument("--disk-margin-gb", type=float, default=15.0)
    p.add_argument("--purge", choices=["auto", "always", "never"], default="auto",
                   help="delete model weights after a model finishes (auto = only when disk is short)")
    p.add_argument("--model-timeout-s", type=int, default=6 * 3600)
    p.add_argument("--stop-on-error", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="print the lm_eval commands and exit")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    runner = Runner(args)
    if args.dry_run:
        for key, model in runner.models.items():
            lm_tasks = [n for t in runner.tasks for n in t["lm_eval_tasks"]]
            print(f"# {key}\n{shlex.join(build_command(model, lm_tasks, runner.work_dir / key, args.seed, args.limit))}")
        return 0
    if not Path(args.results_root).parent.exists():
        print(f"{FATAL_MARKER}: results root parent missing ({args.results_root}); mount Drive or pass --results-root",
              flush=True)
        return 2
    try:
        return runner.run()
    except Exception as e:
        log(f"{FATAL_MARKER}: {e!r}")
        runner.set_status(state="fatal", error=repr(e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
