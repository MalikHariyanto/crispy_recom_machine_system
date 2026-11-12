# Rekomendasi wisata Madura

## Aplikasi Streamlit — Madura Explore

Antarmuka web untuk pencarian rekomendasi, katalog destinasi, insight dataset tanpa unggahan file. Jalankan `pip install -r requirements.txt` lalu `streamlit run app.py`.

**Deploy Streamlit Cloud:** repository `MalikHariyanto/crispy_recom_machine_system`, branch `feat/streamlit-wisata`, main file `app.py`, Python **3.11**. [Panduan deployment dan arsitektur](docs/STREAMLIT.md).

Pencarian default memakai TF-IDF yang ringan; BGE-M3 opsional. Dataset terbaru seluruhnya destinasi Madura sesuai konfirmasi pemilik data; aplikasi langsung memuatnya dari repository. Pelatihan dan evaluasi riset tetap dilakukan melalui notebook di bawah.

Pipeline penelitian asistensi Malik Hariyanto untuk mengolah ulasan Google Maps, membandingkan model klasifikasi atribut destinasi, dan mencoba pemeringkatan destinasi dengan BGE.

## Mulai dari Colab

1. Buka [notebook](notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb), unduh file `ipynb`, lalu unggah ke Colab.
2. Jalankan dengan `DATA_PATH = None`. Sel konfigurasi mengambil repo dan bagian **01** memuat data bawaan otomatis, tanpa unggah Excel. Gunakan `DATA_PATH` hanya untuk memilih workbook alternatif.
3. Jalankan dari **00 Konfigurasi**. Gunakan runtime GPU bila mengaktifkan `RUN_DEEP`. Untuk mencoba audit, LDA, dan baseline lebih dulu, atur `RUN_DEEP = False` sebelum sel instalasi.
4. Untuk mencoba pemeringkatan, atur `RUN_BGE = True` pada bagian **00** lalu isi preferensi di bagian **09**. Jalur ini mengunduh model BGE-M3. Unduhan dan encoding pertama dapat memerlukan waktu serta memori tambahan.
5. Buka folder `hasil_wisata_madura/` di runtime untuk mengambil hasil audit, daftar topik, metrik klasifikasi, atau hasil rekomendasi yang dijalankan.

Untuk penggunaan lokal, buka notebook dari salinan repo pada cabang ini. Gunakan Python 3.10 atau lebih baru serta lingkungan virtual. Bagian **00** akan memakai modul lokal dan memasang paket sesuai konfigurasi. Jika memakai Jupyter, gunakan kernel dari lingkungan virtual tersebut.

## Susunan kode

| Bagian | Isi |
|---|---|
| 00–03 | Konfigurasi, validasi workbook, audit, pembersihan ringan, dan pemisahan berdasarkan ID destinasi |
| 04–05 | Pembanding mayoritas dan TF-IDF + Linear SVC, eksplorasi topik, serta klasifikasi dengan fitur LDA saja |
| 06–07 | Pelatihan FastText, penyusunan urutan vektor, dan dua varian BiLSTM |
| 08 | Metrik agregat serta per kelas pada tingkat ulasan dan destinasi |
| 09–10 | Katalog, rekomendasi BGE, penilaian relevansi opsional, dan daftar keluaran |

Notebook mengatur urutan dan menjelaskan hasil setiap bagian. Implementasi ada di `src/wisata_madura/`.

- `data.py` membaca workbook, mengecek konsistensi label, dan membentuk data latih serta uji.
- `modeling.py` menjalankan baseline, LDA, klasifikasi berbasis fitur topik, dan evaluasi.
- `neural.py` melatih FastText serta BiLSTM dengan satu kepala klasifikasi per target.
- `recommendation.py` membangun katalog, memeringkat destinasi, dan menghitung metrik rekomendasi jika tersedia penilaian independen.

## Dataset dan skenario

Workbook sumber menyediakan `id_destinasi`, `destinasi`, `rating`, `date`, `text_original`, `text_preprocessed`, `rekomendasi_cuaca`, dan `wisata`. Dua kolom terakhir adalah atribut per destinasi. Tanggal dalam versi ini relatif terhadap waktu pengambilan, sedangkan anotasi sentimen belum tersedia. Pemodelan musim kunjungan dan sentimen dapat ditambahkan setelah definisi label dan sumber datanya siap.

Paket aktif di `data/` berasal dari `data/source/dataset_madura_bersih.xlsx` (pembaruan 12 November 2026): **2.058 ulasan dari 27 destinasi**, dalam satu bagian CSV terkompresi. Dataset ini menggantikan paket lama berisi 79.514 ulasan/207 destinasi. Paket berisi teks siap-model, ID dan nama destinasi, dua label, dan penanda audit yang dihitung dari Excel. File `manifest.json` menyimpan jumlah baris dan checksum setiap bagian. Teks ulasan asli, nilai tanggal, dan rating tersedia pada workbook sumber.

Dataset aktif sepenuhnya Madura sesuai konfirmasi pemilik data. Aplikasi memuat dataset tersebut secara otomatis dan langsung menampilkan katalog serta pencarian.

Sekitar 20% ID pada tiap jenis wisata dipilih sebagai data uji. Pengulangan teks dalam satu destinasi disisihkan dan teks uji yang identik dengan teks latih dikeluarkan. Pada dataset lama yang dipakai di laporan, prosedur ini menghasilkan 164 destinasi latih dan 43 destinasi uji; angka tersebut bukan hasil dataset aktif terbaru. Vektor FastText dan kosakata LDA dipelajari dari data latih. Satu model LDA bersama dipakai agar tiap dimensi topik bermakna sama di semua contoh dan dapat dibentuk tanpa membaca label contoh uji.

| Skenario | Masukan dan pengklasifikasi |
|---|---|
| Mayoritas | Kelas yang paling sering muncul pada data latih |
| TF-IDF + Linear SVC | Frekuensi berbobot unigram dan bigram |
| LDA saja | Vektor distribusi topik dengan regresi logistik |
| FastText saja | Urutan vektor kata dengan BiLSTM |
| FastText + LDA | Keluaran BiLSTM digabung dengan vektor topik sebelum kepala klasifikasi |

Perbandingan FastText saja dan FastText + LDA mempertahankan arsitektur urutan. Skenario LDA saja memakai model tabular karena distribusi topik tidak berurutan. Evaluasi mengukur klasifikasi dua atribut yang tersedia. Untuk mengukur kegunaan rekomendasi BGE, masukkan CSV relevansi terpisah dengan kolom `query_id,preferensi,musim,id_destinasi`. Tiap baris memuat satu ID destinasi yang dinilai relevan untuk kueri tersebut. `musim` diisi Kemarau, Penghujan, atau dikosongkan. Tanpa CSV, notebook hanya menampilkan contoh peringkat.

## Rujukan implementasi

- [Gensim FastText](https://radimrehurek.com/gensim/models/fasttext.html)
- [PyTorch LSTM](https://docs.pytorch.org/docs/stable/generated/torch.nn.LSTM.html)
- [Kartu model BGE-M3](https://huggingface.co/BAAI/bge-m3)

## Versi 2 — analisis LDA dan validasi pelatihan

Gunakan notebook pada `notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb` untuk kode terbaru. Berkas dalam `deliverables/revisi-hki/` adalah arsip pengiriman v1; paket terbaru ada pada `deliverables/lda-v2/`. `DATA_PATH=None` tetap memuat seluruh dataset otomatis, tanpa Excel/manual.

Perubahan v2:
- Train/validation/test dipisahkan per destinasi, dengan pemeriksaan ID dan teks identik. Semua model belajar dari train yang sama.
- 18 kandidat LDA: K=2,4,6,8,10,12 × seed=42,43,44. Pemilihan berdasarkan rerata **validation document NPMI**; perplexity, diversity, dan stability Jaccard dilaporkan.
- Stopword Indonesia/Inggris eksplisit dengan negasi dipertahankan, contoh ulasan tiap topik, bobot kata, template penamaan/review manusia, tiga gambar LDA.
- BiLSTM: train/validation loss, early stopping, checkpoint terbaik dipulihkan sebelum prediksi test. Maksimum 15 epoch, patience=3.
- Model/vectorizer LDA, FastText, matriks embedding/token, checkpoint, konfigurasi, hash kode, dan hasil disimpan pada folder run.

**Dasar paper untuk tiap keputusan dan parameter:** [docs/METODOLOGI_DAN_PAPER.md](docs/METODOLOGI_DAN_PAPER.md). Dokumen membedakan dukungan metode, adaptasi lokal, dan angka eksperimen yang belum optimal. Topik yang kurang koheren tetap dilaporkan; pemilihan K tidak membuktikan topiknya sudah baik. Parameter lama dan nilai hasil v1 tidak otomatis berlaku untuk v2.

Keluaran penting:

| Berkas | Dibaca untuk |
|---|---|
| `pencarian_lda.csv`, `pemilihan_topik.csv` | Seluruh kandidat dan ringkasan antar-seed |
| `audit_lda.json`, `kualitas_topik.csv` | Parameter, definisi NPMI, topik lemah, batas grid |
| `bobot_kata_topik.csv`, `contoh_ulasan_topik.csv` | Dasar interpretasi topik |
| `template_review_topik.csv` | Nama/catatan hasil review manusia, bukan label otomatis |
| `pemilihan_topik.png`, `kata_utama_topik.png`, `heatmap_topik_cuaca.png` | Gambar analisis LDA |
| `riwayat_bilstm.csv`, `kurva_bilstm.png`, `models/checkpoint_bilstm.csv` | Loss train/validation dan epoch terbaik |
| `metrik_klasifikasi.csv`, `metrik_per_kelas.csv`, `perbandingan_model.png` | Evaluasi test pada model yang benar-benar dijalankan |
| `audit_dataset.json`, `id_partisi_*.csv` | Data, konfigurasi, versi paket, hash modul, dan split |

Catatan: NPMI berbasis dokumen tidak identik dengan c_v atau NPMI sliding window. Tiga seed pencarian LDA tidak berarti BiLSTM diuji tiga seed. Wilayah belum terverifikasi dan label sentimen/waktu kunjungan belum tersedia. Katalog BGE tetap opsional (`RUN_BGE=False`) dan bukan fusion BGE-E5.

Tes regresi (memerlukan base requirements, gensim dan torch):

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Tes meliputi NPMI dengan probabilitas diketahui, invariansi nomor topik, pemisahan tiga partisi, tidak digunakannya test untuk memilih K/kosakata, dan pemulihan checkpoint terbaik sebelum prediksi.

## Memperbarui paket data

Jalankan `python scripts/build_dataset_bundle.py data/source/dataset_madura_bersih.xlsx` dengan dependensi `requirements-wisata.txt`. Script memvalidasi skema, menghitung ulang penanda audit/checksum, dan mengganti paket lama. Workbook satu sheet (`Sheet1`) serta format lama (`Data Ulasan`) didukung. Nilai label, ID, rating, dan teks sumber tidak dikoreksi otomatis. Hasil pelatihan, laporan, dan screenshot historis tidak dihitung ulang oleh pembaruan dataset.

## Grafik eksplorasi dan pembagian data di Colab

Notebook terbaru memiliki bagian **02B** (batang rating 1–5, batang cuaca, donut cuaca per destinasi, pie jenis wisata dengan persentase, histogram panjang teks) dan **03** (jumlah serta persentase aktual train/validation/test untuk ulasan dan destinasi). Grafik disimpan PNG dan tabel CSV ke folder run. Split tetap berdasarkan ID destinasi dengan pemeriksaan kebocoran teks; bukan pembagian acak baris ulasan.

[Buka langsung di Google Colab](https://colab.research.google.com/github/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb). Clone notebook mengambil branch `feat/streamlit-wisata` agar memakai dataset terbaru.
