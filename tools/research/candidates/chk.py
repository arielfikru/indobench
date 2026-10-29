import sys,time,re,httpx
from huggingface_hub import HfApi,get_token
api=HfApi();tok=get_token()
cli=httpx.Client(follow_redirects=True,timeout=40,headers={"Authorization":"Bearer "+tok})
for repo,sha in [("nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16",None)]:
    time.sleep(1.2)
    st=api.get_safetensors_metadata(repo)
    print(repo,{k:round(v/1e9,2) for k,v in st.parameter_count.items()})
for repo in ["sail/Sailor2-14B-Chat","aisingapore/Gemma-SEA-LION-v4-27B-IT","aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B-Base"]:
    time.sleep(1.2)
    r=cli.get(f"https://huggingface.co/{repo}/raw/main/README.md")
    t=r.text
    for m in list(re.finditer(r"Qwen2\.5[^\n.]{0,80}|gemma-?3[^\n.]{0,80}|Nemotron-3[^\n.]{0,80}|NVIDIA-Nemotron[^\n.]{0,80}",t,re.I))[:3]:
        print(repo,"::",re.sub(r"\s+"," ",m.group(0))[:140])
