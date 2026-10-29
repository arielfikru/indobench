"""Daftar pilihan yang dipakai bersama oleh halaman (lewat GET /api/catalog) dan validate.py.

Semua daftar hidup di file ini. Jangan menyalin kode atau kunci ke tempat lain.
"""

ITEM_TYPES = [
    {
        "id": "instruksi",
        "label": "Instruksi (IFEval-ID)",
        "desc": "Permintaan ke asisten AI dengan 1 sampai 4 aturan yang bisa dicek otomatis.",
    },
    {
        "id": "pengetahuan",
        "label": "Pengetahuan",
        "desc": "Pertanyaan fakta dalam bahasa Indonesia, pilihan ganda atau isian singkat.",
    },
    {
        "id": "sastra",
        "label": "Sastra",
        "desc": "Tugas menulis pantun, syair, gurindam, puisi, atau analisis karya.",
    },
]

REGISTERS = [
    {"id": "baku", "label": "Baku", "desc": "Bahasa resmi sesuai EYD, seperti surat dinas."},
    {"id": "santai", "label": "Santai", "desc": "Bahasa sehari-hari yang sopan, tidak kaku."},
    {"id": "gaul", "label": "Gaul", "desc": "Slang dan gaya bicara anak muda."},
    {"id": "campur", "label": "Campur kode", "desc": "Bahasa Indonesia bercampur bahasa Inggris atau bahasa daerah."},
]

TOPICS = [
    {"id": "umkm", "label": "UMKM dan jualan"},
    {"id": "administrasi", "label": "Administrasi (KTP, SIM, BPJS)"},
    {"id": "kuliner", "label": "Kuliner"},
    {"id": "transportasi", "label": "Transportasi dan mudik"},
    {"id": "kampus", "label": "Kampus dan sekolah"},
    {"id": "kerja", "label": "Kerja dan karier"},
    {"id": "keuangan", "label": "Keuangan sehari-hari"},
    {"id": "teknologi", "label": "Teknologi dan gadget"},
    {"id": "hiburan", "label": "Hiburan (anime, game, musik)"},
    {"id": "komunitas", "label": "Komunitas dan acara"},
    {"id": "keluarga", "label": "Keluarga dan pertemanan"},
]

PARTNERS = ["Mandiri"]
PARTNER_OTHER = "Lainnya"

BIDANG = [
    {"id": "sejarah", "label": "Sejarah"},
    {"id": "geografi", "label": "Geografi"},
    {"id": "budaya", "label": "Budaya"},
    {"id": "tata_bahasa", "label": "Tata bahasa"},
    {"id": "sastra", "label": "Sastra"},
    {"id": "lainnya", "label": "Lainnya"},
]

TINGKAT = [
    {"id": "sd", "label": "SD"},
    {"id": "smp", "label": "SMP"},
    {"id": "sma", "label": "SMA"},
    {"id": "umum", "label": "Umum"},
    {"id": "ahli", "label": "Ahli"},
]

FORMATS = [
    {"id": "pilihan_ganda", "label": "Pilihan ganda", "desc": "3 sampai 5 pilihan, satu jawaban benar."},
    {"id": "jawaban_singkat", "label": "Isian singkat", "desc": "Jawaban pendek yang bisa dicek dengan kunci jawaban."},
]

JENIS_SASTRA = [
    {"id": "pantun", "label": "Pantun"},
    {"id": "syair", "label": "Syair"},
    {"id": "gurindam", "label": "Gurindam"},
    {"id": "puisi_bebas", "label": "Puisi bebas"},
    {"id": "cerpen_mini", "label": "Cerpen mini"},
    {"id": "analisis_karya", "label": "Analisis karya"},
]

CONSENTS = [
    {"id": "tanpa_ai", "label": "Saya menulis soal ini sendiri tanpa bantuan AI."},
    {"id": "data_pribadi", "label": "Soal ini tidak berisi data pribadi asli: nama orang nyata yang bukan tokoh publik, nomor HP, alamat, atau NIK."},
    {"id": "sara_medis_hukum", "label": "Soal ini tidak menyinggung SARA dan tidak berisi saran medis atau hukum yang spesifik."},
    {"id": "bukan_salinan", "label": "Saya tidak menyalin karya orang lain. Kalau memakai karya domain publik, sumbernya saya cantumkan."},
    {"id": "lisensi_cc_by", "label": "Saya setuju soal ini dilisensikan CC BY 4.0 dan boleh disimpan sebagai data privat yang tidak dipublikasikan."},
]

CATEGORIES = [
    {"id": "A", "label": "Register dan sapaan"},
    {"id": "B", "label": "Bahasa dan campur kode"},
    {"id": "C", "label": "Format lokal (EYD)"},
    {"id": "D", "label": "Bentuk budaya"},
    {"id": "E", "label": "Struktur dan format umum"},
]

# 25 jenis constraint dari spec (bagian 5). Contoh frasa diambil dari spec bila ada;
# untuk kategori E, frasa contoh ditulis sebagai bentuk perintah umum.
_CONSTRAINT_ROWS = [
    ("register_informal", "A", "Pakai bahasa santai atau gaul", "jawab pakai bahasa santai/gaul"),
    ("register_formal", "A", "Pakai bahasa baku sesuai EYD", "jawab dengan bahasa baku sesuai EYD"),
    ("no_chat_abbrev", "A", "Tanpa singkatan chat", "jangan pakai singkatan kayak yg, gk, bgt"),
    ("pronoun_required", "A", "Pakai pasangan kata ganti tertentu", "pakai gue-lo"),
    ("honorific_address", "A", "Sapa dengan sapaan tertentu", "panggil aku Kak Rina"),
    ("no_english_words", "B", "Tanpa kata bahasa Inggris", "jangan ada kata bahasa Inggris"),
    ("code_mix_required", "B", "Wajib campur kode dengan Inggris", "jawab gaya anak Jaksel, campur Inggris"),
    ("regional_words_required", "B", "Wajib kosakata daerah (eksperimental)", "selipin minimal 2 kata bahasa Jawa"),
    ("language_only", "B", "Hanya satu bahasa (eksperimental)", "jawab pakai bahasa Sunda aja"),
    ("rupiah_format", "C", "Format Rupiah yang benar", "tulis harganya pakai format Rupiah yang bener"),
    ("date_format_id", "C", "Format tanggal Indonesia", "tulis tanggalnya lengkap"),
    ("time_format_id", "C", "Format jam dan zona waktu", "sebutin jamnya, pakai zona waktu"),
    ("decimal_comma", "C", "Angka desimal dan ribuan yang benar", "tulis angka desimalnya yang bener"),
    ("pantun_abab", "D", "Pantun berpola ABAB", "tutup pakai satu pantun"),
    ("peribahasa_included", "D", "Sertakan peribahasa", "selipin satu peribahasa yang nyambung"),
    ("word_count", "E", "Batas jumlah kata", "maksimal 40 kata"),
    ("sentence_count", "E", "Batas jumlah kalimat", "maksimal 3 kalimat"),
    ("paragraph_count", "E", "Jumlah paragraf", "tulis dalam 3 paragraf"),
    ("bullet_count", "E", "Jumlah poin bullet", "pakai 4 poin bullet"),
    ("json_format", "E", "Jawaban berformat JSON", "jawab dalam format JSON"),
    ("opening_closing", "E", "Kalimat pembuka atau penutup", "mulai dan akhiri dengan kalimat tertentu"),
    ("keyword_include", "E", "Wajib memuat kata kunci", "wajib sebut kata tertentu minimal 2 kali"),
    ("keyword_exclude", "E", "Dilarang memuat kata tertentu", "jangan sebut kata tertentu sama sekali"),
    ("letter_case", "E", "Semua huruf kecil atau kapital", "tulis semua huruf kecil"),
    ("no_emoji", "E", "Tanpa emoji", "jangan pakai emoji"),
]

CONSTRAINTS = [
    {"type": t, "category": c, "label": label, "example": example}
    for (t, c, label, example) in _CONSTRAINT_ROWS
]


def _ids(items):
    return frozenset(item["id"] for item in items)


ITEM_TYPE_IDS = _ids(ITEM_TYPES)
REGISTER_IDS = _ids(REGISTERS)
TOPIC_IDS = _ids(TOPICS)
BIDANG_IDS = _ids(BIDANG)
TINGKAT_IDS = _ids(TINGKAT)
FORMAT_IDS = _ids(FORMATS)
JENIS_SASTRA_IDS = _ids(JENIS_SASTRA)
CONSENT_IDS = _ids(CONSENTS)
CONSTRAINT_TYPES = frozenset(c["type"] for c in CONSTRAINTS)

assert len(CONSTRAINTS) == 25, "spec mengharuskan 25 jenis constraint"
assert len(CONSTRAINT_TYPES) == 25, "jenis constraint harus unik"


def public_catalog() -> dict:
    """Bentuk JSON yang dikirim ke halaman di GET /api/catalog."""
    return {
        "version": "2026Q4",
        "item_types": ITEM_TYPES,
        "registers": REGISTERS,
        "topics": TOPICS,
        "partners": PARTNERS,
        "partner_other": PARTNER_OTHER,
        "bidang": BIDANG,
        "tingkat": TINGKAT,
        "formats": FORMATS,
        "jenis_sastra": JENIS_SASTRA,
        "consents": CONSENTS,
        "categories": CATEGORIES,
        "constraints": CONSTRAINTS,
    }
