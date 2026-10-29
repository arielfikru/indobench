import json
from datetime import datetime, timezone

import pytest

import catalog
from samples import CONSENT_ALL, common, instruksi, pengetahuan, pengetahuan_singkat, sastra
from validate import (
    build_record,
    honeypot_filled,
    text_sha256,
    validate_submission,
)


def ok(payload, known=frozenset()):
    clean, errors = validate_submission(payload, known)
    assert errors == {}, errors
    assert clean is not None
    return clean


def errs(payload, known=frozenset()):
    clean, errors = validate_submission(payload, known)
    assert clean is None
    assert errors, "harus ada error"
    return errors


# ---------- kasus sukses ----------

def test_valid_instruksi_passes():
    clean = ok(instruksi())
    assert clean["item_type"] == "instruksi"
    assert clean["item"]["constraints"] == [
        {"type": "word_count", "params": {}, "note": "TEST: maksimal 20 kata"}
    ]
    assert clean["text_sha256"] == text_sha256(instruksi()["prompt"])


def test_valid_pengetahuan_mcq_passes():
    clean = ok(pengetahuan())
    assert clean["item"]["opsi"] == ["TEST: pilihan A", "TEST: pilihan B", "TEST: pilihan C"]
    assert clean["item"]["kunci"] == "B"


def test_valid_pengetahuan_singkat_passes():
    clean = ok(pengetahuan_singkat())
    assert clean["item"]["varian"] == ["TEST: varian satu", "TEST: varian dua"]
    assert "opsi" not in clean["item"]


def test_valid_sastra_passes():
    clean = ok(sastra())
    assert clean["item"]["aturan"]["pola_rima"] == "a-b-a-b"
    assert clean["item"]["contoh_jawaban"] is None


def test_valid_sastra_with_example_needs_source():
    errors = errs(sastra(contoh_jawaban="TEST: contoh jawaban uji"))
    assert "sumber_contoh" in errors
    clean = ok(sastra(contoh_jawaban="TEST: contoh jawaban uji", sumber_contoh="karya saya sendiri"))
    assert clean["item"]["sumber_contoh"] == "karya saya sendiri"


# ---------- kolom umum ----------

def test_unknown_item_type_rejected():
    assert "item_type" in errs(common(item_type="lainnya"))


def test_item_type_must_be_string():
    assert "item_type" in errs(common(item_type=["instruksi"]))


@pytest.mark.parametrize("name", ["ab", "nama dengan spasi", "nama-strip", "x" * 31, ""])
def test_pseudonim_invalid(name):
    assert "pseudonim" in errs(instruksi(pseudonim=name))


def test_pseudonim_valid_edges():
    ok(instruksi(pseudonim="abc"))
    ok(instruksi(pseudonim="x" * 30))
    ok(instruksi(pseudonim="penulis_0042"))


def test_partner_unknown_rejected():
    assert "partner" in errs(instruksi(partner="Bank Lain"))


def test_partner_lainnya_requires_text():
    assert "partner_lain" in errs(instruksi(partner="Lainnya", partner_lain=""))
    clean = ok(instruksi(partner="Lainnya", partner_lain="Komunitas Uji"))
    assert clean["partner_lain"] == "Komunitas Uji"


def test_email_optional_but_checked_when_given():
    assert ok(instruksi(email=""))["email"] is None
    assert ok(instruksi(email="penulis@contoh.test"))["email"] == "penulis@contoh.test"
    assert "email" in errs(instruksi(email="bukan-email"))


@pytest.mark.parametrize("key", ["tanpa_ai", "data_pribadi", "sara_medis_hukum", "bukan_salinan", "lisensi_cc_by"])
def test_each_consent_required(key):
    consent = dict(CONSENT_ALL)
    consent[key] = False
    assert f"consent_{key}" in errs(instruksi(consent=consent))


def test_consent_must_be_literal_true():
    consent = dict(CONSENT_ALL)
    consent["tanpa_ai"] = "ya"
    assert "consent_tanpa_ai" in errs(instruksi(consent=consent))


def test_missing_consent_block_rejected():
    payload = instruksi()
    del payload["consent"]
    errors = errs(payload)
    assert all(f"consent_{k}" in errors for k in ["tanpa_ai", "data_pribadi", "sara_medis_hukum", "bukan_salinan", "lisensi_cc_by"])


def test_non_dict_payload_rejected():
    clean, errors = validate_submission(["bukan", "objek"])
    assert clean is None and "_form" in errors


# ---------- instruksi ----------

def test_instruksi_prompt_length_bounds():
    assert "prompt" in errs(instruksi(prompt="terlalu pendek"))
    assert "prompt" in errs(instruksi(prompt="TEST: " + "a" * 1000))
    ok(instruksi(prompt="TEST: " + "a" * 994))


def test_instruksi_prompt_required():
    assert "prompt" in errs(instruksi(prompt="   "))


def test_instruksi_register_must_be_valid():
    assert "register" in errs(instruksi(register="formal"))
    for reg in ["baku", "santai", "gaul", "campur"]:
        ok(instruksi(register=reg))


def test_instruksi_topic_must_be_valid():
    assert "topic" in errs(instruksi(topic="politik"))


def test_instruksi_constraints_count_bounds():
    assert "constraints" in errs(instruksi(constraints=[]))
    five = [{"type": t, "note": ""} for t in [
        "word_count", "sentence_count", "paragraph_count", "bullet_count", "no_emoji"]]
    assert "constraints" in errs(instruksi(constraints=five))
    four = [{"type": t, "note": ""} for t in [
        "word_count", "sentence_count", "paragraph_count", "no_emoji"]]
    ok(instruksi(constraints=four))


def test_instruksi_constraint_type_must_exist():
    assert "constraint_0" in errs(instruksi(constraints=[{"type": "tidak_ada", "note": ""}]))


def test_instruksi_constraint_type_must_be_string():
    assert "constraint_0" in errs(instruksi(constraints=[{"type": ["word_count"], "note": ""}]))


def test_instruksi_duplicate_constraint_type_rejected():
    constraints = [{"type": "word_count", "note": ""}, {"type": "word_count", "note": "x"}]
    errors = errs(instruksi(constraints=constraints))
    assert "constraint_1" in errors and "constraint_0" not in errors


def test_instruksi_constraint_row_not_dict():
    assert "constraint_0" in errs(instruksi(constraints=["word_count"]))


def test_instruksi_constraint_note_max_length():
    constraints = [{"type": "word_count", "note": "x" * 201}]
    assert "constraint_0_note" in errs(instruksi(constraints=constraints))


def test_instruksi_all_25_types_accepted_one_by_one():
    for c in catalog.CONSTRAINTS:
        ok(instruksi(constraints=[{"type": c["type"], "note": ""}]))


def test_instruksi_reference_response_optional_and_bounded():
    assert ok(instruksi(reference_response=""))["item"]["reference_response"] is None
    assert "reference_response" in errs(instruksi(reference_response="x" * 3001))


# ---------- pengetahuan ----------

def test_pengetahuan_question_bounds():
    assert "pertanyaan" in errs(pengetahuan(pertanyaan="pendek"))
    assert "pertanyaan" in errs(pengetahuan(pertanyaan="TEST: " + "a" * 500))


def test_pengetahuan_bidang_tingkat_format_checked():
    assert "bidang" in errs(pengetahuan(bidang="matematika"))
    assert "tingkat" in errs(pengetahuan(tingkat="kuliah"))
    assert "format" in errs(pengetahuan(format="esai"))


def test_pengetahuan_sumber_required():
    assert "sumber" in errs(pengetahuan(sumber=""))
    assert "sumber" in errs(pengetahuan(sumber="abc"))


def test_mcq_needs_at_least_three_options():
    assert "opsi" in errs(pengetahuan(opsi=["TEST: A", "TEST: B"]))


def test_mcq_at_most_five_options():
    six = [f"TEST: pilihan {i}" for i in range(6)]
    assert "opsi" in errs(pengetahuan(opsi=six, kunci="A"))


def test_mcq_five_options_allowed():
    five = [f"TEST: pilihan {i}" for i in range(5)]
    ok(pengetahuan(opsi=five, kunci="E"))


def test_mcq_empty_option_rejected():
    assert "opsi_1" in errs(pengetahuan(opsi=["TEST: A", "   ", "TEST: C"], kunci="A"))


def test_mcq_distinct_options_case_insensitive():
    assert "opsi_2" in errs(pengetahuan(opsi=["TEST: Satu", "TEST: Dua", "test:  satu"], kunci="A"))


def test_mcq_kunci_must_point_to_existing_option():
    assert "kunci" in errs(pengetahuan(opsi=["TEST: A", "TEST: B", "TEST: C"], kunci="D"))
    assert "kunci" in errs(pengetahuan(kunci=""))
    assert "kunci" in errs(pengetahuan(kunci="BB"))


def test_mcq_option_length_limit():
    assert "opsi_0" in errs(pengetahuan(opsi=["TEST: " + "a" * 200, "TEST: B", "TEST: C"], kunci="A"))


def test_singkat_requires_kunci_jawaban():
    assert "kunci_jawaban" in errs(pengetahuan_singkat(kunci_jawaban=""))


def test_singkat_varian_limit_and_length():
    many = "\n".join(f"TEST: v{i}" for i in range(11))
    assert "varian" in errs(pengetahuan_singkat(varian=many))
    assert "varian" in errs(pengetahuan_singkat(varian="x" * 101))


def test_singkat_varian_accepts_list():
    clean = ok(pengetahuan_singkat(varian=["TEST: satu", ""]))
    assert clean["item"]["varian"] == ["TEST: satu"]


def test_pengetahuan_provinsi_optional():
    assert ok(pengetahuan(provinsi=""))["item"]["provinsi"] is None
    assert "provinsi" in errs(pengetahuan(provinsi="x" * 61))


# ---------- sastra ----------

def test_sastra_tugas_bounds():
    assert "tugas" in errs(sastra(tugas="pendek"))
    assert "tugas" in errs(sastra(tugas="TEST: " + "a" * 1500))


def test_sastra_jenis_checked():
    assert "jenis" in errs(sastra(jenis="novel"))


def test_sastra_bait_and_baris_ranges():
    assert "jumlah_bait" in errs(sastra(jumlah_bait=0))
    assert "jumlah_bait" in errs(sastra(jumlah_bait=21))
    assert "baris_per_bait" in errs(sastra(baris_per_bait=99))
    assert "jumlah_bait" in errs(sastra(jumlah_bait="dua"))
    assert "jumlah_bait" in errs(sastra(jumlah_bait=True))


def test_sastra_numeric_strings_accepted():
    clean = ok(sastra(jumlah_bait="2", baris_per_bait="4"))
    assert clean["item"]["aturan"]["jumlah_bait"] == 2


def test_sastra_rhyme_pattern():
    assert ok(sastra(pola_rima="A - B - A - B"))["item"]["aturan"]["pola_rima"] == "a-b-a-b"
    assert ok(sastra(pola_rima="aaaa"))["item"]["aturan"]["pola_rima"] == "aaaa"
    assert "pola_rima" in errs(sastra(pola_rima="1-2-1-2"))
    assert "pola_rima" in errs(sastra(pola_rima="abcdefghijklmnopqrs"))


def test_sastra_suku_kata_range_order():
    assert "suku_kata_max" in errs(sastra(suku_kata_min=12, suku_kata_max=8))
    ok(sastra(suku_kata_min=8, suku_kata_max=12))
    ok(sastra(suku_kata_min=8, suku_kata_max=None))


def test_sastra_suku_kata_bounds():
    assert "suku_kata_min" in errs(sastra(suku_kata_min=0))


def test_sastra_kriteria_required():
    assert "kriteria_penilaian" in errs(sastra(kriteria_penilaian="pendek"))


def test_sastra_example_requires_source_only_when_present():
    ok(sastra(contoh_jawaban="", sumber_contoh=""))
    assert "sumber_contoh" in errs(sastra(contoh_jawaban="TEST: contoh", sumber_contoh=""))


# ---------- data pribadi ----------

@pytest.mark.parametrize("text", [
    "TEST: hubungi saya di 081234567890 untuk uji coba",
    "TEST: nomor saya +62 812-3456-7890 untuk uji",
    "TEST: nomor 0812 3456 7890 untuk uji coba",
])
def test_phone_numbers_rejected(text):
    assert "prompt" in errs(instruksi(prompt=text))


def test_nik_rejected():
    assert "prompt" in errs(instruksi(prompt="TEST: NIK uji 3201123456789012 untuk validasi"))


def test_email_in_text_rejected():
    assert "prompt" in errs(instruksi(prompt="TEST: kirim ke uji@contoh.test untuk validasi"))


def test_pii_in_other_text_field_points_to_that_field():
    errors = errs(pengetahuan(sumber="TEST: sumber, hubungi 081234567890"))
    assert "sumber" in errors


def test_prices_and_years_not_flagged():
    ok(instruksi(prompt="TEST: harga kopi Rp18.000 dan total 1.250.000 tahun 2026, pukul 08.30"))


# ---------- duplikat ----------

def test_duplicate_detected_ignoring_case_and_spacing():
    known = {text_sha256(instruksi()["prompt"])}
    variant = "  TEST:   TULIS satu kalimat promo kopi untuk uji validasi sistem.  "
    errors = errs(instruksi(prompt=variant), known)
    assert "prompt" in errors


def test_duplicate_not_flagged_for_new_text():
    known = {text_sha256("TEST: sudah ada di sistem lain.")}
    ok(instruksi(), known)


def test_duplicate_check_uses_pertanyaan_for_pengetahuan():
    known = {text_sha256(pengetahuan()["pertanyaan"])}
    assert "pertanyaan" in errs(pengetahuan(), known)


# ---------- honeypot ----------

def test_honeypot_detection():
    assert honeypot_filled({"website": "https://spam.test"}) is True
    assert honeypot_filled({"website": ""}) is False
    assert honeypot_filled({}) is False
    assert honeypot_filled("bukan dict") is False


# ---------- record ----------

def test_record_has_spec_fields_and_no_email():
    payload = instruksi(email="penulis@contoh.test", partner="Lainnya", partner_lain="Komunitas Uji")
    clean = ok(payload)
    now = datetime(2026, 10, 29, 3, 0, 0, tzinfo=timezone.utc)
    record, contact = build_record(clean, "sub-0123456789", now)

    assert set(record) == {
        "submission_id", "item_type", "author_id", "partner", "partner_lain", "submitted_at",
        "consent", "text_sha256", "status", "reviewers", "split", "version", "item",
    }
    assert record["status"] == "pending_review"
    assert record["reviewers"] == []
    assert record["split"] is None
    assert record["version"] == "2026Q4"
    assert record["author_id"] == "uji_penulis"
    assert record["submitted_at"] == "2026-10-29T03:00:00+00:00"
    assert record["consent"] == CONSENT_ALL
    assert contact == {"submission_id": "sub-0123456789", "author_id": "uji_penulis", "email": "penulis@contoh.test"}


def test_email_never_in_record_json():
    clean = ok(instruksi(email="rahasia@contoh.test"))
    record, _ = build_record(clean, "sub-aaaaaaaaaa")
    dumped = json.dumps(record, ensure_ascii=False)
    assert "rahasia@contoh.test" not in dumped
    assert "email" not in record


def test_record_item_matches_spec_shape_for_instruksi():
    clean = ok(instruksi())
    record, _ = build_record(clean, "sub-aaaaaaaaaa")
    item = record["item"]
    assert set(item) == {"prompt", "register", "topic", "constraints", "reference_response"}
    assert set(item["constraints"][0]) == {"type", "params", "note"}
