"""Penyimpanan submission.

Mode hf: HF_TOKEN dan SUBMISSIONS_REPO diisi -> upload ke dataset privat di Hugging Face.
Mode local: selain itu -> tulis ke submit/_local/ (untuk pengembangan).

Token tidak pernah dicetak atau dicatat.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Iterator

from huggingface_hub import HfApi, hf_hub_download

log = logging.getLogger("submit.storage")

LOCAL_DIR = Path(__file__).resolve().parent / "_local"


class Storage:
    def __init__(self, *, local_dir: Path | None = None,
                 token: str | None = None, repo: str | None = None):
        if token and repo:
            self.mode = "hf"
            self.repo = repo
            self._token = token
            self._api = HfApi(token=token)
            self.local_dir = None
        else:
            self.mode = "local"
            self.repo = None
            self._token = None
            self._api = None
            self.local_dir = Path(local_dir) if local_dir is not None else LOCAL_DIR

    @classmethod
    def from_env(cls) -> "Storage":
        token = os.environ.get("HF_TOKEN", "").strip()
        repo = os.environ.get("SUBMISSIONS_REPO", "").strip()
        if bool(token) != bool(repo):
            log.warning("HF_TOKEN dan SUBMISSIONS_REPO harus diisi keduanya. Memakai penyimpanan lokal.")
        return cls(token=token or None, repo=repo or None)

    def load_hashes(self) -> set[str]:
        """Baca semua submission yang ada sekali saat startup, lalu kumpulkan text_sha256-nya."""
        hashes = set()
        for record in self._iter_records():
            digest = record.get("text_sha256")
            if digest:
                hashes.add(digest)
        return hashes

    def save(self, record: dict, contact: dict | None) -> None:
        sid = record["submission_id"]
        files = {f"submissions/{sid}.json": record}
        if contact:
            files[f"contacts/{sid}.json"] = contact
        if self.mode == "local":
            for rel_path, obj in files.items():
                self._put(rel_path, obj)
            return
        # One commit per submission: the Hub rate-limits commits per repo.
        from huggingface_hub import CommitOperationAdd

        self._api.create_commit(
            repo_id=self.repo,
            repo_type="dataset",
            operations=[CommitOperationAdd(path_in_repo=k, path_or_fileobj=_encode(v)) for k, v in files.items()],
            commit_message=f"Tambah {sid}",
        )

    # ----- internal -----

    def _iter_records(self) -> Iterator[dict]:
        if self.mode == "local":
            folder = self.local_dir / "submissions"
            if not folder.is_dir():
                return
            for path in sorted(folder.glob("*.json")):
                yield json.loads(path.read_text(encoding="utf-8"))
            return
        files = self._api.list_repo_files(repo_id=self.repo, repo_type="dataset")
        for name in files:
            if name.startswith("submissions/") and name.endswith(".json"):
                local_path = hf_hub_download(
                    repo_id=self.repo,
                    filename=name,
                    repo_type="dataset",
                    token=self._token,
                )
                yield json.loads(Path(local_path).read_text(encoding="utf-8"))

    def _put(self, rel_path: str, obj: dict) -> None:
        path = self.local_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_encode(obj))


def _encode(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
