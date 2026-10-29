# Model lokal vs model terbaru: siapa yang lebih paham Indonesia?

*Draft, belum dipublikasi. Angka dari run `full-m4` (Oktober 2026), kode di repo indobench.*

Model AI "rasa lokal" makin banyak: GoTo merilis Sahabat-AI dan turunan Gemma 3 yang dilatih ulang
dengan teks Indonesia. Di saat yang sama, model umum terbaru (Qwen3.8, Gemma 4) terus membaik di
bahasa apa pun. Pertanyaannya sederhana: kalau kamu butuh model yang paham Indonesia, masih perlu
model lokal, atau cukup pakai yang terbaru?

Kami menguji empat model open-weight di empat benchmark berbahasa Indonesia, plus dua model dasarnya (Gemma 3 27B dan Gemma 2 9B) untuk mengukur efek pretraining lokal.

## Yang diuji

| Model | Ukuran | Jenis |
|---|---|---|
| Qwen3.8 27B | 27B | Model umum terbaru (Agustus 2026) |
| Gemma 4 12B | 12B | Model umum terbaru dari Google (Mei 2026) |
| GoTo Gemma 3 27B (`gemma3-27b-cpt-gotoai-v3`) | 27B | Gemma 3 + pretraining lanjutan bahasa Indonesia |
| Sahabat-AI 9B (`gemma2-9b-cpt-sahabatai-v1`) | 9B | Gemma 2 + pretraining lanjutan bahasa Indonesia dan daerah |

Benchmark:

- **IndoMMLU**: 14.904 soal ujian sekolah Indonesia, dari SD sampai SMA.
- **IndoCulture**: 2.429 soal budaya per provinsi ("di Aceh, sarapan di warung kopi biasanya pesan apa?").
- **Global-MMLU ID**: MMLU terjemahan, dipisah jadi soal yang **butuh konteks budaya** (792) dan yang **umum** (2.058).
- **COPAL-ID**: 559 soal nalar sebab-akibat bernuansa lokal, masing-masing dalam bahasa **baku** dan **gaul**.

Semua zero-shot, pakai chat template tiap model, mode thinking dimatikan, seed tetap. Model menjawab
dengan huruf pilihan; kami membandingkan peluang tiap huruf. Setiap angka punya interval kepercayaan
95% (bootstrap 10.000 kali), dan selisih antar model diuji berpasangan per soal.

## Hasil

| Task | Qwen3.8 27B | GoTo Gemma 3 27B | Gemma 4 12B | Sahabat-AI 9B |
|---|---|---|---|---|
| IndoMMLU | **71,4** | 67,6 | 68,4 | 63,6 |
| IndoCulture | **74,1** | **74,1** | 72,3 | 69,9 |
| Global-MMLU ID, budaya | **77,1** | 74,2 | 67,0 | 72,3 |
| Global-MMLU ID, umum | **79,3** | 70,7 | 70,7 | 64,4 |
| COPAL baku | 86,4 | **87,1** | 86,0 | 81,6 |
| COPAL gaul | 82,3 | **83,7** | 81,4 | 80,0 |

Akurasi dalam persen. Tebakan acak: 50 (COPAL), 33 (IndoCulture), 25 (Global-MMLU), ~23 (IndoMMLU).

### 1. Untuk pengetahuan, model terbaru menang

Qwen3.8 unggul jelas di soal pengetahuan: +8,6 poin atas GoTo Gemma 3 di Global-MMLU umum dan +3,8
di IndoMMLU, keduanya bermakna secara statistik. Pretraining lanjutan dengan teks Indonesia tidak
menutup jarak generasi model.

### 2. Untuk budaya dan bahasa, model lokal bertahan

Di soal yang menuntut konteks Indonesia, ceritanya lain. GoTo Gemma 3 seri dengan Qwen3.8 di
IndoCulture dan tertinggi di COPAL, meski selisihnya tidak bermakna. Yang paling mencolok:
Sahabat-AI 9B, dibangun di atas Gemma 2 yang sudah dua generasi lebih tua, **mengalahkan Gemma 4
12B di soal Global-MMLU yang butuh konteks budaya** (+5,3 poin, bermakna), padahal kalah 6,4 poin
di soal umum.

Polanya konsisten: pretraining lokal membeli pemahaman budaya, bukan pengetahuan umum.

### 3. Bahasa gaul masih menurunkan skor, tapi tidak sebesar yang terlihat

Semua model lebih buruk di COPAL versi gaul dibanding versi baku: turun 3,4 sampai 4,7 poin, dan
bermakna di tiga dari empat model. Satu-satunya pengecualian adalah Sahabat-AI (turun 1,6 poin,
tidak bermakna).

### 4. Apakah pretraining lokal membantu? Tergantung modelnya

Cara paling bersih untuk menjawab ini: bandingkan model lokal dengan model dasarnya, pada soal yang
sama persis.

| Task | Gemma 3 27B → GoTo | Gemma 2 9B → Sahabat-AI |
|---|---|---|
| IndoMMLU | 67,2 → 67,6 (**+0,4**) | 61,2 → 63,6 (**+2,4**) |
| IndoCulture | 73,7 → 74,1 (+0,5) | 67,5 → 69,9 (**+2,3**) |
| Global-MMLU ID, budaya | 74,4 → 74,2 (−0,1) | 68,8 → 72,3 (**+3,5**) |
| Global-MMLU ID, umum | 71,2 → 70,7 (−0,5) | 63,8 → 64,4 (+0,6) |
| COPAL baku | 86,6 → 87,1 (+0,5) | 78,5 → 81,6 (**+3,0**) |
| COPAL gaul | 83,0 → 83,7 (+0,7) | 76,9 → 80,0 (+3,0) |

Tebal = bermakna (bootstrap berpasangan, p < 0,05).

**Sahabat-AI membantu.** Di atas Gemma 2 9B, ia naik 2-3,5 poin di hampir semua task, bermakna di
empat dari enam. Kenaikan terbesar justru di soal yang butuh konteks budaya (+3,5), sementara soal
pengetahuan umum hampir tidak bergerak (+0,6). Ini cocok dengan temuan sebelumnya.

**GoTo Gemma 3 praktis sama dengan model dasarnya.** Semua selisih di bawah satu poin; hanya
IndoMMLU (+0,4) yang bermakna, dan itu terlalu kecil untuk terasa. Pada benchmark pilihan ganda ini,
pretraining lanjutan GoTo di atas Gemma 3 tidak membuat model lebih paham Indonesia. Bisa jadi
manfaatnya ada di hal yang belum kami ukur (gaya menulis, mengikuti instruksi, bahasa daerah).
Catatan: kartu model GoTo tidak mencantumkan model dasarnya; kami mengasumsikan Gemma 3 27B IT.

## Catatan: bug di benchmark COPAL bawaan

Run pertama kami memakai task COPAL bawaan lm-evaluation-harness dan mendapat gap baku-gaul 7-9 poin.
Ternyata task itu memotong karakter terakhir setiap premis karena mengira kalimat selalu diakhiri
titik. Kalimat baku memang selalu bertitik; kalimat gaul **79% tidak**, sehingga yang terpotong
adalah huruf asli: "naek angkot" menjadi "naek angko", "masuk angin" menjadi "masuk angi".

Bug itu hanya merugikan versi gaul, persis variabel yang ingin diukur. Setelah format diperbaiki,
skor naik sekitar 15 poin di semua model dan gap gaul menyusut menjadi 2-5 poin. Pelajarannya:
selalu baca prompt yang benar-benar dikirim ke model, bukan hanya skor akhirnya.

## Batasan

- Model dasar Sahabat-AI sebenarnya `sahabatai-v1-base` (Gemma 2 9B yang dilatih ulang); kami
  membandingkan versi instruct dengan Gemma 2 9B IT, jadi selisihnya mencakup pretraining dan
  instruction tuning GoTo sekaligus. Hal yang sama berlaku untuk pasangan Gemma 3.
- Semua soal pilihan ganda. Kemampuan menulis, mengikuti instruksi, atau mengobrol dalam bahasa gaul
  belum diuji; itu tahap berikutnya (IFEval-ID-Gaul).
- Belum ada model tertutup (Claude, GPT, Gemini) sebagai pembanding.
- Empat model saja, satu prompt per task, satu seed. Run kontrol menunjukkan hasil deterministik,
  tapi format prompt lain bisa menggeser angka beberapa poin.

## Biaya

Semua run di Google Colab (RTX PRO 6000 96 GB) dengan vLLM 0.32 dan lm-evaluation-harness 0.4.13:
sekitar 29 compute unit untuk seluruh percobaan, termasuk run ulang.

## Reproduksi

Kode, konfigurasi model (dengan commit hash), prompt, dan skrip statistik ada di repo indobench.
https://github.com/arielfikru/indobench
