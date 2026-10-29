# HF verification (2026-10-28)

| group | id | sha | gated | created | access(config) | params B | bf16 GB | max_len | multimodal | arch | thinking(template) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pair1_gemma3 | google/gemma-3-27b-it | 005ad3404e | manual | 2025-03-01 | 403_gated_not_accepted | None | None | None | None | None | None |
| pair1_gemma3 | GoToCompany/gemma3-27b-cpt-gotoai-v3-instruct | db3fb073bd | False | 2025-12-03 | OK | 27.432 | 54.86 | 131072 | True | Gemma3ForConditionalGeneration | False |
| pair2_qwen | Qwen/Qwen3.6-27B | 6a9e13bd6f | False | 2026-04-21 | OK | 27.781 | 55.56 | 262144 | True | Qwen3_5ForConditionalGeneration | True |
| pair2_qwen | aisingapore/Qwen-SEA-LION-v4.5-27B-IT | 544e416f68 | False | 2026-05-14 | OK | 27.781 | 55.56 | 262144 | True | Qwen3_5ForConditionalGeneration | True |
| pair3_gemma4e2b | google/gemma-4-E2B-it | 3e22461f65 | False | 2026-03-02 | OK | 5.123 | 10.25 | 131072 | True | Gemma4ForConditionalGeneration | True |
| pair3_gemma4e2b | google/gemma-4-E2B | d29ff6b45f | False | 2026-03-02 | OK | 5.123 | 10.25 | 131072 | True | Gemma4ForConditionalGeneration | None |
| pair3_gemma4e2b | aisingapore/Gemma-SEA-LION-v4.5-E2B-IT | c028f609f6 | False | 2026-05-18 | OK | 5.123 | 10.25 | 131072 | True | Gemma4ForConditionalGeneration | True |
| latest_comparators | Qwen/Qwen3.8-27B | 1d4bf0f2ff | False | 2026-08-05 | OK | 27.781 | 55.56 | 262144 | True | Qwen3_5ForConditionalGeneration | True |
| latest_comparators | google/gemma-4-31B-it | 842da3794e | False | 2026-03-11 | OK | 31.273 | 62.55 | 262144 | True | Gemma4ForConditionalGeneration | True |
| latest_comparators | google/gemma-4-31B | 5bbc2fb1c1 | False | 2026-03-12 | OK | 31.273 | 62.55 | 262144 | True | Gemma4ForConditionalGeneration | None |
| latest_comparators | google/gemma-4-26B-A4B-it | 4d7ae4984b | False | 2026-03-11 | OK | 25.806 | 51.61 | 262144 | True | Gemma4ForConditionalGeneration | True |
| latest_comparators | google/gemma-4-26B-A4B | 24548b62aa | False | 2026-03-12 | OK | 25.806 | 51.61 | 262144 | True | Gemma4ForConditionalGeneration | None |
| newer_candidates | aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B | a2390696bf | False | 2026-09-08 | OK | 32.913 | 65.83 | 262144 | False | NemotronHForCausalLM | True |
| newer_candidates | Qwen/Qwen3.8-Flash-Next | de4b8e4d43 | False | 2026-08-24 | OK | 180.0 | 360.0 | 262144 | True | Qwen4ExpForConditionalGeneration | True |
| newer_candidates | google/gemma-4-12B | 023679ed35 | False | 2026-05-23 | OK | 11.96 | 23.92 | 262144 | True | Gemma4UnifiedForConditionalGeneration | None |
| newer_candidates | google/diffusiongemma-26B-A4B-it | f7f5b7f5fa | False | 2026-06-09 | OK | 25.824 | 51.65 | 262144 | True | DiffusionGemmaForBlockDiffusion | True |
| probe_missing_base | GoToCompany/gemma3-27b-cpt-gotoai-v3 |  | 404_not_found |  | None | None | None | None | None | None | None |

## Datasets
| id | sha | gated | access README | files | notes |
|---|---|---|---|---|---|
| openlanguagedata/flores_plus | 1147e2dc59 | auto | OK | 505 | {"ind_Latn": true, "eng_Latn": true, "cultural_sensitivity_label": false, "id": true} |
| facebook/flores | 71abf77d8b | auto | OK | 1224 | {"ind_Latn": true, "eng_Latn": true, "cultural_sensitivity_label": false, "id": true} |
| haryoaw/COPAL | e5c834d171 | False | OK | 4 | "" |
| CohereLabs/Global-MMLU | 0e619dbeb3 | False | OK | 87 | {"ind_Latn": false, "eng_Latn": false, "cultural_sensitivity_label": true, "id": true} |
| indolem/IndoMMLU | df6d6d348d | False | OK | 4 | "" |
| indolem/IndoCulture | d5f33af62c | False | OK | 3 | "" |

## Findings
- Gemma 3 27B IT: google/gemma-3-27b-it is gated=manual; this token returns 403 (license not accepted), so config and params are unverified.
- GoTo repo: GoToCompany/gemma3-27b-cpt-gotoai-v3-instruct exists but was created 2025-12-03, not 2026-10-19. Base GoToCompany/gemma3-27b-cpt-gotoai-v3 is 404 (not found).
- GotoAI-Inc org (different org) has 2026-08 quantized repos: gemma-4-31B-it-W8A16/W4A16, gemma-4-26B-A4B-it-W4A16, gemma-4-12B-it-W4A16, Qwen3.6-27B-W8A16/W4A16, Qwen3.8-27B-W8A16/W4A16. These are quants, not CPT models.
- Qwen official: Qwen/Qwen3.6-27B (2026-04-21) and Qwen/Qwen3.8-27B (2026-08-05, newest dense ~27B). Qwen3.8-27B-FP8 (2026-08-13) is a quant. Qwen3.8-Flash-Next (2026-08-24) is arch Qwen4ExpForConditionalGeneration, ~180B, out of scope. Qwen3.8-2.4T-A95B out of scope. No Qwen3.9/Qwen4 dense <=70B found in newest 30 by Qwen author.
- Google: no Gemma 4.x or Gemma 5 found in newest 30. Newest LLM-ish repos: gemma-4-12B (2026-05-23, arch Gemma4UnifiedForConditionalGeneration, 12B), diffusiongemma-26B-A4B-it (2026-06-09, diffusion arch), QAT variants (2026-06).
- aisingapore: Nemotron-SEA-LION-v4.8 (2026-09-08 to 2026-09-16): 30B-A3B (32.9B, NemotronH arch, not Gemma/Qwen-based) and 120B-A12B (out of scope). No v4.8 Gemma or Qwen variant found. Gemma-SEA-LION-Guard-v2 E2B/E4B/31B (Oct 2026) are safety classifiers, not general LLMs.
- aisingapore/Gemma-SEA-LION-v4.5-E2B-IT (2026-05-18) exists. aisingapore/Gemma-SEA-LION-v4.5-E2B (base) is 404. Riyan200324200324 GGUF is community, not official.
- Sahabat-AI / GoToCompany: no newer official release since 2025-05-30 (Sahabat-AI) and 2025-12-03 (GoTo). Newer Sahabat-named repos in 2026 are community GGUF/mlx conversions of 70B and 8B/9B models.
- Qwen-SEA-LION-v4.5-27B-IT has the same architecture and size as Qwen3.6-27B. Base lineage is not confirmed by config alone.

## Datasets detail
- FLORES: openlanguagedata/flores_plus (237 configs, ind_Latn and eng_Latn present) and facebook/flores (611 configs, ind_Latn and eng_Latn present); both gated=auto, README OK.
- CohereLabs/Global-MMLU: has config `id`; cultural_sensitivity_label feature NOT declared in README YAML, so unverified (needs a data-file read).
- haryoaw/COPAL, indolem/IndoMMLU, indolem/IndoCulture: all readable, gated=False.
