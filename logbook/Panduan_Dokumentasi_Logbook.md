# Panduan gambar dokumentasi logbook minggu 1–12

Setiap sel kolom **Bukti Dokumentasi/Foto** sekarang memiliki penanda **[TEMPEL GAMBAR Mxx-Dxx]**, jenis gambar yang disarankan, serta isian tanggal aktual dan caption/file. Kode yang sama dipakai pada panduan ini. Ini arahan pengisian; gambar/foto belum dimasukkan dan status pelaksanaan belum diubah.

## Cara mengisi

1. Pilih gambar hasil pekerjaan sendiri yang cocok dengan kegiatan yang benar-benar dilakukan: tangkapan layar kode/output, tabel analisis, draf dokumen, atau foto bimbingan bila ada.
2. Klik penanda pada Word lalu sisipkan gambar. Pilih tata letak **In Line with Text** dan sesuaikan lebar dengan sel. Tabel dapat memanjang setelah gambar dimasukkan; untuk gambar besar gunakan halaman lampiran dengan kode bukti yang sama.
3. Beri caption: **M08-D04 — [kegiatan aktual], [tanggal aktual], [nama file/versi/run]**. Jangan menyamakan tanggal rencana dengan tanggal pelaksanaan tanpa bukti.
4. Nama file disarankan: **M08-D04_YYYY-MM-DD_ringkasan.png**. Gunakan tanggal yang benar-benar diketahui; jangan membuat tanggal dari perkiraan.
5. Untuk bimbingan, foto pertemuan atau screenshot konsultasi boleh ditambah catatan pokok bahasan/tindak lanjut. Paraf hanya diisi pembimbing.
6. Jika kegiatan belum dilakukan atau buktinya belum ada, biarkan sebagai rencana/catat statusnya; jangan memakai hasil simulasi atau tabel kosong sebagai bukti kegiatan sudah selesai.

## Sumber hasil run yang sudah tersedia

[Folder hasil v2](../deliverables/lda-v2/hasil-run/) · [Notebook dengan output run](../deliverables/lda-v2/Colab_Wisata_v2_Dijalankan.ipynb) · [Metodologi dan paper](../docs/METODOLOGI_DAN_PAPER.md)

**Kronologi:** hasil v2 dibuat pada **11 November 2026**, sesudah jadwal rencana minggu 1–12 (17 Agustus–6 November 2026). Lampirkan sebagai bukti tindak lanjut pada tanggal aktual. Hasil ini tidak membuktikan eksperimen berlangsung pada tanggal rencana sebelumnya. Jika menempatkannya di lampiran suatu minggu, tulis jelas “tindak lanjut 11 November 2026”; untuk logbook aktual tambahkan entri pada tanggal pelaksanaan.

**Batas bukti:** belum tersedia anotasi sentimen, verifikasi wilayah seluruh destinasi, uji stemming baru, tuning beberapa konfigurasi FastText, maupun output kata terdekat/OOV yang diekspor otomatis. Jangan menandai kegiatan tersebut selesai hanya karena ada saran dokumentasi. BGE tidak dijalankan pada run v2. Sertifikat HKI adalah bukti luaran, bukan foto kegiatan/bimbingan.

## Rekomendasi per hari

### Minggu 1

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M01-D01**<br>Senin, 17 Agustus 2026 | Tangkapan layar folder kerja dan daftar kebutuhan riset. | Folder kerja riset dan daftar kebutuhan milik penulis. Tampilkan susunan folder serta daftar kebutuhan; gunakan tangkapan layar pekerjaan sendiri. |
| **M01-D02**<br>Selasa, 18 Agustus 2026 | Cuplikan tabel kajian pustaka tentang rekomendasi wisata berbasis konteks. | docs/METODOLOGI_DAN_PAPER.md atau matriks kajian pustaka milik penulis. Tampilkan judul paper, penulis/tahun, metode, dan kaitannya dengan riset; halaman paper saja belum menunjukkan hasil telaah. |
| **M01-D03**<br>Rabu, 19 Agustus 2026 | Cuplikan catatan tentang informasi yang dapat diambil dari ulasan wisata. | Catatan kajian sumber ulasan milik penulis. Tampilkan contoh informasi yang bisa diambil dari ulasan dan catatan keterbatasannya. |
| **M01-D04**<br>Kamis, 20 Agustus 2026 | Cuplikan matriks perbandingan konteks musim dan periode libur. | Catatan perbandingan konteks musim/periode libur milik penulis. Tampilkan definisi, sumber bukti waktu, dan apa yang belum diketahui; tanggal relatif bukan tanggal kunjungan absolut. |
| **M01-D05**<br>Jumat, 21 Agustus 2026 | Tangkapan layar draf rumusan masalah, tujuan, dan ruang lingkup riset. | Draf proposal milik penulis. Tampilkan rumusan masalah, tujuan, dan ruang lingkup; wilayah dataset tetap perlu diverifikasi. |

### Minggu 2

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M02-D01**<br>Senin, 24 Agustus 2026 | Cuplikan ringkasan artikel LDA beserta sitasi dan metode yang digunakan. | docs/METODOLOGI_DAN_PAPER.md, bagian LDA (R01–R05). Tampilkan ringkasan metode dan sitasi paper, bukan hanya sampul artikel. |
| **M02-D02**<br>Selasa, 25 Agustus 2026 | Cuplikan catatan FastText berisi contoh kata dan potongan karakter. | docs/METODOLOGI_DAN_PAPER.md, R07; src/wisata_madura/neural.py. Tampilkan catatan subword dan contoh kata; bedakan konfigurasi dengan hasil pelatihan. |
| **M02-D03**<br>Rabu, 26 Agustus 2026 | Diagram rancangan BiLSTM dan keluaran tiap aspek klasifikasi. | src/wisata_madura/neural.py, ReviewBiLSTM. Lampirkan diagram yang dibuat dari arsitektur kode: embedding, BiLSTM, dua kepala atribut; jangan menamai keluaran sebagai sentimen. |
| **M02-D04**<br>Kamis, 27 Agustus 2026 | Diagram alur pencocokan preferensi pengguna dan deskripsi destinasi dengan BGE. | src/wisata_madura/recommendation.py atau diagram rancangan BGE milik penulis. BGE belum dijalankan pada hasil v2. Diagram adalah bukti rancangan, bukan bukti ranking atau fusion BGE-E5. |
| **M02-D05**<br>Jumat, 28 Agustus 2026 | Cuplikan diagram alur penelitian dan tabel kebutuhan data serta metrik. | Draf alur penelitian dan tabel kebutuhan data milik penulis. Tampilkan alur, label yang tersedia, metrik, serta catatan pertanyaan untuk pembimbing. |

### Minggu 3

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M03-D01**<br>Senin, 31 Agustus 2026 | Cuplikan draf proposal pada bagian kriteria seleksi destinasi dan ulasan. | Draf proposal dan kriteria seleksi milik penulis. Tampilkan kriteria destinasi/ulasan dan versi dokumen yang benar-benar digunakan. |
| **M03-D02**<br>Selasa, 1 September 2026 | Tangkapan layar daftar awal destinasi dan tautan Google Maps. | Daftar destinasi dan tautan sumber milik penulis. Sertakan nama/ID dan tautan lokasi yang diperiksa; jangan menganggap seluruh 207 destinasi berada di Madura. |
| **M03-D03**<br>Rabu, 2 September 2026 | Tangkapan layar pratinjau ekspor ulasan tanpa nama akun pengulas. | Ekspor asli pengambilan data, jika tersedia. Tampilkan header dan beberapa baris tanpa nama akun pengulas. Paket siap-model bukan bukti bahwa scraping dilakukan pada tanggal rencana. |
| **M03-D04**<br>Kamis, 3 September 2026 | Cuplikan header dan penjelasan kolom pada berkas kerja ulasan. | Workbook sumber jika tersedia; data/manifest.json hanya menjelaskan paket siap-model. Header rating, date, text_original harus berasal dari workbook asli; kolom tersebut tidak disertakan lengkap dalam paket CSV siap-model. |
| **M03-D05**<br>Jumat, 4 September 2026 | Cuplikan tabel cek kelengkapan sampel dan catatan kendala ekspor. | Catatan kelengkapan ekspor milik penulis. Tampilkan kolom yang dicek, jumlah baris, serta kendala yang benar-benar ditemukan. |

### Minggu 4

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M04-D01**<br>Senin, 7 September 2026 | Tangkapan layar rekap destinasi dan jumlah ulasan yang diambil. | Rekap pengumpulan data asli milik penulis. Tampilkan destinasi, jumlah ulasan, dan sumber; hasil loading paket tidak membuktikan tanggal pengambilan data. |
| **M04-D02**<br>Selasa, 8 September 2026 | Cuplikan tabel pemeriksaan kecocokan ID dan nama destinasi. | Output sel 01 notebook; pemeriksaan ID dan konsistensi label. Tampilkan contoh pasangan ID/nama dan hasil pemeriksaan, bukan hanya ukuran data. |
| **M04-D03**<br>Rabu, 9 September 2026 | Tangkapan layar berkas gabungan yang memperlihatkan struktur kolom. | Output sel 01 notebook atau file gabungan asli jika tersedia. Tampilkan struktur kolom dan jumlah baris. Bedakan gabungan siap-model dari workbook mentah. |
| **M04-D04**<br>Kamis, 10 September 2026 | Keluaran notebook yang merangkum teks kosong, rating kosong, dan duplikat. | deliverables/lda-v2/hasil-run/audit_dataset.json Tampilkan ringkasan audit teks kosong, rating kosong, dan duplikat. Metadata paket adalah penanda audit dari sumber, bukan pemeriksaan ulang semua nilai mentah. |
| **M04-D05**<br>Jumat, 11 September 2026 | Cuplikan rekap jumlah ulasan, sumber, dan periode pengambilan per destinasi. | deliverables/lda-v2/hasil-run/distribusi_label.csv serta catatan sumber/periode pengambilan milik penulis. Jumlah ulasan tersedia; tanggal/periode pengambilan tetap harus didukung catatan asli. |

### Minggu 5

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M05-D01**<br>Senin, 14 September 2026 | Cuplikan tabel kriteria seleksi dan contoh alasan ulasan dikeluarkan. | Catatan seleksi data dan kriteria eksperimen. Tampilkan alasan penyaringan; audit_dataset.json memuat jumlah teks kosong dan pengulangan yang disisihkan. |
| **M05-D02**<br>Selasa, 15 September 2026 | Cuplikan perbandingan teks asli dan teks bersih pada contoh karakter rusak. | Workbook sumber dan perbandingan teks asli/olahan milik penulis. Paket siap-model tidak memuat teks asli lengkap; penanda encoding bukan bukti perbaikan karakter sudah dilakukan. |
| **M05-D03**<br>Rabu, 16 September 2026 | Keluaran notebook yang menunjukkan teks sebelum dan sesudah normalisasi. | Output uji normalisasi yang benar-benar dijalankan; src/wisata_madura/data.py. Tampilkan pasangan teks sebelum/sesudah serta aturan normalisasinya; jangan membuat contoh sebagai data penelitian nyata. |
| **M05-D04**<br>Kamis, 17 September 2026 | Cuplikan hasil deteksi duplikat serta kolom teks asli dan teks olahan. | Workbook sumber atau keluaran pemeriksaan duplikat milik penulis. Tampilkan kriteria duplikat dan jumlahnya. Kolom asli/olahan hanya dapat difoto bila file sumber tersedia. |
| **M05-D05**<br>Jumat, 18 September 2026 | Tangkapan layar ringkasan temuan awal dan daftar masalah data. | deliverables/lda-v2/hasil-run/audit_dataset.json dan catatan masalah data. Tampilkan temuan dan tindak lanjut; pisahkan masalah yang sudah diperbaiki dari yang belum. |

### Minggu 6

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M06-D01**<br>Senin, 21 September 2026 | Keluaran tokenisasi yang memperlihatkan kata tidak dan kurang tetap tersimpan. | src/wisata_madura/topics.py dan output uji tokenisasi milik penulis. Tampilkan stopword dan bukti negasi tetap ada. Stoplist tambahan v2 hanya untuk LDA. |
| **M06-D02**<br>Selasa, 22 September 2026 | Tabel contoh token sebelum dan sesudah stemming. | Hasil uji stemming milik penulis, jika benar-benar dilakukan. V2 tidak menjalankan stemming baru. Jika belum ada pengujian sebelum/sesudah, biarkan sebagai rencana dan jangan mengklaim bukti tersedia. |
| **M06-D03**<br>Rabu, 23 September 2026 | Cuplikan tanggal relatif pada dataset dan catatan kebutuhan tanggal absolut. | Workbook sumber untuk contoh tanggal; audit_dataset.json untuk rekap. Tampilkan tanggal relatif dan catatan kebutuhan tanggal absolut; jangan menebak musim kunjungan. |
| **M06-D04**<br>Kamis, 24 September 2026 | Tabel pembeda label kecocokan cuaca, musim kunjungan, dan periode libur. | Tabel definisi label milik penulis. Bedakan rekomendasi_cuaca destinasi, musim kunjungan, dan periode libur; asal label cuaca belum terverifikasi. |
| **M06-D05**<br>Jumat, 25 September 2026 | Cuplikan pedoman label jenis wisata dan sentimen beserta contoh. | Pedoman anotasi milik penulis, jika sudah disusun. Label jenis wisata tersedia, sentimen belum tersedia; pedoman rancangan tidak sama dengan dataset sentimen tervalidasi. |

### Minggu 7

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M07-D01**<br>Senin, 28 September 2026 | Cuplikan daftar ID sampel dan jumlah ulasan yang dipilih per destinasi. | Daftar sampel yang benar-benar dipilih milik penulis. Tampilkan ID, jumlah sampel per destinasi, dan cara memilihnya; jangan mengklaim sampling anotasi bila hanya sampling model. |
| **M07-D02**<br>Selasa, 29 September 2026 | Tabel contoh label jenis wisata dan kasus yang sulit dikategorikan. | deliverables/lda-v2/hasil-run/distribusi_label.csv dan catatan kasus ambigu milik penulis. Tampilkan nama kategori, ID contoh, dan alasan keraguan; distribusi saja tidak membuktikan validasi label. |
| **M07-D03**<br>Rabu, 30 September 2026 | Cuplikan lembar anotasi sentimen dengan kutipan ulasan tanpa nama pengulas. | Lembar anotasi sentimen milik penulis, jika kegiatan benar-benar dilakukan. Belum ada anotasi sentimen pada paket v2. Jangan mengganti dengan prediksi rekaan; catat belum terlaksana bila memang belum. |
| **M07-D04**<br>Kamis, 1 Oktober 2026 | Tabel sampel berstatus musim belum diketahui beserta alasannya. | Tabel kasus waktu kunjungan belum diketahui milik penulis. Tampilkan ID sampel, bukti tanggal relatif, dan alasan status belum diketahui. |
| **M07-D05**<br>Jumat, 2 Oktober 2026 | Rekap distribusi label dan daftar kasus ambigu untuk bahan bimbingan. | deliverables/lda-v2/hasil-run/distribusi_label.csv serta catatan bimbingan jika ada. Lampirkan rekap dan kasus yang perlu ditinjau. Foto/notulen konsultasi hanya bila konsultasi benar-benar berlangsung. |

### Minggu 8

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M08-D01**<br>Senin, 5 Oktober 2026 | Cuplikan draf laporan kemajuan pada bagian capaian dan kendala. | reports/Laporan_Kemajuan_Malik_Hariyanto.docx atau versi kemajuan asli milik penulis. Tampilkan capaian, kendala, dan versi dokumen yang digunakan saat itu. |
| **M08-D02**<br>Selasa, 6 Oktober 2026 | Keluaran pembagian data yang menunjukkan ID destinasi latih dan uji terpisah. | deliverables/lda-v2/hasil-run/id_partisi_train.csv, id_partisi_validation.csv, id_partisi_test.csv; output sel 03. Tampilkan jumlah train/validation/test dan pemeriksaan ID/teks tidak tumpang tindih. V2 dibuat 11 November 2026: gunakan tanggal aktual itu bila merujuk hasil ini. |
| **M08-D03**<br>Rabu, 7 Oktober 2026 | Keluaran notebook yang menunjukkan ukuran kosakata dan matriks kata. | deliverables/lda-v2/hasil-run/audit_lda.json dan output sel 05A. Tampilkan vocabulary_size, jumlah sampel latih/validasi, dan sumber train. Ukuran matriks tidak boleh dikarang jika belum dicetak. |
| **M08-D04**<br>Kamis, 8 Oktober 2026 | Tabel perbandingan jumlah topik LDA dan kata utama per topik. | deliverables/lda-v2/hasil-run/pemilihan_topik.png dan pencarian_lda.csv Tampilkan kandidat K, seed, coherence, perplexity, dan kestabilan. Ini hasil run 11 November 2026, bukan bukti run pada tanggal rencana. |
| **M08-D05**<br>Jumat, 9 Oktober 2026 | Cuplikan laporan kemajuan yang memuat konfigurasi dan batasan LDA. | Draf laporan kemajuan dan catatan konfigurasi asli milik penulis. Jika memakai konfigurasi v2, beri label revisi 11 November 2026 dan cantumkan batas coherence/topik. |

### Minggu 9

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M09-D01**<br>Senin, 12 Oktober 2026 | Cuplikan lembar monitoring tentang status data, label, dan kendala. | Bahan monitoring milik penulis. Tampilkan status data, label yang tersedia/belum tersedia, kendala, serta tindak lanjut. |
| **M09-D02**<br>Selasa, 13 Oktober 2026 | Cuplikan tabel kata kunci topik LDA beserta contoh ulasan yang relevan. | deliverables/lda-v2/hasil-run/kata_utama_topik.png, contoh_ulasan_topik.csv, kualitas_topik.csv Tampilkan kata topik bersama contoh ulasan dan skor kualitas; topik belum otomatis menjadi aspek tervalidasi. |
| **M09-D03**<br>Rabu, 14 Oktober 2026 | Tangkapan layar proses pembentukan token dari data latih. | Output tokenisasi korpus latih milik penulis; sel 06 dan neural.py. Tampilkan beberapa contoh token dan asal train; ukuran urutan saja belum memperlihatkan pembentukan token. |
| **M09-D04**<br>Kamis, 15 Oktober 2026 | Cuplikan konfigurasi FastText berisi dimensi vektor dan rentang n-gram. | deliverables/lda-v2/hasil-run/audit_dataset.json, deep_config; src/wisata_madura/neural.py. Tampilkan dimensi, ngram, window, epoch dan seed; nilai lokal dibedakan dari prinsip metode paper. |
| **M09-D05**<br>Jumat, 16 Oktober 2026 | Cuplikan catatan peninjauan metode dan daftar tindak lanjut untuk pembimbing. | Catatan peninjauan metode milik penulis; docs/METODOLOGI_DAN_PAPER.md. Tampilkan keputusan, alasan, rujukan paper, keterbatasan, dan pertanyaan untuk pembimbing. |

### Minggu 10

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M10-D01**<br>Senin, 19 Oktober 2026 | Tabel skor koherensi dan catatan keterbacaan untuk tiap jumlah topik. | deliverables/lda-v2/hasil-run/pemilihan_topik.png, pemilihan_topik.csv, kualitas_topik.csv Tampilkan skor serta catatan keterbacaan. Pada v2 K=2 terpilih dalam grid; coherence masih perlu ditelaah, bukan otomatis baik. |
| **M10-D02**<br>Selasa, 20 Oktober 2026 | Cuplikan tabel nama sementara topik, kata utama, dan contoh ulasan. | deliverables/lda-v2/hasil-run/template_review_topik.csv dan contoh_ulasan_topik.csv Isi nama sementara hanya setelah membaca contoh. Templat yang belum diisi merupakan bahan review, bukan bukti review selesai. |
| **M10-D03**<br>Rabu, 21 Oktober 2026 | Tangkapan layar konfigurasi LDA dan pratinjau vektor topik tersimpan. | deliverables/lda-v2/hasil-run/audit_lda.json dan distribusi_topik_dokumen_latih.csv Tampilkan konfigurasi terpilih, ID, dan vektor topik; sertakan tanggal run aktual. |
| **M10-D04**<br>Kamis, 22 Oktober 2026 | Cuplikan sel pelatihan FastText yang menunjukkan parameter dan sumber korpus. | Output sel 06 notebook v2; src/wisata_madura/neural.py. Tampilkan parameter dan train-only corpus. Model FastText dibuat pada folder models saat run. |
| **M10-D05**<br>Jumat, 23 Oktober 2026 | Keluaran daftar kata terdekat dari FastText beserta catatan peninjauan. | Keluaran most_similar dari model FastText milik penulis. Belum diekspor otomatis pada v2. Jalankan pemeriksaan kata terdekat terlebih dahulu sebelum melampirkan hasil. |

### Minggu 11

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M11-D01**<br>Senin, 26 Oktober 2026 | Tabel perbandingan percobaan FastText dan parameter yang diubah. | Tabel eksperimen FastText milik penulis, jika ada. V2 menggunakan satu konfigurasi FastText; belum membandingkan beberapa konfigurasi. Jangan memakai tabel pencarian LDA sebagai bukti tuning FastText. |
| **M11-D02**<br>Selasa, 27 Oktober 2026 | Keluaran FastText untuk kata berimbuhan, variasi ejaan, dan kata baru. | Output pemeriksaan subword/OOV milik penulis. Kodenya mendukung vektor kata baru, tetapi contoh pembuktian harus benar-benar dijalankan dan didokumentasikan. |
| **M11-D03**<br>Rabu, 28 Oktober 2026 | Keluaran notebook yang menunjukkan ukuran urutan token dan matriks embedding. | Output sel 06 notebook v2; folder models pada runtime. Tampilkan bentuk urutan train/validation dan embedding; beri tanggal run aktual, bukan tanggal rencana. |
| **M11-D04**<br>Kamis, 29 Oktober 2026 | Tangkapan layar hasil pemeriksaan urutan ID antara fitur LDA dan FastText. | Keluaran pemeriksaan kesesuaian urutan baris fitur milik penulis. Tampilkan ID contoh dan urutan fitur LDA/FastText yang sama; bila belum ada output cek eksplisit, siapkan pemeriksaannya dahulu. |
| **M11-D05**<br>Jumat, 30 Oktober 2026 | Tabel konfigurasi terpilih dan tiga skenario fitur untuk pengujian. | deliverables/lda-v2/hasil-run/audit_dataset.json, audit_lda.json, serta tabel skenario pada README.md. Tampilkan konfigurasi dan definisi FastText, LDA, serta gabungan; bedakan rencana skenario dari hasil test. |

### Minggu 12

| Kode dan tanggal rencana | Gambar yang disarankan | Lokasi bahan / hal yang perlu ditampilkan |
|---|---|---|
| **M12-D01**<br>Senin, 2 November 2026 | Cuplikan notebook model pembanding dan rekap jumlah destinasi latih serta uji. | deliverables/lda-v2/hasil-run/metrik_klasifikasi.csv dan id_partisi_*.csv; output sel 03/04/08. Tampilkan pembanding serta split train/validation/test. Angka hasil v2 berasal dari run 11 November 2026. |
| **M12-D02**<br>Selasa, 3 November 2026 | Diagram BiLSTM dengan masukan dan keluaran untuk label yang tersedia. | src/wisata_madura/neural.py, ReviewBiLSTM; diagram rancangan milik penulis. Gambarkan embedding → BiLSTM → opsional fitur LDA → dua kepala atribut; sesuaikan dengan kode yang benar-benar digunakan. |
| **M12-D03**<br>Rabu, 4 November 2026 | Keluaran uji sampel yang menunjukkan ukuran masukan dan pemetaan label. | Output sel 06 dan hasil uji sampel milik penulis. Tampilkan shape, pemetaan label, dan kesesuaian fitur. Jika mengklaim uji sampel kecil, lampirkan run sampel kecilnya, bukan hanya run penuh. |
| **M12-D04**<br>Kamis, 5 November 2026 | Templat tabel micro-F1, macro-F1, dan Hamming loss per target. | deliverables/lda-v2/hasil-run/perbandingan_model.png, metrik_klasifikasi.csv, metrik_per_kelas.csv Tampilkan skor per target dan kelas; dapat ditambah kurva_bilstm.png dan checkpoint_bilstm.csv. Semua diberi tanggal run aktual. |
| **M12-D05**<br>Jumat, 6 November 2026 | Cuplikan draf metode dan catatan status eksperimen untuk laporan atau artikel. | Draf laporan/artikel dan catatan metode milik penulis; deliverables/lda-v2/HASIL_EKSEKUSI.md. Tampilkan versi, status eksperimen, dan keterbatasan. Sertifikat HKI adalah bukti luaran terpisah; tidak menggantikan dokumentasi kerja harian. |
