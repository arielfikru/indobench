---
title: indobench submit
emoji: 📝
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

Form for communities to submit Indonesian benchmark items (instruksi, pengetahuan, sastra & puisi).
Submissions go to a private Hugging Face dataset.

Space settings:
- Secret `HF_TOKEN`: fine-grained token with write access to the submissions dataset only.
- Variable `SUBMISSIONS_REPO`: e.g. `your-name/indobench-submissions` (private dataset).

Without both, the app stores submissions under `_local/` (for local testing).

Local run: `pip install -r requirements.txt && uvicorn server:app --port 7860`
