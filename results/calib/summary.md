# Ringkasan indobench: run `calib-27b-v2`

- Metrik: `acc`
- Model di run: 1
- Compare run: -

## a. Skor per model dan task

| Model | Task (lm_eval) | n | Skor [95% CI] | stderr | Random | Di atas random |
|---|---|---|---|---|---|---|
| qwen3.8-27b | copal_id_colloquial | 50 | 0.540 [0.400, 0.680] | 0.071 | 0.500 | tidak |
| qwen3.8-27b | copal_id_standard | 50 | 0.800 [0.680, 0.900] | 0.057 | 0.500 | ya |
| qwen3.8-27b | global_mmlu_full_id_ca_t0 | 50 | 0.620 [0.480, 0.740] | 0.069 | 0.250 | ya |
| qwen3.8-27b | global_mmlu_full_id_cs_t0 | 50 | 0.660 [0.520, 0.780] | 0.068 | 0.250 | ya |
| qwen3.8-27b | indoculture_t0 | 50 | 0.760 [0.640, 0.880] | 0.061 | 0.333 | ya |
| qwen3.8-27b | indommlu_t0 | 50 | 0.860 [0.760, 0.940] | 0.050 | 0.200 | ya |

## b. Selisih pasangan (derived - base)

_Dilewati: tidak ada pasangan derived-base yang lengkap di run ini._
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma3-27b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.6-27b`: salah satu model tidak ada di run_
_Dilewati: `gemma-sea-lion-v4.5-e2b-it` vs `gemma4-e2b-it`: salah satu model tidak ada di run_

## c. Regional vs terbaru

_Dilewati: tidak ada pasangan regional-terbaru yang bisa dibandingkan._
_Dilewati: `gotoai-gemma3-27b-it` vs `qwen3.8-27b`: salah satu model tidak ada di run_
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.8-27b`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_

## d. Gap baku vs kolokial (COPA-ID)

| Model | Baku | Kolokial | n | Gap (baku - kolokial) | CI 95% | p | Status | Metode |
|---|---|---|---|---|---|---|---|---|
| qwen3.8-27b | copal_id_standard | copal_id_colloquial | 50 | +0.260 | [0.100, 0.420] | 0.0008 | bermakna | paired (doc_id sejajar) |

## e. Gap Global-MMLU CS vs CA

| Model | CS | CA | n (CS/CA) | Gap (CS - CA) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| qwen3.8-27b | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 50/50 | +0.040 | [-0.140, 0.220] | 0.7632 | tidak bermakna |

## f. Sanity: model >= 20B dekat random

- `qwen3.8-27b` / `copal_id_colloquial`: skor 0.540 vs random 0.500 (selisih +0.040), periksa setup evaluasi

## h. Fertilitas tokenizer

_Dilewati: `tokenizer_fertility.csv` tidak ditemukan._

