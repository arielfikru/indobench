import json, re, sys, time, os
import httpx
from huggingface_hub import HfApi, get_token
from huggingface_hub.errors import HfHubHTTPError, RepositoryNotFoundError
SP=sys.argv[1]
api=HfApi()
tok=get_token()
H={"Authorization":"Bearer "+tok} if tok else {}
cli=httpx.Client(follow_redirects=True,timeout=40,headers=H)
GROUPS={
"general":"""meta-llama/Llama-3.1-8B-Instruct meta-llama/Meta-Llama-3-8B-Instruct
mistralai/Ministral-3-14B-Instruct-2512-BF16 mistralai/Ministral-3-8B-Instruct-2512-BF16 mistralai/Mistral-Small-3.2-24B-Instruct-2506
microsoft/phi-4 microsoft/Phi-4-mini-instruct openai/gpt-oss-20b allenai/Olmo-3.1-32B-Instruct allenai/Olmo-3-7B-Instruct
ibm-granite/granite-4.2-30b ibm-granite/granite-4.2-8b HuggingFaceTB/SmolLM3-3B CohereLabs/tiny-aya-global CohereLabs/aya-expanse-8b CohereLabs/aya-expanse-32b
tiiuae/Falcon-H1-34B-Instruct tiiuae/Falcon-H1-7B-Instruct nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16
LGAI-EXAONE/EXAONE-4.0.1-32B swiss-ai/Apertus-8B-Instruct-2509 LiquidAI/LFM2.5-24B-A2B LiquidAI/LFM2.5-8B-A1B ServiceNow-AI/SuperApriel-15B-Instruct
google/gemma-4-E4B-it google/gemma-4-12B-it google/gemma-2-9b-it Qwen/Qwen3.6-35B-A3B Qwen/Qwen3.5-9B Qwen/Qwen3-32B""".split(),
"chinese":"""deepseek-ai/DeepSeek-R1-0528-Qwen3-8B internlm/internlm3-8b-instruct zai-org/GLM-4.7-Flash zai-org/GLM-4-32B-0414 zai-org/GLM-4-9B-0414
openbmb/MiniCPM5-2B openbmb/MiniCPM4.1-8B moonshotai/Moonlight-16B-A3B-Instruct baidu/ERNIE-4.5-21B-A3B-PT tencent/Hunyuan-7B-Instruct
XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B inclusionAI/Ling-mini-2.0 inclusionAI/Ling-3.0-tiny ByteDance-Seed/Seed-OSS-36B-Instruct 01-ai/Yi-1.5-34B-Chat""".split(),
"regional":"""aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B aisingapore/Qwen-SEA-LION-v4-32B-IT aisingapore/Gemma-SEA-LION-v4-27B-IT aisingapore/Apertus-SEA-LION-v4-8B-IT
aisingapore/Llama-SEA-LION-v3.5-8B-R aisingapore/Gemma-SEA-LION-v3-9B-IT GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct
Sahabat-AI/llama3-8b-cpt-sahabatai-v1-instruct Sahabat-AI/gemma2-9b-cpt-sahabatai-v1-instruct
sail/Sailor2-20B-Chat sail/Sailor2-14B-Chat sail/Sailor2-8B-Chat sail/Sailor2-L-8B-Chat sail/Sailor2-3B-Chat SeaLLMs/SeaLLMs-v3-7B-Chat indonlp/cendol-llama2-13b-merged-chat""".split()}
last=[0.0]
def pace():
    d=time.time()-last[0]
    if d<1.1: time.sleep(1.1-d)
    last[0]=time.time()
def get(url):
    for a in range(6):
        pace()
        try: r=cli.get(url)
        except Exception as e:
            time.sleep(3); continue
        if r.status_code==429:
            w=int(r.headers.get("retry-after","20")) if r.headers.get("retry-after","").isdigit() else 20*(a+1)
            print("429 wait",w,file=sys.stderr); time.sleep(w); continue
        return r
    return None
def jl(s):
    try: return json.loads(s)
    except Exception: return None
def bfs(cfg,keys):
    q=[cfg]
    while q:
        c=q.pop(0)
        if isinstance(c,dict):
            for k in keys:
                if k in c and c[k] is not None: return c[k]
            q.extend(v for v in c.values() if isinstance(v,(dict,)))
    return None
EXP=["num_experts","n_routed_experts","num_local_experts","moe_num_experts","num_routed_experts","num_moe_experts"]
TOPK=["num_experts_per_tok","moe_k","top_k_experts","num_experts_per_token","moe_topk","top_k"]
SH=["n_shared_experts","num_shared_experts","moe_num_shared_experts"]
def info(repo):
    for a in range(6):
        pace()
        try:
            return api.model_info(repo,expand=["safetensors","cardData","config","gated","createdAt","sha","tags","pipeline_tag","library_name","downloads"])
        except RepositoryNotFoundError: return "404"
        except HfHubHTTPError as e:
            c=getattr(e.response,"status_code",None)
            if c==429: time.sleep(20*(a+1)); continue
            if c in (401,403,404): return str(c)
            time.sleep(3)
        except Exception as e:
            time.sleep(3)
    return "ERR"
out=[]
for g,repos in GROUPS.items():
    for repo in repos:
        rec={"group":g,"repo":repo}
        m=info(repo)
        if isinstance(m,str):
            rec["error"]="model_info:"+m; out.append(rec); print(repo,"FAIL",m,file=sys.stderr); continue
        rec.update(sha=m.sha,created_at=str(m.created_at)[:10],gated=m.gated,pipeline_tag=m.pipeline_tag,library=m.library_name)
        st=m.safetensors
        rec["total_b"]=round(st.total/1e9,2) if st and st.total else None
        rec["dtypes"]={k:round(v/1e9,2) for k,v in (st.parameters.items() if st else [])}
        rec["bf16_gb"]=round(st.total*2/1e9,1) if st and st.total else None
        cd=m.card_data.to_dict() if m.card_data else {}
        rec["license"]=cd.get("license") or cd.get("license_name")
        bm=cd.get("base_model"); rec["base_model"]=bm if isinstance(bm,list) else ([bm] if bm else [])
        lang=cd.get("language"); rec["card_languages"]=lang if isinstance(lang,list) else ([lang] if lang else [])
        mc=m.config or {}
        tmpl=mc.get("chat_template_jinja") or ""
        tc=mc.get("tokenizer_config") or {}
        ct=tc.get("chat_template")
        if isinstance(ct,list): ct=json.dumps(ct)
        tmpl=(tmpl or "")+(ct or "")
        rec["architectures"]=mc.get("architectures")
        rec["model_type"]=mc.get("model_type")
        # config.json
        r=get(f"https://huggingface.co/{repo}/raw/{m.sha}/config.json")
        cfg=None; rec["config_readable"]=False; rec["config_http"]=r.status_code if r is not None else None
        if r is not None and r.status_code==200:
            cfg=jl(r.text); rec["config_readable"]=cfg is not None
        if cfg:
            ne=bfs(cfg,EXP)
            if isinstance(ne,list): ne=len(ne)
            rec["num_experts"]=ne
            rec["topk"]=bfs(cfg,TOPK) if ne else None
            rec["shared_experts"]=bfs(cfg,SH) if ne else None
            rec["is_moe"]=bool(isinstance(ne,int) and ne>1)
            rec["archs_cfg"]=cfg.get("architectures")
            rec["multimodal_cfg"]=any(k in cfg for k in ("vision_config","audio_config","visual","vision_tower","mm_config"))
            rec["quant_cfg"]=(cfg.get("quantization_config") or {}).get("quant_method") if isinstance(cfg.get("quantization_config"),dict) else None
            rec["max_pos"]=bfs(cfg,["max_position_embeddings"])
        # chat template flags
        flags=[]
        for k,pat in [("enable_thinking",r"enable_thinking"),("thinking_kwarg",r"\bthinking\b(?!_budget)"),("reasoning_effort",r"reasoning_effort"),("/think",r"/no_think|/think"),("reasoning_kwarg",r"enable_reasoning|\breasoning\b"),("think_tag",r"<think>")]:
            if re.search(pat,tmpl): flags.append(k)
        rec["template_flags"]=flags; rec["template_len"]=len(tmpl)
        # README
        r=get(f"https://huggingface.co/{repo}/raw/{m.sha}/README.md")
        txt=r.text[:400000] if r is not None and r.status_code==200 else ""
        rec["readme_ok"]=bool(txt)
        mm=re.search(r"(\d+(?:\.\d+)?)\s*B\s*(?:total\s*)?(?:active|activated)|(?:active|activated)\s*(?:parameters)?[^.\n]{0,25}?(\d+(?:\.\d+)?)\s*B\b",txt,re.I)
        rec["active_card"]=(mm.group(1) or mm.group(2)) if mm else None
        n=re.search(r"A(\d+(?:\.\d+)?)B\b",repo.split("/")[1]); rec["active_name"]=n.group(1) if n else None
        ind=re.findall(r"[^\n.]{0,70}(?:Indonesian|Bahasa Indonesia|Bahasa|Indonesia)[^\n.]{0,70}",txt)
        rec["id_mentions"]=len(ind); rec["id_snippet"]=ind[0].strip()[:160] if ind else None
        rec["id_in_lang_meta"]=any(str(l).lower() in ("id","ind","in") for l in rec["card_languages"])
        rec["sea_mentions"]=len(re.findall(r"Southeast Asia|SEA\b",txt))
        rec["card_h1"]=(re.search(r"^#\s+(.+)$",txt,re.M).group(1)[:80] if re.search(r"^#\s+(.+)$",txt,re.M) else None)
        out.append(rec)
        print(repo,rec["total_b"],rec["config_http"],rec.get("is_moe"),flags,rec["id_mentions"],file=sys.stderr)
        json.dump(out,open(SP+"/c2/detail.json","w"),indent=1)
json.dump(out,open(SP+"/c2/detail.json","w"),indent=1)
