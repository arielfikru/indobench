import json,sys
SP=sys.argv[1]
d=json.load(open(SP+"/c2/detail.json")); p2=json.load(open(SP+"/c2/pass2.json")); p3=json.load(open(SP+"/c2/p3.json"))
# active params (B): value, source
ACT={"openai/gpt-oss-20b":(3.6,"card"),
"nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16":(3.5,"card"),"nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16":(3.0,"card"),
"LiquidAI/LFM2.5-24B-A2B":(2.0,"card"),"LiquidAI/LFM2.5-8B-A1B":(1.5,"card"),"Qwen/Qwen3.6-35B-A3B":(3.0,"card"),
"zai-org/GLM-4.7-Flash":(3.0,"name/unverified (card grep found nothing)"),"moonshotai/Moonlight-16B-A3B-Instruct":(3.0,"name (card table 2.81?)"),
"baidu/ERNIE-4.5-21B-A3B-PT":(3.0,"card"),"inclusionAI/Ling-mini-2.0":(1.4,"card"),"inclusionAI/Ling-3.0-tiny":(1.3,"card"),
"aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B":(3.0,"name; same arch as Nemotron-3.5-Lightning")}
THINK={ # toggle in chat template (verified by regex on template unless noted)
"meta-llama/Llama-3.1-8B-Instruct":"none","meta-llama/Meta-Llama-3-8B-Instruct":"none",
"mistralai/Ministral-3-14B-Instruct-2512-BF16":"none (separate Reasoning repo)","mistralai/Ministral-3-8B-Instruct-2512-BF16":"none (separate Reasoning repo)",
"mistralai/Mistral-Small-3.2-24B-Instruct-2506":"unknown (template not in tokenizer_config; Mistral format)",
"microsoft/phi-4":"none","microsoft/Phi-4-mini-instruct":"none","openai/gpt-oss-20b":"reasoning_effort low/med/high only; cannot be turned off",
"allenai/Olmo-3.1-32B-Instruct":"none","allenai/Olmo-3-7B-Instruct":"none",
"ibm-granite/granite-4.2-30b":"enable_thinking","ibm-granite/granite-4.2-8b":"enable_thinking",
"HuggingFaceTB/SmolLM3-3B":"enable_thinking (+ /no_think)","CohereLabs/tiny-aya-global":"none seen in metadata (template not read: repo gated)",
"CohereLabs/aya-expanse-8b":"none (older)","CohereLabs/aya-expanse-32b":"none (older)",
"tiiuae/Falcon-H1-34B-Instruct":"none","tiiuae/Falcon-H1-7B-Instruct":"none",
"nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16":"enable_thinking","nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16":"enable_thinking","nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16":"enable_thinking",
"LGAI-EXAONE/EXAONE-4.0.1-32B":"enable_thinking","swiss-ai/Apertus-8B-Instruct-2509":"enable_thinking",
"LiquidAI/LFM2.5-24B-A2B":"reasoning-by-default model; no off switch found","LiquidAI/LFM2.5-8B-A1B":"reasoning-by-default model; no off switch found",
"ServiceNow-AI/SuperApriel-15B-Instruct":"unknown","google/gemma-4-E4B-it":"enable_thinking","google/gemma-4-12B-it":"enable_thinking",
"google/gemma-2-9b-it":"none","Qwen/Qwen3.6-35B-A3B":"enable_thinking","Qwen/Qwen3.5-9B":"enable_thinking","Qwen/Qwen3-32B":"enable_thinking",
"deepseek-ai/DeepSeek-R1-0528-Qwen3-8B":"reasoning-only (always thinks)","internlm/internlm3-8b-instruct":"none",
"zai-org/GLM-4.7-Flash":"enable_thinking","zai-org/GLM-4-32B-0414":"none","zai-org/GLM-4-9B-0414":"none",
"openbmb/MiniCPM5-2B":"enable_thinking","openbmb/MiniCPM4.1-8B":"enable_thinking",
"moonshotai/Moonlight-16B-A3B-Instruct":"none","baidu/ERNIE-4.5-21B-A3B-PT":"none (Thinking variant is separate repo)",
"tencent/Hunyuan-7B-Instruct":"unknown (card: /no_think prefix; not in template)","XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B":"enable_thinking",
"inclusionAI/Ling-mini-2.0":"none (non-reasoning; Ring-mini is the reasoning twin)","inclusionAI/Ling-3.0-tiny":"enable_thinking",
"ByteDance-Seed/Seed-OSS-36B-Instruct":"thinking_budget (card; 0 = off) not regex-verified","01-ai/Yi-1.5-34B-Chat":"none",
"aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B":"enable_thinking","aisingapore/Qwen-SEA-LION-v4-32B-IT":"enable_thinking",
"aisingapore/Gemma-SEA-LION-v4-27B-IT":"none","aisingapore/Apertus-SEA-LION-v4-8B-IT":"enable_thinking",
"aisingapore/Llama-SEA-LION-v3.5-8B-R":"thinking_mode (default on)","aisingapore/Gemma-SEA-LION-v3-9B-IT":"none"}
for k in d:
    pass
ID={ # id claim: (yes/no/generic/unknown, evidence)
"meta-llama/Llama-3.1-8B-Instruct":("no","8 official langs, no id"),"meta-llama/Meta-Llama-3-8B-Instruct":("no","en only"),
"mistralai/Ministral-3-14B-Instruct-2512-BF16":("no","dozens of langs listed; id not among them"),"mistralai/Ministral-3-8B-Instruct-2512-BF16":("no","same"),
"mistralai/Mistral-Small-3.2-24B-Instruct-2506":("yes","'id' in card language metadata"),
"microsoft/phi-4":("no","card: not intended for multilingual use"),"microsoft/Phi-4-mini-instruct":("no","language list excludes id"),
"openai/gpt-oss-20b":("unknown","no language list"),"allenai/Olmo-3.1-32B-Instruct":("no","en"),"allenai/Olmo-3-7B-Instruct":("no","en"),
"ibm-granite/granite-4.2-30b":("no","12-language list excludes id"),"ibm-granite/granite-4.2-8b":("no","12-language list excludes id"),
"HuggingFaceTB/SmolLM3-3B":("no","6 langs, no id"),"CohereLabs/tiny-aya-global":("yes","'id' in card language metadata (70-lang family)"),
"CohereLabs/aya-expanse-8b":("yes","'id' in language metadata (23 langs)"),"CohereLabs/aya-expanse-32b":("yes","'id' in language metadata"),
"tiiuae/Falcon-H1-34B-Instruct":("no","language metadata excludes id"),"tiiuae/Falcon-H1-7B-Instruct":("no","language metadata excludes id"),
"nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16":("no","en es fr de ja it"),"nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16":("no","en es fr de it ja"),
"nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16":("yes","'id' in language metadata (inherits Gemma 4)"),
"LGAI-EXAONE/EXAONE-4.0.1-32B":("no","en ko es"),"swiss-ai/Apertus-8B-Instruct-2509":("unknown","generic multilingual, ID not named in grep"),
"LiquidAI/LFM2.5-24B-A2B":("yes","card lists Indonesian"),"LiquidAI/LFM2.5-8B-A1B":("no","language list excludes id"),
"ServiceNow-AI/SuperApriel-15B-Instruct":("unknown","no language info"),"google/gemma-4-E4B-it":("generic","140+ languages, ID not named"),
"google/gemma-4-12B-it":("generic","140+ languages, ID not named"),"google/gemma-2-9b-it":("unknown","card not readable (gated)"),
"Qwen/Qwen3.6-35B-A3B":("generic","201 languages claimed, ID not named in card text"),"Qwen/Qwen3.5-9B":("generic","201 languages, ID not named"),
"Qwen/Qwen3-32B":("generic","100+ languages, ID not named"),"deepseek-ai/DeepSeek-R1-0528-Qwen3-8B":("unknown","none"),
"internlm/internlm3-8b-instruct":("unknown","none"),"zai-org/GLM-4.7-Flash":("no","en zh"),"zai-org/GLM-4-32B-0414":("no","zh en"),"zai-org/GLM-4-9B-0414":("no","zh en"),
"openbmb/MiniCPM5-2B":("no","en zh"),"openbmb/MiniCPM4.1-8B":("no","zh en"),"moonshotai/Moonlight-16B-A3B-Instruct":("unknown","none"),
"baidu/ERNIE-4.5-21B-A3B-PT":("no","en zh"),"tencent/Hunyuan-7B-Instruct":("unknown","none"),"XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B":("unknown","none (inherits Qwen3.5 generic)"),
"inclusionAI/Ling-mini-2.0":("unknown","none"),"inclusionAI/Ling-3.0-tiny":("unknown","none"),"ByteDance-Seed/Seed-OSS-36B-Instruct":("unknown","multilingual benchmarks only"),
"01-ai/Yi-1.5-34B-Chat":("unknown","none")}
LIC_NOTE={"Qwen/Qwen3.6-35B-A3B":"","LGAI-EXAONE/EXAONE-4.0.1-32B":"EXAONE license (non-commercial)","CohereLabs/tiny-aya-global":"CC-BY-NC","tiiuae/Falcon-H1-34B-Instruct":"Falcon-LLM license"}
out=[]
for r in d:
    repo=r["repo"]; o=p2[repo]
    dt=r["dtypes"]; tot=round(sum(dt.values()),2) if sum(dt.values())>0 else r["total_b"]
    rec={"group":r["group"],"repo":repo,"sha":r["sha"],"created_at":r["created_at"],"gated":r["gated"],
     "config_readable_with_token":r["config_readable"],"config_http":r.get("config_http"),
     "total_b":tot,"dtypes_b":dt,"bf16_gb":round(tot*2,1) if tot else None,
     "kind":"MoE" if r.get("is_moe") else "dense","num_experts":r.get("num_experts"),"topk":r.get("topk"),"shared_experts":r.get("shared_experts"),
     "architectures":r.get("architectures"),"model_type":r.get("model_type"),"pipeline_tag":r["pipeline_tag"],
     "multimodal":bool(r["pipeline_tag"] in ("image-text-to-text","any-to-any") or r.get("multimodal_cfg") or (r.get("architectures") or [""])[0].endswith("ConditionalGeneration")),
     "license":r["license"],"base_model_meta":r["base_model"],"card_languages":r["card_languages"],
     "native_quant":r.get("quant_cfg"),"thinking_toggle":THINK.get(repo,"unknown")}
    if r.get("is_moe"):
        a=ACT.get(repo); rec["active_b"]=a[0] if a else None; rec["active_src"]=a[1] if a else "unknown"
    else: rec["active_b"]=tot; rec["active_src"]="dense"
    if r["group"]=="regional":
        rec["id_claimed"]="yes"; rec["id_evidence"]="SEA/ID-targeted model; 'id' in card language metadata" if r["id_in_lang_meta"] else "regional model; card text"
    else:
        c,e=ID.get(repo,("unknown",""))
        rec["id_claimed"]=c; rec["id_evidence"]=e
    rec["id_snippet"]=r.get("id_snippet")
    out.append(rec)
# manual fixes
for rec in out:
    if rec["repo"]=="openai/gpt-oss-20b": rec["total_b"]=21.0; rec["bf16_gb"]=42.0; rec["note"]="native MXFP4 experts (~13 GB on disk); safetensors count is packed U8 (20.9); bf16_gb is an upcast estimate from card's 21B"
    if rec["repo"]=="ServiceNow-AI/SuperApriel-15B-Instruct": rec["total_b"]=None; rec["bf16_gb"]=None; rec["note"]="no safetensors metadata; ~15B by name only"
    if rec["repo"]=="indonlp/cendol-llama2-13b-merged-chat": rec["note"]="weights stored FP32 (52 GB on disk); no chat_template (custom prompt format); Llama-2 era (Dec 2023)"
    if rec["repo"].startswith("google/gemma-4-E4B"): rec["note"]="E4B = ~4B effective; 8.0B total incl. per-layer embeddings"
    if rec["repo"]=="nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16": rec["note"]="model_info.total=31.58 vs file-level metadata 32.91; used 32.91 (get_safetensors_metadata)"
    if rec["repo"].startswith("Sahabat-AI/"): rec["note"]="same weights family as GoToCompany/ twin (different sha, re-upload 2025-05-30); treat as duplicate"
    if rec["repo"].startswith("mistralai/Ministral-3"): rec["note"]="BF16 repo used (plain Instruct-2512 repo ships FP8); multimodal (Pixtral-style vision tower)"
    if rec["repo"] in ("meta-llama/Llama-3.1-8B-Instruct","meta-llama/Meta-Llama-3-8B-Instruct","google/gemma-2-9b-it","CohereLabs/tiny-aya-global","CohereLabs/aya-expanse-8b","CohereLabs/aya-expanse-32b"): rec["note"]=(rec.get("note","")+" config.json returned 403 with current token: accept license on HF first (info from API metadata only)").strip()
    if rec["repo"]=="aisingapore/Gemma-SEA-LION-v4-27B-IT": rec["note"]="metadata base_model = Gemma-SEA-LION-v4-27B (CPT); card links gemma-3-27b-it as upstream"
    if rec["repo"]=="aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B": rec["note"]="metadata base_model = ...-30B-A3B-Base, which per its card is built on NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16; file metadata total 32.91 (Nano-3 IT 31.58)"
    if rec["repo"]=="tencent/Hunyuan-7B-Instruct": rec["note"]="license field missing in metadata (Tencent Hunyuan community license)"
    if rec["repo"]=="01-ai/Yi-1.5-34B-Chat": rec["note"]="2024 release; last Yi chat model"
    if rec["repo"]=="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B": rec["note"]="reasoning-only distill (Qwen3-8B base); DeepSeek proper chat models are >40B"
json.dump({"as_of":"2026-10-28","method":"HfApi.list_models(author) x42 + model_info(expand)+raw config.json+raw README per shortlisted repo (62 repos); total_b = sum of safetensors dtype counts; bf16_gb = 2*total",
 "extra_pair_bases":p3,"no_qualifying_models":{"stepfun-ai":"only Step-3.5/3.7-Flash (200B), VL/audio/prover models","Skywork":"only OR1/R1V reasoning, SWE-32B, image/video models; MindLink-32B-0801 not fetched","baichuan-inc":"only Baichuan-M1-14B/M2-32B (medical)","MiniMaxAI":"M-series 220B+, H3 is video","meituan-longcat":"LongCat-Flash-Lite 69B is smallest LLM","Yellow-AI-NLP":"only komodo-7b-base (gated, base, no instruct)","THUDM":"no repos under this author (moved to zai-org)","deepseek-ai":"only R1 distills in range; V4-Flash 291B+","moonshotai":"Kimi-Linear-48B-A3B out of range; Kimi-VL-A3B 16B is VLM","tencent":"Hy-* 2026 repos are research/utility; Hunyuan-A13B 80B","internlm":"internlm3-8b-instruct (2025-01); Intern-S1-mini/S2-Preview are multimodal science models","meta-llama":"no new text <40B since Llama-3.2 (2024); Llama-4 Scout 109B"},
 "candidates":out},open(SP+"/candidates.json","w"),indent=1)
print(len(out))
