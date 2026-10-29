import json,time
from huggingface_hub import HfApi
api=HfApi();o={}
for r in ["Qwen/Qwen2.5-7B-Instruct","Qwen/Qwen2.5-14B-Instruct","Qwen/Qwen2.5-32B-Instruct","Qwen/Qwen2-7B-Instruct"]:
    time.sleep(1.2)
    try:
        m=api.model_info(r,expand=["safetensors","gated","createdAt","sha","cardData"])
        o[r]=dict(sha=m.sha,created=str(m.created_at)[:10],gated=m.gated,total_b=round(m.safetensors.total/1e9,2),license=(m.card_data.to_dict().get("license") if m.card_data else None))
    except Exception as e: o[r]=str(e)[:80]
print(json.dumps(o,indent=1)); json.dump(o,open("p3.json","w"))
