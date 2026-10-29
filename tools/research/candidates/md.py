import json,sys
SP=sys.argv[1]
c=json.load(open(SP+"/candidates.json"))["candidates"]
def row(r):
    g=r["gated"]; acc=("open" if g is False else f"gated={g}")+("" if r["config_readable_with_token"] else ", cfg 403")
    ta=f'{r["total_b"]}/{r["active_b"]}' if r["total_b"] else "?/?"
    if r["kind"]=="MoE": ta+=f' ({r["active_src"]})'
    kind=r["kind"]+(f' {r["num_experts"]}e top{r["topk"]}' + (f'+{r["shared_experts"]}sh' if r["shared_experts"] else "") if r["kind"]=="MoE" else "")
    return f'| {r["repo"]} | {r["sha"][:8]} | {r["created_at"]} | {acc} | {kind} | {ta} | {r["bf16_gb"]} | {(r["architectures"] or ["?"])[0]} | {"MM" if r["multimodal"] else "text"} | {r["thinking_toggle"]} | {r["license"]} | {", ".join(r["base_model_meta"]) or "-"} | {r["id_claimed"]} ({r["id_evidence"]}) | {r.get("note","")} |'
H="| repo | sha | created | access | dense/MoE | total/active B | bf16 GB | arch | modality | thinking toggle | license | base_model (meta) | ID/SEA claimed | note |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
L=["# Candidate open-weight instruct LLMs for indobench (1B-40B total params)","",
"As of 2026-10-28. Verified live against HF Hub: model_info (sha, created_at, gated, safetensors, cardData), raw config.json at the pinned sha, raw README. 64 repos fetched, 0 weights downloaded. Models already in configs/models.yaml are NOT listed.",
"Conventions: total B = sum of safetensors dtype counts; bf16 GB = 2 x total (weights only); active B for MoE: 'card' = read from model card, 'name' = from A<N>B in repo name (unverified), experts/top-k from config.json. created = repo creation date (not last update). 'cfg 403' = this token cannot read config.json (license not accepted); metadata came from the API only. ID claim: yes = card/metadata names Indonesian or 'id'; generic = N-language claim without naming ID; no = language list present without ID; unknown = nothing.","",
"Legacy flags: Llama-3/3.1, Gemma-2, Aya Expanse, Yi-1.5, SeaLLMs-v3, Cendol are 2023-2024 releases, kept only as pair bases or SEA/ID references.",""]
for g,t in [("general","General (non-Chinese labs)"),("chinese","Chinese labs"),("regional","Regional SEA / Indonesian")]:
    L+=[f"## {t}","",H]+[row(r) for r in c if r["group"]==g]+[""]
ex=json.load(open(SP+"/candidates.json"))
L+=["## Pair-base references (verified extra)","","| repo | sha | created | total B | license |","|---|---|---|---|---|"]
for k,v in ex["extra_pair_bases"].items(): L.append(f'| {k} | {v["sha"][:8]} | {v["created"]} | {v["total_b"]} | {v["license"]} |')
L+=["","## Proposed base-vs-regional pairs","",
"| regional | base instruct (available) | link evidence | strength |","|---|---|---|---|",
"| aisingapore/Apertus-SEA-LION-v4-8B-IT | swiss-ai/Apertus-8B-Instruct-2509 | cardData base_model = exactly this repo; both 8.05B BF16, ungated | STRONG (metadata) |",
"| aisingapore/Qwen-SEA-LION-v4-32B-IT | Qwen/Qwen3-32B | cardData base_model = Qwen/Qwen3-32B; 32.76B both; both enable_thinking | STRONG (metadata) |",
"| aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B | nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | metadata base = ...-A3B-Base; that Base's card cites NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16; same NemotronH MoE (128e top6); totals 32.91 vs 31.58 | MEDIUM (card chain; IT recipe differs) |",
"| aisingapore/Gemma-SEA-LION-v4-27B-IT | google/gemma-3-27b-it (already in matrix) | card links gemma-3-27b-it; metadata base is the CPT Gemma-SEA-LION-v4-27B | MEDIUM; second regional derivative of the matrix's Gemma 3 base |",
"| aisingapore/Gemma-SEA-LION-v3-9B-IT AND GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct | google/gemma-2-9b-it (gated manual) | both cards say CPT on Gemma2-9B base | MEDIUM; two regional CPTs on one base (2024) |",
"| GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct | meta-llama/Meta-Llama-3-8B-Instruct (gated manual) | card: continued pre-trained Llama3 8B | MEDIUM (2024) |",
"| aisingapore/Llama-SEA-LION-v3.5-8B-R | meta-llama/Llama-3.1-8B-Instruct (gated manual) | metadata base = Llama-SEA-LION-v3-8B-IT, itself CPT of Llama-3.1-8B (chain, not fetched) | WEAK-MEDIUM (2025-04, R = reasoning, thinking_mode on by default) |",
"| sail/Sailor2-14B-Chat / Sailor2-8B-Chat | Qwen/Qwen2.5-14B-Instruct / Qwen2.5-7B-Instruct | Sailor2 card: built on Qwen2.5 base models; metadata base = sail/Sailor2-XB (CPT base); Sailor2-20B-Chat base size match unverified | MEDIUM (2024-12/2025-02) |",
"| SeaLLMs/SeaLLMs-v3-7B-Chat | Qwen/Qwen2-7B-Instruct | arch Qwen2ForCausalLM, 7.62B equal; card lineage NOT confirmed in this run | WEAK (2024-07) |",
"| (non-regional) nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16 | google/gemma-4-E4B-it | metadata base_model = google/gemma-4-E4B-it; NVIDIA post-train, 'id' in language metadata | STRONG (general derivative) |","",
"Not pairable: Cendol (Llama-2 era), Yellow-AI-NLP/komodo-7b-base (base only, no instruct), CohereLabs tiny-aya-earth/fire/water regional siblings of tiny-aya-global (not fetched; gated).","",
"## Labs with no qualifying model in 1B-40B (checked via author listing)",""]
for k,v in ex["no_qualifying_models"].items(): L.append(f"- {k}: {v}")
L+=["","## Caveats","- Active params for MoE: 'card' rows read from README text; 'name' rows are inferred from A<N>B and unverified; GLM-4.7-Flash README grep found no active figure.",
"- Thinking-toggle column comes from regex on the chat template in tokenizer_config / chat_template.jinja; Mistral-Small-3.2, Tiny Aya (gated), Gemma-2/Llama (gated) not readable; Seed-OSS and Hunyuan are from card knowledge.",
"- ID/SEA claim is a text grep of the card; a 'generic' or 'unknown' entry does not mean the model cannot do Indonesian.",
"- Nothing was loaded in vLLM; architecture support for Gemma4Unified (gemma-4-12B-it), Glm4MoeLite, BailingMoeV3, Apriel2 etc. in the pinned vllm is unchecked.",
"- Listing used last-created ordering with limits 400/author; very old but relevant repos beyond that window could be missed (checked: Llama-3, Gemma-2, Aya, Yi, Sailor, SeaLLMs, Cendol found via listings)."]
open(SP+"/notes_candidates.md","w").write("\n".join(L)+"\n")
