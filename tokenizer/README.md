# Tokenizer fertility

`fertility.py` measures how many tokens each model's tokenizer spends on Indonesian (`ind_Latn`) versus English (`eng_Latn`) over the parallel FLORES+ devtest set. It loads tokenizer files only (no weights), CPU only.

Run:

```
uv run --with transformers --with tokenizers --with sentencepiece --with protobuf \
  --with pyyaml --with huggingface_hub python tokenizer/fertility.py [--models k1,k2] [--split dev]
```

- Output: `results/tokenizer_fertility.csv`, plus a compact table on stdout.
- `--check-tokenizers`: load tokenizers and print hashes only (no dataset, no CSV).
- Metrics: `n_words` is a whitespace split of the raw sentence (punctuation not stripped). `premium_id_en` = Indonesian tokens / English tokens; it is set on the `ind_Latn` row only.
- `tokenizer_hash` = sha256 of the backend `tokenizer.json`. Models with the same hash share measurements.
- Gated or failing tokenizers write `status=error: ...` rows and do not stop the run.
- Dataset: `openlanguagedata/flores_plus` pinned to revision `1147e2dc59f37fbb5c22fd8478770de02cd399f9`. The account owning `HF_TOKEN` must have accepted the dataset terms.
