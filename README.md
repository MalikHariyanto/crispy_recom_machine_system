# Madura Explore — riset dan aplikasi wisata Madura

Dataset aktif: **2.058 ulasan, 27 destinasi, 8 kategori wisata** dari `data/source/dataset_madura_bersih.xlsx`. Seluruh dataset dinyatakan Madura oleh pemilik data. Paket model terkompresi pada `data/` diverifikasi melalui checksum manifest.

## Colab v3 · Input → Proses → Output

[Buka langsung di Google Colab](https://colab.research.google.com/github/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb) · [Kode notebook](notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb) · [Panduan lengkap](docs/COLAB_V3.md).

Urutan section:

| Section | Isi |
|---|---|
| 00 | Setup, mode full/smoke, parameter dan seed |
| 01 | Input otomatis, checksum, skema, teks dan dua label |
| 02 | Audit dan grafik rating/cuaca/jenis/panjang ulasan |
| 03 | Pembersihan dan split train/validation/test per destinasi |
| 04 | Pemodelan LDA, seleksi K dengan validation NPMI |
| 05 | Interpretasi bobot kata dan contoh ulasan tiap topik |
| 06 | Embedding FastText dari train saja, token IDs, matriks embedding |
| 07 | Modeling dua BiLSTM dan pembanding, validation checkpoint |
| 08 | Output prediksi test, metrik/support per kelas, ringkasan seed |
| 09 | Diagram alur aktual, provenance, daftar output, ZIP |

Setiap section menjelaskan **Input, Proses, Output**. `DATA_PATH=None` langsung memuat data bawaan tanpa upload. `MODE="full"` menjalankan 18 kandidat LDA dan tiga seed embedding/BiLSTM; GPU disarankan. `MODE="smoke"` menguji alur cepat dan bukan eksperimen final. `RUN_DEEP=False` melewati embedding/BiLSTM secara eksplisit.

LDA menghasilkan distribusi topik dari count kata; FastText menghasilkan embedding token. BiLSTM memproses embedding, lalu hidden state digabung dengan distribusi topik pada varian gabungan. Dua kepala memprediksi kecocokan cuaca dan jenis wisata. Rating hanya dipakai dalam EDA. Ini bukan klasifikasi sentimen.

## Protokol dan interpretasi

V3 mencegah ID destinasi dan teks identik bertumpang tindih antarpartisi. Kandidat split dipilih berdasarkan ukuran kelompok serta distribusi label yang diumumkan sebelum fitting, bukan skor model. Default terbaru: **1.168/268/426 ulasan** dan **16/5/6 destinasi** untuk train/validation/test setelah pembersihan. Proporsi tidak dipaksakan tepat 64/16/20 karena kelompok tidak dipecah.

Pembobotan sampel/kelas berasal dari kelompok train; FastText dan kosakata/LDA fit train saja. Validation memilih K/checkpoint. Test dilaporkan untuk seluruh model/seed yang ditetapkan, tanpa memilih seed terbaik. Pembanding klasik satu run; deep tiga seed. Kelas train-only dan support nol dilaporkan; enam destinasi test membatasi kesimpulan. Tidak ada klaim bias nol, K semantik benar, atau penambahan LDA pasti meningkatkan skor.

[Landasan keputusan dan paper](docs/METODOLOGI_DAN_PAPER.md) · [Log akses sumber literatur](docs/literature_access_2026-11-12.json). Sebagian full text dibatasi jaringan; metadata/abstrak/sumber implementasi yang diakses dibedakan dari full text yang belum terbaca.

## Streamlit · SISRE

Satu halaman rekomendasi wisata: pencarian, filter musim/jenis, saran pencarian, dan kartu lokasi. Data dimuat otomatis; tidak memerlukan unggahan file pengguna.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Deploy Streamlit Cloud: repository `MalikHariyanto/crispy_recom_machine_system`, branch **`feat/streamlit-wisata`**, main file **`app.py`**, Python **3.11**. [Panduan deployment](docs/STREAMLIT.md).

Default pencarian TF-IDF ringan; BGE-M3 opsional memerlukan dependensi/model tambahan. Pipeline klasifikasi Colab dan ranking wisata merupakan evaluasi berbeda. Metrik classifier bukan bukti akurasi rekomendasi BGE/TF-IDF.

## Struktur

```text
app.py / .streamlit/                 entry point dan tema Streamlit
src/wisata_madura/
  data.py                            loader, audit, split v2 historis
  protocol.py                        split v3 dan bobot destinasi
  topics.py                          LDA, seleksi, diagnostik topik
  neural.py                          FastText, BiLSTM, checkpoint
  modeling.py                        pembanding klasik dan evaluasi
  visualization.py                   EDA dan grafik split
  reporting.py                       alur, prediksi, ringkasan, manifest
  web/                               UI, cache, layanan pencarian
notebooks/                           notebook pembelajaran utama
scripts/build_colab_notebook.py       satu sumber pembentuk notebook
scripts/build_dataset_bundle.py       pembentuk paket data ber-checksum
tests/                               tes protokol, model, data, dan UI
```

Notebook lama menjadi tautan ke notebook utama; implementasi model tidak disalin berulang. Rebuild notebook dengan `python scripts/build_colab_notebook.py`.

## Pengujian riset

```bash
pip install -r requirements-wisata.txt
pip install 'gensim>=4.4,<5' 'torch>=2.2,<3'
PYTHONPATH=src python -m unittest discover -s tests -v
```

Tes UI juga memerlukan `requirements.txt`. Tes meliputi kebocoran kelompok/teks, invariansi seleksi LDA terhadap teks test, checkpoint terbaik, bobot kelompok, cakupan metrik, bundle Excel, dan navigasi Streamlit. Untuk tes Colab penuh, jalankan notebook dengan `MODE="full"`.

## Pembaruan data dan arsip

```bash
python scripts/build_dataset_bundle.py data/source/dataset_madura_bersih.xlsx
```

Memerlukan dependensi riset termasuk openpyxl. Script mendukung sheet `Sheet1` tunggal maupun `Data Ulasan`, memvalidasi skema, menghitung audit/checksum, dan mengganti paket lama. Cache web memakai versi manifest.

Berkas lama pada `deliverables/`, `reports/lampiran/`, dan laporan PDF/DOCX adalah artefak penelitian sebelumnya. Angka 79.514/207, split v2, dan hasil v1/v2 tidak otomatis menjadi hasil dataset/protokol v3. Jangan membandingkan perubahan skor sebagai efek arsitektur saja ketika split/pembobotan/definisi metrik berubah.

## Tuning kelompok (eksplorasi)

[Notebook tuning](notebooks/Colab_Tuning_Kelompok_Madura.ipynb) · [Buka di Colab](https://colab.research.google.com/github/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/notebooks/Colab_Tuning_Kelompok_Madura.ipynb) · [Protokol](docs/TUNING_PROTOCOL.md).

Tiga fold destinasi, dua seed, empat kandidat konfigurasi dan dua ablation. Seluruh dataset lama diperlakukan sebagai development karena test sebelumnya sudah diamati. Validation dipakai memilih parameter; skornya bukan estimasi independen. Pemeriksaan data eksternal disediakan, tetapi evaluasi independen dan refit model final menunggu data baru serta protokol beku.
