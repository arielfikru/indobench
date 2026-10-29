# NOTES_tasks.md: Indonesian benchmark tasks and version pins

Date: 2026-10-28. Scope: `tasks/`, `configs/tasks.yaml`, `requirements.txt`, `requirements-local.txt`, `.venv-local/`, this file.

## 0. Summary

| Benchmark | Source | Task names (lm_eval) | Items (test) | Status |
|---|---|---|---|---|
| COPAL-ID standard | built-in | `copal_id_standard` | 559 | built-in, dummy PASS |
| COPAL-ID colloquial | built-in | `copal_id_colloquial` | 559 | built-in, dummy PASS |
| Global-MMLU id, full | built-in | `global_mmlu_full_id` (+4 subgroups) | 14042 | built-in, dummy PASS |
| Global-MMLU id, CS | custom | `global_mmlu_full_id_cs_t0` | 792 | custom, dummy PASS |
| Global-MMLU id, CA | custom | `global_mmlu_full_id_ca_t0` | 2058 | custom, dummy PASS |
| IndoMMLU | custom | `indommlu_t0` (group `indommlu`) | 14904 | custom, dummy PASS |
| IndoCulture | custom | `indoculture_t0` (group `indoculture`) | 2429 | custom, dummy PASS |

Pins: `vllm==0.32.0`, `lm_eval==0.4.13` (VM) and `lm_eval==0.4.13` (local).

## 1. Environment

- `uv venv .venv-local --python 3.12` gives CPython 3.12.13.
- `lm_eval` 0.4.13 is the newest on PyPI (checked: `https://pypi.org/pypi/lm_eval/json`).
- Installed locally: `datasets` 5.1.0, `transformers` 5.19.0 (VM-matched, see §5), `tokenizers` 0.23.3, `pyyaml` 6.0.3, `numpy` 2.5.4, `pandas` 3.1.0, `huggingface_hub` 2.3.0.
- `.venv-local/` is NOT gitignored: the repo has no `.gitignore` (`git check-ignore` returns nothing). Adding one is outside this task's file scope; see §8.

## 2. Built-in lm_eval search (`lm_eval ls tasks`)

- **COPAL-ID**: `copal_id` group, with `copal_id_standard` (`tasks/copal_id/standard.yaml`) and `copal_id_colloquial` (`colloquial.yaml`, `test_split: test_colloquial`). Dataset `haryoaw/COPAL` config `id`, which has splits `test` and `test_colloquial`. Standard and colloquial are already separate tasks. Metric: `acc` only.
- **Global-MMLU**: two versions exist.
  - `global_mmlu_full_id` = `CohereForAI/Global-MMLU` config `id`, 14042 test rows (`global_mmlu/full/id/_id_template_yaml`). Subgroups `..._stem`, `_humanities`, `_social_sciences`, `_other`. Template: `"{question}\nA. ..\nD. ..\nAnswer:"`, target = letter in `answer`.
  - `global_mmlu_id` = **Global-MMLU-Lite** `id` (`global_mmlu/default/id/`), 400 test rows.
  - **No CS/CA split exists in lm_eval.** `grep -i sensitiv` over `global_mmlu/` only matches the README text.
- **IndoMMLU**: not built in (no `indolem`, `indommlu` in any task YAML).
- **IndoCulture**: not built in.
- Other Indonesian hits (not used): `include_base_44_indonesian*` (INCLUDE), `mmlu_prox_id`, `mmlu_prox_lite_id`, `mmmlu_id_id*` (OpenAI MMMLU). Not in scope; they could be added later.

## 3. Custom tasks

Layout (loaded with `--include_path tasks`, no fork):

```
tasks/indommlu/          _default_template_yaml  utils.py  indommlu_t0.yaml  indommlu.yaml (group)
tasks/indoculture/       _default_template_yaml  utils.py  indoculture_t0.yaml  indoculture.yaml (group)
tasks/global_mmlu_full_id_cs_ca/  _default_template_yaml  utils.py  global_mmlu_full_id_cs_t0.yaml  global_mmlu_full_id_ca_t0.yaml  global_mmlu_full_id_cs_ca.yaml (group)
```

Template files have no `.yaml` extension, so lm_eval does not load them as tasks. A new prompt variant is `<name>_t<k>.yaml` with `include: _default_template_yaml` and a different `doc_to_text`.

### 3.1 IndoMMLU (`indolem/IndoMMLU`)

- **Loader**: the repo contains `IndoMMLU.py`, a legacy loading script. `datasets` 5.x does not run those, so the data is read from `IndoMMLU.csv` through `dataset_path: csv` and a pinned URL (`resolve/df6d6d348d7f8a0b1c98b56f4443977b60fae0f5/IndoMMLU.csv`).
- **Columns**: `id, sumber, keterangan sumber, kelas, nomor, subject, level, soal` (question), `jawaban` (options, one string with `A. ..\nB. ..` lines), `kunci` (gold letter), `is_for_fewshot` (0/1).
- **Rows**: 14981 total. `is_for_fewshot == 1` gives 75 rows, which are the paper's few-shot pool. `is_for_fewshot == 0` gives 14906, the paper's test count.
- **Option counts** (test rows): 3 options: 1249, 4: 6986, 5: 6669. Random baseline = mean(1/n) = **0.2346**.
- **Broken rows**: ids 4223 (gold E, only 4 options) and 14150 (gold D, only 3 options) are dropped. Evaluable test items = **14904**.
- **Filter** in `utils.process_docs`: keep `is_for_fewshot == 0`, drop broken gold rows, set `choices_letters` = `A..(n letters)`.
- **Template t0**: `"{soal}\n{jawaban}\nJawaban:"`, with targets ` A`..` E`. This is the paper's question-plus-options format with an Indonesian answer prefix. The paper's header prompt (`"Ini adalah soal [subject] untuk [level]. Pilihlah salah satu jawaban..."`) is NOT included. It would be a template `t1`.
- **License**: cc-by-nc-sa-4.0 (non-commercial). Relevant if results are published.

### 3.2 IndoCulture (`indolem/IndoCulture`)

- **Loader**: `test.csv` only (the repo has no script). Read through `dataset_path: csv` with a pinned URL (`resolve/d5f33af62c9b6e808ee11b75c13f042c3e5c7690/test.csv`).
- **Columns**: `id, province, topic, is_province_specific (bool), context, options (stringified Python list of 3 strings "A. ...", "B. ...", "C. ..."), answer (A/B/C)`.
- **Rows**: 2429 (all test). `answer` distribution: A 863, B 772, C 794. `is_province_specific`: True 1847, False 582. 13 topics.
- **No question field**: `context` is a declarative sentence ending in "." (2429/2429). The format is inferred from the CSV; the dataset card is empty (33 bytes, license only).
- **Template t0**: `"{context}\n{options_text}\nJawaban:"`, with targets ` A`/` B`/` C`. The options come from `ast.literal_eval(options)` in `utils.process_docs`, which also asserts each option starts with its letter.
- Random baseline = **0.3333**.

### 3.3 Global-MMLU CS / CA (`CohereLabs/Global-MMLU`, config `id`)

- **Columns**: `sample_id, subject, subject_category, question, option_a..option_d, answer, required_knowledge, time_sensitive, reference, culture, region, country, cultural_sensitivity_label, is_annotated`.
- **`cultural_sensitivity_label`** values in the `id` test split: `CS` 792, `CA` 2058, `-` 11192. Total labelled = 2850, which matches the dataset card ("2850 questions per language").
- **Subsets**: `utils.process_cs` / `process_ca` filter on `cultural_sensitivity_label == "CS"` / `"CA"`. The `-` rows (unlabelled) are in neither subset.
- **Template t0**: same options and targets as built-in `global_mmlu_full_id`, but with `"Jawaban:"` in place of `"Answer:"`, per the Indonesian-prompt instruction. These subsets are therefore **not an exact slice of the built-in full score**. If an exact slice is needed, use the built-in English template for the CS/CA filter too (one-line change in `_default_template_yaml`).
- Random baseline = 0.25.
- **Lite alternative** (not implemented): `CohereLabs/Global-MMLU-Lite` config `id` has 400 test rows, balanced CS 200 / CA 200, with a `cultural_sensitivity_label` column. It could be a CS/CA pair with less compute, but it is far smaller and uses a different sample.

### 3.4 Rendered prompts (one per task, from `--limit 5` dummy runs, samples jsonl `arguments.gen_args_0.arg_0`)

**indommlu_t0** (doc_id 0, gold D; continuations ` A`..` E`):
```
Peristiwa kelahiran, penerangan agung, dan kematian Sidharta Gautama terjadi pada tanggal yang sama, yakni bulan purnama di bulan Mei. Ketiga peristiwa tersebut dirayakan umat Buddha sebagai hari raya....
A. Galungan
B. Kuningan
C. Paskah
D. Waisak
E. Nyepi
Jawaban:
```

**indoculture_t0** (doc_id 0, gold B; continuations ` A`/` B`/` C`):
```
Abdulah ingin sarapan pagi dan pergi ke warung kopi.
A. Abdulah memesan burger dan martabak telur.
B. Abdulah memesan kopi dan nasi gurih.
C. Abdulah memesan jus dan nasi kambing.
Jawaban:
```

**global_mmlu_full_id_cs_t0** (doc_id 0, gold C):
```
Ketika bepergian ke utara dari Amerika Serikat ke Kanada, Anda akan akan melihat Bintang Utara (Polaris) menjadi _________.
A. Lebih terang
B. Lebih redup
C. Lebih tinggi di langit
D. Lebih rendah di langit
Jawaban:
```
(The doubled "akan akan" is in the source dataset.)

**global_mmlu_full_id_ca_t0** (doc_id 0, gold B): question "Pernyataan 1 | Grup faktor dari sebuah grup non-Abelian adalah non-Abelian. Pernyataan 2 | ..." with options "A. Benar, Benar" ... "D. Salah, Benar", then `Jawaban:`.

**copal_id_standard** (doc_id 0, gold 0): `'Pria itu memangku tasnya saat menaiki angkutan umum karena'`, continuations `' pria itu berjaga-jaga agar tasnya tidak dicuri.'` / `' tasnya empuk.'`

**copal_id_colloquial** (doc_id 0, gold 0): `'Cowok itu mangku tasnya pas lagi naek angko karena'`, continuations `' cowoknya jaga-jaga biar tasnya gak diambil'` / `' tasnya empukk'`

**global_mmlu_full_id** (built-in): not sampled here. Its template is `"{question}\nA. ..\nD. ..\nAnswer:"`.

## 4. Dummy validation (`lm_eval --model dummy --include_path tasks`)

Command pattern: `lm_eval --model dummy --tasks <task> --include_path tasks --limit 5 --log_samples --output_path <scratch>/dummy_runs/<task>`. Logs are in `<scratch>/dummy_runs/<task>.log`.

| Task | `--limit 5` | Full count (no limit) | Result |
|---|---|---|---|
| indommlu_t0 | PASS (acc 0.4 on 5 items, acc == acc_norm) | 14904 | PASS |
| indoculture_t0 | PASS (acc 0.4) | 2429 | PASS |
| global_mmlu_full_id_cs_t0 | PASS (acc 0.2) | 792 | PASS |
| global_mmlu_full_id_ca_t0 | PASS (acc 0.2) | 2058 | PASS |
| copal_id_standard | PASS (acc 0.8) | 559 | PASS |
| copal_id_colloquial | PASS (acc 0.8) | 559 | PASS |
| global_mmlu_full_id (built-in, 4 subgroups) | PASS (acc 0.31 over 5 per subgroup) | 14042 (per dataset) | PASS |

Notes:
- The dummy model is random. These runs only test that the pipeline works: loading, filtering, choices, targets, and metric computation. They say nothing about model quality.
- `acc` == `acc_norm` on every logged sample for all four MCQ custom tasks. Reason: each choice is a single letter, so the byte length in `acc_norm` is identical across choices and the normalization cancels. Both metrics are kept as requested, but `acc_norm` is redundant here.
- COPAL has only `acc` (no `acc_norm` in its YAML).
- Full counts come from `n-samples` in the results JSON, from the dummy runs without `--limit`.

## 5. Version pins

### 5.1 PyPI and lm_eval

- `lm_eval` latest on PyPI = **0.4.13**. Pinned `lm_eval==0.4.13` and `lm_eval[vllm]==0.4.13` on the VM.
- `lm_eval[vllm]` extra requires `vllm>=0.18`, which 0.32.0 satisfies (`requires_dist` in lm_eval METADATA).

### 5.2 vllm choice: **0.32.0** (PyPI upload 2026-10-18, 10 days before today)

Evidence (raw files at tag `v0.32.0`, `https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/...`):

- **Architectures** in `vllm/model_executor/models/registry.py`:
  - `Gemma3ForConditionalGeneration` at line 404 (`gemma3_mm`)
  - `Gemma4ForConditionalGeneration` at line 413 (`gemma4_mm`)
  - `Qwen3_5ForConditionalGeneration` at line 595 (`qwen3_5`)
  - Same three also present at 0.31.0 (lines 409, 418, 596) and 0.30.0 (lines 410, 419, 597), so the fallback is 0.31.0 if a version older than two weeks is preferred.
- **Torch pin**: `requirements/cuda.txt` has `torch==2.13.0`, `torchaudio==2.11.0`, `torchvision==0.28.0`.
- **CUDA**: PyPI default wheel is CUDA 13.0 (release notes, GitHub release `v0.32.0`, "PyPI (CUDA 13.0) | `pip install vllm`"). The same release notes also list "CUDA 12.9 Python wheels", but the PyPI channel for those was not checked, so only the CUDA 13.0 PyPI wheel is relied on. Dry-run resolve of `requirements.txt` pulls `nvidia-cuda-runtime==13.0.96`, consistent with the CUDA 13.0 default.
- **Blackwell sm_120**: `CMakeLists.txt:120` `CUDA_SUPPORTED_ARCHS` includes `12.0`. Release notes list SM120 items (split-K attention #58482, SM120 TP configs #58495). Which CMake branch the PyPI wheel uses was not confirmed (the file has several branches).
- **Dry-run resolve** (`uv pip compile requirements.txt --python-version 3.12 --python-platform x86_64-manylinux_2_28`): `vllm==0.32.0`, `torch==2.13.0`, `torchvision==0.28.0`, `torchaudio==2.11.0`, `transformers==5.19.0`, `huggingface-hub==2.3.0`, `datasets==5.1.0`, `lm-eval==0.4.13`, `hf-transfer==0.1.9`. No conflicts. The resolve did not install or download the GPU stack.

### 5.3 requirements files

- `requirements.txt` (VM): `vllm==0.32.0`, `lm_eval[vllm]==0.4.13`, `datasets==5.1.0`, `pyyaml==6.0.3`, `huggingface_hub==2.3.0`, `hf_transfer==0.1.9`. The file explains why torch is not listed: vllm pins its own torch, and a separate torch install or Colab's preinstalled torch breaks the compiled kernels.
- `requirements-local.txt` (Mac): `lm_eval==0.4.13`, `transformers==5.19.0`, `tokenizers==0.23.3`, `datasets==5.1.0`, `pyyaml==6.0.3`, `numpy==2.5.4`, `pandas==3.1.0`, `huggingface_hub==2.3.0`. No vllm, no torch.
- Local `numpy` (2.5.4) differs from the VM's resolved numpy (2.3.5, pulled by vllm). Harmless: numpy is not used by the VM run.

## 6. Running the models: text-only and `enable_thinking=false` through lm_eval 0.4.13 + vllm 0.32.0

### 6.1 Text-only (no image or audio encoder input)

- **Kwarg**: `language_model_only=True`.
  - `vllm/config/multimodal.py:304-306`: `language_model_only: bool = False`. "disables all multimodal inputs by setting all modality limits to 0. Equivalent to setting `--limit-mm-per-prompt` to 0 for every modality."
  - `multimodal.py:699`: `get_limit_per_prompt` returns 0 when it is set.
  - CLI equivalent: `--language-model-only` (`vllm/engine/arg_utils.py:1460`).
  - `vllm/model_executor/models/interfaces.py:339-350` (`_mark_tower_model`): tower modules "are automatically skipped when `--limit-mm-per-prompt` is set to zero for all of their modalities". Gemma4 (`gemma4_mm.py`, vision tower around line 1096) and Qwen3.5 (`qwen3_5.py` around lines 510-514) build their towers inside `_mark_tower_model(vllm_config, {"image","video"})`. **So vision towers should not be built.** The VM run should confirm this with the log or memory use (unverified, see §7).
- **Why not `limit_mm_per_prompt`**: it is a dict (`{"image": 0}`). lm_eval's `--model_args` string (below) cannot carry nested dicts, so the flat bool is the only CLI-safe option.
- **Pass-through**: lm_eval passes unknown kwargs into `LLM(**model_args)` (`vllm_causallms.py:147` `self.model_args.update(kwargs)`, `:154` `LLM(**self.model_args)`). `LLM.__init__` forwards `**kwargs` into `EngineArgs(...)` (`vllm/entrypoints/llm.py:336`), and `EngineArgs` has the field (`vllm/engine/arg_utils.py:633`).

### 6.2 `enable_thinking=false`

- **Working route**: top-level `enable_thinking=False` in `--model_args`.
  - `vllm_causallms.py:85` `enable_thinking: bool | None = None` (top-level param).
  - `vllm_causallms.py:283-284` and `:296-297`: `apply_chat_template(..., enable_thinking=self.enable_thinking, **self.chat_template_args)`.
- **Bug in lm_eval 0.4.13** (`vllm_causallms.py:183-188`):
  ```
  self.chat_template_args = chat_template_args or {}
  self.enable_thinking = self.chat_template_args.pop("enable_thinking", enable_thinking)
  self.enable_thinking = enable_thinking          # <- line 188 overwrites the pop result
  ```
  So `enable_thinking` set inside `chat_template_args` is silently discarded, and the value becomes the top-level argument, which defaults to `None`. Passing `enable_thinking` via `chat_template_args` does NOT work. Use the top-level kwarg.
  - Caution: `None` is passed to the chat template explicitly. For Qwen-style templates, `enable_thinking is defined and enable_thinking is false` is false when the value is `None`, so thinking could stay on. Always pass `enable_thinking=False` explicitly.
- **`--model_args` format**: `simple_parse_args_string` (`lm_eval/utils.py:224-240`) splits on `,` and `=`. Values go through `handle_arg_string` (`utils.py:156`): `true`/`false` become bool, `None` becomes None, and quoted values stay strings. **Nested dicts and JSON are not supported on the CLI.** `chat_template_args` can only be passed as a Python dict (`evaluator.py:57`, `model_args` may be a dict).
- **Scope of `enable_thinking`**:
  - The chat template is applied **only with `--apply_chat_template`**. Without it, the MCQ prompts are raw text and the flag has no effect.
  - `vllm_causallms.py:469-473`: `loglikelihood()` raises if `enable_thinking` is truthy. So `enable_thinking=False` is the only valid setting for these MCQ tasks.
  - `evaluator.py:170-185` only warns when a model name contains "inst" or "chat" and `apply_chat_template` is off.

### 6.3 Example invocation (VM, not run here)

```
lm_eval --model vllm \
  --model_args pretrained=google/gemma-4-E2B-it,revision=3e22461f65e89153144f8adb70e3b8c2cc9845a7,dtype=bfloat16,max_model_len=8192,gpu_memory_utilization=0.90,language_model_only=True,enable_thinking=False \
  --tasks indommlu_t0 --include_path tasks --limit 50 --log_samples --output_path <out>
```

Add `--apply_chat_template` only if the chat-template prompt format is wanted. The current MCQ tasks are raw-text zero-shot.

## 7. Unverified / caveats

1. **No GPU run anywhere.** The vllm pin is checked from source and PyPI metadata, not by installing or serving a model. Blackwell sm_120 kernels are unverified.
2. **Driver**: the default PyPI wheel is CUDA 13.0. The Colab VM driver must support CUDA 13.0. Not checked.
3. **Vision tower skip** under `language_model_only` is derived from `_mark_tower_model` docs and code, not from a run. Confirm on the VM (memory, log, or weight count).
4. **`enable_thinking`** only matters with `--apply_chat_template`. The raw-text MCQ setup never triggers it. The lm_eval bug at `vllm_causallms.py:183-188` was read from the source; not tested with a run.
5. **`acc_norm` equals `acc`** on letter-choice tasks (verified on the dummy samples, and explained by byte-length reasoning). Report `acc` as the primary metric for indommlu, indoculture and global_mmlu.
6. **IndoMMLU**: CSV loader and pinned URL are validated on the dummy run (14904 items). The paper's header prompt is not used (`t1` candidate). 2 broken rows dropped (ids 4223, 14150).
7. **IndoCulture prompt format is inferred** (no question field, empty dataset card). The `Jawaban:` continuation is my choice. Check with the authors or the paper if a different format is expected. The paper's exact prompt is not verified.
8. **Global-MMLU CS/CA** use `Jawaban:` (Indonesian), so they are not an exact slice of the built-in English-template full score. Only 2850 of 14042 rows are labelled CS/CA.
9. **Dummy validation** checks only the pipeline, not model behavior.
10. **Licenses**: IndoMMLU and IndoCulture are cc-by-nc-sa-4.0. Global-MMLU license not checked (the dataset card is not in the local copy).
11. **`--config` YAML loading** was not verified: `EvaluatorConfig.model_args` is a dict (`config/evaluate_config.py:70`), but I did not confirm that the CLI accepts a config file.
12. **vllm 0.32.0 is 10 days old.** 0.31.0 (2026-10-05) has the same three architectures, the same torch 2.13.0 pin and CUDA 13.0 wheels, if you want an older release.
13. **Gated models**: `gemma3-27b-it` and `gemma4` need license acceptance on HF. Not checked here.
14. **Repo hygiene**: `.venv-local/` is not in any `.gitignore`. No `.gitignore` exists in the repo, and it is outside my file scope.

## 8. Files touched

- Created: `tasks/indommlu/{_default_template_yaml,utils.py,indommlu_t0.yaml,indommlu.yaml}`
- Created: `tasks/indoculture/{_default_template_yaml,utils.py,indoculture_t0.yaml,indoculture.yaml}`
- Created: `tasks/global_mmlu_full_id_cs_ca/{_default_template_yaml,utils.py,global_mmlu_full_id_cs_t0.yaml,global_mmlu_full_id_ca_t0.yaml,global_mmlu_full_id_cs_ca.yaml}`
- Created: `configs/tasks.yaml`, `requirements.txt`, `requirements-local.txt`, `NOTES_tasks.md`, `.venv-local/`
- Scratch (outside repo): `<scratchpad>/dummy_runs/`, `<scratchpad>/raw/` (downloaded IndoMMLU/IndoCulture files), `<scratchpad>/vllm_src/` (vllm 0.32.0 source excerpts)

## COPAL-ID: built-in lm_eval task replaced (2026-10-29)

lm_eval 0.4.13 `copal_id` cuts the last character of every premise (`premise.strip()[:-1]`, assumes a
trailing period). 78.9% of colloquial premises have none, so a real letter was lost ("naek angkot" ->
"naek angko"); standard premises were unaffected. It also scores free-text endings by summed
log-likelihood (models picked the shorter ending 60-62% of the time on colloquial vs 51.5% gold).
Run full-m4 measured a 7-9 point standard-colloquial gap with it; the fixed lettered-MCQ task
(`tasks/copal_id`, `copal_id_*_t0`) gives 1.6-4.7 points and ~+15 points absolute.
Old results: `results/runs/full-m4-copal-legacy/`; diagnosis: `analysis/copal_check.py`.
