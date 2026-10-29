# Membangun Benchmark LLM Bahasa Indonesia: Cara LLM Dievaluasi, Ciri Bahasa Indonesia, dan Roadmap untuk Developer Solo (Oktober 2026)

**Jawaban singkat: alat benchmark Indonesia yang paling berguna saat ini *bukan* versi terjemahan MMLU yang ke-sekian. Yang dibutuhkan adalah harness yang bisa direproduksi, dibangun di atas lm-evaluation-harness/Inspect, berjalan lokal di Mac, dan fokus ke celah yang belum diisi siapa pun: bahasa informal/gaul dan campur kode, instruction following serta kualitas chat yang dinilai penutur asli, plus held-out set privat yang rutin diperbarui.** Untuk dimensi "klasik" (NLU, pengetahuan sekolah, budaya), sudah ada dataset native yang bagus seperti IndoMMLU, IndoCulture, COPAL-ID, IndoCareer, IndoSafety, dan SEA-HELM. Itu cukup diintegrasikan saja, tidak perlu dibuat ulang.

## TL;DR

- **Cara LLM di-benchmark tahun 2026:** campuran MCQ berbasis log-likelihood/generatif (MMLU-Pro, GPQA, HLE), tugas yang bisa diverifikasi otomatis (matematika, kode, IFEval), LLM-as-judge (MT-Bench/Arena-Hard), dan arena preferensi manusia (Elo/Bradley-Terry). Masalah utamanya adalah kontaminasi, saturasi, dan sensitivitas format prompt (selisih akurasi bisa sampai 76 poin hanya karena format).\[1\] Hugging Face pun memensiunkan Open LLM Leaderboard pada 13 Maret 2025 setelah mengevaluasi lebih dari 13.000 model. Dalam pengumumannya, Clémentine Fourrier menulis bahwa leaderboard itu "slowly becoming obsolete" dan "could encourage people to hill climb irrelevant directions in the field".
- **Bahasa Indonesia untuk evaluasi:** morfologi afiksasi dan reduplikasi membuat tokenisasi boros (Llama-2: 2,858 token/kata untuk Indonesia vs 1,666 untuk Inggris).\[2\] Register baku dan gaul Jakarta berbeda jauh, dan model terbaik turun ke 65,47% di COPAL-ID yang native dibanding 79,40% di XCOPA-ID hasil terjemahan.\[3\] Campur kode Indonesia–Inggris–bahasa daerah adalah hal sehari-hari, sementara benchmark terjemahan tidak menangkap budaya lokal.
- **Rekomendasi:** jangan bikin harness dari nol. Bungkus lm-evaluation-harness (backend `local-chat-completions`/`gguf`/`vllm`) untuk tugas yang skornya objektif, lalu tambahkan modul "IndoChat" untuk penilaian generatif dengan juri LLM yang dikalibrasi terhadap rating penutur asli dari komunitas Anda. Mulailah dengan MVP 6 kategori dan 10–15 model open-weight, dan publikasikan leaderboard statis beserta semua prompt, seed, dan versi.

---

## Bagian 1 — Bagaimana LLM biasanya di-benchmark (state of the art 2026)

### 1.1 Kategori benchmark utama

| Kategori | Contoh benchmark | Cara skor | Status 2026 |
|---|---|---|---|
| Pengetahuan / MCQ | MMLU, MMLU-Pro, GPQA Diamond, Humanity's Last Exam (HLE) | Akurasi | MMLU sudah jenuh. GPQA Diamond (198 soal; pakar PhD ≈65%, non-pakar dengan internet ≈34%) mendekati saturasi. HLE (2.500 soal buatan pakar) jadi "plafon" baru\[4\] |
| Penalaran/matematika | GSM8K, MATH/MATH500, AIME | Exact match jawaban akhir | GSM8K jenuh; AIME dipakai untuk model reasoning |
| Kode | HumanEval, LiveCodeBench, SWE-bench | pass@k, unit test | LiveCodeBench/SWE-bench lebih tahan kontaminasi |
| Instruction following | IFEval | Cek aturan secara programatik | Murah dan objektif, sangat cocok untuk diadaptasi |
| Kualitas chat | MT-Bench, AlpacaEval, Arena-Hard | LLM-as-judge (skor 1–10 atau win-rate) | Standar, tapi bias juri |
| Preferensi manusia | LMArena (Chatbot Arena) | Elo / Bradley-Terry dari voting berpasangan | Ada kritik soal pengujian privat dan sampling yang tidak seimbang ("The Leaderboard Illusion", 2025)\[5\] |
| Kontaminasi-resisten | LiveBench | Soal baru diperbarui bulanan | Pola yang patut ditiru\[6\] |
| Safety, bias, toksisitas | Benchmark refusal/harm, BBQ-style bias | Unsafe rate oleh juri/klasifikator | Butuh lokalisasi budaya |
| Long-context, tool use/agentic, faktualitas | Needle-in-haystack/RULER, tau-bench/BFCL, SimpleQA | Bervariasi | Semakin penting untuk model 2026 |

### 1.2 Metode penilaian

- **Log-likelihood MCQ:** model tidak menghasilkan teks. Yang dibandingkan adalah probabilitas tiap opsi jawaban. Cara ini murah, deterministik, dan cocok untuk base model, tetapi butuh akses logprob (tidak tersedia di banyak API chat) dan kurang mencerminkan pemakaian nyata model chat.
- **Generatif + parsing:** model menjawab bebas, lalu jawaban diekstrak (huruf opsi atau angka). Masalah parseability bisa mendominasi skor, dan studi 2026 tentang *Format Sensitivity Index* menemukan bahwa parseability sangat memediasi perbedaan akurasi.\[7\]
- **Metrik teks:** exact match/F1 untuk QA ekstraktif; BLEU/chrF++ untuk terjemahan (chrF lebih ramah morfologi aglutinatif dibanding BLEU); COMET untuk MT berbasis model; ROUGE untuk ringkasan.
- **pass@k** untuk kode, berdasarkan eksekusi unit test.
- **LLM-as-judge:** pointwise (skor 1–10) atau pairwise (A vs B). Biasnya sudah terdokumentasi: posisi, panjang jawaban, preferensi terhadap gaya model sendiri. Untuk bahasa non-Inggris, Fu & Liu (EMNLP Findings 2025) menemukan konsistensi juri lintas 25 bahasa hanya Fleiss' Kappa ≈0,3, dan baik ukuran model maupun pelatihan multilingual tidak otomatis memperbaikinya. Ensemble beberapa juri dengan voting mayoritas disarankan.\[8\]\[9\]
- **Pairwise + Elo/Bradley-Terry:** dari banyak perbandingan berpasangan, dihitung rating global dengan confidence interval.

### 1.3 Harness/framework evaluasi

- **EleutherAI lm-evaluation-harness:** standar de facto. Task didefinisikan lewat YAML (dataset HF, template prompt, metrik, few-shot). Backend model meliputi `hf`, `vllm`, `sglang`, `openai-completions`/`openai-chat-completions`, `local-completions`/`local-chat-completions` (server OpenAI-compatible apa pun, termasuk Ollama, LM Studio, mlx-lm server), serta `gguf` yang memanggil `llama-server` milik llama.cpp lewat endpoint `/v1/completions`. Sejak September 2026 backend, filter, dan metrik bisa didaftarkan sebagai **plugin** dari paket sendiri tanpa fork.\[10\] Ini sangat relevan untuk Anda. Task Indonesia yang sudah ada antara lain `copal_id` (standar & kolokial) dan `global_mmlu`.\[11\]\[12\] Catatan: untuk endpoint chat-completions, loglikelihood biasanya tidak tersedia (hanya `generate_until`).
- **Hugging Face lighteval:** mengklaim 1.000+ task, dengan dukungan multilingual terbaik (template prompt per bahasa, metrik "quasi exact match" multibahasa). TyDi QA Indonesia sudah ada.\[13\] Proyek FineTasks-nya menyeleksi task multilingual yang memberi "sinyal" stabil, dan metodologinya layak ditiru.\[14\]\[15\]\[16\]
- **HELM (Stanford CRFM):** evaluasi "holistik" multi-metrik. SEA-HELM adalah turunan regionalnya.
- **UK AISI Inspect:** framework Python yang kuat untuk eval generatif, agentik, dan berbasis juri (konsep *dataset → solver → scorer*), mendukung banyak provider termasuk server OpenAI-compatible lokal. Cocok untuk modul chat, juri, dan safety.
- **OpenCompass** (Shanghai AI Lab): suite besar, kuat untuk model Tiongkok.
- **Pemuatan model:** HF transformers (referensi kebenaran), vLLM (throughput tinggi, GPU NVIDIA), llama.cpp/GGUF (CPU/Metal, kuantisasi), MLX (Apple Silicon), dan API OpenAI-compatible.

### 1.4 Leaderboard dan masalah metodologis

- **Open LLM Leaderboard (HF)** dipensiunkan pada 13 Maret 2025, lewat pengumuman Clémentine Fourrier di Space open_llm_leaderboard: "For the last 2 years, we've evaluated over 13K models". Alasannya, menurut pengumuman yang sama: "The leaderboard is slowly becoming obsolete; we feel it could encourage people to hill climb irrelevant directions in the field." Pelajarannya untuk Anda: leaderboard statis tanpa penyegaran akan cepat mati.
- **Kontaminasi:** soal benchmark publik bocor ke data pretraining. Penangkalnya: held-out set privat, soal dinamis/baru, dan canary string.
- **Saturasi:** begitu banyak model mencapai >90%, benchmark tidak lagi membedakan.\[6\]
- **Sensitivitas format prompt:** Sclar dkk. (ICLR 2024) menunjukkan format yang secara makna setara bisa menghasilkan selisih **hingga 76 poin akurasi** (LLaMA-2-13B), dengan median spread 7,5 poin. Sensitivitas ini tidak hilang dengan model lebih besar, few-shot lebih banyak, atau instruction tuning.\[17\]\[18\] Implikasinya: laporkan rentang di beberapa template, bukan satu angka.\[19\]
- **Few-shot vs zero-shot dan chat template:** model instruct bisa anjlok kalau chat template tidak diterapkan, atau sebaliknya. Ini wajib dicatat di setiap run.
- **Reproduksibilitas:** vLLM kadang berbeda output dari HF, dan lm-eval memperlakukan HF sebagai implementasi referensi.\[20\] Kuantisasi (Q4 vs BF16) juga mengubah skor.
- **Translationese:** benchmark terjemahan mewarisi bias budaya sumber. Global-MMLU menemukan 28% soal MMLU memerlukan pengetahuan yang sensitif budaya, dan peringkat model berubah ketika dievaluasi hanya di subset tersebut.\[21\]\[22\]

### 1.5 Benchmark multilingual dan Asia Tenggara

- **Global-MMLU (Cohere, ACL 2025):** 42 bahasa termasuk Indonesia. 2.850 soal per bahasa diberi anotasi *Culturally Sensitive* (792) vs *Culturally Agnostic* (2.058). Penulis merekomendasikan agar skor kedua subset dilaporkan terpisah.\[23\]\[24\]
- **MMMLU (OpenAI)**, **INCLUDE**, **BLEnD**: MMLU terjemahan profesional, soal ujian lokal multibahasa, dan pengetahuan budaya sehari-hari.
- **SEA-HELM (AI Singapore, ACL Findings 2025; dulu BHASA):** lima pilar, yaitu NLP Classics, LLM-specifics, SEA Linguistics, SEA Culture, dan Safety. Datasetnya native atau diterjemahkan dan dilokalisasi bersama penutur asli, dan prompt ditulis dalam bahasa target. Skor dinormalisasi terhadap baseline acak lalu diagregasi berjenjang (task → kompetensi → bahasa → rata-rata SEA). Komponen Indonesianya: NusaX (sentimen, CC BY-SA 4.0), TyDi QA-GoldP (Apache 2.0), IndoNLI (CC BY-SA 3.0), XCOPA, FLORES (terjemahan), XL-Sum (ringkasan, CC BY-NC-SA 4.0), MABL (metafora), LINDSEA (linguistik), SEA-IFEval, SEA-MTBench (CC BY-NC-SA 4.0), dan MLHSD (toksisitas).\[25\]\[26\]\[27\] Versi terbaru dipakai untuk SEA-LION v4.8 dengan cakupan tujuh bahasa SEA, dan ada juga SEA-HELM Audio (2026).\[26\]\[28\]
- **SeaExam & SeaBench (DAMO/SeaLLMs, NAACL Findings 2025):** SeaExam berisi soal ujian asli Indonesia/Thailand/Vietnam, sedangkan SeaBench berisi tugas chat multi-turn open-ended. Pembandingnya, MMLU-SEA dan MT-bench-SEA, diterjemahkan dengan Google Translate API, dan penulis menunjukkan benchmark lokal lebih baik membedakan model. Ada temuan menarik: untuk bahasa Indonesia, SeaExam *tidak* lebih diskriminatif daripada versi terjemahannya.\[29\]\[30\]
- **SeaEval**, **SEACrowd** (hub 254 dataset, 38 bahasa asli SEA), dan **NusaCrowd** (137 dataset, 19 bahasa).\[31\]

---

## Bagian 2 — Bahasa Indonesia dari sudut pandang evaluasi LLM

### 2.1 Ciri linguistik yang relevan

- **Morfologi aglutinatif:** prefiks me-/ber-/di-/ter-/pe-, sufiks -kan/-i/-an/-nya, konfiks ke-…-an dan per-…-an, serta alomorf nasal (me- → mem-/men-/meng-/meny-). Implikasinya: (a) tokenisasi memecah kata jadi banyak subword; (b) metrik berbasis kata (BLEU) menghukum varian morfologis yang sah, sehingga chrF/COMET atau juri lebih adil; (c) tugas linguistik seperti pemilihan afiks yang tepat (*memperbaiki* vs *memperbaikkan*) adalah sinyal kemampuan bahasa yang murni.
- **Reduplikasi:** *rumah-rumah* (jamak), *sayur-mayur*, *bolak-balik*, *jalan-jalan* (makna berbeda). Penulisan dengan tanda hubung juga memengaruhi tokenisasi.
- **Tanpa tense dan gender gramatikal:** waktu ditandai adverbia (*sudah, sedang, akan*). Pronomina *dia* netral gender, sehingga menerjemahkan ke Inggris memaksa model menebak gender. Ini bisa jadi uji bias.
- **Urutan kata SVO** yang relatif fleksibel, dengan konstruksi pasif (di-) yang sangat sering muncul.
- **Pronomina dan honorifik:** *saya/aku/gue*, *Anda/kamu/lo/elu*, *Bapak/Ibu/Kak/Mas/Mbak*. Kesesuaian register adalah dimensi kualitas jawaban chat yang sering gagal di model, misalnya menjawab dengan "Anda" yang kaku ketika pengguna menulis santai, atau sebaliknya.
- **Register baku vs informal:** ragam baku mengacu ke EYD/KBBI, sementara kolokial Jakarta memakai *gue/lo, nggak/gak, udah, banget, -in* (menggantikan -kan/-i: *beliin*), dan *nge-* (*ngetag*). Singkatan chat seperti *yg, gk, bgt, otw, wkwk, btw* juga lazim. Data COPAL-ID menunjukkan bahwa model open-source turun lebih jauh di versi kolokial, terutama pada kategori nuansa bahasa, yang menandakan data pretraining kurang mewakili ragam ini.\[32\]
- **Campur kode:** terjadi bahkan di tingkat morfem. Contohnya *quotenya* (kata Inggris + -nya) dan *ngetag* (prefiks Betawi nge- + *tag*), seperti dicatat dalam "One Country, 700+ Languages" (Aji dkk., ACL 2022).\[33\]
- **700+ bahasa daerah:** Jawa (dengan tingkat tutur ngoko/krama), Sunda, Bali, Minang, Batak, Betawi, Bugis, dan lain-lain. LoraxBench (EMNLP 2025, 20 bahasa) menemukan performa jauh lebih rendah pada bahasa non-Indonesia, dan register tinggi seperti Krama Javanese ikut menurunkan performa.\[34\]\[35\]

### 2.2 Tokenisasi

- **Data primer yang tersedia:** paper Komodo (arXiv 2403.09362) melaporkan fertilitas rata-rata Llama-2-7B sebesar **2,858 token/kata untuk Indonesia, 2,658 untuk bahasa daerah, dan 1,666 untuk Inggris** (vocab 32K). Tokenizer Komodo-7B yang diperluas (vocab 35.008) menurunkannya ke 2,031 untuk Indonesia.\[2\] Artinya, di Llama-2 teks Indonesia memakan sekitar 1,7× token per kata dibanding Inggris (perhitungan dari angka paper).
- **Celah data penting:** saya *tidak* menemukan tabel fertilitas Indonesia–Inggris yang dipublikasikan secara primer untuk tokenizer modern (Llama 3.x, Qwen2.5/3, Gemma 2/3, Mistral, SEA-LION, Sailor2). Beberapa paper 2026 mengukurnya di FLORES-200, tetapi angkanya hanya muncul di grafik. Sebuah blog developer mengklaim Llama 3.1 (yang juga dipakai Sahabat-AI 70B) menghasilkan 2,34 token/kata untuk Indonesia vs 1,41 untuk Inggris, namun ini sumber sekunder yang belum diverifikasi.\[36\] Estimasi wajar (inferensi, bukan data) untuk premium Indonesia di tokenizer modern ber-vocab besar adalah sekitar 1,2–1,7× Inggris.
- **Fakta kunci:** model Indonesia/SEA turunan umumnya **mempertahankan tokenizer basisnya**. Sahabat-AI memakai tokenizer Llama/Gemma, SEA-LION v3/v4 memakai tokenizer Gemma 2/Gemma 3/Llama 3.1, Sailor2 memakai tokenizer Qwen2.5, dan SEA-LION v4.8 memakai tokenizer Nemotron 3 apa adanya.\[37\]\[38\] Laporan SEA-LION v4.8 sendiri menyimpulkan bahwa "additional language data cannot fully compensate for inefficient tokenization."\[26\]\[36\]\[39\]\[40\]\[41\]
- **Implikasi untuk tool Anda:** jadikan **fertilitas dan premium token** sebagai metrik leaderboard sendiri (biaya API, latensi, dan sisa konteks efektif). Ukur di FLORES-200 `ind_Latn` vs `eng_Latn` serta di korpus kolokial (premiumnya kemungkinan lebih tinggi untuk gaul dan singkatan). Ini kontribusi orisinal yang murah, karena belum ada tabel publiknya.

### 2.3 Budaya dan pengetahuan lokal

Benchmark terjemahan gagal karena (1) konteksnya Amerika (kurikulum, hukum, satuan, tokoh); (2) translationese (kalimat kaku yang tidak pernah ditulis orang Indonesia); dan (3) tidak menguji pengetahuan lokal seperti adat per provinsi, makanan, hari raya, Pancasila, UU/regulasi Indonesia, sejarah, dan sensitivitas SARA. Bukti empirisnya: di COPAL-ID, model open-source terbaik hanya 65,47% dibanding 79,40% di XCOPA-ID terjemahan, sementara penutur Jakarta mendekati sempurna.\[3\] IndoSafety juga menunjukkan bahwa model yang tampak aman dalam bahasa Indonesia formal "bocor" ketika diprompt dengan ragam kolokial atau bahasa daerah.\[42\]

---

## Bagian 3 — Benchmark, dataset, dan leaderboard Indonesia yang sudah ada

| Benchmark | Mengukur | Ukuran | Cara dibuat | Lisensi / catatan | Keterbatasan |
|---|---|---|---|---|---|
| **IndoNLU** (2020) | 12 tugas NLU (sentimen, NER, POS, NLI, dll.) | 12 task | Kumpulan dataset native | Campuran | Era encoder; banyak yang jenuh untuk LLM |
| **IndoNLG / IndoLEM** | Ringkasan, terjemahan, QA / NLU+NLG | Beberapa task | Native | Campuran | Format lama, perlu adaptasi prompt |
| **NusaX** (EACL 2023) | Sentimen + MT, 10 bahasa daerah + Indonesia + Inggris | Paralel | Terjemahan manusia | CC BY-SA 4.0 | Sentimen saja sudah mudah bagi LLM besar |
| **NusaCrowd / SEACrowd** | Hub dataset | 137 / 254 dataset | Agregasi | Beragam, cek per dataset | Bukan benchmark tunggal\[31\] |
| **IndoNLI** (EMNLP 2021) | NLI | — | Native, ditulis ahli | CC BY-SA 3.0 | Dipakai di SEA-HELM |
| **IndoMMLU** (EMNLP 2023) | Pengetahuan ujian SD–UTBK, 64 task; 46% bahasa Indonesia + 9 bahasa/budaya daerah | 14.981 soal (versi HF rapi: 14.906/63 task) | Dikumpulkan 7 guru profesional dari ujian publik | Cek repo (CC BY-NC-SA) | MCQ saja; tanpa aritmetika, essay, gambar; rawan kontaminasi karena publik sejak 2023\[43\]\[44\]\[45\]\[46\] |
| **IndoCulture** (TACL 2024) | Penalaran budaya per lokasi, 11 provinsi | 2.429 soal | Ditulis 22 anotator dari 11 provinsi | Publik | Single-hop; 11 dari 38 provinsi\[47\]\[48\] |
| **COPAL-ID** (NAACL 2024) | Penalaran kausal dengan nuansa lokal Jakarta, versi baku dan kolokial | Test set saja | Ditulis dan divalidasi penutur asli dari nol | CC BY-SA 4.0 | Jakarta-sentris; format COPA biner\[49\]\[50\] |
| **IndoCareer** (2024/2025) | Ujian profesi (22 profesi, 6 sektor) | 8.834 MCQ | Soal ujian profesi nyata | Cek repo | MCQ; isu hak cipta soal\[51\] |
| **IndoToxic2024 / MLHSD** | Deteksi toksisitas/ujaran kebencian | — | Native | MLHSD: CC BY-NC-SA 4.0 | Klasifikasi, bukan perilaku generatif |
| **IndoSafety** (EMNLP 2025) | Safety generatif berbasis budaya: 19 jenis bahaya, termasuk penyalahgunaan Pancasila, klaim supranatural, SARA | Eval-1: 2.514 prompt; Eval-2: 2.500 paralel (5 ragam: baku, kolokial, Jawa, Sunda, Minang) | Diverifikasi manusia | Publik (cek lisensi) | Penilaian unsafe bergantung pada juri\[42\]\[52\] |
| **IndoPref** (IJCNLP-AACL 2025) | Preferensi berpasangan, naturalness | 522 prompt, 4.099 preferensi, 10 kategori | Sepenuhnya ditulis manusia Indonesia | Publik | Hanya 5 model yang dibandingkan; sangat berguna untuk kalibrasi juri\[53\] |
| **LoraxBench** (EMNLP 2025) | 6 tugas × 20 bahasa Indonesia, dengan 2 register untuk 3 bahasa | — | Ditulis manusia | Publik | Fokus bahasa daerah\[35\]\[54\] |
| **IndoBias** (2026) | Bias budaya; 336 kelompok demografis; Indonesia + Jawa/Sunda/Makassar | — | Ditulis dan divalidasi native | Baru | Belum banyak dipakai\[55\] |
| **ID-MoCQA, CultureTalk-ID** (2025–2026) | QA budaya multi-hop; dialog budaya dalam bahasa daerah | — | Turunan IndoCulture/COPAL-ID + anotator | Baru | Turunan, sehingga bisa mewarisi bias sumber |
| **Indonesia di SEA-HELM / SeaExam / SeaBench / Global-MMLU** | Lihat Bagian 1.5 | — | Campuran | Beragam (beberapa NC) | SeaExam-ID kurang diskriminatif\[30\] |

**Leaderboard:** SEA-HELM leaderboard (leaderboard.sea-lion.ai) adalah yang paling aktif dan punya tampilan per bahasa.\[56\] Sahabat-AI punya Space "Sahabat AI Leaderboard" di Hugging Face.\[57\]\[58\] SeaExam/SeaBench juga punya leaderboard.\[59\] Sejauh yang saya temukan, **belum ada leaderboard Indonesia-sentris yang independen, berjalan rutin, dan berfokus pada model open-weight yang bisa dijalankan lokal.** Itulah ceruk Anda.

### Gap yang belum tertutup (peluang diferensiasi)

1. **Chat dan instruction following dalam ragam informal/gaul.** IFEval dan MT-Bench versi SEA ditulis dalam ragam relatif formal, dan COPAL-ID kolokial hanya MCQ.
2. **Kesesuaian register dan honorifik** (apakah model menjawab "lo/gue" ke pengguna santai dan "Bapak/Ibu" ke konteks formal). Belum ada benchmark khusus.
3. **Campur kode generatif** Indonesia–Inggris dan Indonesia–daerah, baik dalam pemahaman maupun produksi yang natural.
4. **Coding dengan prompt bahasa Indonesia** (tugas developer lokal, misalnya "bikinin endpoint FastAPI…"). Hampir kosong, padahal komunitas Anda adalah developer.
5. **Penalaran matematika native Indonesia** (IndoMMLU sengaja membuang aritmetika).\[60\]
6. **Long-context Indonesia** (dokumen hukum/peraturan, berita panjang) dan **RAG atas dokumen Indonesia**.
7. **Faktualitas lokal yang dinamis** (peristiwa terbaru, regulasi baru) yang tahan kontaminasi.
8. **Evaluasi generatif yang dinilai penutur asli dalam skala besar.** IndoPref hanya membandingkan 5 model.

---

## Bagian 4 — Model open-source yang layak dievaluasi (status Oktober 2026)

| Keluarga | Versi terkini yang ditemukan | Catatan |
|---|---|---|
| **Sahabat-AI** (GoTo, Indosat, AI Singapore) | Llama-Sahabat-AI-v2-70B-IT (rilis Juni 2025); v1: llama3-8b dan gemma2-9b CPT | Mendukung Indonesia, Jawa, Sunda, Batak Toba, Bali. Dievaluasi dengan IndoMMLU, SEA-HELM, SEA-IFEval, dan SEA-MTBench (juri gpt-4-1106-preview vs baseline gpt-3.5-turbo). Menurut laporan peluncuran 70B, model generasi sebelumnya (8B dan 9B) sudah diunduh lebih dari 35.000 kali di Hugging Face. 70B terlalu berat untuk Mac kecuali dikuantisasi agresif |
| **SEA-LION** (AI Singapore) | Gemma-SEA-LION-v4-27B-IT (Agustus 2025; menurut kartu model HF, CPT ~500B token yang diambil dari lebih dari 1 triliun token di 11 bahasa SEA, lalu post-training ~10M sampel); Qwen-SEA-LION-v4.5-27B-IT (basis Qwen3.6-27B); Nemotron-SEA-LION-v4.8 30B-A3B & 120B-A12B (2026) | v4-27B tersedia di Ollama (q4_k_m ~18 GB), cocok untuk Mac.\[37\]\[38\]\[61\]\[62\] v4.8-120B naik di SEA-HELM dari 49,30 ke 63,44 dibanding basisnya. Di SEA-HELM Audio, SEA-LION-4.5-27B mencatat 94,29% IFEval Indonesia (teks) vs 89,52% Gemini 3.5 Flash (paper yang sama juga mencantumkan 93,33%, sehingga ada inkonsistensi kecil)\[26\]\[28\] |
| **Sailor / Sailor2** (Sea AI Lab) | Sailor2-1B/8B/20B-Chat | Basis Qwen2.5 dengan tokenizer Qwen2.5.\[39\]\[63\] Di IndoSafety, Sailor2 adalah model paling tidak aman: 36,7% respons unsafe di IndoSafety-Eval-1 dan 32–40% di IndoSafety-Eval-2 |
| **SeaLLMs** (DAMO) | SeaLLMs-v3-7B-Chat | Pembanding generasi lama\[34\]\[64\] |
| **Komodo, Cendol, Merak** | Komodo-7B, Cendol (Llama2/mT5), Merak | Generasi 2023–2024, berguna sebagai baseline historis |
| **Multilingual umum** | Qwen3.x, Gemma 3, Llama 3.x/4, Mistral, DeepSeek, gpt-oss, Aya Expanse | Di paper SEA-HELM, Qwen2.5-72B (69,8 ID) dan aya-expanse-32b (68,1 ID) bersaing ketat dengan Llama3.1-70B SEA-LION v3 (71,1 ID). Sailor2-20B hanya 55,8 ID\[57\] |

**Interpretasi:** keunggulan model "lokal" atas model multilingual terbaru tidaklah otomatis. LoraxBench menemukan "no clear lead" antara model regional dan multilingual umum, dan di sebagian tugas Gemma 9B dan Sahabat-AI justru kuat.\[34\] Inilah alasan kuat untuk benchmark independen yang membandingkan semuanya secara apple-to-apple, dengan prompt, template, dan kuantisasi yang sama.

---

## Bagian 5 — Rekomendasi praktis untuk membangun tool

### 5.1 Prioritas kategori

**MVP (bulan 1–3):**
1. **Integrasi ulang dataset native yang sudah ada** lewat task YAML lm-eval: IndoMMLU (subset), IndoCulture, COPAL-ID (baku + kolokial, dilaporkan terpisah), IndoCareer, dan Global-MMLU-ID (pisahkan CS/CA). Biayanya rendah dan langsung memberi baseline yang kredibel.
2. **IFEval-ID-Gaul (baru):** sekitar 300–500 instruksi dengan constraint yang dicek programatik (jumlah kata, format JSON, harus memakai "lo/gue", tidak boleh ada kata Inggris, harus ada pantun 4 baris a-b-a-b). Murah, objektif, dan orisinal.
3. **IndoChat (baru):** sekitar 200 prompt multi-turn native dalam campuran register dan campur kode, kategori sehari-hari (UMKM, administrasi KTP/BPJS, kuliner, curhat, coding). Dinilai secara pairwise oleh juri LLM yang dikalibrasi.
4. **Metrik efisiensi tokenizer:** fertilitas dan premium token di FLORES-200 plus korpus kolokial.

**Fase 2 (bulan 4–6):** IndoCode (soal coding berprompt bahasa Indonesia dengan unit test), safety (integrasikan IndoSafety Eval-2), matematika native (soal cerita bergaya UN/OSN yang ditulis ulang), dan uji register/honorifik.

**Fase 3:** long-context dan RAG atas dokumen hukum/berita Indonesia, set faktualitas dinamis yang diperbarui per kuartal, bahasa daerah (Jawa, Sunda, Betawi), dan arena voting komunitas.

### 5.2 Pembuatan data

- **Native lebih dulu, terjemahan hanya untuk tugas yang netral budaya**, dan itu pun harus di-post-edit manusia dan diberi label "translated".
- **Crowdsourcing via komunitas:** gunakan alur tulis → review silang buta oleh 2 orang → adjudikasi (meniru pipeline COPAL-ID dan IndoCulture). Kumpulkan metadata penulis (asal daerah, register) untuk analisis. Sediakan panduan penulisan dan contoh soal yang "buruk".
- **Held-out set privat:** publikasikan sekitar 20–30% soal sebagai dev/contoh, dan simpan sisanya privat. Evaluasi set privat dijalankan oleh Anda sendiri. Tambahkan canary string di file publik.
- **Penyegaran berkala:** misalnya rilis "IndoBench-2027Q1", dengan soal baru tiap kuartal, soal lama dipensiunkan ke set publik, dan tren skor model dilacak (pola LiveBench).
- **Kualitas:** ukur kesepakatan antar-anotator (Krippendorff's α atau Cohen's κ) dan buang soal dengan kesepakatan rendah.

### 5.3 Metrik dan penilaian

- **MCQ:** jalankan *dua mode*, yaitu log-likelihood (untuk base model dan backend yang punya logprob) dan generatif+parsing (untuk model chat/API). Laporkan akurasi ternormalisasi terhadap baseline acak (seperti SEA-HELM).
- **Robustness format:** untuk setiap task MCQ pakai 3–5 template prompt berbahasa Indonesia, lalu laporkan rata-rata ± spread (Sclar dkk.).\[19\]
- **Generatif:** chrF++ untuk MT, dan juri untuk chat.
- **Juri LLM dalam bahasa Indonesia:** jangan percaya begitu saja, mengingat Kappa ≈0,3 lintas bahasa. Protokol yang saya sarankan:
  1. Kumpulkan sekitar 300–500 pasangan jawaban yang dinilai penutur asli dari komunitas (minimal 3 rater per item), atau gunakan IndoPref (4.099 preferensi) sebagai set kalibrasi awal.
  2. Uji 2–3 kandidat juri (misalnya Qwen3 besar dan SEA-LION v4.x secara lokal, serta satu model komersial via API jika anggaran ada). Ukur agreement dengan manusia (Cohen's κ, persentase setuju) dan pilih juri atau ensemble terbaik.
  3. Pakai pairwise dengan **pertukaran posisi** (A/B lalu B/A) untuk menetralkan bias posisi, batasi efek panjang (length-controlled), dan sediakan rubrik berbahasa Indonesia yang eksplisit (ketepatan, kewajaran bahasa, kesesuaian register, budaya).
  4. Hitung peringkat dengan Bradley-Terry beserta bootstrap confidence interval.
  5. Re-kalibrasi setiap kali juri diganti, dan publikasikan angka agreement-nya.

### 5.4 Arsitektur tooling

**Rekomendasi: jangan bikin harness dari nol.** Strukturnya:

```
indobench/
├── tasks/            # YAML lm-eval (MCQ, IFEval-ID) + task Inspect (chat, safety, judge)
├── plugins/          # plugin lm-eval: metrik chrF-ID, filter parsing jawaban Indonesia
├── runners/          # orchestrator Python: matriks (model × task × template × seed)
├── backends.yaml     # endpoint: ollama / llama-server / mlx_lm.server / vllm (cloud GPU)
├── results/          # JSONL per-sample + manifest (hash dataset, versi harness, quant, chat template)
└── site/             # Next.js statis: leaderboard, per-task, per-register, contoh jawaban
```

- **Eksekusi lokal di Mac M5:** jalankan model lewat `llama-server` (GGUF, Metal) atau `mlx_lm.server` (OpenAI-compatible), lalu panggil dengan backend `local-chat-completions` atau `gguf` milik lm-eval. Untuk log-likelihood MCQ dengan GGUF, backend `gguf` mendukung loglikelihood (wajib sertakan tokenizer, karena tanpanya bisa hang).\[65\] Untuk model besar (70B+) atau throughput tinggi, sewa GPU cloud per jam dan pakai `vllm`.
- **Modul generatif dan juri:** pakai Inspect (solver/scorer) atau runner Python async sederhana dengan FastAPI/httpx. Stack Python Anda sudah cocok.
- **Reproduksibilitas (wajib dicatat per run):** ID model + revisi/commit HF, format dan level kuantisasi, chat template (hash Jinja), system prompt, template prompt, n-shot, suhu (0 untuk tugas deterministik), seed, max tokens, mode "thinking" on/off (penting untuk Qwen3/Gemma generasi baru), versi lm-eval/Inspect, dan hash dataset. Simpan output per sampel agar bisa diaudit.
- **Leaderboard:** situs Next.js statis yang dibangun dari JSON hasil (gratis di Vercel/Cloudflare Pages). Tampilkan skor per kategori, *bukan hanya rata-rata*, filter "bisa jalan di laptop 16/32/64 GB", dan premium token. Alternatifnya, HF Space dengan template leaderboard resmi.
- **Rust/Go** tidak diperlukan di MVP. Kalau nanti butuh, bisa dipakai untuk CLI atau proxy load-balancing antar endpoint.

### 5.5 Komputasi dan biaya

- **Mac M5 (tergantung RAM unified):** model 7–14B Q4/Q8 nyaman, dan 27–32B Q4 (~18–20 GB) layak di mesin ≥36–48 GB. Throughput lokal kira-kira puluhan token/detik, jadi MCQ dalam jumlah ribuan soal per model butuh hitungan jam. Gunakan subset statistik yang memadai (500–1.000 item per task) untuk iterasi, dan set penuh hanya untuk rilis.
- **70B+ (Sahabat-AI v2 70B, Nemotron-SEA-LION 120B):** sewa GPU per jam. Kartu model menyebut 70B BF16 butuh sekitar 140 GB VRAM. Untuk varian bitsandbytes 4-bit, kartu HF komixenon/GoToCompany-Llama-Sahabat-AI-v2-70B-IT-BNB4 (diuji di A100, "VRAM 40G") menyebut bobotnya saja butuh sekitar 36 GB VRAM, belum termasuk KV cache.
- **Juri API:** biaya terbesar di modul chat. Pairwise N model membutuhkan O(N²) perbandingan, jadi pakai skema "lawan baseline tetap" atau sampling pasangan adaptif.
- **Hemat:** cache output generasi (jangan generate ulang ketika hanya juri yang berubah), dan evaluasi model kuantisasi yang memang dipakai orang (Q4_K_M) sambil melaporkannya secara eksplisit.

### 5.6 Lisensi dan etika

- **Dataset pihak ketiga:** banyak yang **NC** (XL-Sum, SEA-MTBench, MLHSD: CC BY-NC-SA). Tidak masalah untuk leaderboard nirlaba, tapi jangan dikomersialkan. Redistribusi harus mengikuti lisensi asli, jadi lebih aman memuat dari HF repo aslinya daripada menyalin.
- **Soal ujian** (UN/UTBK/ujian profesi/CPNS): status hak ciptanya tidak jelas. Lebih aman *menulis ulang* soal bergaya ujian daripada menyalin.
- **Teks berita/medsos:** pakai kutipan pendek atau parafrase, dan jangan menyertakan data pribadi. Patuhi **UU PDP**: hapus nama, nomor telepon, NIK, dan akun medsos dari data crowdsourcing.
- **Kontributor komunitas:** minta persetujuan lisensi (misalnya CC BY 4.0 untuk set publik), beri kredit, dan pertimbangkan kompensasi. Untuk konten safety, sediakan opsi dan dukungan bagi anotator yang terpapar konten berbahaya.
- **Topik SARA:** prompt safety disimpan privat, dan rilis contoh dibuat dengan hati-hati.
- **Lisensi model:** Gemma Terms of Use, Llama Community License, dan sebagainya. Memublikasikan skor umumnya aman, tetapi baca ketentuannya bila Anda mendistribusikan ulang bobot atau GGUF.

### 5.7 Pelajaran dari proyek yang sudah ada

- **SEA-HELM:** libatkan penutur asli di setiap tahap, tulis prompt dalam bahasa target, normalisasi skor terhadap baseline acak, dan sajikan tampilan per bahasa/per task.\[26\]
- **SeaExam/SeaBench:** soal lokal lebih diskriminatif daripada terjemahan, *tetapi tidak selalu* (untuk Indonesia, SeaExam tidak lebih diskriminatif). Validasi daya beda soal Anda secara empiris.
- **COPAL-ID:** selalu sediakan versi baku dan kolokial. Ini fitur pembeda termurah.
- **IndoSafety:** uji paralel lintas ragam dan bahasa daerah membuka kebocoran safety yang tidak terlihat di ragam formal.\[42\]
- **Open LLM Leaderboard:** benchmark statis berbasis MCQ akan usang.\[66\] Rencanakan penyegaran sejak hari pertama.
- **Sahabat-AI:** model lokal pun menilai diri dengan juri GPT-4 vs baseline GPT-3.5.\[67\] Benchmark independen dengan juri yang tervalidasi manusia akan sangat bernilai bagi ekosistem, termasuk sebagai kontribusi ke Sahabat-AI yang dulu Anda minati.

---

## Roadmap yang direkomendasikan

| Fase | Waktu | Deliverable |
|---|---|---|
| 0. Fondasi | Minggu 1–2 | Repo `indobench`; lm-eval terpasang dengan backend `local-chat-completions` ke Ollama/llama-server/mlx_lm; jalankan COPAL-ID, Global-MMLU-ID, dan IndoMMLU-subset pada 3 model (Qwen3 8B, Gemma-SEA-LION-v4-27B, Sahabat-AI 9B); skrip fertilitas tokenizer di FLORES-200 |
| 1. MVP publik | Bulan 1–3 | Tambah IndoCulture, IndoCareer, dan 3–5 template prompt per task; tulis IFEval-ID-Gaul (300+ item) bersama komunitas; leaderboard Next.js statis v0.1 untuk 10–15 model open-weight dengan manifest reproduksibilitas lengkap |
| 2. Generatif dan juri | Bulan 3–5 | IndoChat (200 prompt multi-turn native, campur register); 500 rating pairwise penutur asli + IndoPref untuk kalibrasi; pilih juri dengan κ tertinggi; peringkat Bradley-Terry dengan CI |
| 3. Perluasan | Bulan 5–8 | IndoCode (prompt Indonesia + unit test), IndoSafety Eval-2, matematika native, uji register/honorifik; held-out privat dan rilis "2027Q1" |
| 4. Komunitas dan keberlanjutan | Bulan 8+ | Arena voting komunitas (Elo), penyegaran kuartalan, bahasa daerah (Jawa/Sunda/Betawi), paper/technical report (misalnya workshop SEALP atau ACL), kolaborasi dengan AI Singapore/Sahabat-AI/IndoNLP |

## Caveats

- Banyak angka performa model berasal dari laporan pengembang modelnya sendiri (SEA-LION, Sahabat-AI) dengan juri dan setup mereka. Angka-angka itu tidak bisa dibandingkan langsung lintas paper.
- Rincian versi model 2026 (Qwen3.6, SEA-LION v4.5/v4.8, Gemini 3.5) diambil dari kartu model dan preprint terbaru yang sebagian belum peer-reviewed.
- Angka fertilitas tokenizer modern untuk bahasa Indonesia belum tersedia di sumber primer. Satu-satunya angka primer yang saya temukan adalah untuk Llama-2. Ukur sendiri sebelum memakainya sebagai klaim.
- Ringkasan sekunder sempat menyebut unsafe rate Sahabat-AI 25–45% "di bahasa daerah". Paper IndoSafety asli (ACL Anthology 2025.emnlp-main.465) ternyata menyebut angka 25–45% itu untuk kategori risiko *region-specific sensitivity*, bukan untuk bahasa daerah: "even SahabatAI shows 25-45% unsafe rates in region-specific sensitivity." Saat mengutip, rujuk tabel paper asli.
- Rekomendasi kebutuhan RAM/throughput di Mac adalah estimasi kasar dan sangat bergantung pada konfigurasi RAM M5 Anda.

## Sources

1. [LLM Sensitivity to Prompt Formatting](https://www.emergentmind.com/papers/2310.11324)
2. [Komodo: A Linguistic Expedition into Indonesia's Regional Languages](https://arxiv.org/pdf/2403.09362)
3. [Daily Papers - Hugging Face](https://huggingface.co/papers?q=multilingual+common-sense+reasoning)
4. [Harbor Adapters and Harbor-Index: Infrastructure and a Curated Meta-Dataset for Large-Scale Agentic Evaluation](https://arxiv.org/pdf/2609.04298)
5. [LLM rankings in 2026: how leaderboards work and which to trust](https://opper.ai/blog/llm-rankings-explained)
6. [Meta-Benchmarks for Financial-Services LLM Evaluation](https://arxiv.org/pdf/2607.01740)
7. [Format Sensitivity Index: Token-Controlled Prompt Wrapper Robustness and Schema Compliance in LLM Benchmarking](https://arxiv.org/pdf/2607.09665)
8. [LLM-as-Judge Evaluation](https://www.emergentmind.com/topics/llm-as-a-judge-evaluation)
9. [Challenges and Recommendations for LLM-as-a-Judge in Multilingual Settings and for Low-Resource Languages](https://arxiv.org/html/2607.02235)
10. [GitHub - EleutherAI/lm-evaluation-harness: A framework for few-shot evaluation of language models. · GitHub](https://github.com/EleutherAI/lm-evaluation-harness)
11. [lm-evaluation-harness/lm\_eval/tasks/global\_mmlu/README.md at main · EleutherAI/lm-evaluation-harness · GitHub](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/global_mmlu/README.md)
12. [lm-evaluation-harness/lm\_eval/tasks/copal\_id/README.md at main · EleutherAI/lm-evaluation-harness · GitHub](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/copal_id/README.md)
13. [GitHub - huggingface/lighteval: Lighteval is your all-in-one toolkit for evaluating LLMs across multiple backends · GitHub](https://github.com/huggingface/lighteval)
14. [Scaling FineWeb to 1000+ languages: Step 1: finding signal in 100s of evaluation tasks](https://huggingfacefw-blogpost-fine-tasks.hf.space/)
15. [lighteval/src/lighteval/tasks/multilingual/tasks/tydiqa.py at main · huggingface/lighteval · GitHub](https://github.com/huggingface/lighteval/blob/main/src/lighteval/tasks/multilingual/tasks/tydiqa.py)
16. [Enhancing Multilingual LLM Pretraining with Model-Based Data Selection](https://aclanthology.org/2025.swisstext-1.4.pdf)
17. [EvalSafetyGap: A Hybrid Survey and Conceptual Framework for LLM Evaluation-Safety Failures](https://arxiv.org/pdf/2606.30219)
18. [Published as a conference paper at ICLR 2024](https://par.nsf.gov/servlets/purl/10520219)
19. [Published as a conference paper at ICLR 2024](https://arxiv.org/pdf/2310.11324)
20. [GitHub - davda54/lm-evaluation-harness: A framework for few-shot evaluation of language models. · GitHub](https://github.com/davda54/lm-evaluation-harness)
21. [(PDF) Global MMLU: Understanding and Addressing Cultural and Linguistic Biases in Multilingual Evaluation](https://www.researchgate.net/publication/386454908_Global_MMLU_Understanding_and_Addressing_Cultural_and_Linguistic_Biases_in_Multilingual_Evaluation)
22. [Global MMLU: Understanding and Addressing Cultural and Linguistic Biases in Multilingual Evaluation - ACL Anthology](https://aclanthology.org/2025.acl-long.919/)
23. [CohereLabs/Global-MMLU · Datasets at Hugging Face](https://huggingface.co/datasets/CohereLabs/Global-MMLU)
24. [Global MMLU : Understanding and Addressing Cultural and Linguistic Biases in](https://arxiv.org/pdf/2412.03304)
25. [arXiv:2502.14301v2 \[cs.CL\] 2 Jun 2025 SEA-HELM:](https://arxiv.org/pdf/2502.14301)
26. [SEA-LION-v4.8: A Technical Report](https://arxiv.org/pdf/2609.18310)
27. [\[2502.14301\] SEA-HELM: Southeast Asian Holistic Evaluation of Language Models](https://arxiv.org/abs/2502.14301)
28. [SEA-HELM Audio: Evaluating Multilingual ASR-LLM Pipeline Performance Across SEA-HELM Subsets](https://arxiv.org/html/2610.19869)
29. [SeaExam and SeaBench: Benchmarking LLMs with Local](https://arxiv.org/pdf/2502.06298)
30. [SeaExam and SeaBench: Benchmarking LLMs with Local Multilingual Questions in Southeast Asia](https://arxiv.org/html/2502.06298v1)
31. [SEACrowd: A Multilingual Multimodal Data Hub and Benchmark Suite for Southeast Asian Languages](https://arxiv.org/pdf/2406.10118)
32. [COPAL-ID: Indonesian Language Reasoning with Local Culture and Nuances \[Quick Review\]](https://liner.com/review/copalid-indonesian-language-reasoning-with-local-culture-and-nuances)
33. [One Country, 700+ Languages: NLP Challenges for Underrepresented Languages and Dialects in Indonesia](https://arxiv.org/pdf/2203.13357)
34. [LoraxBench: A Multitask, Multilingual Benchmark Suite for 20 Indonesian Languages](https://arxiv.org/pdf/2508.12459)
35. [LORAXBENCH: A Multitask, Multilingual Benchmark Suite ...](https://aclanthology.org/2025.emnlp-main.881.pdf)
36. [Sahabat AI: Indonesian LLM Developer Guide and Token Costs](https://www.matthewswong.com/en/blog/sahabat-ai-indonesian-llm-developer-guide/)
37. [aisingapore/Gemma-SEA-LION-v4-27B · Hugging Face](https://huggingface.co/aisingapore/Gemma-SEA-LION-v4-27B)
38. [aisingapore/Gemma-SEA-LION-v4-27B-IT · Hugging Face](https://huggingface.co/aisingapore/Gemma-SEA-LION-v4-27B-IT)
39. [Sailor2: Sailing in South-East Asia with Inclusive Multilingual LLMs](https://arxiv.org/html/2502.12982v1)
40. [aisingapore/Gemma-SEA-LION-v3-9B · Hugging Face](https://huggingface.co/aisingapore/Gemma-SEA-LION-v3-9B)
41. [aisingapore/Llama-SEA-LION-v3-70B · Hugging Face](https://huggingface.co/aisingapore/Llama-SEA-LION-v3-70B)
42. [IndoSafety: Culturally Grounded Safety for LLMs in Indonesian Languages — Lacuna](https://lacuna.tiptreesystems.com/work/indosafety-culturally-grounded-safety-for-llms-in-indonesian-languages/wrk_37da3a69c47c95ed724448fcc92aad9c)
43. [Large Language Models Only Pass Primary School Exams in ...](https://aclanthology.org/2023.emnlp-main.760.pdf)
44. [Large Language Models Only Pass Primary School Exams in Indonesia: A Comprehensive Test on IndoMMLU - ACL Anthology](https://aclanthology.org/2023.emnlp-main.760/)
45. [GitHub - fajri91/IndoMMLU · GitHub](https://github.com/fajri91/IndoMMLU)
46. [Large Language Models Only Pass Primary School Exams in Indonesia: A Comprehensive Test on IndoMMLU — Lacuna](https://lacuna.tiptreesystems.com/work/large-language-models-only-pass-primary-school-exams-in-indonesia-a/wrk_2b93279f022c9d10992d9963863d4a65)
47. [Injecting Knowledge from Social Science Journals to Improve Indonesian Cultural Understanding by LLMs](https://arxiv.org/html/2601.12921)
48. [IndoCulture: Exploring Geographically-Influenced Cultural](https://arxiv.org/pdf/2404.01854)
49. [haryoaw/COPAL · Datasets at Hugging Face](https://huggingface.co/datasets/haryoaw/COPAL)
50. [SEACrowd/copal · Datasets at Hugging Face](https://huggingface.co/datasets/SEACrowd/copal)
51. [arXiv:2409.08564v2 \[cs.CL\] 22 Feb 2025](https://arxiv.org/pdf/2409.08564)
52. [IndoSafety: Culturally Grounded Safety for LLMs in Indonesian Languages · Pith Review](https://pith.science/paper/2506.02573)
53. [\[2507.22159\] IndoPref: A Multi-Domain Pairwise Preference Dataset for Indonesian](https://arxiv.org/abs/2507.22159)
54. [\[2508.12459\] LoraxBench: A Multitask, Multilingual Benchmark Suite for 20 Indonesian Languages](https://arxiv.org/abs/2508.12459)
55. [IndoBias: A Dual Track Culturally Grounded Benchmark for LLMs Bias Evaluation in Indonesian Languages](https://arxiv.org/html/2606.01260v1)
56. [Gemma SEA LION v4 27B IT NVFP4](https://huggingface.co/aisingapore/Gemma-SEA-LION-v4-27B-IT-NVFP4)
57. [SEA-HELM: Southeast Asian Holistic Evaluation of Language Models](https://arxiv.org/html/2502.14301)
58. [Sahabat-AI (Sahabat-AI)](https://huggingface.co/Sahabat-AI)
59. [GitHub - DAMO-NLP-SG/SeaExam: SeaExam: Benchmarking LLMs for Southeast Aisa languages with Human Exam Questions · GitHub](https://github.com/DAMO-NLP-SG/SeaExam)
60. [arXiv:2310.04928v2 \[cs.CL\] 21 Oct 2023](https://arxiv.org/pdf/2310.04928)
61. [aisingapore/Gemma-SEA-LION-v4-27B-IT](https://ollama.com/aisingapore/Gemma-SEA-LION-v4-27B-IT)
62. [aisingapore/Qwen-SEA-LION-v4.5-27B-IT](https://ollama.com/aisingapore/Qwen-SEA-LION-v4.5-27B-IT)
63. [GitHub - sail-sg/sailor2: 🔱 Sailor2: Sailing in South-East Asia with Inclusive Multilingual LLMs · GitHub](https://github.com/sail-sg/sailor2/tree/main)
64. [SEA-LION: Southeast Asian Languages in One Network](https://arxiv.org/pdf/2504.05747)
65. [lm-eval-harness Practical Guide](https://jonathanding.github.io/llm-learning/en/articles/lm-eval-harness-guide/)
66. [Hugging Face retires the Open LLM Leaderboard • It Does What Now?](https://itdoeswhatnow.com/m/2025-03-14-hugging-face-retires-the-open-llm-leaderboard/)
67. [Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT · Hugging Face](https://huggingface.co/Sahabat-AI/Llama-Sahabat-AI-v2-70B-IT)
