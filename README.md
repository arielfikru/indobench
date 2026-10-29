# indobench

Benchmark of open-weight LLMs in Indonesian, built on EleutherAI lm-evaluation-harness (vLLM backend), run on a Google Colab GPU through the Colab CLI.

Phase 0 asks two questions:
1. Do regional derivatives of older bases (GoTo's Gemma 3 27B CPT, GoTo Sahabat-AI on Gemma 2 9B) still beat the newest general models (Qwen3.8, Gemma 4) in Indonesian?
2. How much does regional continued pretraining add over its own base, especially in colloquial Indonesian?

## Results (run `full-m4`, October 2026)

Accuracy (%), zero-shot. Full tables with 95% CIs and paired tests: [`results/summary.md`](results/summary.md). Write-up: [`blog/phase0-draft.md`](blog/phase0-draft.md).

![Results table](results/results_table.png)

<details>
<summary>Same table as text</summary>

| Task | Qwen3.8 27B | GoTo Gemma 3 27B | Gemma 3 27B | Gemma 4 12B | Sahabat-AI 9B | Gemma 2 9B |
|---|---|---|---|---|---|---|
| IndoMMLU | **71.4** | 67.6 | 67.2 | 68.4 | 63.6 | 61.2 |
| IndoCulture | **74.1** | **74.1** | 73.7 | 72.3 | 69.9 | 67.5 |
| Global-MMLU ID, culturally sensitive | **77.1** | 74.2 | 74.4 | 67.0 | 72.3 | 68.8 |
| Global-MMLU ID, culturally agnostic | **79.3** | 70.7 | 71.2 | 70.7 | 64.4 | 63.8 |
| COPAL-ID standard | 86.4 | **87.1** | 86.6 | 86.0 | 81.6 | 78.5 |
| COPAL-ID colloquial | 82.3 | **83.7** | 83.0 | 81.4 | 80.0 | 76.9 |

</details>

- The newest general model wins on knowledge (Qwen3.8: +8.6 on Global-MMLU culturally agnostic, +3.8 on IndoMMLU over GoTo Gemma 3).
- On culture and language, the regional models tie or lead.
- Regional CPT effect over its own base: GoTo Gemma 3 27B is within 1 point of Gemma 3 27B on every task. Sahabat-AI 9B gains 2-3.5 points over Gemma 2 9B, significant on 4 of 6 tasks, largest on culturally sensitive questions.
- Colloquial Indonesian still costs 2-5 points on COPAL-ID.
- lm_eval's built-in `copal_id` task cuts the last character of 79% of colloquial premises; we use a fixed MCQ version (`tasks/copal_id`). Details in `NOTES_tasks.md`.

## Layout

| Path | What |
|---|---|
| `configs/models.yaml` | model matrix: repo, pinned commit SHA, dtype, max_model_len, pairs, chat-template notes |
| `configs/tasks.yaml` | benchmarks → lm_eval task names, random baselines, subsets |
| `tasks/` | custom lm_eval tasks (IndoMMLU, IndoCulture, Global-MMLU CS/CA, COPAL-ID), loaded with `--include_path` |
| `runner/run_matrix.py` | runs on the VM: one lm_eval subprocess per model, resumable, writes manifest |
| `runner/verify_env.py` | VM check: versions + one tiny generate |
| `runner/run_api.py` | closed-model comparator over the OpenRouter API (generative letter answers); not run yet |
| `scripts/` | local drivers: provision, sync_code, start_run, watch, pull_results, teardown |
| `analysis/summarize.py` | local: scores, bootstrap CI, paired deltas, noise floor → `results/summary.{md,csv}` |
| `analysis/results_table.py` | renders `results/results_table.png` from `results/summary.csv` |
| `analysis/copal_check.py` | diagnosis of the built-in COPAL-ID task from sample logs |
| `blog/` | write-up of phase 0 |
| `tokenizer/fertility.py` | local, CPU: tokens per word on FLORES-200 ind_Latn vs eng_Latn |
| `docs/research/` | research notes (Colab CLI, HF repo checks, landscape) |
| `spec-ifeval-id-gaul.md` | phase 1 spec |

## Setup choices
- **GPU:** Colab G4 (RTX PRO 6000, 96 GB) by default, A100 80 GB as fallback. All models run BF16; 27–31B models do not fit in 40 GB, so provisioning stops the VM if VRAM < 79 GB.
- **Text-only, non-thinking:** multimodal models load with `language_model_only=True`; thinking-capable chat templates get `enable_thinking=False`. Both are recorded per model in the manifest.
- **Zero-shot, chat template applied, loglikelihood MCQ, fixed seed (1234), `--log_samples`.**
- **Long jobs:** the runner is started detached on the VM (`nohup setsid`) and polled with short `colab exec` calls. A plain `colab exec` keeps the kernel busy, and `colab run` tears the VM down on any error.
- **HF token:** uploaded as a file to `~/.cache/huggingface/token` on the VM. Never via `colab exec`/`--env`, because `colab log` keeps exec code and env values in plaintext.

## Run from scratch

Requirements on the Mac: `colab` CLI (logged in), `uv`, `HF_TOKEN` in the environment (or the `huggingface-api-key` keychain item). Accept the HF licenses for `google/gemma-3-27b-it`, `google/gemma-2-9b-it` and `openlanguagedata/flores_plus` first.

1. Tokenizer fertility (local, no GPU):
   ```bash
   uv run --with transformers --with tokenizers --with sentencepiece --with protobuf --with pyyaml --with huggingface_hub python tokenizer/fertility.py
   ```
2. Check the Colab balance, then provision (asks for confirmation):
   ```bash
   scripts/provision.sh --gpu G4
   ```
3. Mount Drive (needs one browser consent click):
   ```bash
   colab drivemount -s indobench
   ```
   Without Drive, set `INDOBENCH_RESULTS_ROOT=/content/indobench_results` before the next steps.
4. Smoke test (Gemma 4 E2B pair, 50 docs per task), twice, for the noise floor:
   ```bash
   scripts/start_run.sh smoke-a --models smoke --limit 50
   scripts/watch.sh
   scripts/start_run.sh smoke-b --models smoke --limit 50
   scripts/watch.sh
   ```
5. Full matrix:
   ```bash
   scripts/start_run.sh full-v1 --models all
   scripts/watch.sh --stop
   ```
   Re-running the same command resumes: finished model × task pairs (`DONE.json`) are skipped.
6. Pull results and stop the VM:
   ```bash
   scripts/pull_results.sh full-v1
   scripts/teardown.sh
   ```
7. Summarize:
   ```bash
   uv run --with numpy --with pyyaml python analysis/summarize.py --results results/runs --run-id full-v1 --out results/
   ```
   For the noise floor, run the same summarize on `smoke-a` with `--compare-run smoke-b`.

Always run `scripts/teardown.sh` when a run ends or fails: an idle VM still burns compute units.

## Licenses
Code: Apache-2.0 (see LICENSE). Datasets are loaded from their original HF repos and are not redistributed. IndoMMLU and IndoCulture are CC BY-NC-SA 4.0, COPAL-ID is CC BY-SA 4.0, FLORES+ is CC BY-SA 4.0.
