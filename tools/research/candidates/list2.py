import json, time, sys, re
from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError
SP=sys.argv[1]
api=HfApi()
AUTH="meta-llama mistralai microsoft openai allenai ibm-granite HuggingFaceTB CohereLabs tiiuae nvidia LGAI-EXAONE swiss-ai LiquidAI ServiceNow-AI google Qwen deepseek-ai internlm zai-org THUDM openbmb moonshotai baidu tencent stepfun-ai XiaomiMiMo inclusionAI ByteDance-Seed 01-ai Skywork baichuan-inc MiniMaxAI meituan-longcat aisingapore GoToCompany Sahabat-AI sail SeaLLMs DAMO-NLP-SG Yellow-AI-NLP indonlp".split()
QUANT=re.compile(r"(gguf|awq|gptq|fp8|fp4|int4|int8|4bit|8bit|nvfp4|mlx|bnb|exl2|onnx|w4a16|w8a8|quant|eagle|lora|adapter|mxfp|-bf16-vllm)",re.I)
LIM={"x":1}
out={}
SKIP=set("GoToCompany Sahabat-AI Yellow-AI-NLP indonlp SeaLLMs THUDM ServiceNow-AI moonshotai MiniMaxAI".split())
for a in [x for x in AUTH if x not in SKIP]:
    for attempt in range(6):
        try:
            time.sleep(1.1)
            ms=list(api.list_models(author=a,sort="created_at",limit=LIM.get(a,400),expand=["safetensors","gated","createdAt","sha","pipeline_tag","tags","downloads","library_name"]))
            out[a]=[{"id":m.id,"sha":m.sha,"created":str(m.created_at)[:10],"gated":m.gated,"pipe":m.pipeline_tag,"tot":(m.safetensors.total if m.safetensors else None),"dl":m.downloads,"lib":m.library_name} for m in ms if not QUANT.search(m.id)]
            print(a,len(ms),file=sys.stderr);break
        except HfHubHTTPError as e:
            code=getattr(e.response,"status_code",None)
            print(a,"ERR",code,file=sys.stderr)
            time.sleep(15*(attempt+1) if code==429 else 3)
        except Exception as e:
            print(a,"ERR",type(e).__name__,str(e)[:100],file=sys.stderr);time.sleep(3)
json.dump(out,open(SP+"/c2/listing2.json","w"),indent=1)
