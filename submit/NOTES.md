# submit/ notes (IFEval-ID submission site)

## Status
- Built: FastAPI backend (server.py, validate.py, storage.py, catalog.py), page (static/index.html, style.css, app.js), Dockerfile, README.md, pinned requirements.txt, tests (97 passing).
- Verified locally: pytest 97 passed; curl POST of one fake item per type (TEST: fixtures) saved under _local (deleted after); honeypot rejected; GET / 200; GET /api/catalog lists 25 constraints.
- Browser at 375px (local): no console errors, no horizontal scroll, catalog populates, empty submit shows summary + inline errors, valid instruksi submit shows id and clears item fields while keeping pseudonim.

## Not verified
- Pengetahuan/sastra forms in the browser (only via curl and unit tests).
- Real Hugging Face write path (tested only with a fake HfApi). huggingface_hub 2.3.0 is pinned; upload_file signature checked, not exercised against the Hub.
- Docker image not built. Dockerfile untested.
- Rate-limit IP source: uses the last X-Forwarded-For entry (appended by the proxy), else socket address. Not confirmed behind the HF proxy.

## Decisions to review
- Rate limit counts every POST past the size check, including invalid ones.
- Body limit 50 * 1024 bytes.
- sastra: added `sumber_contoh`, required when `contoh_jawaban` is given (brief said "with source" but no field name).
- Constraint hint phrases for E1-E10 were written by me (spec §5 gave no example lines for E items).
- Constraint `params` are always `{}`; writers never enter them.
- Each submission is one HF commit (create_commit with submission + contact).

## Next steps
- Build the Docker image locally and run it on port 7860.
- Set the Space secret HF_TOKEN (write to the private submissions dataset only) and variable SUBMISSIONS_REPO.
- Decide the IP source for rate limiting once deployed.
