# Ringkasan indobench: run `api-claude`

- Metrik: `acc`
- Model di run: 3
- Compare run: -

## a. Skor per model dan task

| Model | Task (lm_eval) | n | Skor [95% CI] | stderr | Random | Di atas random |
|---|---|---|---|---|---|---|
| claude-haiku-5.5 | copal_id_colloquial_t0 | 559 | 0.809 [0.776, 0.841] | 0.017 | 0.007 | ya |
| claude-haiku-5.5 | copal_id_standard_t0 | 559 | 0.846 [0.816, 0.875] | 0.015 | 0.003 | ya |
| claude-haiku-5.5 | global_mmlu_full_id_ca_t0 | 2058 | 0.809 [0.791, 0.826] | 0.009 | 0.006 | ya |
| claude-haiku-5.5 | global_mmlu_full_id_cs_t0 | 792 | 0.758 [0.727, 0.787] | 0.015 | 0.002 | ya |
| claude-haiku-5.5 | indoculture_t0 | 2429 | 0.762 [0.745, 0.779] | 0.009 | 0.004 | ya |
| claude-haiku-5.5 | indommlu_t0 | 14904 | 0.711 [0.704, 0.718] | 0.004 | 0.006 | ya |
| claude-opus-5.5 | copal_id_colloquial_t0 | 559 | 0.973 [0.959, 0.986] | 0.007 | 0.200 | ya |
| claude-opus-5.5 | copal_id_standard_t0 | 559 | 0.970 [0.955, 0.984] | 0.007 | 0.200 | ya |
| claude-opus-5.5 | global_mmlu_full_id_ca_t0 | 2058 | 0.946 [0.936, 0.955] | 0.005 | 0.200 | ya |
| claude-opus-5.5 | global_mmlu_full_id_cs_t0 | 792 | 0.939 [0.922, 0.956] | 0.008 | 0.200 | ya |
| claude-opus-5.5 | indoculture_t0 | 2429 | 0.932 [0.922, 0.942] | 0.005 | 0.200 | ya |
| claude-opus-5.5 | indommlu_t0 | 14904 | 0.857 [0.851, 0.862] | 0.003 | 0.200 | ya |
| claude-sonnet-5.5 | copal_id_colloquial_t0 | 559 | 0.911 [0.886, 0.934] | 0.012 | 0.004 | ya |
| claude-sonnet-5.5 | copal_id_standard_t0 | 559 | 0.946 [0.927, 0.964] | 0.010 | 0.002 | ya |
| claude-sonnet-5.5 | global_mmlu_full_id_ca_t0 | 2058 | 0.917 [0.905, 0.929] | 0.006 | 0.003 | ya |
| claude-sonnet-5.5 | global_mmlu_full_id_cs_t0 | 792 | 0.881 [0.859, 0.904] | 0.011 | 0.004 | ya |
| claude-sonnet-5.5 | indoculture_t0 | 2429 | 0.879 [0.866, 0.891] | 0.007 | 0.006 | ya |
| claude-sonnet-5.5 | indommlu_t0 | 14904 | 0.812 [0.805, 0.818] | 0.003 | 0.002 | ya |

## b. Selisih pasangan (derived - base)

_Dilewati: tidak ada pasangan derived-base yang lengkap di run ini._
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma3-27b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.6-27b`: salah satu model tidak ada di run_
_Dilewati: `gemma-sea-lion-v4.5-e2b-it` vs `gemma4-e2b-it`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `gemma2-9b-it`: salah satu model tidak ada di run_

## c. Regional vs terbaru

_Dilewati: tidak ada pasangan regional-terbaru yang bisa dibandingkan._
_Dilewati: `gotoai-gemma3-27b-it` vs `qwen3.8-27b`: salah satu model tidak ada di run_
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-12b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.8-27b`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-12b-it`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `qwen3.8-27b`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `gemma4-12b-it`: salah satu model tidak ada di run_

## d. Gap baku vs kolokial (COPA-ID)

| Model | Baku | Kolokial | n | Gap (baku - kolokial) | CI 95% | p | Status | Metode |
|---|---|---|---|---|---|---|---|---|
| claude-haiku-5.5 | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.038 | [0.002, 0.073] | 0.0470 | bermakna | paired (doc_id sejajar) |
| claude-opus-5.5 | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | -0.004 | [-0.018, 0.011] | 0.7332 | tidak bermakna | paired (doc_id sejajar) |
| claude-sonnet-5.5 | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.036 | [0.014, 0.057] | 0.0020 | bermakna | paired (doc_id sejajar) |

## e. Gap Global-MMLU CS vs CA

| Model | CS | CA | n (CS/CA) | Gap (CS - CA) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| claude-haiku-5.5 | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | -0.051 | [-0.085, -0.017] | 0.0030 | bermakna |
| claude-opus-5.5 | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | -0.006 | [-0.026, 0.012] | 0.5366 | tidak bermakna |
| claude-sonnet-5.5 | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | -0.036 | [-0.062, -0.011] | 0.0042 | bermakna |

## f. Sanity: model >= 20B dekat random

Tidak ada model >= 20B yang skornya dalam 5 poin dari random.
_Dilewati: `claude-haiku-5.5` tidak ada di models.yaml, cek params dilewati_
_Dilewati: `claude-opus-5.5` tidak ada di models.yaml, cek params dilewati_
_Dilewati: `claude-sonnet-5.5` tidak ada di models.yaml, cek params dilewati_

## i. Semua model vs terbaik per task (paired bootstrap, koreksi Holm per task)

| Task | Terbaik | Model | Delta vs terbaik | CI 95% | p | p Holm sig. | Status |
|---|---|---|---|---|---|---|---|
| copal_id_colloquial_t0 | claude-opus-5.5 | claude-haiku-5.5 | -0.165 | [-0.199, -0.132] | 0.0000 | ya | di bawah terbaik |
| copal_id_colloquial_t0 | claude-opus-5.5 | claude-sonnet-5.5 | -0.063 | [-0.086, -0.041] | 0.0000 | ya | di bawah terbaik |
| copal_id_standard_t0 | claude-opus-5.5 | claude-haiku-5.5 | -0.123 | [-0.154, -0.095] | 0.0000 | ya | di bawah terbaik |
| copal_id_standard_t0 | claude-opus-5.5 | claude-sonnet-5.5 | -0.023 | [-0.045, -0.004] | 0.0276 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | claude-opus-5.5 | claude-haiku-5.5 | -0.137 | [-0.154, -0.121] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | claude-opus-5.5 | claude-sonnet-5.5 | -0.028 | [-0.038, -0.018] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_cs_t0 | claude-opus-5.5 | claude-haiku-5.5 | -0.182 | [-0.211, -0.153] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_cs_t0 | claude-opus-5.5 | claude-sonnet-5.5 | -0.058 | [-0.078, -0.039] | 0.0000 | ya | di bawah terbaik |
| indoculture_t0 | claude-opus-5.5 | claude-haiku-5.5 | -0.170 | [-0.188, -0.153] | 0.0000 | ya | di bawah terbaik |
| indoculture_t0 | claude-opus-5.5 | claude-sonnet-5.5 | -0.054 | [-0.066, -0.041] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | claude-opus-5.5 | claude-haiku-5.5 | -0.145 | [-0.152, -0.139] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | claude-opus-5.5 | claude-sonnet-5.5 | -0.045 | [-0.050, -0.040] | 0.0000 | ya | di bawah terbaik |

## h. Fertilitas tokenizer

_Dilewati: `tokenizer_fertility.csv` tidak ditemukan._

## Catatan

- model `claude-haiku-5.5` di run tidak ada di models.yaml (tanpa info pair/params)
- model `claude-opus-5.5` di run tidak ada di models.yaml (tanpa info pair/params)
- model `claude-sonnet-5.5` di run tidak ada di models.yaml (tanpa info pair/params)

