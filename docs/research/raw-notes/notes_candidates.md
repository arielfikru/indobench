# Candidate open-weight instruct LLMs for indobench (1B-40B total params)

As of 2026-10-28. Verified live against HF Hub: model_info (sha, created_at, gated, safetensors, cardData), raw config.json at the pinned sha, raw README. 64 repos fetched, 0 weights downloaded. Models already in configs/models.yaml are NOT listed.
Conventions: total B = sum of safetensors dtype counts; bf16 GB = 2 x total (weights only); active B for MoE: 'card' = read from model card, 'name' = from A<N>B in repo name (unverified), experts/top-k from config.json. created = repo creation date (not last update). 'cfg 403' = this token cannot read config.json (license not accepted); metadata came from the API only. ID claim: yes = card/metadata names Indonesian or 'id'; generic = N-language claim without naming ID; no = language list present without ID; unknown = nothing.

Legacy flags: Llama-3/3.1, Gemma-2, Aya Expanse, Yi-1.5, SeaLLMs-v3, Cendol are 2023-2024 releases, kept only as pair bases or SEA/ID references.

## General (non-Chinese labs)

| repo | sha | created | access | dense/MoE | total/active B | bf16 GB | arch | modality | thinking toggle | license | base_model (meta) | ID/SEA claimed | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| meta-llama/Llama-3.1-8B-Instruct | 0e9e39f2 | 2024-07-18 | gated=manual, cfg 403 | dense | 8.03/8.03 | 16.1 | LlamaForCausalLM | text | none | llama3.1 | meta-llama/Meta-Llama-3.1-8B | no (8 official langs, no id) | config.json returned 403 with current token: accept license on HF first (info from API metadata only) |
| meta-llama/Meta-Llama-3-8B-Instruct | 8afb486c | 2024-04-17 | gated=manual, cfg 403 | dense | 8.03/8.03 | 16.1 | LlamaForCausalLM | text | none | llama3 | - | no (en only) | config.json returned 403 with current token: accept license on HF first (info from API metadata only) |
| mistralai/Ministral-3-14B-Instruct-2512-BF16 | 3cea74c1 | 2025-10-31 | open | dense | 13.95/13.95 | 27.9 | Mistral3ForConditionalGeneration | MM | none (separate Reasoning repo) | apache-2.0 | mistralai/Ministral-3-14B-Base-2512 | no (dozens of langs listed; id not among them) | BF16 repo used (plain Instruct-2512 repo ships FP8); multimodal (Pixtral-style vision tower) |
| mistralai/Ministral-3-8B-Instruct-2512-BF16 | f6fae979 | 2025-10-31 | open | dense | 8.92/8.92 | 17.8 | Mistral3ForConditionalGeneration | MM | none (separate Reasoning repo) | apache-2.0 | mistralai/Ministral-3-8B-Base-2512 | no (same) | BF16 repo used (plain Instruct-2512 repo ships FP8); multimodal (Pixtral-style vision tower) |
| mistralai/Mistral-Small-3.2-24B-Instruct-2506 | 95a6d26c | 2025-06-19 | open | dense | 24.01/24.01 | 48.0 | Mistral3ForConditionalGeneration | MM | unknown (template not in tokenizer_config; Mistral format) | apache-2.0 | mistralai/Mistral-Small-3.1-24B-Base-2503 | yes ('id' in card language metadata) |  |
| microsoft/phi-4 | 2db69c1c | 2024-12-11 | open | dense | 14.66/14.66 | 29.3 | Phi3ForCausalLM | text | none | mit | - | no (card: not intended for multilingual use) |  |
| microsoft/Phi-4-mini-instruct | cfbefacb | 2025-02-19 | open | dense | 3.84/3.84 | 7.7 | Phi3ForCausalLM | text | none | mit | - | no (language list excludes id) |  |
| openai/gpt-oss-20b | 6cee5e81 | 2025-08-04 | open | MoE 32e top4 | 21.0/3.6 (card) | 42.0 | GptOssForCausalLM | text | reasoning_effort low/med/high only; cannot be turned off | apache-2.0 | - | unknown (no language list) | native MXFP4 experts (~13 GB on disk); safetensors count is packed U8 (20.9); bf16_gb is an upcast estimate from card's 21B |
| allenai/Olmo-3.1-32B-Instruct | ac0587e4 | 2025-12-10 | open | dense | 32.23/32.23 | 64.5 | Olmo3ForCausalLM | text | none | apache-2.0 | allenai/Olmo-3.1-32B-Instruct-DPO | no (en) |  |
| allenai/Olmo-3-7B-Instruct | 6e5971d9 | 2025-11-19 | open | dense | 7.3/7.3 | 14.6 | Olmo3ForCausalLM | text | none | apache-2.0 | allenai/Olmo-3-7B-Instruct-DPO | no (en) |  |
| ibm-granite/granite-4.2-30b | 9e668ce1 | 2026-08-07 | open | dense | 29.28/29.28 | 58.6 | GraniteForCausalLM | text | enable_thinking | apache-2.0 | ibm-granite/granite-4.1-30b-base | no (12-language list excludes id) |  |
| ibm-granite/granite-4.2-8b | a7042144 | 2026-08-07 | open | dense | 8.79/8.79 | 17.6 | GraniteForCausalLM | text | enable_thinking | apache-2.0 | ibm-granite/granite-4.1-8b-base | no (12-language list excludes id) |  |
| HuggingFaceTB/SmolLM3-3B | a07cc9a0 | 2025-07-08 | open | dense | 3.08/3.08 | 6.2 | SmolLM3ForCausalLM | text | enable_thinking (+ /no_think) | apache-2.0 | HuggingFaceTB/SmolLM3-3B-Base | no (6 langs, no id) |  |
| CohereLabs/tiny-aya-global | af89d219 | 2026-02-13 | gated=auto, cfg 403 | dense | 3.35/3.35 | 6.7 | Cohere2ForCausalLM | text | none seen in metadata (template not read: repo gated) | cc-by-nc-4.0 | CohereLabs/tiny-aya-base | yes ('id' in card language metadata (70-lang family)) | config.json returned 403 with current token: accept license on HF first (info from API metadata only) |
| CohereLabs/aya-expanse-8b | 5062468b | 2024-10-23 | gated=auto, cfg 403 | dense | 8.03/8.03 | 16.1 | CohereForCausalLM | text | none (older) | cc-by-nc-4.0 | - | yes ('id' in language metadata (23 langs)) | config.json returned 403 with current token: accept license on HF first (info from API metadata only) |
| CohereLabs/aya-expanse-32b | b306ea27 | 2024-10-23 | gated=auto, cfg 403 | dense | 32.3/32.3 | 64.6 | CohereForCausalLM | text | none (older) | cc-by-nc-4.0 | - | yes ('id' in language metadata) | config.json returned 403 with current token: accept license on HF first (info from API metadata only) |
| tiiuae/Falcon-H1-34B-Instruct | 6e6890e2 | 2025-05-01 | open | dense | 33.64/33.64 | 67.3 | FalconH1ForCausalLM | text | none | other | tiiuae/Falcon-H1-34B-Base | no (language metadata excludes id) |  |
| tiiuae/Falcon-H1-7B-Instruct | 41e72f27 | 2025-05-01 | open | dense | 7.59/7.59 | 15.2 | FalconH1ForCausalLM | text | none | other | tiiuae/Falcon-H1-7B-Base | no (language metadata excludes id) |  |
| nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | bf77c317 | 2025-12-04 | open | MoE 128e top6+1sh | 31.58/3.5 (card) | 63.2 | NemotronHForCausalLM | text | enable_thinking | other | - | no (en es fr de ja it) |  |
| nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | a9904d24 | 2026-08-01 | open | MoE 128e top6+1sh | 32.91/3.0 (card) | 65.8 | NemotronHForCausalLM | text | enable_thinking | other | - | no (en es fr de it ja) | model_info.total=31.58 vs file-level metadata 32.91; used 32.91 (get_safetensors_metadata) |
| nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16 | 49843eed | 2026-10-05 | open | dense | 8.0/8.0 | 16.0 | Gemma4ForConditionalGeneration | MM | enable_thinking | other | google/gemma-4-E4B-it | yes ('id' in language metadata (inherits Gemma 4)) |  |
| LGAI-EXAONE/EXAONE-4.0.1-32B | a6b0bd4b | 2025-07-29 | open | dense | 32.0/32.0 | 64.0 | Exaone4ForCausalLM | text | enable_thinking | other | LGAI-EXAONE/EXAONE-4.0-32B | no (en ko es) |  |
| swiss-ai/Apertus-8B-Instruct-2509 | b946d404 | 2025-08-13 | open | dense | 8.05/8.05 | 16.1 | ApertusForCausalLM | text | enable_thinking | apache-2.0 | swiss-ai/Apertus-8B-2509 | unknown (generic multilingual, ID not named in grep) |  |
| LiquidAI/LFM2.5-24B-A2B | 3fcfdbfa | 2026-10-12 | open | MoE 64e top4 | 23.97/2.0 (card) | 47.9 | Lfm2MoeForCausalLM | text | reasoning-by-default model; no off switch found | other | LiquidAI/LFM2.5-24B-A2B-Base | yes (card lists Indonesian) |  |
| LiquidAI/LFM2.5-8B-A1B | 5dd22602 | 2026-05-28 | open | MoE 32e top4 | 8.47/1.5 (card) | 16.9 | Lfm2MoeForCausalLM | text | reasoning-by-default model; no off switch found | other | LiquidAI/LFM2.5-8B-A1B-Base | no (language list excludes id) |  |
| ServiceNow-AI/SuperApriel-15B-Instruct | 7012e860 | 2026-04-07 | open | dense | ?/? | None | Apriel2ForConditionalGeneration | MM | unknown | mit | - | unknown (no language info) | no safetensors metadata; ~15B by name only |
| google/gemma-4-E4B-it | ee0ef602 | 2026-03-02 | open | dense | 8.0/8.0 | 16.0 | Gemma4ForConditionalGeneration | MM | enable_thinking | apache-2.0 | google/gemma-4-E4B | generic (140+ languages, ID not named) | E4B = ~4B effective; 8.0B total incl. per-layer embeddings |
| google/gemma-4-12B-it | 707f0a3b | 2026-05-23 | open | dense | 11.96/11.96 | 23.9 | Gemma4UnifiedForConditionalGeneration | MM | enable_thinking | apache-2.0 | google/gemma-4-12B | generic (140+ languages, ID not named) |  |
| google/gemma-2-9b-it | 11c9b309 | 2024-06-24 | gated=manual, cfg 403 | dense | 9.24/9.24 | 18.5 | Gemma2ForCausalLM | text | none | gemma | google/gemma-2-9b | unknown (card not readable (gated)) | config.json returned 403 with current token: accept license on HF first (info from API metadata only) |
| Qwen/Qwen3.6-35B-A3B | 995ad96e | 2026-04-15 | open | MoE 256e top8 | 35.95/3.0 (card) | 71.9 | Qwen3_5MoeForConditionalGeneration | MM | enable_thinking | apache-2.0 | - | generic (201 languages claimed, ID not named in card text) |  |
| Qwen/Qwen3.5-9B | c2022362 | 2026-02-27 | open | dense | 9.65/9.65 | 19.3 | Qwen3_5ForConditionalGeneration | MM | enable_thinking | apache-2.0 | Qwen/Qwen3.5-9B-Base | generic (201 languages, ID not named) |  |
| Qwen/Qwen3-32B | 9216db57 | 2025-04-27 | open | dense | 32.76/32.76 | 65.5 | Qwen3ForCausalLM | text | enable_thinking | apache-2.0 | - | generic (100+ languages, ID not named) |  |

## Chinese labs

| repo | sha | created | access | dense/MoE | total/active B | bf16 GB | arch | modality | thinking toggle | license | base_model (meta) | ID/SEA claimed | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-ai/DeepSeek-R1-0528-Qwen3-8B | 6e8885a6 | 2025-05-29 | open | dense | 8.19/8.19 | 16.4 | Qwen3ForCausalLM | text | reasoning-only (always thinks) | mit | - | unknown (none) | reasoning-only distill (Qwen3-8B base); DeepSeek proper chat models are >40B |
| internlm/internlm3-8b-instruct | 28c99415 | 2025-01-13 | open | dense | 8.8/8.8 | 17.6 | InternLM3ForCausalLM | text | none | apache-2.0 | - | unknown (none) |  |
| zai-org/GLM-4.7-Flash | 7dd20894 | 2026-01-19 | open | MoE 64e top4+1sh | 31.22/3.0 (name/unverified (card grep found nothing)) | 62.4 | Glm4MoeLiteForCausalLM | text | enable_thinking | mit | - | no (en zh) |  |
| zai-org/GLM-4-32B-0414 | 077b5c2f | 2025-04-07 | open | dense | 32.57/32.57 | 65.1 | Glm4ForCausalLM | text | none | mit | - | no (zh en) |  |
| zai-org/GLM-4-9B-0414 | 645b8482 | 2025-04-07 | open | dense | 9.4/9.4 | 18.8 | Glm4ForCausalLM | text | none | mit | - | no (zh en) |  |
| openbmb/MiniCPM5-2B | f9740005 | 2026-09-06 | open | dense | 2.52/2.52 | 5.0 | LlamaForCausalLM | text | enable_thinking | apache-2.0 | - | no (en zh) |  |
| openbmb/MiniCPM4.1-8B | 3a8dfed9 | 2025-09-02 | open | dense | 8.19/8.19 | 16.4 | MiniCPMForCausalLM | text | enable_thinking | apache-2.0 | - | no (zh en) |  |
| moonshotai/Moonlight-16B-A3B-Instruct | 4e735b07 | 2025-02-22 | open | MoE 64e top6+2sh | 15.96/3.0 (name (card table 2.81?)) | 31.9 | DeepseekV3ForCausalLM | text | none | mit | - | unknown (none) |  |
| baidu/ERNIE-4.5-21B-A3B-PT | 87db9548 | 2025-06-28 | open | MoE 64e top6+2sh | 21.94/3.0 (card) | 43.9 | Ernie4_5_MoeForCausalLM | text | none (Thinking variant is separate repo) | apache-2.0 | - | no (en zh) |  |
| tencent/Hunyuan-7B-Instruct | 6fd6ecb0 | 2025-07-30 | open | dense | 7.5/7.5 | 15.0 | HunYuanDenseV1ForCausalLM | text | unknown (card: /no_think prefix; not in template) | None | tencent/Hunyuan-7B-Pretrain | unknown (none) | license field missing in metadata (Tencent Hunyuan community license) |
| XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B | 1f09ddcc | 2026-09-21 | open | dense | 9.41/9.41 | 18.8 | Qwen3_5ForConditionalGeneration | MM | enable_thinking | mit | Qwen/Qwen3.5-9B | unknown (none (inherits Qwen3.5 generic)) |  |
| inclusionAI/Ling-mini-2.0 | a810f641 | 2025-09-08 | open | MoE 256e top8+1sh | 16.26/1.4 (card) | 32.5 | BailingMoeV2ForCausalLM | text | none (non-reasoning; Ring-mini is the reasoning twin) | mit | inclusionAI/Ling-mini-base-2.0 | unknown (none) |  |
| inclusionAI/Ling-3.0-tiny | 9a98e35f | 2026-08-10 | open | MoE 128e top8+1sh | 7.89/1.3 (card) | 15.8 | BailingMoeV3ForCausalLM | text | enable_thinking | mit | - | unknown (none) |  |
| ByteDance-Seed/Seed-OSS-36B-Instruct | 497f1dca | 2025-08-20 | open | dense | 36.15/36.15 | 72.3 | SeedOssForCausalLM | text | thinking_budget (card; 0 = off) not regex-verified | apache-2.0 | - | unknown (multilingual benchmarks only) |  |
| 01-ai/Yi-1.5-34B-Chat | fa4ffba1 | 2024-05-10 | open | dense | 34.39/34.39 | 68.8 | LlamaForCausalLM | text | none | apache-2.0 | - | unknown (none) | 2024 release; last Yi chat model |

## Regional SEA / Indonesian

| repo | sha | created | access | dense/MoE | total/active B | bf16 GB | arch | modality | thinking toggle | license | base_model (meta) | ID/SEA claimed | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B | a2390696 | 2026-09-08 | open | MoE 128e top6+1sh | 32.91/3.0 (name; same arch as Nemotron-3.5-Lightning) | 65.8 | NemotronHForCausalLM | text | enable_thinking | mit | aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B-Base | yes (SEA/ID-targeted model; 'id' in card language metadata) | metadata base_model = ...-30B-A3B-Base, which per its card is built on NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16; file metadata total 32.91 (Nano-3 IT 31.58) |
| aisingapore/Qwen-SEA-LION-v4-32B-IT | f1169f46 | 2025-10-16 | open | dense | 32.76/32.76 | 65.5 | Qwen3ForCausalLM | text | enable_thinking | mit | Qwen/Qwen3-32B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| aisingapore/Gemma-SEA-LION-v4-27B-IT | c41c2915 | 2025-08-11 | open | dense | 27.43/27.43 | 54.9 | Gemma3ForConditionalGeneration | MM | none | gemma | aisingapore/Gemma-SEA-LION-v4-27B | yes (SEA/ID-targeted model; 'id' in card language metadata) | metadata base_model = Gemma-SEA-LION-v4-27B (CPT); card links gemma-3-27b-it as upstream |
| aisingapore/Apertus-SEA-LION-v4-8B-IT | 3cb02025 | 2026-02-05 | open | dense | 8.05/8.05 | 16.1 | ApertusForCausalLM | text | enable_thinking | mit | swiss-ai/Apertus-8B-Instruct-2509 | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| aisingapore/Llama-SEA-LION-v3.5-8B-R | dfdbc9bd | 2025-04-13 | open | dense | 8.03/8.03 | 16.1 | LlamaForCausalLM | text | thinking_mode (default on) | llama3.1 | aisingapore/Llama-SEA-LION-v3-8B-IT | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| aisingapore/Gemma-SEA-LION-v3-9B-IT | 25fc0cd6 | 2024-10-30 | open | dense | 9.24/9.24 | 18.5 | Gemma2ForCausalLM | text | none | gemma | aisingapore/Gemma-SEA-LION-v3-9B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct | 20fd3cff | 2024-11-06 | open | dense | 8.03/8.03 | 16.1 | LlamaForCausalLM | text | unknown | llama3 | GoToCompany/llama3-8b-cpt-sahabatai-v1-base | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct | ca19cec8 | 2024-11-06 | open | dense | 9.24/9.24 | 18.5 | Gemma2ForCausalLM | text | unknown | gemma | GoToCompany/gemma2-9b-cpt-sahabatai-v1-base | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| Sahabat-AI/llama3-8b-cpt-sahabatai-v1-instruct | 579b7f73 | 2025-05-30 | open | dense | 8.03/8.03 | 16.1 | LlamaForCausalLM | text | unknown | llama3 | GoToCompany/llama3-8b-cpt-sahabatai-v1-base | yes (SEA/ID-targeted model; 'id' in card language metadata) | same weights family as GoToCompany/ twin (different sha, re-upload 2025-05-30); treat as duplicate |
| Sahabat-AI/gemma2-9b-cpt-sahabatai-v1-instruct | ecd7c80b | 2025-05-30 | open | dense | 9.24/9.24 | 18.5 | Gemma2ForCausalLM | text | unknown | gemma | GoToCompany/gemma2-9b-cpt-sahabatai-v1-base | yes (SEA/ID-targeted model; 'id' in card language metadata) | same weights family as GoToCompany/ twin (different sha, re-upload 2025-05-30); treat as duplicate |
| sail/Sailor2-20B-Chat | bca071eb | 2025-02-18 | open | dense | 19.17/19.17 | 38.3 | Qwen2ForCausalLM | text | unknown | apache-2.0 | sail/Sailor2-20B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| sail/Sailor2-14B-Chat | 81973021 | 2025-02-18 | open | dense | 14.44/14.44 | 28.9 | Qwen2ForCausalLM | text | unknown | apache-2.0 | sail/Sailor2-14B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| sail/Sailor2-8B-Chat | 577d5b27 | 2024-12-03 | open | dense | 8.55/8.55 | 17.1 | Qwen2ForCausalLM | text | unknown | apache-2.0 | sail/Sailor2-8B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| sail/Sailor2-L-8B-Chat | face9427 | 2025-02-18 | open | dense | 8.55/8.55 | 17.1 | Qwen2ForCausalLM | text | unknown | apache-2.0 | sail/Sailor2-L-8B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| sail/Sailor2-3B-Chat | d6072264 | 2025-02-18 | open | dense | 3.58/3.58 | 7.2 | Qwen2ForCausalLM | text | unknown | apache-2.0 | sail/Sailor2-3B | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| SeaLLMs/SeaLLMs-v3-7B-Chat | a9900348 | 2024-07-03 | open | dense | 7.62/7.62 | 15.2 | Qwen2ForCausalLM | text | unknown | other | - | yes (SEA/ID-targeted model; 'id' in card language metadata) |  |
| indonlp/cendol-llama2-13b-merged-chat | 1e1d8692 | 2023-12-25 | open | dense | 13.02/13.02 | 26.0 | LlamaForCausalLM | text | unknown | apache-2.0 | - | yes (SEA/ID-targeted model; 'id' in card language metadata) | weights stored FP32 (52 GB on disk); no chat_template (custom prompt format); Llama-2 era (Dec 2023) |

## Pair-base references (verified extra)

| repo | sha | created | total B | license |
|---|---|---|---|---|
| Qwen/Qwen2.5-7B-Instruct | a09a3545 | 2024-09-16 | 7.62 | apache-2.0 |
| Qwen/Qwen2.5-14B-Instruct | cf98f3b3 | 2024-09-16 | 14.77 | apache-2.0 |
| Qwen/Qwen2.5-32B-Instruct | 5ede1c97 | 2024-09-17 | 32.76 | apache-2.0 |
| Qwen/Qwen2-7B-Instruct | f2826a00 | 2024-06-04 | 7.62 | apache-2.0 |

## Proposed base-vs-regional pairs

| regional | base instruct (available) | link evidence | strength |
|---|---|---|---|
| aisingapore/Apertus-SEA-LION-v4-8B-IT | swiss-ai/Apertus-8B-Instruct-2509 | cardData base_model = exactly this repo; both 8.05B BF16, ungated | STRONG (metadata) |
| aisingapore/Qwen-SEA-LION-v4-32B-IT | Qwen/Qwen3-32B | cardData base_model = Qwen/Qwen3-32B; 32.76B both; both enable_thinking | STRONG (metadata) |
| aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B | nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | metadata base = ...-A3B-Base; that Base's card cites NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16; same NemotronH MoE (128e top6); totals 32.91 vs 31.58 | MEDIUM (card chain; IT recipe differs) |
| aisingapore/Gemma-SEA-LION-v4-27B-IT | google/gemma-3-27b-it (already in matrix) | card links gemma-3-27b-it; metadata base is the CPT Gemma-SEA-LION-v4-27B | MEDIUM; second regional derivative of the matrix's Gemma 3 base |
| aisingapore/Gemma-SEA-LION-v3-9B-IT AND GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct | google/gemma-2-9b-it (gated manual) | both cards say CPT on Gemma2-9B base | MEDIUM; two regional CPTs on one base (2024) |
| GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct | meta-llama/Meta-Llama-3-8B-Instruct (gated manual) | card: continued pre-trained Llama3 8B | MEDIUM (2024) |
| aisingapore/Llama-SEA-LION-v3.5-8B-R | meta-llama/Llama-3.1-8B-Instruct (gated manual) | metadata base = Llama-SEA-LION-v3-8B-IT, itself CPT of Llama-3.1-8B (chain, not fetched) | WEAK-MEDIUM (2025-04, R = reasoning, thinking_mode on by default) |
| sail/Sailor2-14B-Chat / Sailor2-8B-Chat | Qwen/Qwen2.5-14B-Instruct / Qwen2.5-7B-Instruct | Sailor2 card: built on Qwen2.5 base models; metadata base = sail/Sailor2-XB (CPT base); Sailor2-20B-Chat base size match unverified | MEDIUM (2024-12/2025-02) |
| SeaLLMs/SeaLLMs-v3-7B-Chat | Qwen/Qwen2-7B-Instruct | arch Qwen2ForCausalLM, 7.62B equal; card lineage NOT confirmed in this run | WEAK (2024-07) |
| (non-regional) nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16 | google/gemma-4-E4B-it | metadata base_model = google/gemma-4-E4B-it; NVIDIA post-train, 'id' in language metadata | STRONG (general derivative) |

Not pairable: Cendol (Llama-2 era), Yellow-AI-NLP/komodo-7b-base (base only, no instruct), CohereLabs tiny-aya-earth/fire/water regional siblings of tiny-aya-global (not fetched; gated).

## Labs with no qualifying model in 1B-40B (checked via author listing)

- stepfun-ai: only Step-3.5/3.7-Flash (200B), VL/audio/prover models
- Skywork: only OR1/R1V reasoning, SWE-32B, image/video models; MindLink-32B-0801 not fetched
- baichuan-inc: only Baichuan-M1-14B/M2-32B (medical)
- MiniMaxAI: M-series 220B+, H3 is video
- meituan-longcat: LongCat-Flash-Lite 69B is smallest LLM
- Yellow-AI-NLP: only komodo-7b-base (gated, base, no instruct)
- THUDM: no repos under this author (moved to zai-org)
- deepseek-ai: only R1 distills in range; V4-Flash 291B+
- moonshotai: Kimi-Linear-48B-A3B out of range; Kimi-VL-A3B 16B is VLM
- tencent: Hy-* 2026 repos are research/utility; Hunyuan-A13B 80B
- internlm: internlm3-8b-instruct (2025-01); Intern-S1-mini/S2-Preview are multimodal science models
- meta-llama: no new text <40B since Llama-3.2 (2024); Llama-4 Scout 109B

## Caveats
- Active params for MoE: 'card' rows read from README text; 'name' rows are inferred from A<N>B and unverified; GLM-4.7-Flash README grep found no active figure.
- Thinking-toggle column comes from regex on the chat template in tokenizer_config / chat_template.jinja; Mistral-Small-3.2, Tiny Aya (gated), Gemma-2/Llama (gated) not readable; Seed-OSS and Hunyuan are from card knowledge.
- ID/SEA claim is a text grep of the card; a 'generic' or 'unknown' entry does not mean the model cannot do Indonesian.
- Nothing was loaded in vLLM; architecture support for Gemma4Unified (gemma-4-12B-it), Glm4MoeLite, BailingMoeV3, Apriel2 etc. in the pinned vllm is unchecked.
- Listing used last-created ordering with limits 400/author; very old but relevant repos beyond that window could be missed (checked: Llama-3, Gemma-2, Aya, Yi, Sailor, SeaLLMs, Cendol found via listings).
