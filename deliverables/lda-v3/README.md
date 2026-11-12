# Hasil run pengguna v3 — rujukan dokumentasi terbaru

Sumber: unggahan `Colab_Audit_Wisata_Madura_Otomatis_(4).ipynb`. Run yang tercetak: `20261112-131554-444000` (12 November 2026), mode full. Notebook disimpan tanpa mengubah kode, metadata atau output. Semua sel kode memiliki execution count dan tidak ada output error tersimpan; hal ini bukan verifikasi ulang komputasi atau validitas metodologi. Tidak dilakukan run ulang dalam pengarsipan ini.

[Notebook dengan output](Colab_Wisata_v3_Dijalankan.ipynb) · [Semua grafik asli](grafik/)

## Pemetaan ke dokumentasi logbook

| Bagian logbook | Bahan dokumentasi dari run ini | Bagian notebook |
|---|---|---|
| Minggu 4, Kamis | Tabel audit teks kosong/duplikasi/encoding; bukan grafik EDA saja | 02 Audit/EDA |
| Minggu 4–5, rekap data | Grafik rating, cuaca, jenis wisata serta histogram panjang teks sebagai tambahan rekap; bukan bukti scraping | 02 Audit/EDA |
| Minggu 7, rekap label | `eda_rating_cuaca_jenis.png` dan tabel cuaca/jenis | 02 Audit/EDA |
| Minggu 8, Selasa | `partisi_dataset.png` + tabel cakupan kelas + pemeriksaan ID/teks | 03 Split |
| Minggu 8, Kamis | `pemilihan_topik.png` + tabel kandidat dan keluaran K terpilih | 04 LDA |
| Minggu 9, Selasa | `kata_utama_topik.png`, `heatmap_topik_cuaca.png` + tabel kualitas dan contoh ulasan | 05 Interpretasi topik |
| Minggu 10, Senin | `pemilihan_topik.png` + diagnosis koherensi/keterbacaan | 04–05 |
| Minggu 10, Selasa | Kata utama dan contoh ulasan; nama topik sementara perlu peninjauan manusia | 05 Interpretasi topik |
| Minggu 11, Rabu | Shape token dan embedding aktual; bukan chart hasil evaluasi | 06 Embedding |
| Minggu 12, Senin | Grafik partisi + tabel model pembanding | 03, 07, 08 |
| Minggu 12, Kamis | `perbandingan_model.png`, tabel metrik dan dukungan per kelas; `kurva_bilstm_seed_42/43/44.png` untuk loss train/validation | 07 Modeling, 08 Evaluasi |
| Minggu 2, Jumat / pembaruan alur metode | `alur_pipeline.png`, dengan tanggal run aktual, bukan bukti pelaksanaan pada tanggal rencana | 09 Provenance |

Tanggal kegiatan di logbook harus mengikuti realisasi. Run 12 November dapat dicatat sebagai hasil tindak lanjut, bukan menggantikan tanggal kegiatan Agustus–November secara otomatis. Grafik tidak menggantikan foto bimbingan atau bukti pengumpulan data.

## Fakta yang ditampilkan dalam output

- Dataset: 2.058 ulasan / 27 destinasi. Cakupan Madura dinyatakan dalam notebook berdasarkan konfirmasi pemilik data, bukan hasil verifikasi lokasi independen dalam pengarsipan ini.
- Audit: 42 duplikat persis tambahan, 0 teks normalisasi kosong, 2.058 tanggal relatif, dan 233 indikasi encoding (bukan otomatis 233 teks rusak).
- Setelah penyaringan: train 1.168 ulasan / 16 destinasi, validation 268 / 5, test 426 / 6. Total akhir 1.862 ulasan.
- Pembersihan: 159 pengulangan dalam destinasi disisihkan; 15 teks validation dan 22 teks test identik lintas partisi dikeluarkan. Ini berbeda dari hitungan duplikat persis.
- K=2 terpilih pada run ini; jumlah topik dan rasio split tetap dirujuk dari output, bukan ditetapkan dari diagram lama.
- Dua varian BiLSTM dijalankan untuk seed 42, 43, dan 44 pada CUDA. Baseline hanya satu run; jangan menyebut semua model diuji tiga kali.
- Macro-F1 utama menggunakan seluruh kelas dataset, termasuk kelas tanpa support test. Test hanya 6 destinasi; kelas yang tidak muncul tidak memiliki bukti generalisasi test. Periksa `macro_f1_present` dan support untuk interpretasi.
- Notebook ini mengevaluasi klasifikasi atribut, bukan ranking BGE. Tidak ada hasil kualitas rekomendasi BGE yang diklaim.

## Batas arsip

Sebelas PNG pada folder `grafik/` diekstrak persis dari output notebook. Manifest `asal_grafik.json` mencatat lokasi sel/output serta checksum. File CSV, model dan ZIP yang disebut oleh output merupakan lokasi ekspor di runtime Colab; file tersebut tidak seluruhnya tertanam dalam unggahan notebook, sehingga tidak dianggap telah tersedia sebagai berkas terpisah di sini. Notebook dan grafik ini menjadi rujukan hasil terbaru; arsip v2 tetap terpisah karena laporan sebelumnya mengutipnya.
