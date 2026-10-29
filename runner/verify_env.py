"""Check the VM before a run: versions, GPU, and one tiny text-only generate.

Run as a subprocess (never inside the Colab kernel, which would keep GPU memory):
  python3 runner/verify_env.py [--model gemma4-e2b-it]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gemma4-e2b-it")
    p.add_argument("--hf-cache", default="/content/hf_cache")
    args = p.parse_args()

    os.environ["HF_HOME"] = args.hf_cache
    os.environ.setdefault("HF_TOKEN_PATH", str(Path.home() / ".cache/huggingface/token"))

    import lm_eval
    import torch
    import vllm
    from vllm import LLM, SamplingParams

    print(json.dumps({
        "torch": torch.__version__, "cuda": torch.version.cuda, "vllm": vllm.__version__,
        "lm_eval": lm_eval.__version__, "gpu": torch.cuda.get_device_name(0),
        "vram_gb": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1),
    }))

    cfg = yaml.safe_load((REPO_ROOT / "configs/models.yaml").read_text())
    model = {**cfg["defaults"], **cfg["models"][args.model]}
    llm = LLM(
        model=model["repo"], revision=model["revision"], dtype=model["dtype"], max_model_len=2048,
        gpu_memory_utilization=0.5, seed=0, **(model.get("text_only_args") or {}),
    )
    out = llm.chat(
        [{"role": "user", "content": "Apa ibu kota Indonesia? Jawab satu kata saja."}],
        SamplingParams(max_tokens=32, temperature=0),
        chat_template_kwargs=model.get("thinking_args") or {},
    )
    text = out[0].outputs[0].text
    print("GENERATE:", repr(text))
    return 0 if "jakarta" in text.lower() else 1


if __name__ == "__main__":
    sys.exit(main())
