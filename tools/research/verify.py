import json, re, os, traceback
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import HfHubHTTPError

api = HfApi()
SP = os.environ["SP_DIR"]

MODELS = [
    # (group, repo_id)
    ("pair1_gemma3", "google/gemma-3-27b-it"),
    ("pair1_gemma3", "GoToCompany/gemma3-27b-cpt-gotoai-v3-instruct"),
    ("pair2_qwen", "Qwen/Qwen3.6-27B"),
    ("pair2_qwen", "aisingapore/Qwen-SEA-LION-v4.5-27B-IT"),
    ("pair3_gemma4e2b", "google/gemma-4-E2B-it"),
    ("pair3_gemma4e2b", "google/gemma-4-E2B"),
    ("pair3_gemma4e2b", "aisingapore/Gemma-SEA-LION-v4.5-E2B-IT"),
    ("latest_comparators", "Qwen/Qwen3.8-27B"),
    ("latest_comparators", "google/gemma-4-31B-it"),
    ("latest_comparators", "google/gemma-4-31B"),
    ("latest_comparators", "google/gemma-4-26B-A4B-it"),
    ("latest_comparators", "google/gemma-4-26B-A4B"),
    ("newer_candidates", "aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B"),
    ("newer_candidates", "Qwen/Qwen3.8-Flash-Next"),
    ("newer_candidates", "google/gemma-4-12B"),
    ("newer_candidates", "google/diffusiongemma-26B-A4B-it"),
    ("probe_missing_base", "GoToCompany/gemma3-27b-cpt-gotoai-v3"),
]

DATASETS = [
    "openlanguagedata/flores_plus",
    "facebook/flores",
    "haryoaw/COPAL",
    "CohereLabs/Global-MMLU",
    "indolem/IndoMMLU",
    "indolem/IndoCulture",
]

def err_kind(e):
    name = type(e).__name__
    code = getattr(getattr(e, "response", None), "status_code", None)
    if name == "GatedRepoError":
        return "403_gated_not_accepted"
    if name == "RepositoryNotFoundError":
        return "404_not_found"
    if name == "EntryNotFoundError":
        return "file_not_in_repo"
    if code is not None:
        return f"http_{code}"
    return name

def dl(repo, fname, repo_type=None):
    try:
        p = hf_hub_download(repo, fname, repo_type=repo_type)
        return p, "OK"
    except Exception as e:
        return None, err_kind(e)

def dig(d, *keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return d[k]
    return None

out = {"models": {}, "datasets": {}}

for group, rid in MODELS:
    r = {"group": group, "id": rid}
    try:
        mi = api.model_info(rid)
        r.update(sha=mi.sha, gated=str(mi.gated), last_modified=str(mi.last_modified),
                 created_at=str(mi.created_at), pipeline_tag=mi.pipeline_tag,
                 private=mi.private)
    except Exception as e:
        r["meta_error"] = err_kind(e)
        out["models"][rid] = r
        continue

    cfg_path, access = dl(rid, "config.json")
    r["access_config_json"] = access
    if cfg_path:
        cfg = json.load(open(cfg_path))
        tc = cfg.get("text_config") or {}
        r["architectures"] = cfg.get("architectures")
        r["model_type"] = cfg.get("model_type")
        r["max_position_embeddings"] = dig(cfg, "max_position_embeddings") or dig(tc, "max_position_embeddings")
        r["sliding_window"] = dig(tc, "sliding_window") or dig(cfg, "sliding_window")
        r["torch_dtype"] = dig(cfg, "torch_dtype", "dtype") or dig(tc, "torch_dtype", "dtype")
        r["has_vision_config"] = "vision_config" in cfg or "vision_config" in tc
        r["has_audio_config"] = "audio_config" in cfg or "audio_config" in tc
        r["multimodal"] = bool(r["has_vision_config"] or r["has_audio_config"])
        r["config_keys_sample"] = sorted(list(cfg.keys()))[:40]
        r["text_config_model_type"] = tc.get("model_type")
        r["num_hidden_layers"] = dig(tc, "num_hidden_layers") or dig(cfg, "num_hidden_layers")
        r["hidden_size"] = dig(tc, "hidden_size") or dig(cfg, "hidden_size")
        r["num_experts"] = dig(tc, "num_experts") or dig(cfg, "num_experts")
        r["config_thinking_hint"] = any(
            k in json.dumps(cfg).lower() for k in ["thinking", "enable_think"])

    try:
        st = api.get_safetensors_metadata(rid)
        total = sum(st.parameter_count.values())
        r["param_count_total"] = total
        r["param_count_by_dtype"] = dict(st.parameter_count)
        r["param_B"] = round(total / 1e9, 3)
        r["bf16_GB_est"] = round(total * 2 / 1e9, 2)
        r["safetensors_access"] = "OK"
    except Exception as e:
        r["safetensors_access"] = err_kind(e)
        r["safetensors_note"] = str(e)[:150]

    # chat template: small files only
    tpath, t_access = dl(rid, "chat_template.jinja")
    template_text = None
    if tpath:
        template_text = open(tpath, encoding="utf-8").read()
        r["chat_template_source"] = "chat_template.jinja"
    else:
        tc_path, _ = dl(rid, "tokenizer_config.json")
        if tc_path:
            tcj = json.load(open(tc_path, encoding="utf-8"))
            ct = tcj.get("chat_template")
            if isinstance(ct, list):
                ct = "\n".join(x.get("template", "") for x in ct if isinstance(x, dict))
            template_text = ct
            r["chat_template_source"] = "tokenizer_config.json"
            r["model_max_length_tokenizer"] = tcj.get("model_max_length")
    if template_text:
        low = template_text.lower()
        hits = [k for k in ["enable_thinking", "<think>", "</think>", "thinking", "<|think|>", "reasoning"] if k in low]
        r["template_thinking_hits"] = hits
        r["thinking_in_template"] = bool(hits)
    else:
        r["template_thinking_hits"] = []
        r["thinking_in_template"] = None
        r["chat_template_note"] = f"no template found ({t_access})"

    out["models"][rid] = r
    print("done", rid, r.get("access_config_json"), r.get("param_B"))

for ds in DATASETS:
    d = {"id": ds}
    try:
        di = api.dataset_info(ds)
        d.update(sha=di.sha, gated=str(di.gated), last_modified=str(di.last_modified), private=di.private)
    except Exception as e:
        d["meta_error"] = err_kind(e)
        out["datasets"][ds] = d
        continue
    p, acc = dl(ds, "README.md", repo_type="dataset")
    d["access_readme"] = acc
    try:
        files = api.list_repo_files(ds, repo_type="dataset")
        d["file_count"] = len(files)
        d["files_sample"] = files[:40]
    except Exception as e:
        d["list_files_error"] = err_kind(e)
    out["datasets"][ds] = d
    print("ds", ds, acc)

# FLORES ind_Latn/eng_Latn presence and Global-MMLU config/column check: use README/yaml only
def readme_text(repo):
    p, acc = dl(repo, "README.md", repo_type="dataset")
    return (open(p, encoding="utf-8").read() if p else None), acc

for ds in ["openlanguagedata/flores_plus", "facebook/flores", "CohereLabs/Global-MMLU"]:
    txt, acc = readme_text(ds)
    if txt:
        hits = {k: (k in txt) for k in ["ind_Latn", "eng_Latn", "cultural_sensitivity_label", "id"]}
        out["datasets"][ds]["readme_mentions"] = hits

# Global-MMLU: config names from README yaml
txt, _ = readme_text("CohereLabs/Global-MMLU")
if txt:
    cfgs = re.findall(r"config_name:\s*(\S+)", txt)
    out["datasets"]["CohereLabs/Global-MMLU"]["config_names_from_readme"] = sorted(set(cfgs))[:200]

with open(os.path.join(SP, "hf_models.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE", os.path.join(SP, "hf_models.json"))
