# Spesifikasi IFEval-ID-Gaul v0.1

## 1. Tujuan
Benchmark instruction following bahasa Indonesia lintas register (baku, santai, gaul, campur kode). Model diberi permintaan realistis yang memuat 1–4 constraint, lalu setiap constraint dicek oleh kode deterministik tanpa juri LLM.

Benchmark ini mengukur kepatuhan pada constraint, bukan kualitas isi jawaban. Kualitas isi diukur terpisah (IndoChat, fase berikutnya) dan dilaporkan berdampingan.

## 2. Skema data (JSONL, satu item per baris)
```json
{
  "id": "ifg-0001",
  "prompt": "Bikinin caption IG buat promo kopi susu gula aren harga 18 ribu. Pakai bahasa gaul, maksimal 40 kata, tulis harganya pakai format Rupiah yang bener, jangan ada kata bahasa Inggris",
  "register": "gaul",
  "topic": "umkm",
  "constraints": [
    {"type": "word_count", "params": {"max": 40}},
    {"type": "rupiah_format", "params": {"expected_amount": 18000}},
    {"type": "no_english_words", "params": {}},
    {"type": "register_informal", "params": {"min_markers": 2}}
  ],
  "split": "private",
  "version": "2026Q4",
  "author_id": "w017",
  "reviewers": ["r003", "r011"],
  "reference_response": "..."
}
```
- `register`: `baku` | `santai` | `gaul` | `campur`
- `split`: `public` | `private`
- `author_id` dan `reviewers` berupa pseudonim, bukan nama asli.
- `reference_response` opsional, kecuali untuk batch 1 (lihat bagian 7).

## 3. Prapemrosesan respons
- Selalu: hapus blok thinking (`<think>...</think>` dan penanda lain yang tercatat di `configs/models.yaml`).
- **Strict:** respons dinilai apa adanya setelah langkah di atas.
- **Loose (default, mengikuti konvensi IFEval):** constraint dianggap lolos kalau lolos di salah satu varian berikut:
  1. respons asli
  2. tanpa markdown emphasis (`**`, `*`, `_`, backtick)
  3. tanpa baris pertama
  4. tanpa baris terakhir
  5. kombinasi 2 dengan 3 atau 4

  Pencocokan teks di mode loose bersifat case-insensitive, kecuali constraint yang memang menguji huruf kapital.
- Beberapa constraint punya relaksasi loose tambahan. Itu disebut di masing-masing constraint.

## 4. Komponen bersama (`indobench/verifiers/common/`)
- **Tokenizer kata:**
  - Pisah di whitespace, buang tanda baca di tepi token.
  - Reduplikasi dengan tanda hubung dihitung 1 kata (`rumah-rumah`, `sayur-mayur`).
  - Angka, URL, dan email masing-masing 1 kata.
  - Klitik (`-nya`, `-lah`, `-kah`, `-pun`) tetap menempel.
- **Pemecah kalimat:**
  - Pisah di `.`, `?`, `!`.
  - Kecualikan singkatan baku dari `lexicons/singkatan_baku.txt` (dll., dsb., dst., tsb., hlm., No., Dr., Prof., Bpk., s.d.).
  - Kecualikan angka seperti `14.30`, `1.250`, `3,5`.
- **Penghitung suku kata (rule-based):**
  - Hitung inti vokal.
  - `ai`, `au`, `oi`, `ei` dihitung satu suku kata hanya di akhir kata (`pantai`, `pulau`, `amboi`, `survei`). Di tempat lain dihitung dua (`ma-in`, `a-ir`, `ka-in`).
- **Stemmer:** Sastrawi (PySastrawi), untuk mode pencocokan `lemma`.
- **Language ID:** GlotLID atau fastText LID dengan versi model di-pin. Hanya dipakai di `language_only`, dan opsional di `regional_words_required`.
- **Leksikon:**
  - Semua leksikon versi-terkunci di `lexicons/`, dengan README yang mencatat sumber dan lisensi tiap file.
  - Jangan scrape KBBI Daring. Pakai sumber berlisensi terbuka dan catat lisensinya.
  - File yang dibutuhkan: `informal_markers.txt`, `informal_suffix_in.txt`, `chat_abbrev.txt`, `singkatan_baku.txt`, `id_words.txt`, `serapan_allowlist.txt`, `ambiguous.txt`, `en_words.txt`, `jv_words.txt`, `su_words.txt`, `betawi_words.txt`, `peribahasa.txt`, `bulan.txt`.
- **Deteksi emoji:** data Unicode emoji (misalnya paket `emoji`), termasuk ZWJ sequence.

## 5. Taksonomi constraint (25 jenis)
Format tiap entri: contoh instruksi di prompt → params → aturan strict → relaksasi loose tambahan (kalau ada) → catatan.

### A. Register dan sapaan

**A1 `register_informal`**
- Contoh: "jawab pakai bahasa santai/gaul"
- Params: `min_markers` (default 2)
- Strict:
  - Penanda dari `informal_markers.txt` muncul minimal `min_markers` kali (contoh penanda: gue, gw, lo, lu, banget, aja, udah, nggak, gak, enggak, kok, dong, sih, deh, nih, kayak, bikin, pengen, gimana).
  - Verba bersufiks `-in` dari `informal_suffix_in.txt` (beliin, kasihin) ikut dihitung sebagai penanda.
  - Kata "Anda" tidak muncul sama sekali.
- Loose: minimal 1 penanda.

**A2 `register_formal`**
- Contoh: "jawab dengan bahasa baku sesuai EYD"
- Strict: tidak ada kemunculan `informal_markers` maupun `chat_abbrev`.
- Loose: maksimal 1 kemunculan.
- Catatan: singkatan baku (dll., dsb.) diizinkan.

**A3 `no_chat_abbrev`**
- Contoh: "jangan pakai singkatan kayak yg, gk, bgt"
- Strict: tidak ada token dari `chat_abbrev.txt` (yg, dgn, utk, krn, bgt, gpp, jd, sm, tdk, blm, sdh, otw, btw, wkwk).

**A4 `pronoun_required`**
- Contoh: "pakai gue-lo", "pakai aku-kamu", "pakai saya-Anda"
- Params: `required` (daftar set kata ganti yang wajib muncul)
- Set kata ganti:
  - gue = {gue, gw, gua}
  - lo = {lo, lu, elo, elu}
  - aku = {aku}
  - kamu = {kamu}
  - saya = {saya}
  - Anda = {Anda}
- Strict: semua set di `required` muncul minimal sekali, dan set dari pasangan lain sama sekali tidak muncul.
- Loose: cukup set pasangan lain tidak muncul.
- Catatan: klitik `-ku`/`-mu` tidak dihitung di v0.1 karena terlalu banyak false positive (ilmu, jamu, temu, palu).

**A5 `honorific_address`**
- Contoh: "panggil aku Kak Rina"
- Params: `sapaan` (Kak | Bapak | Ibu | Mas | Mbak | Bang), `name` (opsional)
- Strict: string "Sapaan Nama" (atau "Sapaan" saja kalau tanpa nama) muncul minimal sekali, dengan huruf kapital sesuai EYD.

### B. Bahasa dan campur kode

**B1 `no_english_words`**
- Contoh: "jangan ada kata bahasa Inggris"
- Strict: tidak ada token yang terdapat di `en_words` sekaligus tidak terdapat di `id_words` ∪ `serapan_allowlist`.
  - Token berhuruf kapital di tengah kalimat dianggap nama diri dan dilewati.
  - Token di `ambiguous.txt` tidak dihitung.
- Loose: maksimal 1 pelanggaran.
- Catatan: allowlist kata serapan mencakup kata seperti kopi, promo, internet, data, bank, video, film, menu, hotel.

**B2 `code_mix_required`**
- Contoh: "jawab gaya anak Jaksel, campur Inggris"
- Params: `min_en` (default 3), `min_id_ratio` (default 0,6)
- Strict: minimal `min_en` token Inggris murni, dan proporsi token Indonesia minimal `min_id_ratio`.
- Loose: cukup syarat `min_en`.

**B3 `regional_words_required`** (eksperimental)
- Contoh: "selipin minimal 2 kata bahasa Jawa"
- Params: `language` (jv | su | betawi), `min_count`
- Strict: minimal `min_count` token unik dari leksikon bahasa itu yang tidak ada di `id_words`.
- Loose: minimal 1.
- Catatan: kosakata Betawi banyak tumpang tindih dengan bahasa informal Jakarta. Tetap eksperimental sampai lolos validasi manusia.

**B4 `language_only`** (eksperimental untuk jv dan su)
- Contoh: "jawab pakai bahasa Sunda aja"
- Params: `language` (id | jv | su)
- Strict: semua kalimat dengan minimal 3 kata diprediksi LID sebagai bahasa target.
- Loose: minimal 80% kalimat.

### C. Format lokal (EYD)

**C1 `rupiah_format`**
- Contoh: "tulis harganya pakai format Rupiah yang bener"
- Params: `expected_amount` (opsional, integer rupiah)
- Strict:
  - Setiap penyebutan uang cocok dengan salah satu pola:
    - `Rp\d{1,3}(\.\d{3})*(,\d{2})?` (contoh: Rp18.000, Rp18.000,00)
    - `Rp\d+(,\d+)? (ribu|juta|miliar|triliun)` (contoh: Rp2,5 juta)
  - Tidak ada pola salah: `Rp ` (dengan spasi), `Rp.`, `IDR`, `\d+rb`, `\d+k` dalam konteks harga, atau ribuan dipisah koma.
  - Kalau `expected_amount` ada, nilainya muncul dalam format yang benar.
- Loose: cukup `expected_amount` muncul minimal sekali dalam format benar. Pola salah lain diabaikan.

**C2 `date_format_id`**
- Contoh: "tulis tanggalnya lengkap"
- Params: `style` (`panjang` = "28 Oktober 2026", `angka` = "28-10-2026"), `expected_date` (opsional)
- Strict:
  - Semua tanggal sesuai `style`.
  - Nama bulan memakai bahasa Indonesia dengan huruf awal kapital (Januari–Desember).
  - Tidak ada nama bulan bahasa Inggris dan tidak ada format MM/DD.
- Loose: cukup `expected_date` muncul sesuai `style` minimal sekali.

**C3 `time_format_id`**
- Contoh: "sebutin jamnya, pakai zona waktu"
- Params: `zone_required` (WIB | WITA | WIT | any | none), `expected_time` (opsional)
- Strict:
  - Waktu ditulis dengan titik, `HH.MM` (EYD: pukul 14.30).
  - Diikuti zona waktu kalau diminta.
  - Tidak ada format `HH:MM` maupun AM/PM.
- Loose: cukup `expected_time` muncul, boleh dengan titik atau titik dua.

**C4 `decimal_comma`**
- Contoh: "tulis angka desimalnya yang bener"
- Strict:
  - Desimal memakai koma (3,5) dan ribuan memakai titik (1.250.000).
  - Pelanggaran: `\d+\.\d{1,2}\b`, atau `\d{1,3}(,\d{3})+\b` di luar konteks desimal yang jelas.
  - Kecualikan waktu: angka yang didahului "pukul"/"jam" atau diikuti WIB/WITA/WIT.
- Loose: kasus ambigu (misalnya `1,250`) tidak dihitung.
- Catatan: hanya dipakai di prompt yang memang memancing angka desimal.

### D. Bentuk budaya

**D1 `pantun_abab`**
- Contoh: "tutup pakai satu pantun"
- Params: `stanzas` (default 1)
- Strict:
  - Ditemukan blok 4 baris berturut-turut untuk setiap bait.
  - Tiap baris berisi 8–12 suku kata.
  - Bunyi akhir baris 1 sama dengan baris 3, dan baris 2 sama dengan baris 4.
  - Rima a berbeda dari rima b.
- Loose: cukup pola rima a-b-a-b. Jumlah suku kata diabaikan, dan syarat a ≠ b tidak wajib.
- Catatan:
  - "Bunyi akhir" = vokal terakhir beserta konsonan sesudahnya (-ang, -i, -ah), dibandingkan setelah lowercase dan tanda baca dibuang.
  - Hubungan sampiran dan isi tidak dicek.

**D2 `peribahasa_included`**
- Contoh: "selipin satu peribahasa yang nyambung"
- Strict: minimal satu peribahasa dari `peribahasa.txt` cocok secara fuzzy dengan skor ≥ 0,9. Pencocokan memakai sliding window setelah lowercase dan tanda baca dibuang.
- Loose: ambang skor 0,8.
- Catatan: relevansi peribahasa terhadap konteks tidak dicek.

### E. Struktur dan format umum

**E1 `word_count`**
- Params: `min` dan/atau `max`
- Strict: jumlah kata (tokenizer bersama) berada di rentang.

**E2 `sentence_count`**
- Params: `min` dan/atau `max`
- Strict: jumlah kalimat (pemecah kalimat bersama) berada di rentang.

**E3 `paragraph_count`**
- Params: `exact`, atau `min`/`max`
- Strict: jumlah paragraf sesuai. Paragraf dipisahkan baris kosong.

**E4 `bullet_count`**
- Params: `exact`
- Strict: jumlah baris bullet tepat `exact`. Bullet = baris yang diawali `-`, `*`, `•`, atau `\d+[.)]`.

**E5 `json_format`**
- Params: `required_keys` (opsional)
- Strict: seluruh respons adalah JSON valid tanpa teks lain, dan semua `required_keys` ada.
- Loose: JSON boleh dibungkus code fence ```json.

**E6 `opening_closing`**
- Params: `starts_with` dan/atau `ends_with`
- Strict: cocok persis setelah whitespace di tepi dipangkas.
- Loose: case-insensitive dan tanda baca di akhir diabaikan.

**E7 `keyword_include`**
- Params: `keyword`, `min_count`, `match` (exact | lemma)
- Strict: kata kunci muncul minimal `min_count` kali.
- Catatan: mode `lemma` memakai Sastrawi, sehingga "jual" cocok dengan menjual, dijual, dan jualan.

**E8 `keyword_exclude`**
- Params: `keywords`, `match` (exact | lemma)
- Strict: tidak ada kemunculan sama sekali.

**E9 `letter_case`**
- Params: `case` (lower | upper)
- Strict: semua huruf alfabet sesuai `case`.
- Loose: minimal 95% huruf sesuai.

**E10 `no_emoji`**
- Strict: tidak ada karakter emoji, termasuk ZWJ sequence.
- Catatan: kaomoji dan emotikon teks seperti (^_^) atau :) tidak dihitung sebagai emoji.

## 6. Pemeriksa konflik (`tools/check_conflicts.py`)
Setiap item dicek sebelum masuk dataset. Hasilnya **error** (item ditolak) atau **warn** (item ditinjau manual).

Error:
- `register_formal` × `register_informal`, `code_mix_required`, `pronoun_required` dengan set gue/lo
- `no_english_words` × `code_mix_required`
- `letter_case` × `honorific_address`, `date_format_id` (kedua constraint ini butuh huruf kapital), juga × `opening_closing` kalau teksnya mengandung huruf yang bertentangan dengan `case`
- `json_format` × `pantun_abab`, `paragraph_count`, `bullet_count`, `opening_closing`
- `language_only` dengan target selain id × constraint A1–A4, B1, B2 (leksikon constraint tersebut berbahasa Indonesia)

Warn:
- `word_count` dengan `max` di bawah kebutuhan minimum constraint lain (misalnya pantun butuh sekitar 30 kata)
- `register_formal` × `regional_words_required`
- Lebih dari satu constraint yang menyentuh hal yang sama, misalnya dua `word_count`

## 7. Dataset
- **Ukuran:** 1.000 prompt, masing-masing 1–4 constraint (rata-rata sekitar 2,5, jadi sekitar 2.500 instance instruksi).
- **Distribusi register:** baku 25%, santai 25%, gaul 30%, campur kode 20%.
- **Sebaran constraint:**
  - Tiap jenis constraint muncul minimal 80 kali.
  - Constraint berlabel eksperimental tidak masuk skor utama sampai lolos validasi (bagian 9).
- **Topik:**
  - Yang dipakai: UMKM dan jualan, administrasi (KTP, SIM, BPJS), kuliner, transportasi dan mudik, kampus dan sekolah, kerja dan karier, keuangan sehari-hari, teknologi dan gadget, hiburan (anime, game, musik), komunitas dan acara, keluarga dan pertemanan.
  - Yang dihindari: SARA, saran medis atau hukum yang spesifik, dan data pribadi asli.
- **Split:**
  - 250 item publik (CC BY 4.0, file diberi canary string).
  - 750 item privat.
- **Batch:** 4 batch × 250 item. Batch 1 sekaligus dipakai untuk memvalidasi verifier dan panduan penulisan.
- **Penulisan:**
  - Item ditulis penutur asli, bukan LLM.
  - Constraint dirangkai secara natural ke dalam permintaan yang realistis (lihat contoh di bagian 2), dan harus bisa dipenuhi.
- **Jawaban referensi:**
  - Wajib untuk seluruh batch 1, dan untuk sampel 20% di batch berikutnya.
  - Harus lolos semua verifier strict. Ini sekaligus membuktikan item bisa dipenuhi dan menjadi contoh positif untuk pengujian.
- **Review:**
  - 2 reviewer buta mengecek kewajaran, keterpenuhan, dan kebenaran params.
  - Perbedaan penilaian diadjudikasi.

## 8. Scoring (`tools/score.py`)
- **Metrik:**
  - Prompt-level accuracy, strict dan loose: persentase prompt yang semua constraint-nya lolos.
  - Instruction-level accuracy, strict dan loose: persentase constraint yang lolos.
- **Skor utama (headline):** prompt-level strict accuracy, setara IFEval.
- **Breakdown:** per kategori (A–E), per jenis constraint, dan per register prompt.
- **Interval kepercayaan:**
  - CI 95% dihitung dengan bootstrap atas prompt, bukan atas instruksi, karena constraint dalam satu prompt saling berkorelasi.
  - 10.000 resample, seed tetap.
- **Perbandingan dua model:**
  - Pakai paired bootstrap atas prompt yang sama, lalu laporkan delta beserta CI-nya.
  - Selisih dianggap bermakna kalau CI delta tidak memuat 0.
- **Batasan:** skor ini tidak mengukur kualitas isi jawaban. Laporkan berdampingan dengan IndoChat.

## 9. Validasi verifier
- **Unit test:** setiap verifier punya minimal 10 contoh lolos dan 10 contoh gagal, termasuk edge case, ditulis dalam bahasa Indonesia.
- **Kesepakatan dengan manusia:**
  - Untuk tiap jenis constraint, ambil sampel 50 respons model nyata (campuran lolos dan gagal), lalu minta 2 penutur asli memberi label lolos/gagal.
  - Target kesepakatan verifier vs label manusia: ≥ 95% untuk constraint format (C, E), ≥ 90% untuk constraint berbasis leksikon (A, B, D).
  - Kalau di bawah target, perbaiki leksikon atau aturannya, atau tandai constraint itu eksperimental.
- **Versi:**
  - Leksikon dan model LID versi-terkunci.
  - Setiap perubahan leksikon menghasilkan versi verifier baru. Skor dari versi verifier berbeda tidak dibandingkan langsung.

## 10. Integrasi dengan harness
- Ikuti pola task `ifeval` di lm-evaluation-harness (`generate_until` + `process_results` di `utils.py`). Pasang sebagai task custom lewat include path, jangan fork.
- Simpan respons mentah per model, supaya bisa dinilai ulang saat verifier diperbarui tanpa generate ulang.
- Prompt dikirim sebagai pesan user dengan chat template model, tanpa system prompt. Catat ini di manifest.

## 11. Yang harus dibangun
- `indobench/verifiers/`: 25 verifier dan komponen bersama.
- `lexicons/`: draft awal beserta README sumber dan lisensi. Draft ini nantinya dikurasi manusia.
- `schema/ifeval_id_gaul.schema.json` beserta validatornya.
- `tools/check_conflicts.py`
- `tools/score.py`: akurasi, CI bootstrap, paired bootstrap.
- Task lm-eval custom.
- `docs/panduan-penulis.md`: panduan untuk penulis prompt, berisi contoh baik dan buruk, daftar constraint dalam bahasa awam, dan aturan anti-konflik.
- Template CSV untuk penulis dan skrip konversi CSV → JSONL.

Batasan: fixture untuk unit test boleh ditulis Claude Code, tetapi item dataset sungguhan tidak boleh ditulis Claude Code.
