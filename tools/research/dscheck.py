import os, re, yaml
from huggingface_hub import hf_hub_download
out = {}
for repo in ["CohereLabs/Global-MMLU", "openlanguagedata/flores_plus", "facebook/flores"]:
    p = hf_hub_download(repo, "README.md", repo_type="dataset")
    txt = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    meta = yaml.safe_load(m.group(1)) if m else {}
    cfgs = meta.get("configs", []) if meta else []
    names = [c.get("config_name") for c in cfgs]
    feats = set()
    for c in cfgs:
        di = c.get("dataset_info") or {}
        for f in (di.get("features") or []):
            feats.add(f.get("name"))
    out[repo] = {"n_configs": len(names), "config_names_sample": names[:12],
                 "has_ind_Latn_config": any(n and "ind_Latn" in n for n in names),
                 "has_eng_Latn_config": any(n and "eng_Latn" in n for n in names),
                 "has_id_config": "id" in names,
                 "feature_names_sample": sorted([f for f in feats if f])[:40],
                 "has_cultural_sensitivity_label_feature": "cultural_sensitivity_label" in feats}
for k, v in out.items():
    print(k, v)
