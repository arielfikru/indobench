import json, re, sys, time
import httpx
from huggingface_hub import HfApi, get_token
from huggingface_hub.errors import HfHubHTTPError
SP=sys.argv[1]
api=HfApi(); tok=get_token()
cli=httpx.Client(follow_redirects=True,timeout=40,headers={"Authorization":"Bearer "+tok} if tok else {})
d=json.load(open(SP+"/c2/detail.json"))
last=[0.0]
def pace():
    x=time.time()-last[0]
    if x<1.1: time.sleep(1.1-x)
    last[0]=time.time()
def snip(t,pat,n=1,w=90):
    o=[]
    for m in re.finditer(pat,t,re.I):
        s=max(0,m.start()-w);e=min(len(t),m.end()+w)
        o.append(re.sub(r"\s+"," ",t[s:e]))
        if len(o)>=n:break
    return o
res={}
for r in d:
    repo=r["repo"]; sha=r["sha"]; o={}
    # template
    tm=""
    for a in range(5):
        pace()
        try:
            m=api.model_info(repo,expand=["config"]); c=m.config or {}
            tc=(c.get("tokenizer_config") or {}).get("chat_template")
            if isinstance(tc,list): tc=json.dumps(tc)
            tm=(c.get("chat_template_jinja") or "")+(tc or "")
            break
        except HfHubHTTPError as e:
            if getattr(e.response,"status_code",None)==429: time.sleep(20*(a+1))
            else: break
        except Exception: time.sleep(3)
    o["tmpl_len"]=len(tm)
    o["enable_thinking"]=snip(tm,r"enable_thinking",1,60)
    o["thinking_var"]=snip(tm,r"(?:if|not|is defined|get\()[^%}]{0,40}\bthinking\b|\bthinking\s*(?:is|==|!=)",1,60)
    o["reasoning_effort"]=snip(tm,r"reasoning_effort",1,60)
    o["soft_switch"]=snip(tm,r"/no_think|/think",1,40)
    o["enable_reasoning"]=snip(tm,r"enable_reasoning|reasoning_mode|thinking_mode|think_mode",1,60)
    # readme
    if r["id_mentions"]==0 or r["group"]=="regional" or r.get("is_moe"):
        pace()
        try: rr=cli.get(f"https://huggingface.co/{repo}/raw/{sha}/README.md")
        except Exception: rr=None
        txt=rr.text[:400000] if rr is not None and rr.status_code==200 else ""
        o["readme_status"]=rr.status_code if rr is not None else None
        o["lang_lines"]=snip(txt,r"\d+\+?\s*(?:languages|language)|multilingual",2,70)
        o["active_lines"]=snip(txt,r"active(?:ated)?\s+param|\bA\d+(?:\.\d+)?B\b[^.\n]{0,20}active|\d+(?:\.\d+)?\s*B\s+(?:active|activated)",2,70) if r.get("is_moe") else []
        o["lineage"]=snip(txt,r"(?:based on|built (?:on|upon)|continued pre-?train\w*|fine-?tuned from|derived from|further pre-?train\w*)[^.\n]{0,100}",2,10) if r["group"]=="regional" else []
        o["id_lines"]=snip(txt,r"Indonesian|Bahasa Indonesia",2,70)
    res[repo]=o
    print(repo,o["tmpl_len"],file=sys.stderr)
json.dump(res,open(SP+"/c2/pass2.json","w"),indent=1)
