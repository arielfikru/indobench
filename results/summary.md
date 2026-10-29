# Ringkasan indobench: run `full-m4`

- Metrik: `acc`
- Model di run: 6
- Compare run: -

## a. Skor per model dan task

| Model | Task (lm_eval) | n | Skor [95% CI] | stderr | Random | Di atas random |
|---|---|---|---|---|---|---|
| gemma2-9b-it | copal_id_colloquial_t0 | 559 | 0.769 [0.733, 0.803] | 0.018 | 0.500 | ya |
| gemma2-9b-it | copal_id_standard_t0 | 559 | 0.785 [0.751, 0.819] | 0.017 | 0.500 | ya |
| gemma2-9b-it | global_mmlu_full_id_ca_t0 | 2058 | 0.638 [0.617, 0.658] | 0.011 | 0.250 | ya |
| gemma2-9b-it | global_mmlu_full_id_cs_t0 | 792 | 0.688 [0.655, 0.720] | 0.016 | 0.250 | ya |
| gemma2-9b-it | indoculture_t0 | 2429 | 0.675 [0.657, 0.693] | 0.010 | 0.333 | ya |
| gemma2-9b-it | indommlu_t0 | 14904 | 0.612 [0.604, 0.620] | 0.004 | 0.235 | ya |
| gemma3-27b-it | copal_id_colloquial_t0 | 559 | 0.830 [0.800, 0.860] | 0.016 | 0.500 | ya |
| gemma3-27b-it | copal_id_standard_t0 | 559 | 0.866 [0.837, 0.894] | 0.014 | 0.500 | ya |
| gemma3-27b-it | global_mmlu_full_id_ca_t0 | 2058 | 0.712 [0.692, 0.731] | 0.010 | 0.250 | ya |
| gemma3-27b-it | global_mmlu_full_id_cs_t0 | 792 | 0.744 [0.713, 0.773] | 0.016 | 0.250 | ya |
| gemma3-27b-it | indoculture_t0 | 2429 | 0.737 [0.719, 0.754] | 0.009 | 0.333 | ya |
| gemma3-27b-it | indommlu_t0 | 14904 | 0.672 [0.665, 0.679] | 0.004 | 0.235 | ya |
| gemma4-12b-it | copal_id_colloquial_t0 | 559 | 0.814 [0.782, 0.846] | 0.016 | 0.500 | ya |
| gemma4-12b-it | copal_id_standard_t0 | 559 | 0.860 [0.830, 0.887] | 0.015 | 0.500 | ya |
| gemma4-12b-it | global_mmlu_full_id_ca_t0 | 2058 | 0.707 [0.688, 0.727] | 0.010 | 0.250 | ya |
| gemma4-12b-it | global_mmlu_full_id_cs_t0 | 792 | 0.670 [0.639, 0.703] | 0.017 | 0.250 | ya |
| gemma4-12b-it | indoculture_t0 | 2429 | 0.723 [0.705, 0.741] | 0.009 | 0.333 | ya |
| gemma4-12b-it | indommlu_t0 | 14904 | 0.684 [0.676, 0.691] | 0.004 | 0.235 | ya |
| gotoai-gemma3-27b-it | copal_id_colloquial_t0 | 559 | 0.837 [0.807, 0.868] | 0.016 | 0.500 | ya |
| gotoai-gemma3-27b-it | copal_id_standard_t0 | 559 | 0.871 [0.843, 0.898] | 0.014 | 0.500 | ya |
| gotoai-gemma3-27b-it | global_mmlu_full_id_ca_t0 | 2058 | 0.707 [0.687, 0.726] | 0.010 | 0.250 | ya |
| gotoai-gemma3-27b-it | global_mmlu_full_id_cs_t0 | 792 | 0.742 [0.712, 0.773] | 0.016 | 0.250 | ya |
| gotoai-gemma3-27b-it | indoculture_t0 | 2429 | 0.741 [0.724, 0.758] | 0.009 | 0.333 | ya |
| gotoai-gemma3-27b-it | indommlu_t0 | 14904 | 0.676 [0.669, 0.684] | 0.004 | 0.235 | ya |
| qwen3.8-27b | copal_id_colloquial_t0 | 559 | 0.823 [0.791, 0.853] | 0.016 | 0.500 | ya |
| qwen3.8-27b | copal_id_standard_t0 | 559 | 0.864 [0.835, 0.893] | 0.015 | 0.500 | ya |
| qwen3.8-27b | global_mmlu_full_id_ca_t0 | 2058 | 0.793 [0.775, 0.810] | 0.009 | 0.250 | ya |
| qwen3.8-27b | global_mmlu_full_id_cs_t0 | 792 | 0.771 [0.742, 0.801] | 0.015 | 0.250 | ya |
| qwen3.8-27b | indoculture_t0 | 2429 | 0.741 [0.724, 0.759] | 0.009 | 0.333 | ya |
| qwen3.8-27b | indommlu_t0 | 14904 | 0.714 [0.707, 0.721] | 0.004 | 0.235 | ya |
| sahabatai-gemma2-9b-it | copal_id_colloquial_t0 | 559 | 0.800 [0.766, 0.832] | 0.017 | 0.500 | ya |
| sahabatai-gemma2-9b-it | copal_id_standard_t0 | 559 | 0.816 [0.782, 0.848] | 0.016 | 0.500 | ya |
| sahabatai-gemma2-9b-it | global_mmlu_full_id_ca_t0 | 2058 | 0.644 [0.622, 0.664] | 0.011 | 0.250 | ya |
| sahabatai-gemma2-9b-it | global_mmlu_full_id_cs_t0 | 792 | 0.723 [0.692, 0.754] | 0.016 | 0.250 | ya |
| sahabatai-gemma2-9b-it | indoculture_t0 | 2429 | 0.699 [0.680, 0.717] | 0.009 | 0.333 | ya |
| sahabatai-gemma2-9b-it | indommlu_t0 | 14904 | 0.636 [0.628, 0.644] | 0.004 | 0.235 | ya |

## b. Selisih pasangan (derived - base)

| Derived | Base | Task | n (doc_id irisan) | Delta (derived - base) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| gotoai-gemma3-27b-it | gemma3-27b-it | copal_id_colloquial_t0 | 559 | +0.007 | [-0.005, 0.020] | 0.3610 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma3-27b-it | copal_id_standard_t0 | 559 | +0.005 | [-0.009, 0.020] | 0.5460 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma3-27b-it | global_mmlu_full_id_ca_t0 | 2058 | -0.005 | [-0.013, 0.003] | 0.2312 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma3-27b-it | global_mmlu_full_id_cs_t0 | 792 | -0.001 | [-0.015, 0.011] | 0.9234 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma3-27b-it | indoculture_t0 | 2429 | +0.005 | [-0.003, 0.012] | 0.2756 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma3-27b-it | indommlu_t0 | 14904 | +0.004 | [0.001, 0.008] | 0.0114 | bermakna |
| sahabatai-gemma2-9b-it | gemma2-9b-it | copal_id_colloquial_t0 | 559 | +0.030 | [0.000, 0.063] | 0.0656 | tidak bermakna |
| sahabatai-gemma2-9b-it | gemma2-9b-it | copal_id_standard_t0 | 559 | +0.030 | [0.004, 0.059] | 0.0324 | bermakna |
| sahabatai-gemma2-9b-it | gemma2-9b-it | global_mmlu_full_id_ca_t0 | 2058 | +0.006 | [-0.009, 0.020] | 0.4402 | tidak bermakna |
| sahabatai-gemma2-9b-it | gemma2-9b-it | global_mmlu_full_id_cs_t0 | 792 | +0.035 | [0.013, 0.058] | 0.0020 | bermakna |
| sahabatai-gemma2-9b-it | gemma2-9b-it | indoculture_t0 | 2429 | +0.023 | [0.010, 0.036] | 0.0002 | bermakna |
| sahabatai-gemma2-9b-it | gemma2-9b-it | indommlu_t0 | 14904 | +0.024 | [0.018, 0.029] | 0.0000 | bermakna |
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.6-27b`: salah satu model tidak ada di run_
_Dilewati: `gemma-sea-lion-v4.5-e2b-it` vs `gemma4-e2b-it`: salah satu model tidak ada di run_

## c. Regional vs terbaru

| Regional | Terbaru | Task | n (doc_id irisan) | Delta (regional - terbaru) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| gotoai-gemma3-27b-it | qwen3.8-27b | copal_id_colloquial_t0 | 559 | +0.014 | [-0.018, 0.048] | 0.4258 | tidak bermakna |
| gotoai-gemma3-27b-it | qwen3.8-27b | copal_id_standard_t0 | 559 | +0.007 | [-0.023, 0.038] | 0.7026 | tidak bermakna |
| gotoai-gemma3-27b-it | qwen3.8-27b | global_mmlu_full_id_ca_t0 | 2058 | -0.086 | [-0.103, -0.068] | 0.0000 | bermakna |
| gotoai-gemma3-27b-it | qwen3.8-27b | global_mmlu_full_id_cs_t0 | 792 | -0.029 | [-0.059, 0.001] | 0.0708 | tidak bermakna |
| gotoai-gemma3-27b-it | qwen3.8-27b | indoculture_t0 | 2429 | -0.000 | [-0.018, 0.017] | 0.9908 | tidak bermakna |
| gotoai-gemma3-27b-it | qwen3.8-27b | indommlu_t0 | 14904 | -0.038 | [-0.045, -0.031] | 0.0000 | bermakna |
| gotoai-gemma3-27b-it | gemma4-12b-it | copal_id_colloquial_t0 | 559 | +0.023 | [-0.014, 0.059] | 0.2266 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma4-12b-it | copal_id_standard_t0 | 559 | +0.011 | [-0.020, 0.043] | 0.5432 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma4-12b-it | global_mmlu_full_id_ca_t0 | 2058 | -0.000 | [-0.020, 0.018] | 0.9654 | tidak bermakna |
| gotoai-gemma3-27b-it | gemma4-12b-it | global_mmlu_full_id_cs_t0 | 792 | +0.072 | [0.040, 0.104] | 0.0000 | bermakna |
| gotoai-gemma3-27b-it | gemma4-12b-it | indoculture_t0 | 2429 | +0.018 | [0.000, 0.036] | 0.0462 | bermakna |
| gotoai-gemma3-27b-it | gemma4-12b-it | indommlu_t0 | 14904 | -0.007 | [-0.014, -0.001] | 0.0306 | bermakna |
| sahabatai-gemma2-9b-it | qwen3.8-27b | copal_id_colloquial_t0 | 559 | -0.023 | [-0.061, 0.013] | 0.2212 | tidak bermakna |
| sahabatai-gemma2-9b-it | qwen3.8-27b | copal_id_standard_t0 | 559 | -0.048 | [-0.082, -0.016] | 0.0046 | bermakna |
| sahabatai-gemma2-9b-it | qwen3.8-27b | global_mmlu_full_id_ca_t0 | 2058 | -0.149 | [-0.169, -0.129] | 0.0000 | bermakna |
| sahabatai-gemma2-9b-it | qwen3.8-27b | global_mmlu_full_id_cs_t0 | 792 | -0.048 | [-0.080, -0.018] | 0.0024 | bermakna |
| sahabatai-gemma2-9b-it | qwen3.8-27b | indoculture_t0 | 2429 | -0.043 | [-0.062, -0.023] | 0.0000 | bermakna |
| sahabatai-gemma2-9b-it | qwen3.8-27b | indommlu_t0 | 14904 | -0.078 | [-0.086, -0.071] | 0.0000 | bermakna |
| sahabatai-gemma2-9b-it | gemma4-12b-it | copal_id_colloquial_t0 | 559 | -0.014 | [-0.054, 0.025] | 0.5092 | tidak bermakna |
| sahabatai-gemma2-9b-it | gemma4-12b-it | copal_id_standard_t0 | 559 | -0.045 | [-0.077, -0.013] | 0.0086 | bermakna |
| sahabatai-gemma2-9b-it | gemma4-12b-it | global_mmlu_full_id_ca_t0 | 2058 | -0.064 | [-0.085, -0.044] | 0.0000 | bermakna |
| sahabatai-gemma2-9b-it | gemma4-12b-it | global_mmlu_full_id_cs_t0 | 792 | +0.053 | [0.020, 0.086] | 0.0012 | bermakna |
| sahabatai-gemma2-9b-it | gemma4-12b-it | indoculture_t0 | 2429 | -0.024 | [-0.044, -0.004] | 0.0168 | bermakna |
| sahabatai-gemma2-9b-it | gemma4-12b-it | indommlu_t0 | 14904 | -0.048 | [-0.055, -0.040] | 0.0000 | bermakna |
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `gotoai-gemma3-27b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `qwen3.8-27b`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_
_Dilewati: `qwen-sea-lion-v4.5-27b-it` vs `gemma4-12b-it`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `gemma4-31b-it`: salah satu model tidak ada di run_
_Dilewati: `sahabatai-gemma2-9b-it` vs `gemma4-26b-a4b-it`: salah satu model tidak ada di run_

## d. Gap baku vs kolokial (COPA-ID)

| Model | Baku | Kolokial | n | Gap (baku - kolokial) | CI 95% | p | Status | Metode |
|---|---|---|---|---|---|---|---|---|
| gemma2-9b-it | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.016 | [-0.014, 0.048] | 0.3482 | tidak bermakna | paired (doc_id sejajar) |
| gemma3-27b-it | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.036 | [0.011, 0.061] | 0.0064 | bermakna | paired (doc_id sejajar) |
| gemma4-12b-it | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.047 | [0.018, 0.077] | 0.0008 | bermakna | paired (doc_id sejajar) |
| gotoai-gemma3-27b-it | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.034 | [0.007, 0.061] | 0.0148 | bermakna | paired (doc_id sejajar) |
| qwen3.8-27b | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.041 | [0.011, 0.072] | 0.0070 | bermakna | paired (doc_id sejajar) |
| sahabatai-gemma2-9b-it | copal_id_standard_t0 | copal_id_colloquial_t0 | 559 | +0.016 | [-0.007, 0.041] | 0.2182 | tidak bermakna | paired (doc_id sejajar) |

## e. Gap Global-MMLU CS vs CA

| Model | CS | CA | n (CS/CA) | Gap (CS - CA) | CI 95% | p | Status |
|---|---|---|---|---|---|---|---|
| gemma2-9b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | +0.050 | [0.012, 0.088] | 0.0116 | bermakna |
| gemma3-27b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | +0.032 | [-0.005, 0.068] | 0.0874 | tidak bermakna |
| gemma4-12b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | -0.037 | [-0.075, 0.002] | 0.0638 | tidak bermakna |
| gotoai-gemma3-27b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | +0.035 | [-0.001, 0.071] | 0.0554 | tidak bermakna |
| qwen3.8-27b | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | -0.021 | [-0.055, 0.013] | 0.2192 | tidak bermakna |
| sahabatai-gemma2-9b-it | global_mmlu_full_id_cs_t0 | global_mmlu_full_id_ca_t0 | 792/2058 | +0.080 | [0.042, 0.117] | 0.0002 | bermakna |

## f. Sanity: model >= 20B dekat random

Tidak ada model >= 20B yang skornya dalam 5 poin dari random.

## i. Semua model vs terbaik per task (paired bootstrap, koreksi Holm per task)

| Task | Terbaik | Model | Delta vs terbaik | CI 95% | p | p Holm sig. | Status |
|---|---|---|---|---|---|---|---|
| copal_id_colloquial_t0 | gotoai-gemma3-27b-it | gemma2-9b-it | -0.068 | [-0.104, -0.032] | 0.0000 | ya | di bawah terbaik |
| copal_id_colloquial_t0 | gotoai-gemma3-27b-it | gemma3-27b-it | -0.007 | [-0.020, 0.005] | 0.3610 | tidak | seri dengan terbaik |
| copal_id_colloquial_t0 | gotoai-gemma3-27b-it | gemma4-12b-it | -0.023 | [-0.059, 0.014] | 0.2266 | tidak | seri dengan terbaik |
| copal_id_colloquial_t0 | gotoai-gemma3-27b-it | qwen3.8-27b | -0.014 | [-0.048, 0.018] | 0.4258 | tidak | seri dengan terbaik |
| copal_id_colloquial_t0 | gotoai-gemma3-27b-it | sahabatai-gemma2-9b-it | -0.038 | [-0.068, -0.009] | 0.0162 | tidak | seri dengan terbaik |
| copal_id_standard_t0 | gotoai-gemma3-27b-it | gemma2-9b-it | -0.086 | [-0.118, -0.054] | 0.0000 | ya | di bawah terbaik |
| copal_id_standard_t0 | gotoai-gemma3-27b-it | gemma3-27b-it | -0.005 | [-0.020, 0.009] | 0.5460 | tidak | seri dengan terbaik |
| copal_id_standard_t0 | gotoai-gemma3-27b-it | gemma4-12b-it | -0.011 | [-0.043, 0.020] | 0.5432 | tidak | seri dengan terbaik |
| copal_id_standard_t0 | gotoai-gemma3-27b-it | qwen3.8-27b | -0.007 | [-0.038, 0.023] | 0.7026 | tidak | seri dengan terbaik |
| copal_id_standard_t0 | gotoai-gemma3-27b-it | sahabatai-gemma2-9b-it | -0.055 | [-0.086, -0.025] | 0.0006 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gemma2-9b-it | -0.155 | [-0.175, -0.134] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gemma3-27b-it | -0.081 | [-0.098, -0.063] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gemma4-12b-it | -0.085 | [-0.104, -0.066] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.086 | [-0.103, -0.068] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.149 | [-0.169, -0.129] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gemma2-9b-it | -0.083 | [-0.115, -0.052] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gemma3-27b-it | -0.028 | [-0.057, 0.003] | 0.0820 | tidak | seri dengan terbaik |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gemma4-12b-it | -0.101 | [-0.133, -0.071] | 0.0000 | ya | di bawah terbaik |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.029 | [-0.059, 0.001] | 0.0708 | tidak | seri dengan terbaik |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.048 | [-0.080, -0.018] | 0.0024 | ya | di bawah terbaik |
| indoculture_t0 | qwen3.8-27b | gemma2-9b-it | -0.066 | [-0.086, -0.047] | 0.0000 | ya | di bawah terbaik |
| indoculture_t0 | qwen3.8-27b | gemma3-27b-it | -0.005 | [-0.023, 0.013] | 0.6152 | tidak | seri dengan terbaik |
| indoculture_t0 | qwen3.8-27b | gemma4-12b-it | -0.019 | [-0.037, 0.000] | 0.0522 | tidak | seri dengan terbaik |
| indoculture_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.000 | [-0.018, 0.017] | 0.9908 | tidak | seri dengan terbaik |
| indoculture_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.043 | [-0.062, -0.023] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | qwen3.8-27b | gemma2-9b-it | -0.102 | [-0.110, -0.094] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | qwen3.8-27b | gemma3-27b-it | -0.042 | [-0.049, -0.035] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | qwen3.8-27b | gemma4-12b-it | -0.030 | [-0.037, -0.023] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.038 | [-0.045, -0.031] | 0.0000 | ya | di bawah terbaik |
| indommlu_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.078 | [-0.086, -0.071] | 0.0000 | ya | di bawah terbaik |

## j. CI berkelompok (cluster bootstrap, task berkluster saja)

**a. Skor dengan CI iid vs CI berkelompok**

| Model | Task | n item | n klaster | Skor [CI iid] | CI berkelompok | Rasio lebar (berkelompok / iid) |
|---|---|---|---|---|---|---|
| gemma2-9b-it | global_mmlu_full_id_ca_t0 | 2058 | 55 | 0.638 [0.617, 0.658] | [0.600, 0.675] | 1.80x |
| gemma2-9b-it | global_mmlu_full_id_cs_t0 | 792 | 45 | 0.688 [0.655, 0.720] | [0.619, 0.752] | 2.07x |
| gemma2-9b-it | indoculture_t0 | 2429 | 11 | 0.675 [0.657, 0.693] | [0.628, 0.733] | 2.87x |
| gemma2-9b-it | indommlu_t0 | 14904 | 25 | 0.612 [0.604, 0.620] | [0.545, 0.662] | 7.46x |
| gemma3-27b-it | global_mmlu_full_id_ca_t0 | 2058 | 55 | 0.712 [0.692, 0.731] | [0.673, 0.750] | 1.96x |
| gemma3-27b-it | global_mmlu_full_id_cs_t0 | 792 | 45 | 0.744 [0.713, 0.773] | [0.682, 0.802] | 2.02x |
| gemma3-27b-it | indoculture_t0 | 2429 | 11 | 0.737 [0.719, 0.754] | [0.698, 0.778] | 2.28x |
| gemma3-27b-it | indommlu_t0 | 14904 | 25 | 0.672 [0.665, 0.679] | [0.612, 0.715] | 6.99x |
| gemma4-12b-it | global_mmlu_full_id_ca_t0 | 2058 | 55 | 0.707 [0.688, 0.727] | [0.672, 0.742] | 1.80x |
| gemma4-12b-it | global_mmlu_full_id_cs_t0 | 792 | 45 | 0.670 [0.639, 0.703] | [0.602, 0.732] | 2.02x |
| gemma4-12b-it | indoculture_t0 | 2429 | 11 | 0.723 [0.705, 0.741] | [0.680, 0.775] | 2.63x |
| gemma4-12b-it | indommlu_t0 | 14904 | 25 | 0.684 [0.676, 0.691] | [0.616, 0.731] | 7.84x |
| gotoai-gemma3-27b-it | global_mmlu_full_id_ca_t0 | 2058 | 55 | 0.707 [0.687, 0.726] | [0.665, 0.748] | 2.14x |
| gotoai-gemma3-27b-it | global_mmlu_full_id_cs_t0 | 792 | 45 | 0.742 [0.712, 0.773] | [0.679, 0.803] | 2.03x |
| gotoai-gemma3-27b-it | indoculture_t0 | 2429 | 11 | 0.741 [0.724, 0.758] | [0.702, 0.782] | 2.33x |
| gotoai-gemma3-27b-it | indommlu_t0 | 14904 | 25 | 0.676 [0.669, 0.684] | [0.617, 0.718] | 6.85x |
| qwen3.8-27b | global_mmlu_full_id_ca_t0 | 2058 | 55 | 0.793 [0.775, 0.810] | [0.757, 0.827] | 2.03x |
| qwen3.8-27b | global_mmlu_full_id_cs_t0 | 792 | 45 | 0.771 [0.742, 0.801] | [0.713, 0.827] | 1.96x |
| qwen3.8-27b | indoculture_t0 | 2429 | 11 | 0.741 [0.724, 0.759] | [0.698, 0.790] | 2.67x |
| qwen3.8-27b | indommlu_t0 | 14904 | 25 | 0.714 [0.707, 0.721] | [0.651, 0.760] | 7.50x |
| sahabatai-gemma2-9b-it | global_mmlu_full_id_ca_t0 | 2058 | 55 | 0.644 [0.622, 0.664] | [0.599, 0.687] | 2.11x |
| sahabatai-gemma2-9b-it | global_mmlu_full_id_cs_t0 | 792 | 45 | 0.723 [0.692, 0.754] | [0.650, 0.788] | 2.23x |
| sahabatai-gemma2-9b-it | indoculture_t0 | 2429 | 11 | 0.699 [0.680, 0.717] | [0.656, 0.750] | 2.56x |
| sahabatai-gemma2-9b-it | indommlu_t0 | 14904 | 25 | 0.636 [0.628, 0.644] | [0.574, 0.682] | 7.09x |

**b1. Selisih pasangan derived - base (task berkluster)**

| Derived | Base | Task | n klaster | Delta | CI iid | CI berkelompok | p berkelompok | Status iid | Status berkelompok | Berubah |
|---|---|---|---|---|---|---|---|---|---|---|
| gotoai-gemma3-27b-it | gemma3-27b-it | global_mmlu_full_id_ca_t0 | 55 | -0.005 | [-0.013, 0.003] | [-0.012, 0.002] | 0.2080 | tidak bermakna | tidak bermakna | tidak |
| gotoai-gemma3-27b-it | gemma3-27b-it | global_mmlu_full_id_cs_t0 | 45 | -0.001 | [-0.015, 0.011] | [-0.015, 0.012] | 0.9106 | tidak bermakna | tidak bermakna | tidak |
| gotoai-gemma3-27b-it | gemma3-27b-it | indoculture_t0 | 11 | +0.005 | [-0.003, 0.012] | [-0.003, 0.012] | 0.2702 | tidak bermakna | tidak bermakna | tidak |
| gotoai-gemma3-27b-it | gemma3-27b-it | indommlu_t0 | 25 | +0.004 | [0.001, 0.008] | [0.001, 0.009] | 0.0082 | bermakna | bermakna | tidak |
| sahabatai-gemma2-9b-it | gemma2-9b-it | global_mmlu_full_id_ca_t0 | 55 | +0.006 | [-0.009, 0.020] | [-0.011, 0.022] | 0.5010 | tidak bermakna | tidak bermakna | tidak |
| sahabatai-gemma2-9b-it | gemma2-9b-it | global_mmlu_full_id_cs_t0 | 45 | +0.035 | [0.013, 0.058] | [0.012, 0.056] | 0.0042 | bermakna | bermakna | tidak |
| sahabatai-gemma2-9b-it | gemma2-9b-it | indoculture_t0 | 11 | +0.023 | [0.010, 0.036] | [0.010, 0.038] | 0.0004 | bermakna | bermakna | tidak |
| sahabatai-gemma2-9b-it | gemma2-9b-it | indommlu_t0 | 25 | +0.024 | [0.018, 0.029] | [0.013, 0.038] | 0.0000 | bermakna | bermakna | tidak |

**b2. Semua model vs terbaik per task (task berkluster, Holm per task)**

| Task | Terbaik | Model | Delta vs terbaik | CI iid | CI berkelompok | p berkelompok | Holm sig. berkelompok | Status iid | Status berkelompok | Berubah |
|---|---|---|---|---|---|---|---|---|---|---|
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gemma2-9b-it | -0.155 | [-0.175, -0.134] | [-0.175, -0.133] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gemma3-27b-it | -0.081 | [-0.098, -0.063] | [-0.102, -0.060] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gemma4-12b-it | -0.085 | [-0.104, -0.066] | [-0.106, -0.064] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.086 | [-0.103, -0.068] | [-0.107, -0.065] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_ca_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.149 | [-0.169, -0.129] | [-0.174, -0.124] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gemma2-9b-it | -0.083 | [-0.115, -0.052] | [-0.117, -0.049] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gemma3-27b-it | -0.028 | [-0.057, 0.003] | [-0.063, 0.007] | 0.1230 | tidak | seri dengan terbaik | seri dengan terbaik | tidak |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gemma4-12b-it | -0.101 | [-0.133, -0.071] | [-0.130, -0.072] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.029 | [-0.059, 0.001] | [-0.065, 0.005] | 0.1062 | tidak | seri dengan terbaik | seri dengan terbaik | tidak |
| global_mmlu_full_id_cs_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.048 | [-0.080, -0.018] | [-0.086, -0.013] | 0.0072 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indoculture_t0 | qwen3.8-27b | gemma2-9b-it | -0.066 | [-0.086, -0.047] | [-0.088, -0.044] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indoculture_t0 | qwen3.8-27b | gemma3-27b-it | -0.005 | [-0.023, 0.013] | [-0.021, 0.010] | 0.5698 | tidak | seri dengan terbaik | seri dengan terbaik | tidak |
| indoculture_t0 | qwen3.8-27b | gemma4-12b-it | -0.019 | [-0.037, 0.000] | [-0.035, 0.000] | 0.0520 | tidak | seri dengan terbaik | seri dengan terbaik | tidak |
| indoculture_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.000 | [-0.018, 0.017] | [-0.014, 0.013] | 0.9870 | tidak | seri dengan terbaik | seri dengan terbaik | tidak |
| indoculture_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.043 | [-0.062, -0.023] | [-0.055, -0.028] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indommlu_t0 | qwen3.8-27b | gemma2-9b-it | -0.102 | [-0.110, -0.094] | [-0.116, -0.088] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indommlu_t0 | qwen3.8-27b | gemma3-27b-it | -0.042 | [-0.049, -0.035] | [-0.049, -0.034] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indommlu_t0 | qwen3.8-27b | gemma4-12b-it | -0.030 | [-0.037, -0.023] | [-0.045, -0.019] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indommlu_t0 | qwen3.8-27b | gotoai-gemma3-27b-it | -0.038 | [-0.045, -0.031] | [-0.047, -0.026] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |
| indommlu_t0 | qwen3.8-27b | sahabatai-gemma2-9b-it | -0.078 | [-0.086, -0.071] | [-0.089, -0.065] | 0.0000 | ya | di bawah terbaik | di bawah terbaik | tidak |

## h. Fertilitas tokenizer

| model_key | repo | revision | tokenizer_hash | vocab_size | lang | n_sentences | n_words | n_tokens | fertility | chars_per_token | premium_id_en | fertility_ratio_id_en | dataset | dataset_revision | split | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma3-27b-it | google/gemma-3-27b-it | 005ad3404e59d6023443cb575daa05336842228a |  |  | ind_Latn |  |  |  |  |  |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | error: OSError: You are trying to access a gated repo. |
| gemma3-27b-it | google/gemma-3-27b-it | 005ad3404e59d6023443cb575daa05336842228a |  |  | eng_Latn |  |  |  |  |  |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | error: OSError: You are trying to access a gated repo. |
| gotoai-gemma3-27b-it | GoToCompany/gemma3-27b-cpt-gotoai-v3-instruct | db3fb073bd44bf9554cbe6d9b94e54024cafcc37 | c1a087240686a7d1 | 262145 | ind_Latn | 1012 | 19811 | 31196 | 1.5747 | 4.5621 | 1.1505 | 1.2719 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gotoai-gemma3-27b-it | GoToCompany/gemma3-27b-cpt-gotoai-v3-instruct | db3fb073bd44bf9554cbe6d9b94e54024cafcc37 | c1a087240686a7d1 | 262145 | eng_Latn | 1012 | 21901 | 27114 | 1.238 | 4.8671 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| qwen3.6-27b | Qwen/Qwen3.6-27B | 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 | 4d765ac5a92a75f2 | 248077 | ind_Latn | 1012 | 19811 | 30064 | 1.5175 | 4.7338 | 1.092 | 1.2073 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| qwen3.6-27b | Qwen/Qwen3.6-27B | 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 | 4d765ac5a92a75f2 | 248077 | eng_Latn | 1012 | 21901 | 27530 | 1.257 | 4.7935 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| qwen-sea-lion-v4.5-27b-it | aisingapore/Qwen-SEA-LION-v4.5-27B-IT | 544e416f68a5700c7577547ad48e351e7d294116 | 4d765ac5a92a75f2 | 248077 | ind_Latn | 1012 | 19811 | 30064 | 1.5175 | 4.7338 | 1.092 | 1.2073 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| qwen-sea-lion-v4.5-27b-it | aisingapore/Qwen-SEA-LION-v4.5-27B-IT | 544e416f68a5700c7577547ad48e351e7d294116 | 4d765ac5a92a75f2 | 248077 | eng_Latn | 1012 | 21901 | 27530 | 1.257 | 4.7935 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma4-e2b-it | google/gemma-4-E2B-it | 3e22461f65e89153144f8adb70e3b8c2cc9845a7 | bca34862f49c6a63 | 262144 | ind_Latn | 1012 | 19811 | 31196 | 1.5747 | 4.5621 | 1.1505 | 1.2719 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma4-e2b-it | google/gemma-4-E2B-it | 3e22461f65e89153144f8adb70e3b8c2cc9845a7 | bca34862f49c6a63 | 262144 | eng_Latn | 1012 | 21901 | 27114 | 1.238 | 4.8671 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma-sea-lion-v4.5-e2b-it | aisingapore/Gemma-SEA-LION-v4.5-E2B-IT | c028f609f6f84dd0e9b669dad9dc1f9fd61b8bed | bca34862f49c6a63 | 262144 | ind_Latn | 1012 | 19811 | 31196 | 1.5747 | 4.5621 | 1.1505 | 1.2719 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma-sea-lion-v4.5-e2b-it | aisingapore/Gemma-SEA-LION-v4.5-E2B-IT | c028f609f6f84dd0e9b669dad9dc1f9fd61b8bed | bca34862f49c6a63 | 262144 | eng_Latn | 1012 | 21901 | 27114 | 1.238 | 4.8671 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| qwen3.8-27b | Qwen/Qwen3.8-27B | 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 | 4d765ac5a92a75f2 | 248077 | ind_Latn | 1012 | 19811 | 30064 | 1.5175 | 4.7338 | 1.092 | 1.2073 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| qwen3.8-27b | Qwen/Qwen3.8-27B | 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 | 4d765ac5a92a75f2 | 248077 | eng_Latn | 1012 | 21901 | 27530 | 1.257 | 4.7935 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma4-31b-it | google/gemma-4-31B-it | 842da3794eaa0b77d5f08bae87a17459d91ff475 | bca34862f49c6a63 | 262144 | ind_Latn | 1012 | 19811 | 31196 | 1.5747 | 4.5621 | 1.1505 | 1.2719 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma4-31b-it | google/gemma-4-31B-it | 842da3794eaa0b77d5f08bae87a17459d91ff475 | bca34862f49c6a63 | 262144 | eng_Latn | 1012 | 21901 | 27114 | 1.238 | 4.8671 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma4-26b-a4b-it | google/gemma-4-26B-A4B-it | 4d7ae4984b7db7de8f8457170b3f1a419ee76d52 | bca34862f49c6a63 | 262144 | ind_Latn | 1012 | 19811 | 31196 | 1.5747 | 4.5621 | 1.1505 | 1.2719 | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |
| gemma4-26b-a4b-it | google/gemma-4-26B-A4B-it | 4d7ae4984b7db7de8f8457170b3f1a419ee76d52 | bca34862f49c6a63 | 262144 | eng_Latn | 1012 | 21901 | 27114 | 1.238 | 4.8671 |  |  | openlanguagedata/flores_plus | 1147e2dc59f37fbb5c22fd8478770de02cd399f9 | devtest | ok |

