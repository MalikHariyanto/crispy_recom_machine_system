# Colab v3: Input → Proses → Output

[Notebook GitHub](../notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb) · [Jalankan di Colab](https://colab.research.google.com/github/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb).

## Urutan belajar

| Section | Input | Proses | Output utama |
|---|---|---|---|
| 00 Setup | Repo, mode, seed | Instalasi dan konfigurasi | Dependensi, folder run, hash kode |
| 01 Input | Excel terbaru, manifest | Validasi checksum/skema; normalisasi | `reviews`, rating dan dua label |
| 02 Audit/EDA | Seluruh reviews | Statistik, batang/pie/histogram | Grafik PNG, tabel CSV, audit |
| 03 Split | Reviews dan rasio yang ditetapkan | Deduplikasi, pemisahan ID kelompok, pemeriksaan teks | Train/validation/test, cakupan setiap kelas |
| 04 LDA | Teks train dan validation | CountVectorizer train-only; grid K/seed; seleksi validation NPMI | Distribusi topik, K terpilih, model/vectorizer |
| 05 Interpretasi | Model LDA yang sudah fit | Baca kata, contoh, topik lemah | Template penamaan topik manusia |
| 06 Embedding | Teks train | FastText skip-gram/subword; frozen lookup untuk holdout | Token IDs, embedding matrix, FastText per seed |
| 07 Modeling | Embedding + distribusi topik + label | Dua BiLSTM, early stopping, pembanding | Checkpoint, loss, prediksi belum dinilai |
| 08 Evaluasi | Prediksi semua run dan label test | Metrik per ulasan/per destinasi, semua seed | Prediksi, per-class support, rerata/SD seed |
| 09 Ekspor | Semua artefak dan parameter | Provenance dan ZIP | Audit, daftar file, arsip unduhan |

Bagian embedding dan modeling sengaja terpisah. LDA dan FastText adalah dua jalur fitur yang sama-sama fit pada **train**, kemudian distribusi topik LDA dikonkatenasi dengan hidden state BiLSTM. LDA tidak menghasilkan embedding FastText dan tidak langsung memberi label cuaca/jenis. Dua kepala klasifikasi memprediksi dua target satu label per contoh; bukan classifier sentimen multilabel.

## Jalankan

Gunakan runtime Colab baru dan jalankan dari atas. `DATA_PATH=None` memuat dataset Madura terbaru tanpa upload. `MODE="full"` memakai 18 kandidat LDA dan tiga seed embedding/BiLSTM, masing-masing dua ablation (maksimal 15 epoch, early stopping). GPU disarankan. `MODE="smoke"` menguji alur dengan grid kecil dan dua epoch; tidak boleh dilaporkan sebagai eksperimen final. `RUN_DEEP=False` melewati embedding/BiLSTM secara eksplisit.

Hasil tersimpan pada folder run unik. Keluaran section 09 adalah ZIP; aktifkan dua baris `google.colab.files.download` bila ingin mengunduh otomatis. Model pickle/joblib/torch hanya boleh dimuat dari run/sumber tepercaya.

## Perbaikan protokol

Dataset saat ini berisi 27 destinasi dengan ukuran sangat berbeda. Split v2 menghasilkan hanya 342 ulasan train dan 1.446 test. V3 memakai 2.048 kandidat kelompok berseed tetap, memilih penyimpangan ukuran ulasan dan distribusi cuaca terkecil sesuai formula yang diumumkan. Pemilihan memakai metadata ID/ukuran/label, **tidak memakai skor model, embedding, atau topik**. Ini desain rekayasa lokal, bukan algoritma yang diklaim persis berasal dari jurnal.

Dengan konfigurasi default, setelah pembersihan: **1.168 train / 268 validation / 426 test ulasan**; **16/5/6 destinasi**. Persentase ulasan 62,73%/14,39%/22,88%. Grafik selalu dihitung dari hasil aktual. Validation/test membuang teks identik yang sudah ada pada partisi sebelumnya; train tidak menerima label atau fitur hasil fit holdout.

Destinasi berkelas singleton tetap di train. Tabel `cakupan_kelas_partisi.csv` mengungkap kelas yang tidak terwakili di validation/test. Hal ini membatasi pemilihan checkpoint dan bukti generalisasi; tidak disembunyikan melalui rerata metrik.

Bobot sampel memberi setiap destinasi massa total yang sama dalam training. Bobot kelas dihitung dari frekuensi **destinasi train**, lalu digunakan oleh SVC, regresi logistik, dan loss dua kepala. Validation menggunakan bobot kelas train serta pembobotan unit destinasi validation. Ini mengurangi dominasi destinasi ramai, bukan jaminan bahwa semua bentuk bias hilang. TF-IDF dan FastText masih mempelajari statistik korpus train; ketimpangan representasi serta kesalahan preprocessing/label sumber tetap mungkin ada.

## Tidak ada pelatihan berulang yang tidak perlu

- Hanya satu implementasi LDA aktif, `analyze_topics`; fungsi LDA v1 yang terpisah sudah dihapus.
- Model/vectorizer LDA hasil seleksi dipakai ulang untuk interpretasi dan classifier.
- FastText fit sekali per seed; embedding yang sama dipakai kedua ablation BiLSTM pada seed tersebut.
- Pembanding klasik dilatih sekali. Tidak digandakan menjadi tiga observasi identik; kolom `runs` membedakan satu run klasik dan tiga seed deep.
- Notebook lama menjadi tautan menuju notebook utama. Sumber notebook dipusatkan pada `scripts/build_colab_notebook.py` agar penjelasan, parameter, dan kode tetap konsisten.
- BGE dan aplikasi Streamlit tetap tahap rekomendasi terpisah. Metrik classifier tidak disebut sebagai akurasi ranking wisata.

## Membaca hasil secara tepat

Macro-F1 utama mengevaluasi seluruh kelas yang diketahui; kelas tanpa support test tetap dicantumkan dengan nol dan support=0. `macro_f1_present` melaporkan kelas yang benar-benar hadir di test, sebagai pelengkap dengan denominator berbeda. Accuracy=micro-F1 dan Hamming loss=1−accuracy untuk setiap target satu label; ketiganya bukan bukti independen. Voting destinasi memakai mayoritas; seri diputuskan dengan urutan label, tanpa label aktual.

K terpilih dapat tetap memiliki NPMI negatif. Ini berarti kata topik kurang sering muncul bersama menurut ukuran dokumen yang digunakan; jangan menamai topik itu sebagai aspek tervalidasi. Rerata ± SD tiga seed hanya menunjukkan variasi acak dalam satu split, bukan confidence interval atau validasi antardataset. Enam destinasi test terlalu sedikit untuk klaim umum yang kuat. Hindari tuning ulang setelah membaca skor test; eksperimen berikutnya harus mencatat protokol dan menyimpan evaluasi baru yang independen.

Hasil v3 tidak langsung dibandingkan dengan v2 sebagai efek arsitektur: dataset/split/pembobotan/definisi macro-F1 sudah berubah. Tidak ada jaminan penambahan LDA memperbaiki hasil; seluruh ablation dilaporkan.

## Modul

`data.py`: loader/audit. `protocol.py`: split dan bobot destinasi. `topics.py`: count/LDA/seleksi. `neural.py`: FastText dan BiLSTM. `modeling.py`: pembanding dan metrik. `visualization.py`: EDA dan grafik split. `reporting.py`: prediksi, ringkasan seed, manifest output. Notebook mengorkestrasi dan menjelaskan; tidak menyalin implementasi model ke setiap sel.

## Landasan dan bukti

Lihat [pemetaan keputusan ke paper](METODOLOGI_DAN_PAPER.md) dan [log akses literatur](literature_access_2026-11-12.json). Tinjauan ini terarah pada fondasi metode dan evaluasi, bukan klaim akses seluruh jurnal relevan atau systematic review lengkap. Sebagian publisher/full text dibatasi jaringan. Metadata/abstrak resmi dan implementasi sumber yang berhasil diakses dibedakan dari full text yang belum terbaca.
