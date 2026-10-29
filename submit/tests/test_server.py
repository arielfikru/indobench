import json
import re

import pytest
from fastapi.testclient import TestClient

import storage as storage_module
from samples import CONSENT_ALL, instruksi, pengetahuan, pengetahuan_singkat, sastra
from server import create_app
from storage import Storage

SID_RE = re.compile(r"sub-[0-9a-f]{10}")


@pytest.fixture
def store(tmp_path):
    return Storage(local_dir=tmp_path / "_local")


@pytest.fixture
def client(store):
    return TestClient(create_app(storage=store))


def post(client, payload):
    return client.post("/api/submit", json=payload)


def files_in(store, folder):
    base = store.local_dir / folder
    return sorted(base.glob("*.json")) if base.is_dir() else []


# ---------- halaman dan katalog ----------

def test_index_serves_indonesian_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert 'lang="id"' in body
    assert "Kirim soal" in body
    assert "Panduan menulis" in body
    assert "Tentang" in body
    assert 'name="website"' in body


def test_static_assets_served(client):
    for path in ["/static/style.css", "/static/app.js"]:
        assert client.get(path).status_code == 200


def test_catalog_lists_everything_the_page_needs(client):
    data = client.get("/api/catalog").json()
    assert len(data["constraints"]) == 25
    assert {r["id"] for r in data["registers"]} == {"baku", "santai", "gaul", "campur"}
    assert len(data["topics"]) == 11
    assert data["partners"] == ["Mandiri"]
    assert {c["id"] for c in data["consents"]} == set(CONSENT_ALL)
    assert {i["id"] for i in data["item_types"]} == {"instruksi", "pengetahuan", "sastra"}


# ---------- POST sukses ----------

def test_instruksi_submission_saved(client, store):
    response = post(client, instruksi(email="penulis@contoh.test"))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ok"] is True
    assert SID_RE.fullmatch(data["submission_id"])

    sid = data["submission_id"]
    record = json.loads((store.local_dir / "submissions" / f"{sid}.json").read_text(encoding="utf-8"))
    assert record["item_type"] == "instruksi"
    assert record["status"] == "pending_review"
    assert record["item"]["prompt"].startswith("TEST:")


def test_email_kept_out_of_record_and_stored_in_contacts(client, store):
    response = post(client, instruksi(email="rahasia@contoh.test"))
    sid = response.json()["submission_id"]

    record_text = (store.local_dir / "submissions" / f"{sid}.json").read_text(encoding="utf-8")
    assert "rahasia@contoh.test" not in record_text

    contact = json.loads((store.local_dir / "contacts" / f"{sid}.json").read_text(encoding="utf-8"))
    assert contact == {"submission_id": sid, "author_id": "uji_penulis", "email": "rahasia@contoh.test"}


def test_pengetahuan_mcq_submission(client, store):
    response = post(client, pengetahuan())
    assert response.status_code == 200, response.text
    sid = response.json()["submission_id"]
    record = json.loads((store.local_dir / "submissions" / f"{sid}.json").read_text(encoding="utf-8"))
    assert record["item"]["format"] == "pilihan_ganda"
    assert record["item"]["kunci"] == "B"


def test_pengetahuan_singkat_submission(client):
    assert post(client, pengetahuan_singkat()).status_code == 200


def test_sastra_submission(client):
    assert post(client, sastra()).status_code == 200


def test_one_submission_of_each_type_writes_six_files(client, store):
    for payload in [instruksi(), pengetahuan(), sastra()]:
        assert post(client, payload).status_code == 200
    assert len(files_in(store, "submissions")) == 3
    assert len(files_in(store, "contacts")) == 3


# ---------- penolakan ----------

def test_validation_errors_returned_as_dict(client, store):
    response = post(client, instruksi(prompt="pendek", register="formal"))
    assert response.status_code == 400
    data = response.json()
    assert data["ok"] is False
    assert "prompt" in data["errors"] and "register" in data["errors"]
    assert files_in(store, "submissions") == []


def test_honeypot_rejected_with_generic_message(client, store):
    response = post(client, instruksi(website="https://spam.test"))
    assert response.status_code == 400
    assert response.json()["ok"] is False
    assert "_form" in response.json()["errors"]
    assert files_in(store, "submissions") == []


def test_malformed_json_rejected(client, store):
    response = client.post("/api/submit", content=b"{bukan json", headers={"content-type": "application/json"})
    assert response.status_code == 400
    assert files_in(store, "submissions") == []


def test_non_object_json_rejected(client):
    response = client.post("/api/submit", json=["daftar"])
    assert response.status_code == 400


def test_empty_body_rejected(client):
    response = client.post("/api/submit", content=b"")
    assert response.status_code == 400


def test_body_over_50kb_rejected(client, store):
    big = instruksi(prompt="TEST: " + "a" * 60_000)
    response = post(client, big)
    assert response.status_code == 413
    assert response.json()["ok"] is False
    assert files_in(store, "submissions") == []


def test_body_under_limit_is_not_rejected_for_size(client):
    response = post(client, instruksi(reference_response="TEST: " + "b" * 2990))
    assert response.status_code == 200


def test_duplicate_submission_rejected_on_second_try(client, store):
    assert post(client, instruksi()).status_code == 200
    response = post(client, instruksi(prompt="  TEST:  Tulis satu kalimat promo kopi untuk uji validasi sistem. "))
    assert response.status_code == 400
    assert "prompt" in response.json()["errors"]
    assert len(files_in(store, "submissions")) == 1


def test_duplicate_known_from_disk_at_startup(tmp_path):
    store = Storage(local_dir=tmp_path / "_local")
    first = TestClient(create_app(storage=store))
    assert post(first, instruksi()).status_code == 200

    restarted = TestClient(create_app(storage=Storage(local_dir=tmp_path / "_local")))
    response = post(restarted, instruksi())
    assert response.status_code == 400
    assert "prompt" in response.json()["errors"]


def test_rate_limit_returns_429_in_indonesian(tmp_path):
    store = Storage(local_dir=tmp_path / "_local")
    client = TestClient(create_app(storage=store, rate_limit=2))
    assert post(client, instruksi(prompt="TEST: satu permintaan uji untuk limit")).status_code == 200
    assert post(client, instruksi(prompt="TEST: dua permintaan uji untuk limit")).status_code == 200
    response = post(client, instruksi(prompt="TEST: tiga permintaan uji untuk limit"))
    assert response.status_code == 429
    assert "Coba lagi nanti" in response.json()["errors"]["_form"]


def test_rate_limit_per_forwarded_ip(tmp_path):
    client = TestClient(create_app(storage=Storage(local_dir=tmp_path / "_local"), rate_limit=1))
    a = client.post("/api/submit", json=instruksi(), headers={"x-forwarded-for": "10.0.0.1"})
    b = client.post("/api/submit", json=instruksi(prompt="TEST: permintaan uji kedua dari ip lain"),
                    headers={"x-forwarded-for": "10.0.0.2"})
    assert a.status_code == 200
    assert b.status_code == 200


# ---------- penyimpanan Hugging Face (tiruan) ----------

class FakeHfApi:
    instances = []

    def __init__(self, token=None):
        self.token = token
        self.commits = []
        FakeHfApi.instances.append(self)

    def list_repo_files(self, repo_id, repo_type=None):
        return ["README.md", "submissions/sub-old0000001.json", "contacts/sub-old0000001.json"]

    def create_commit(self, *, repo_id, operations, repo_type=None, **kwargs):
        self.commits.append((repo_id, repo_type, [op.path_in_repo for op in operations]))


def test_hf_mode_uploads_to_private_dataset_paths(monkeypatch):
    FakeHfApi.instances.clear()
    monkeypatch.setattr(storage_module, "HfApi", FakeHfApi)
    monkeypatch.setattr(
        storage_module,
        "hf_hub_download",
        lambda **kwargs: _write_old_record(kwargs["filename"]),
    )

    store = Storage(token="hf_test_token_jangan_dicetak", repo="contoh/submissions-privat")
    assert store.mode == "hf"
    client = TestClient(create_app(storage=store))

    response = post(client, instruksi())
    assert response.status_code == 200, response.text

    api = FakeHfApi.instances[-1]
    sid = response.json()["submission_id"]
    # One commit per submission (Hub commit rate limits), record and contact together.
    assert api.commits == [("contoh/submissions-privat", "dataset",
                            [f"submissions/{sid}.json", f"contacts/{sid}.json"])]
    assert b"hf_test_token" not in response.content


def test_hf_startup_loads_existing_hashes(monkeypatch):
    FakeHfApi.instances.clear()
    monkeypatch.setattr(storage_module, "HfApi", FakeHfApi)
    monkeypatch.setattr(storage_module, "hf_hub_download", lambda **kwargs: _write_old_record(kwargs["filename"]))
    store = Storage(token="tok", repo="contoh/x")
    assert store.load_hashes() == {"0" * 64}


def _write_old_record(filename):
    import tempfile
    from pathlib import Path

    tmp = Path(tempfile.mkdtemp(prefix="submit-test-")) / Path(filename).name
    tmp.write_text(json.dumps({"submission_id": "sub-old0000001", "text_sha256": "0" * 64}), encoding="utf-8")
    return str(tmp)


def test_storage_mode_defaults_to_local_without_env(monkeypatch, tmp_path):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("SUBMISSIONS_REPO", raising=False)
    store = Storage.from_env()
    assert store.mode == "local"
    assert store.local_dir.name == "_local"


def test_storage_mode_needs_both_env_vars(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "tok")
    monkeypatch.delenv("SUBMISSIONS_REPO", raising=False)
    assert Storage.from_env().mode == "local"
