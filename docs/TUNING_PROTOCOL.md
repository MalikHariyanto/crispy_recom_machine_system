# Protokol tuning kelompok destinasi

Status: **eksplorasi development**, evaluasi independen belum tersedia. Dataset yang pernah menjadi test pada v2/v3 sudah diamati, sehingga seluruh 27 destinasi diperlakukan sebagai development. Membagi ulang dataset ini tidak menciptakan final holdout yang independen.

## Rencana sebelum fitting

- 3 fold berdasarkan ID destinasi, seed fold 20261112. Setiap destinasi eligible menjadi validation tepat sekali; tidak ada ID/teks identik yang berbagi train dan validation dalam fold yang sama.
- Kelas singleton cuaca/jenis dijaga train-only. Cakupan tiap kelas/fold diekspor; bukan klaim generalisasi untuk kelas tersebut.
- Dua seed pelatihan: 42/43. LDA K 2/4/6, seed 42/43, maksimal10 iterasi, fit kosakata/model hanya pada train. Validation memilih K.
- Empat kandidat ditetapkan pada `CANDIDATES`: compact, wider, slower, finetune. Embedding80/128, hidden32/64, lr.001/.0003, dropout.2/.3/.4, frozen/fine-tuning. Panjang urutan menggunakan kuantil .90/.95 train, dibatasi16–128. Maksimal15 epoch/patience3.
- Setiap kandidat dibandingkan dengan/tanpa LDA. Bobot kelompok/kelas berasal dari train. Baseline klasik fit sekali/fold dan dilaporkan terpisah.
- Objective: rerata destination macro-F1 kedua target per fold/seed, kemudian rerata seluruh unit tersebut. Seluruh kelas development disertakan; support nol ditampilkan. Seri memakai urutan kandidat kemudian nama model.
- Protokol/fingerprint dataset/fold assignment disimpan sebelum pelatihan. Run tidak boleh menimpa folder protokol lama.

Validation dipakai berulang untuk K/checkpoint/hiperparameter. Karena itu skor seleksi cenderung optimistis dan bukan nested CV atau estimasi final tanpa bias. SD antar-fold/seed bukan confidence interval. Tidak ada pemilihan seed terbaik atau klaim optimum global. Tidak ada klaim bahwa kandidat deep mengalahkan baseline jika tabel menunjukkan sebaliknya.

## Efisiensi dan isolasi

FastText fit sekali per fold/seed/kombinasi embedding-panjang dan dipakai ulang. Setiap BiLSTM menyalin matriks embedding, sehingga fine-tuning satu ablation tidak memengaruhi inisialisasi ablation lain. Tidak ada dataset independen sebagai argumen `run_grouped_tuning`; slot `test` pada API model lama diisi validation fold untuk memperoleh prediksi validation, dan tidak dilaporkan sebagai test independen.

Notebook: [Colab_Tuning_Kelompok_Madura.ipynb](../notebooks/Colab_Tuning_Kelompok_Madura.ipynb). Sumber notebook: `scripts/build_tuning_notebook.py`. Implementasi: `src/wisata_madura/tuning.py`.

## Evaluasi independen yang masih diperlukan

1. Bekukan pilihan konfigurasi dan aturan refit/epoch menggunakan development saja. Checkpoint tuning per-fold belum merupakan model final.
2. Sediakan data destinasi baru yang belum dipakai memilih protokol/fit/tuning. Catat asal dan tanggal pengumpulannya; jangan mengganti ID dataset lama agar terlihat baru.
3. Jalankan `validate_independent_data`: tolak overlap ID, nama destinasi, teks, serta label baru yang memerlukan protokol lain. Pemeriksaan otomatis tidak membuktikan provenance independen.
4. Latih model final menurut protokol beku, lalu evaluasi data eksternal sekali. Jika hasil dipakai untuk tuning ulang, diperlukan evaluasi independen baru.

Belum ada data eksternal baru dalam sesi ini. Karena itu tidak ada skor independen, klaim generalisasi baru, atau deployment model otomatis. Terpilih pada validation hanya berarti terbaik di antara kandidat yang diuji pada development ini.
