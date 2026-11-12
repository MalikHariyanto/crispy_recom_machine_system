# Dokumentasi minggu 6 — prapemrosesan dan definisi label

[Download Excel](https://github.com/MalikHariyanto/crispy_recom_machine_system/raw/refs/heads/main/logbook/dokumentasi/minggu_06/Dokumentasi_Minggu_06.xlsx)

| Hari | Sheet Excel | Yang di-screenshot | Status |
|---|---|---|---|
| Senin | Senin_Tokenisasi; Senin_Negasi | Teks model, token sesudah stopword, dan kata negasi | Uji tambahan dijalankan 12 November 2026 dengan aturan kode rujukan run v3 |
| Selasa | Selasa_Stemming | Status dan kebutuhan uji; belum ada hasil sebelum/sesudah | Stemming belum dijalankan; jangan dianggap dokumentasi uji selesai |
| Rabu | Rabu_Tanggal | Nilai date dari sampel sumber dan catatan kebutuhan waktu absolut | Audit notebook v3 mencatat 2.058 tanggal relatif; sampel berasal dari workbook aktif |
| Kamis | Kamis_Konteks | Perbedaan atribut cuaca, musim kunjungan, periode libur | Label cuaca tersedia; asal anotasi belum terverifikasi |
| Jumat | Jumat_Jenis_Wisata; Jumat_Sentimen | Delapan kategori wisata dan pedoman awal sentimen | Jenis wisata tersedia; sentimen masih rancangan, belum label tervalidasi |

Gunakan tanggal aktual pemeriksaan. Rujukan run v3 adalah 12 November 2026; jangan menganggap hasil tersebut membuktikan pelaksanaan pada tanggal baris logbook September. Tidak diperlukan chart evaluasi untuk minggu 6; grafik pemilihan topik, loss, dan evaluasi cocok untuk minggu berikutnya.

## Asal uji Senin

Skrip `scripts/prepare_logbook_week6.py` mengambil aturan stopword dan token_pattern dari `src/wisata_madura/topics.py` pada commit sumber notebook `722d07a23376e2f0407425cac22ceb469e9eb429`. Contoh memakai kolom text_preprocessed dari workbook aktif, dinormalisasi sesuai aturan teks model, lalu diuji dengan analyzer CountVectorizer. Ini pemeriksaan tambahan, bukan output token kata yang tertanam di notebook dan bukan run ulang model. Empat contoh aktual tersedia untuk kata tidak/kurang/bukan/belum; aturan jangan juga diperiksa pada stoplist, tanpa mengarang contoh jika tidak ditemukan.

Kata yang lolos tokenisasi/stopword masih dapat tersaring saat vocabulary di-fit dengan min_df, max_df, atau max_features. Pemeriksaan tidak menyatakan seluruh negasi dari teks asli tetap ada setelah seluruh praproses sumber. Stoplist tambahan hanya berlaku pada LDA.

Jejak uji tersedia di `uji_tokenisasi.json` dan sheet Panduan. Stemming tidak dijalankan. Nilai sumber, label, serta tanggal tidak dikoreksi atau ditebak. Delapan kategori wisata dihitung dari workbook aktif, bukan memakai 14 kategori dataset historis.

Buat ulang dengan `python scripts/prepare_logbook_week6.py`. Diperlukan pandas, scikit-learn, openpyxl serta objek Git commit sumber. Skrip memperbarui workbook dokumentasi dan jejak uji; tidak melatih model atau mengubah logbook secara otomatis.
