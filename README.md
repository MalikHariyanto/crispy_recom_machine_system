# Rekomendasi wisata Madura

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

Paket di `data/` memuat 79.514 ulasan dari 207 destinasi dalam lima bagian CSV terkompresi. Paket berisi teks siap-model, ID dan nama destinasi, dua label, dan penanda audit yang dihitung dari Excel. File `manifest.json` menyimpan jumlah baris dan checksum setiap bagian. Teks ulasan asli, nilai tanggal, dan rating tersedia pada workbook sumber.

Workbook memuat lokasi dari luar Madura, termasuk Kebun Binatang Surabaya, dan belum menyediakan kolom kabupaten. Bagian 01 menulis `template_verifikasi_wilayah.csv`. Isi `kabupaten` dengan Bangkalan, Sampang, Pamekasan, Sumenep, atau Di luar Madura setelah memeriksa lokasi. Biarkan kosong jika lokasi belum terverifikasi. Simpan dengan nama lain dan setel `REGION_PATH` untuk memakai hanya ID yang terverifikasi di Madura. Tanpa CSV tersebut, metrik dan katalog mencakup workbook campuran.

Sekitar 20% ID pada tiap jenis wisata dipilih sebagai data uji. Pengulangan teks dalam satu destinasi disisihkan dan teks uji yang identik dengan teks latih dikeluarkan. Pada seluruh workbook yang dipakai di laporan, prosedur ini menghasilkan 164 destinasi latih dan 43 destinasi uji. Vektor FastText dan kosakata LDA dipelajari dari data latih. Satu model LDA bersama dipakai agar tiap dimensi topik bermakna sama di semua contoh dan dapat dibentuk tanpa membaca label contoh uji.

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
