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

![Tabel hasil](../results/results_table.png)

Angka tebal adalah skor tertinggi. Sel yang diarsir adalah skor tertinggi plus semua model yang
tidak berbeda bermakna darinya (bootstrap berpasangan per soal, dikoreksi Holm per task). Angka
± di bawah skor adalah interval kepercayaan 95%. Tebakan acak: 50 (COPAL), 33 (IndoCulture),
25 (Global-MMLU), ~23 (IndoMMLU).

### 1. Untuk soal ujian dan MMLU terjemahan, model terbaru menang

Qwen3.8 unggul jelas di IndoMMLU (+3,0 poin atas model terbaik berikutnya) dan di Global-MMLU
umum (+8,1), dan keunggulannya bermakna terhadap semua model lain. Pretraining lanjutan dengan teks
Indonesia tidak menutup jarak generasi model.

### 2. Untuk budaya Indonesia dan nalar, hasilnya seri

Di IndoCulture, satu-satunya benchmark di sini yang benar-benar menguji budaya Indonesia, Qwen3.8
dan GoTo Gemma 3 sama-sama 74,1. Gemma 3 dan Gemma 4 12B tidak berbeda bermakna dari keduanya.

Di COPAL-ID, GoTo Gemma 3 memang tertinggi, tapi empat model teratas secara statistik seri. Gemma 3
biasa, tanpa pretraining lokal, skornya hampir sama. Jadi ini kekuatan keluarga Gemma 3, bukan hasil
pretraining GoTo.

Hati-hati dengan baris Global-MMLU "culturally sensitive". Menurut paper Global-MMLU, sebagian
besar soal kategori itu menuntut pengetahuan budaya **Barat**, bukan budaya Indonesia. Di sana pun
Qwen3.8 tertinggi.

### 3. Bahasa gaul masih menurunkan skor, tapi tidak sebesar yang terlihat

Hampir semua model lebih buruk di COPAL versi gaul dibanding versi baku: turunnya 1,6 sampai 4,7
poin. Penurunan itu bermakna di empat model 27B/12B, tapi tidak di dua model berbasis Gemma 2 9B
(Sahabat-AI dan Gemma 2), yang skor versi bakunya memang sudah lebih rendah.

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

**Sahabat-AI membantu, tapi tidak merata.** Di atas Gemma 2 9B, ia naik 0,6 sampai 3,5 poin, dan
bermakna di empat dari enam task (IndoMMLU, IndoCulture, Global-MMLU "culturally sensitive", COPAL
baku). Di IndoCulture naiknya +2,3. Di Global-MMLU umum hampir tidak bergerak (+0,6), dan di COPAL
gaul naik +3,0 tapi belum bermakna (p = 0,07).

**GoTo Gemma 3 praktis sama dengan model dasarnya.** Semua selisih di bawah satu poin; hanya
IndoMMLU (+0,4) yang bermakna, dan itu terlalu kecil untuk terasa. Pada benchmark pilihan ganda ini,
pretraining lanjutan GoTo di atas Gemma 3 tidak menunjukkan kenaikan yang terukur. Bisa jadi
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

- **Kontaminasi belum diuji.** Keempat dataset sudah publik sejak 2023-2024, sebelum model-model ini
  dilatih, dan beberapa kartu model melaporkan IndoMMLU. Sebagian skor bisa saja hasil hafalan.
- **Ukuran model berbeda.** Perbandingan yang adil hanya pasangan model lokal vs dasarnya dan
  sesama model 27B. Baris 12B dan 9B adalah konteks, bukan pertandingan seimbang.
- **Cara penilaian.** Skor dihitung dari peluang huruf jawaban setelah prefix "Jawaban:" di dalam
  chat template. Penilaian generatif atau tanpa chat template bisa menggeser angka dan urutan.
- **Statistik.** Interval kepercayaan dihitung per soal dan belum dikluster per mata pelajaran atau
  provinsi, jadi sedikit terlalu sempit untuk IndoMMLU dan IndoCulture.
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
