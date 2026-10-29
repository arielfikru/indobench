"""Validasi dan pembentukan record submission.

Modul ini murni: tanpa FastAPI, tanpa I/O. Error dikembalikan sebagai dict
field -> pesan Indonesia. Kunci error sama dengan atribut data-field di halaman.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone

import catalog as C

GENERIC_ERROR = "Permintaan tidak dapat diproses. Muat ulang halaman lalu coba lagi."

MAIN_KEY = {"instruksi": "prompt", "pengetahuan": "pertanyaan", "sastra": "tugas"}
CONSENT_KEYS = tuple(c["id"] for c in C.CONSENTS)
PARTNER_CHOICES = frozenset(C.PARTNERS) | {C.PARTNER_OTHER}

PSEUDONYM_RE = re.compile(r"[A-Za-z0-9_]{3,30}")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
# 08xx atau +62/62 diikuti 8. Spasi, titik, atau strip boleh di antara digit.
PHONE_RE = re.compile(r"(?<!\d)(?:\+62[\s.-]?|62|0)8(?:[\s.-]?\d){7,11}(?!\d)")
NIK_RE = re.compile(r"(?<!\d)\d{16}(?!\d)")
RIMA_RE = re.compile(r"[a-z](?:-?[a-z]){1,15}")

PII_MESSAGE = "Hapus data pribadi (email, nomor HP, atau NIK). Pakai contoh umum."


def _normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).lower().split())


def text_sha256(text: str) -> str:
    """Hash teks utama setelah lowercase dan normalisasi spasi. Dipakai untuk cek duplikat."""
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


def honeypot_filled(payload) -> bool:
    return isinstance(payload, dict) and bool(payload.get("website"))


class _Form:
    """Pengumpul error dan teks bebas untuk pemeriksaan PII."""

    def __init__(self, payload: dict):
        self.data = payload
        self.errors: dict[str, str] = {}
        self.scan: list[tuple[str, str]] = []

    def fail(self, key: str, msg: str) -> None:
        self.errors.setdefault(key, msg)

    def text(self, key, *, required=False, min_len=0, max_len=1000, scan=True,
             err_key=None, source=None) -> str:
        err = err_key or key
        src = self.data if source is None else source
        raw = src.get(key)
        if raw is None:
            raw = ""
        if not isinstance(raw, str):
            self.fail(err, "Isi dengan teks.")
            return ""
        val = raw.strip()
        if not val:
            if required:
                self.fail(err, "Wajib diisi.")
            return ""
        if len(val) < min_len:
            self.fail(err, f"Minimal {min_len} karakter.")
        elif len(val) > max_len:
            self.fail(err, f"Maksimal {max_len} karakter.")
        if scan:
            self.scan.append((err, val))
        return val

    def int_opt(self, key, lo, hi):
        raw = self.data.get(key)
        if raw is None or isinstance(raw, bool):
            if isinstance(raw, bool):
                self.fail(key, "Isi dengan angka bulat.")
            return None
        if isinstance(raw, str) and not raw.strip():
            return None
        try:
            n = int(str(raw).strip())
        except ValueError:
            self.fail(key, "Isi dengan angka bulat.")
            return None
        if not lo <= n <= hi:
            self.fail(key, f"Isi angka antara {lo} dan {hi}.")
            return None
        return n


def _choice(f: _Form, d: dict, key: str, allowed, msg: str) -> str:
    value = d.get(key)
    if isinstance(value, str) and value in allowed:
        return value
    f.fail(key, msg)
    return ""


# ---------- jenis instruksi (IFEval-ID) ----------

def _build_instruksi(f: _Form, d: dict):
    prompt = f.text("prompt", required=True, min_len=20, max_len=1000)
    register = _choice(f, d, "register", C.REGISTER_IDS, "Pilih register.")
    topic = _choice(f, d, "topic", C.TOPIC_IDS, "Pilih topik.")

    rows = []
    raw = d.get("constraints")
    if not isinstance(raw, list) or not 1 <= len(raw) <= 4:
        f.fail("constraints", "Isi 1 sampai 4 constraint.")
    else:
        seen = set()
        for i, row in enumerate(raw):
            key = f"constraint_{i}"
            if not isinstance(row, dict):
                f.fail(key, "Pilih jenis constraint.")
                continue
            ctype = row.get("type")
            if not (isinstance(ctype, str) and ctype in C.CONSTRAINT_TYPES):
                f.fail(key, "Pilih jenis constraint.")
            elif ctype in seen:
                f.fail(key, "Jenis constraint ini sudah dipakai di baris lain.")
            else:
                seen.add(ctype)
            note = f.text("note", max_len=200, source=row, err_key=f"{key}_note")
            rows.append({"type": ctype, "params": {}, "note": note or None})

    reference = f.text("reference_response", max_len=3000)
    item = {
        "prompt": prompt,
        "register": register,
        "topic": topic,
        "constraints": rows,
        "reference_response": reference or None,
    }
    return item, prompt


# ---------- jenis pengetahuan ----------

def _mcq(f: _Form, d: dict) -> dict:
    raw = d.get("opsi")
    if not isinstance(raw, list) or not 3 <= len(raw) <= 5:
        f.fail("opsi", "Isi 3 sampai 5 pilihan jawaban.")
        raw = raw if isinstance(raw, list) else []
    options, seen = [], set()
    for i, value in enumerate(raw[:5]):
        key = f"opsi_{i}"
        text = value.strip() if isinstance(value, str) else ""
        if not text:
            f.fail(key, "Isi teks pilihan ini.")
            continue
        if len(text) > 200:
            f.fail(key, "Maksimal 200 karakter.")
        f.scan.append((key, text))
        norm = _normalize(text)
        if norm in seen:
            f.fail(key, "Pilihan ini sama dengan pilihan lain.")
        seen.add(norm)
        options.append(text)

    letters = "ABCDE"[: len(raw)] if 3 <= len(raw) <= 5 else ""
    kunci = d.get("kunci")
    if not (isinstance(kunci, str) and len(kunci) == 1 and kunci in letters):
        f.fail("kunci", "Pilih kunci jawaban yang benar.")
        kunci = ""
    return {"opsi": options, "kunci": kunci}


def _isian(f: _Form, d: dict) -> dict:
    kunci = f.text("kunci_jawaban", required=True, max_len=200)
    raw = d.get("varian", [])
    if isinstance(raw, str):
        items = raw.splitlines()
    elif isinstance(raw, list):
        items = raw
    else:
        f.fail("varian", "Format varian tidak valid.")
        items = []
    variants = []
    for value in items:
        if not isinstance(value, str):
            f.fail("varian", "Format varian tidak valid.")
            continue
        text = value.strip()
        if not text:
            continue
        if len(text) > 100:
            f.fail("varian", "Setiap varian maksimal 100 karakter.")
            continue
        f.scan.append(("varian", text))
        variants.append(text)
    if len(variants) > 10:
        f.fail("varian", "Maksimal 10 varian jawaban.")
    return {"kunci_jawaban": kunci, "varian": variants}


def _build_pengetahuan(f: _Form, d: dict):
    pertanyaan = f.text("pertanyaan", required=True, min_len=20, max_len=500)
    bidang = _choice(f, d, "bidang", C.BIDANG_IDS, "Pilih bidang.")
    provinsi = f.text("provinsi", max_len=60)
    tingkat = _choice(f, d, "tingkat", C.TINGKAT_IDS, "Pilih tingkat.")
    fmt = _choice(f, d, "format", C.FORMAT_IDS, "Pilih format soal.")

    item = {
        "pertanyaan": pertanyaan,
        "bidang": bidang,
        "provinsi": provinsi or None,
        "tingkat": tingkat,
        "format": fmt,
    }
    if fmt == "pilihan_ganda":
        item.update(_mcq(f, d))
    elif fmt == "jawaban_singkat":
        item.update(_isian(f, d))
    item["sumber"] = f.text("sumber", required=True, min_len=5, max_len=300)
    item["penjelasan"] = f.text("penjelasan", max_len=1000) or None
    return item, pertanyaan


# ---------- jenis sastra ----------

def _build_sastra(f: _Form, d: dict):
    tugas = f.text("tugas", required=True, min_len=20, max_len=1500)
    jenis = _choice(f, d, "jenis", C.JENIS_SASTRA_IDS, "Pilih jenis karya.")

    jumlah_bait = f.int_opt("jumlah_bait", 1, 20)
    baris_per_bait = f.int_opt("baris_per_bait", 1, 20)

    pola = f.text("pola_rima", max_len=40, scan=False)
    pola_norm = re.sub(r"\s+", "", pola.lower()) if pola else ""
    if pola_norm and not RIMA_RE.fullmatch(pola_norm):
        f.fail("pola_rima", "Pakai pola seperti a-b-a-b atau aaaa.")

    suku_min = f.int_opt("suku_kata_min", 1, 30)
    suku_max = f.int_opt("suku_kata_max", 1, 30)
    if suku_min is not None and suku_max is not None and suku_min > suku_max:
        f.fail("suku_kata_max", "Maksimal harus sama atau lebih besar dari minimal.")

    kriteria = f.text("kriteria_penilaian", required=True, min_len=20, max_len=600)
    contoh = f.text("contoh_jawaban", max_len=3000)
    sumber_contoh = f.text("sumber_contoh", max_len=300, required=bool(contoh))

    item = {
        "jenis": jenis,
        "tugas": tugas,
        "aturan": {
            "jumlah_bait": jumlah_bait,
            "baris_per_bait": baris_per_bait,
            "pola_rima": pola_norm or None,
            "suku_kata_min": suku_min,
            "suku_kata_max": suku_max,
        },
        "kriteria_penilaian": kriteria,
        "contoh_jawaban": contoh or None,
        "sumber_contoh": sumber_contoh or None,
    }
    return item, tugas


_BUILDERS = {
    "instruksi": _build_instruksi,
    "pengetahuan": _build_pengetahuan,
    "sastra": _build_sastra,
}


def validate_submission(payload, known_hashes=frozenset()):
    """Kembalikan (clean, errors). Jika errors tidak kosong, clean bernilai None.

    known_hashes: kumpulan text_sha256 yang sudah tersimpan (untuk cek duplikat).
    """
    if not isinstance(payload, dict):
        return None, {"_form": GENERIC_ERROR}

    f = _Form(payload)
    item_type = _choice(f, payload, "item_type", C.ITEM_TYPE_IDS, "Pilih jenis soal.")

    pseudonim = f.text("pseudonim", required=True, min_len=3, max_len=30, scan=False)
    if pseudonim and not PSEUDONYM_RE.fullmatch(pseudonim):
        f.fail("pseudonim", "Pakai huruf, angka, dan garis bawah (_) saja.")

    partner = _choice(f, payload, "partner", PARTNER_CHOICES, "Pilih komunitas atau kampus asal.")
    partner_lain = None
    if partner == C.PARTNER_OTHER:
        partner_lain = f.text("partner_lain", required=True, min_len=2, max_len=60)

    email = f.text("email", max_len=120, scan=False)
    if email and not EMAIL_RE.fullmatch(email):
        f.fail("email", "Format email belum benar.")

    consent_raw = payload.get("consent")
    consent = {}
    for key in CONSENT_KEYS:
        ok = isinstance(consent_raw, dict) and consent_raw.get(key) is True
        consent[key] = ok
        if not ok:
            f.fail(f"consent_{key}", "Centang persetujuan ini untuk melanjutkan.")

    item, main_text = {}, ""
    if item_type in _BUILDERS:
        item, main_text = _BUILDERS[item_type](f, payload)

    for key, value in f.scan:
        if EMAIL_RE.search(value) or PHONE_RE.search(value) or NIK_RE.search(value):
            f.fail(key, PII_MESSAGE)

    text_hash = None
    if item_type in MAIN_KEY and main_text:
        text_hash = text_sha256(main_text)
        if text_hash in known_hashes:
            f.fail(MAIN_KEY[item_type], "Soal ini mirip dengan soal yang sudah pernah dikirim.")

    if f.errors:
        return None, dict(f.errors)

    clean = {
        "item_type": item_type,
        "pseudonim": pseudonim,
        "partner": partner,
        "partner_lain": partner_lain,
        "email": email or None,
        "consent": consent,
        "item": item,
        "text_sha256": text_hash,
    }
    return clean, {}


def build_record(clean: dict, submission_id: str, now: datetime | None = None):
    """Kembalikan (record, contact). Email hanya ada di contact, tidak di record."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    record = {
        "submission_id": submission_id,
        "item_type": clean["item_type"],
        "author_id": clean["pseudonim"],
        "partner": clean["partner"],
        "partner_lain": clean["partner_lain"],
        "submitted_at": now.isoformat(timespec="seconds"),
        "consent": clean["consent"],
        "text_sha256": clean["text_sha256"],
        "status": "pending_review",
        "reviewers": [],
        "split": None,
        "version": "2026Q4",
        "item": clean["item"],
    }
    contact = {
        "submission_id": submission_id,
        "author_id": clean["pseudonim"],
        "email": clean["email"],
    }
    return record, contact
