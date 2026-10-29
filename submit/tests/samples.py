"""Contoh data uji. Semua teks diawali "TEST:" supaya jelas bukan soal sungguhan."""

import copy

CONSENT_ALL = {
    "tanpa_ai": True,
    "data_pribadi": True,
    "sara_medis_hukum": True,
    "bukan_salinan": True,
    "lisensi_cc_by": True,
}


def _with(base: dict, **over) -> dict:
    data = copy.deepcopy(base)
    data.update(over)
    return data


def common(**over) -> dict:
    base = {
        "item_type": "instruksi",
        "pseudonim": "uji_penulis",
        "partner": "Mandiri",
        "partner_lain": "",
        "email": "",
        "website": "",
        "consent": dict(CONSENT_ALL),
    }
    return _with(base, **over)


def instruksi(**over) -> dict:
    base = common(
        item_type="instruksi",
        prompt="TEST: Tulis satu kalimat promo kopi untuk uji validasi sistem.",
        register="santai",
        topic="kuliner",
        constraints=[{"type": "word_count", "note": "TEST: maksimal 20 kata"}],
        reference_response="",
    )
    return _with(base, **over)


def pengetahuan(**over) -> dict:
    base = common(
        item_type="pengetahuan",
        pertanyaan="TEST: Pertanyaan uji coba untuk validasi sistem, bukan soal sungguhan.",
        bidang="sejarah",
        provinsi="",
        tingkat="umum",
        format="pilihan_ganda",
        opsi=["TEST: pilihan A", "TEST: pilihan B", "TEST: pilihan C"],
        kunci="B",
        kunci_jawaban="",
        varian="",
        sumber="TEST: sumber uji coba",
        penjelasan="",
    )
    return _with(base, **over)


def pengetahuan_singkat(**over) -> dict:
    base = {
        "format": "jawaban_singkat",
        "opsi": [],
        "kunci": "",
        "kunci_jawaban": "TEST: jawaban uji",
        "varian": "TEST: varian satu\nTEST: varian dua",
    }
    base.update(over)
    return pengetahuan(**base)


def sastra(**over) -> dict:
    base = common(
        item_type="sastra",
        jenis="pantun",
        tugas="TEST: Tulis pantun uji coba untuk validasi sistem.",
        jumlah_bait=1,
        baris_per_bait=4,
        pola_rima="a-b-a-b",
        suku_kata_min=None,
        suku_kata_max=None,
        kriteria_penilaian="TEST: kriteria uji coba untuk validasi sistem.",
        contoh_jawaban="",
        sumber_contoh="",
    )
    return _with(base, **over)
