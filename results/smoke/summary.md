# Ringkasan indobench: run `smoke-a`

- Metrik: `acc`
- Model di run: 2
- Compare run: `smoke-b`

## a. Skor per model dan task

| Model | Task (lm_eval) | n | Skor [95% CI] | stderr | Random | Di atas random |
|---|---|---|---|---|---|---|
| gemma-sea-lion-v4.5-e2b-it | copal_id_colloquial | 50 | 0.560 [0.420, 0.700] | 0.071 | 0.500 | tidak |
| gemma-sea-lion-v4.5-e2b-it | copal_id_standard | 50 | 0.620 [0.480, 0.740] | 0.069 | 0.500 | tidak |
| gemma-sea-lion-v4.5-e2b-it | global_mmlu_full_id_ca_t0 | 50 | 0.200 [0.100, 0.320] | 0.057 | 0.250 | tidak |
| gemma-sea-lion-v4.5-e2b-it | global_mmlu_full_id_cs_t0 | 50 | 0.360 [0.220, 0.500] | 0.069 | 0.250 | tidak |
| gemma-sea-lion-v4.5-e2b-it | indoculture_t0 | 50 | 0.280 [0.160, 0.400] | 0.064 | 0.333 | tidak |
| gemma-sea-lion-v4.5-e2b-it | indommlu_t0 | 50 | 0.440 [0.300, 0.580] | 0.071 | 0.200 | ya |
| gemma4-e2b-it | copal_id_colloquial | 50 | 0.540 [0.400, 0.680] | 0.071 | 0.500 | tidak |
| gemma4-e2b-it | copal_id_standard | 50 | 0.640 [0.500, 0.760] | 0.069 | 0.500 | tidak |
| gemma4-e2b-it | global_mmlu_full_id_ca_t0 | 50 | 0.200 [0.100, 0.320] | 0.057 | 0.250 | tidak |
| gemma4-e2b-it | global_mmlu_full_id_cs_t0 | 50 | 0.360 [0.220, 0.500] | 0.069 | 0.250 | tidak |
| gemma4-e2b-it | indoculture_t0 | 50 | 0.280 [0.160, 0.400] | 0.064 | 0.333 | tidak |
| gemma4-e2b-it | indommlu_t0 | 50 | 0.440 [0.300, 0.580] | 0.071 | 0.200 | ya |

## b. Selisih pasangan (derived - base)

| Derived | Base | Task | n (doc_id irisan) | Delta (derived - base) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| gemma-sea-lion-v4.5-e2b-it | gemma4-e2b-it | copal_id_colloquial | 50 | +0.020 | [0.000, 0.060] | 0.7246 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | gemma4-e2b-it | copal_id_standard | 50 | -0.020 | [-0.060, 0.000] | 0.7314 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | gemma4-e2b-it | global_mmlu_full_id_ca_t0 | 50 | +0.000 | [-0.080, 0.080] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | gemma4-e2b-it | global_mmlu_full_id_cs_t0 | 50 | +0.000 | [-0.060, 0.060] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | gemma4-e2b-it | indoculture_t0 | 50 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | gemma4-e2b-it | indommlu_t0 | 50 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma3-27b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.6-27b`: salah satu model tidak ada di run_

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
| gemma-sea-lion-v4.5-e2b-it | copal_id_standard | copal_id_colloquial | 50 | +0.060 | [-0.080, 0.200] | 0.4932 | tidak bermakna | paired (doc_id sejajar) |
| gemma4-e2b-it | copal_id_standard | copal_id_colloquial | 50 | +0.100 | [-0.040, 0.240] | 0.2048 | tidak bermakna | paired (doc_id sejajar) |

## e. Gap Global-MMLU CS vs CA

| Model | CS | CA | n (CS/CA) | Gap (CS - CA) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| gemma-sea-lion-v4.5-e2b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 50/50 | +0.160 | [-0.020, 0.340] | 0.0900 | tidak bermakna |
| gemma4-e2b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 50/50 | +0.160 | [-0.020, 0.320] | 0.0858 | tidak bermakna |

## f. Sanity: model >= 20B dekat random

Tidak ada model >= 20B yang skornya dalam 5 poin dari random.

## g. Noise floor antar-run

| Model | Task | n | Skor run1 | Skor run2 | Delta (run1 - run2) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|---|
| gemma-sea-lion-v4.5-e2b-it | copal_id_colloquial | 50 | 0.560 | 0.560 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | copal_id_standard | 50 | 0.620 | 0.620 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | global_mmlu_full_id_ca_t0 | 50 | 0.200 | 0.200 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | global_mmlu_full_id_cs_t0 | 50 | 0.360 | 0.360 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | indoculture_t0 | 50 | 0.280 | 0.280 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma-sea-lion-v4.5-e2b-it | indommlu_t0 | 50 | 0.440 | 0.440 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma4-e2b-it | copal_id_colloquial | 50 | 0.540 | 0.520 | +0.020 | [0.000, 0.060] | 0.7328 | tidak bermakna |
| gemma4-e2b-it | copal_id_standard | 50 | 0.640 | 0.640 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma4-e2b-it | global_mmlu_full_id_ca_t0 | 50 | 0.200 | 0.200 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma4-e2b-it | global_mmlu_full_id_cs_t0 | 50 | 0.360 | 0.360 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma4-e2b-it | indoculture_t0 | 50 | 0.280 | 0.280 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |
| gemma4-e2b-it | indommlu_t0 | 50 | 0.440 | 0.440 | +0.000 | [0.000, 0.000] | 1.0000 | tidak bermakna |

## h. Fertilitas tokenizer

_Dilewati: `tokenizer_fertility.csv` tidak ditemukan._

