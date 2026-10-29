"""Tokenizer fertility and Indonesian token premium on FLORES+ devtest.

For each model in configs/models.yaml, loads only the tokenizer (pinned revision)
and counts tokens for Indonesian (ind_Latn) and English (eng_Latn) over the
parallel FLORES+ sentences. Gated or failing tokenizers get a status=error row.

Definitions:
  n_words   whitespace split of the raw sentence (str.split()); punctuation is
            not stripped, so "kucing," counts as one word.
  n_tokens  len(tokenizer(text, add_special_tokens=False)["input_ids"]).
  fertility n_tokens / n_words.
  premium_id_en          tokens_ind_total / tokens_eng_total (main metric).
  fertility_ratio_id_en  fertility_ind / fertility_eng.
  tokenizer_hash         sha256 of the backend tokenizer.json (vocab, merges,
                         normalizer, pre-tokenizer). Stricter than vocab+merges,
                         so models sharing a hash truly tokenize identically.

Example:
  uv run --with transformers --with tokenizers --with sentencepiece \
      --with protobuf --with pyyaml --with huggingface_hub \
      python tokenizer/fertility.py --models qwen3.8-27b,gemma4-31b-it
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
MODELS_YAML = ROOT / "configs" / "models.yaml"
DEFAULT_OUT = ROOT / "results" / "tokenizer_fertility.csv"

DATASET = "openlanguagedata/flores_plus"
DATASET_REVISION = "1147e2dc59f37fbb5c22fd8478770de02cd399f9"
LANGS = ("ind_Latn", "eng_Latn")
SANITY_RANGE = (1.0, 3.0)

CSV_COLUMNS = [
    "model_key", "repo", "revision", "tokenizer_hash", "vocab_size", "lang",
    "n_sentences", "n_words", "n_tokens", "fertility", "chars_per_token",
    "premium_id_en", "fertility_ratio_id_en", "dataset", "dataset_revision",
    "split", "status",
]


@dataclass(frozen=True)
class LangStats:
    n_sentences: int
    n_words: int
    n_tokens: int
    n_chars: int

    @property
    def fertility(self) -> float:
        return self.n_tokens / self.n_words

    @property
    def chars_per_token(self) -> float:
        return self.n_chars / self.n_tokens


def load_models(keys: list[str] | None) -> dict[str, dict[str, Any]]:
    models = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))["models"]
    if keys is None:
        return models
    unknown = [k for k in keys if k not in models]
    if unknown:
        raise SystemExit(f"Unknown model keys: {', '.join(unknown)}")
    return {k: models[k] for k in keys}


def read_split(lang: str, split: str) -> dict[str, str]:
    path = hf_hub_download(
        DATASET, f"{split}/{lang}.jsonl", repo_type="dataset", revision=DATASET_REVISION
    )
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    texts = {str(r["id"]): r["text"] for r in rows}
    if len(texts) != len(rows):
        raise ValueError(f"{lang}/{split}: duplicate ids in file")
    return texts


def load_parallel(split: str) -> dict[str, list[str]]:
    ind = read_split("ind_Latn", split)
    eng = read_split("eng_Latn", split)
    if ind.keys() != eng.keys():
        diff = len(ind.keys() ^ eng.keys())
        raise ValueError(f"{split}: {diff} ids differ between ind_Latn and eng_Latn")
    ids = sorted(ind)
    return {"ind_Latn": [ind[i] for i in ids], "eng_Latn": [eng[i] for i in ids]}


def load_tokenizer(repo: str, revision: str) -> Any:
    return AutoTokenizer.from_pretrained(repo, revision=revision, use_fast=True)


def tokenizer_hash(tok: Any) -> str:
    backend = getattr(tok, "backend_tokenizer", None)
    if backend is not None:
        payload = backend.to_str()
    else:
        payload = json.dumps(sorted(tok.get_vocab().items()), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def measure(tok: Any, texts: list[str]) -> LangStats:
    ids = tok(texts, add_special_tokens=False)["input_ids"]
    return LangStats(
        n_sentences=len(texts),
        n_words=sum(len(t.split()) for t in texts),
        n_tokens=sum(len(x) for x in ids),
        n_chars=sum(len(t) for t in texts),
    )


def base_row(key: str, cfg: dict[str, Any], split: str) -> dict[str, Any]:
    return {
        "model_key": key,
        "repo": cfg["repo"],
        "revision": cfg["revision"],
        "tokenizer_hash": "",
        "vocab_size": "",
        "dataset": DATASET,
        "dataset_revision": DATASET_REVISION,
        "split": split,
    }


def error_rows(key: str, cfg: dict[str, Any], split: str, status: str) -> list[dict[str, Any]]:
    rows = []
    for lang in LANGS:
        row = base_row(key, cfg, split)
        row.update({"lang": lang, "status": status})
        rows.append(row)
    return rows


def ok_rows(
    key: str,
    cfg: dict[str, Any],
    split: str,
    digest: str,
    vocab_size: int,
    stats: dict[str, LangStats],
) -> list[dict[str, Any]]:
    id_s, en_s = stats["ind_Latn"], stats["eng_Latn"]
    premium = id_s.n_tokens / en_s.n_tokens
    ratio = id_s.fertility / en_s.fertility
    rows = []
    for lang in LANGS:
        s = stats[lang]
        row = base_row(key, cfg, split)
        row.update({
            "tokenizer_hash": digest,
            "vocab_size": vocab_size,
            "lang": lang,
            "n_sentences": s.n_sentences,
            "n_words": s.n_words,
            "n_tokens": s.n_tokens,
            "fertility": round(s.fertility, 4),
            "chars_per_token": round(s.chars_per_token, 4),
            "premium_id_en": round(premium, 4) if lang == "ind_Latn" else "",
            "fertility_ratio_id_en": round(ratio, 4) if lang == "ind_Latn" else "",
            "status": "ok",
        })
        rows.append(row)
    return rows


def short_error(exc: Exception) -> str:
    first = str(exc).strip().splitlines()[0] if str(exc).strip() else ""
    return f"error: {type(exc).__name__}: {first[:200]}"


def evaluate_models(
    models: dict[str, dict[str, Any]],
    split: str,
    corpus: dict[str, list[str]] | None,
) -> list[dict[str, Any]]:
    cache: dict[str, tuple[int, dict[str, LangStats]]] = {}
    rows: list[dict[str, Any]] = []
    for key, cfg in models.items():
        try:
            tok = load_tokenizer(cfg["repo"], cfg["revision"])
            digest = tokenizer_hash(tok)
            if corpus is not None and digest not in cache:
                stats = {lang: measure(tok, corpus[lang]) for lang in LANGS}
                cache[digest] = (len(tok), stats)
            if corpus is not None:
                vocab_size, stats = cache[digest]
                rows.extend(ok_rows(key, cfg, split, digest, vocab_size, stats))
            else:
                rows.append({**base_row(key, cfg, split), "tokenizer_hash": digest,
                             "vocab_size": len(tok), "status": "ok"})
            print(f"[{key}] ok hash={digest} vocab={len(tok)}", file=sys.stderr)
        except Exception as exc:
            status = short_error(exc)
            rows.extend(error_rows(key, cfg, split, status))
            print(f"[{key}] {status}", file=sys.stderr)
    return rows


def write_csv(rows: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def print_table(rows: list[dict[str, Any]]) -> None:
    by_key: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_key.setdefault(row["model_key"], {})[row["lang"]] = row
    print(f"{'model_key':<28}{'fert_en':>9}{'fert_id':>9}{'premium':>9}  note")
    for key, langs in by_key.items():
        en, idr = langs["eng_Latn"], langs["ind_Latn"]
        if en["status"] != "ok":
            print(f"{key:<28}{'-':>9}{'-':>9}{'-':>9}  {en['status'][:80]}")
            continue
        notes = []
        for r in (en, idr):
            if not SANITY_RANGE[0] <= float(r["fertility"]) <= SANITY_RANGE[1]:
                notes.append(f"CHECK fertility {r['lang']}")
        print(f"{key:<28}{float(en['fertility']):>9.3f}{float(idr['fertility']):>9.3f}"
              f"{float(idr['premium_id_en']):>9.3f}  {'; '.join(notes)}")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tokenizer fertility on FLORES+ devtest.")
    p.add_argument("--models", help="comma-separated keys from configs/models.yaml (default: all)")
    p.add_argument("--split", choices=["devtest", "dev"], default="devtest")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output CSV path")
    p.add_argument("--check-tokenizers", action="store_true",
                   help="only load tokenizers and print hashes; no dataset, no CSV")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    keys = [k.strip() for k in args.models.split(",")] if args.models else None
    models = load_models(keys)

    corpus = None
    if not args.check_tokenizers:
        try:
            corpus = load_parallel(args.split)
        except Exception as exc:
            print(f"Dataset access failed: {short_error(exc)}", file=sys.stderr)
            print(f"Accept access at https://huggingface.co/datasets/{DATASET} "
                  "with the account that owns HF_TOKEN.", file=sys.stderr)
            return 1

    rows = evaluate_models(models, args.split, corpus)
    if args.check_tokenizers:
        return 0
    write_csv(rows, args.out)
    print_table(rows)
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
