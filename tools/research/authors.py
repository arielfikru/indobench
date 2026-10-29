from huggingface_hub import HfApi
api = HfApi()
def show(m):
    print(f"  {m.id} | created={getattr(m,'created_at',None)} | gated={getattr(m,'gated',None)}")
for a in ["Qwen", "google", "aisingapore", "GoToCompany", "Sahabat-AI"]:
    print(f"== author {a} (newest 30 by createdAt)")
    try:
        for m in api.list_models(author=a, sort="createdAt", limit=30):
            show(m)
    except Exception as e:
        print("  ERR", type(e).__name__, str(e)[:150])
print("== exact probes")
for rid in ["Qwen/Qwen3.6-27B","Qwen/Qwen3.8-27B","Qwen/Qwen3.8-27B-Instruct","Qwen/Qwen3.6-27B-Instruct",
            "aisingapore/Qwen-SEA-LION-v4.5-27B-IT","aisingapore/Gemma-SEA-LION-v4.5-E2B-IT","aisingapore/Gemma-SEA-LION-v4.5-E2B",
            "google/gemma-3-27b-it","google/gemma-4-E2B-it","google/gemma-4-E2B","google/gemma-4-31B-it","google/gemma-4-31B",
            "google/gemma-4-26B-A4B-it","google/gemma-4-26B-A4B","GoToCompany/gemma3-27b-cpt-gotoai-v3-instruct",
            "GoToCompany/gemma3-27b-cpt-gotoai-v3","Qwen/Qwen3.9-27B","google/gemma-5-27b-it"]:
    try:
        i = api.model_info(rid)
        print(f"  OK {rid} | sha={i.sha[:10]} | gated={i.gated} | created={i.created_at}")
    except Exception as e:
        print(f"  MISS {rid} | {type(e).__name__}")
