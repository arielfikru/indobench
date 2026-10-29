import json
from huggingface_hub import HfApi, __version__
print(__version__)
api=HfApi()
ms=list(api.list_models(author="allenai",sort="created_at",limit=3,expand=["safetensors","config","cardData","gated","createdAt","sha","pipeline_tag","tags","baseModels","downloads","library_name"]))
for m in ms:
    print(m.id,m.sha,m.created_at,m.gated,m.pipeline_tag,m.safetensors.total if m.safetensors else None, (m.config or {}).get("architectures"), list((m.config or {}).keys()), m.card_data and (m.card_data.get("license"),m.card_data.get("base_model"),m.card_data.get("language")))
