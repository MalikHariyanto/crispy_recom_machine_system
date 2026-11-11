# Hasil eksekusi pipeline v2

Sumber run: `20261111-143703-377135`. Semua sel kode notebook tereksekusi; tidak ada error tersimpan. `RUN_DEEP=True`, `RUN_BGE=False`. Mesin CPU, bukan Colab GPU; hasil GPU mungkin berbeda.

Kode dieksekusi sebelum commit perbaikan dibuat. `source_commit` dalam audit menunjuk HEAD induk saat run; **hash setiap modul dalam audit sudah dicocokkan dengan kode yang dikirim**. Seed/versi paket dan seluruh parameter ada pada JSON dan dokumen metodologi.

Lima tes regresi selesai dan lulus (unittest, 4,328 detik). Perbandingan lengkap berikut berasal dari test yang sama:

| Model | Macro-F1 cuaca | Macro-F1 jenis wisata |
|---|---:|---:|
| mayoritas | 0.3582 | 0.0247 |
| tfidf_linear_svc | 0.5572 | 0.5767 |
| lda_logreg | 0.5285 | 0.0620 |
| fasttext_bilstm | 0.5812 | 0.5566 |
| fasttext_lda_bilstm | 0.5285 | 0.5820 |

Tambahan LDA memperbaiki Macro-F1 jenis wisata dibanding varian FastText pada run ini, tetapi menurunkan Macro-F1 cuaca. Ini bukan bukti perbaikan universal. BiLSTM hanya satu seed; test hanya satu partisi 43 destinasi. Pilihan K berbasis coherence tidak dioptimalkan untuk F1 jenis wisata.

Pemilihan K=2 berada pada batas bawah grid dan topik masih luas. Rerata validation NPMI negatif. Contoh ulasan dan template review disertakan agar penamaan topik dilakukan dari bukti, bukan otomatis menganggapnya sentimen/aspek. Perlu validasi manusia sebelum klaim ilmiah tentang makna topik.

Seluruh parameter dan rujukan: [metodologi dan paper](../../docs/METODOLOGI_DAN_PAPER.md). Laporan HKI sebelumnya tidak diubah oleh eksperimen baru; sertifikat HKI tidak menjadi bukti keberhasilan eksperimen ini.
