from huggingface_hub import HfApi
api = HfApi()
authors = ["Qwen", "google", "aisingapore", "GoToCompany", "Sahabat-AI"]
def show(m):
    print(f"  {m.id} | created={getattr(m,'created_at',None)} | mod={getattr(m,'last_modified',None)} | gated={getattr(m,'gated',None)} | tag={getattr(m,'pipeline_tag',None)}")
for a in authors:
    print(f"== author {a} (newest 40 by createdAt)")
    try:
        for m in api.list_models(author=a, sort="createdAt", limit=40, expand=["createdAt", "gated", "lastModified", "pipelineTag"]):
            show(m)
    except Exception as e:
        print("  ERR", type(e).__name__, str(e)[:200])
for q in ["gemma-3-27b", "gemma-4", "gemma4", "qwen3.6", "qwen3.8", "SEA-LION", "gotoai", "GoTo", "Sahabat"]:
    print(f"== search '{q}'")
    try:
        for m in api.list_models(search=q, sort="createdAt", limit=25, expand=["createdAt", "gated"]):
            show(m)
    except Exception as e:
        print("  ERR", type(e).__name__, str(e)[:200])
