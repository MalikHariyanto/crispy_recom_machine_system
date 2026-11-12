# Dokumentasi minggu 7 — langsung dari DB Browser dan Colab

Tidak ada Excel tambahan. Gunakan database ulasan yang sudah dibuka dan notebook run v3.

## Persiapan sekali di DB Browser

1. Buka `dataset_wisata.sqlite` yang diberikan pada minggu 3. Salinan sumber tersedia di [folder minggu 3](../minggu_03/).
2. Buka [Siapkan_Review_Minggu_07.sql](Siapkan_Review_Minggu_07.sql), salin seluruh isi SQL. Pada DB Browser pilih **Execute SQL**, tempel kode, lalu jalankan **seluruh skrip** (tombol Run all / F5). Bila memakai tombol yang mengeksekusi pilihan, pilih seluruh kode dahulu. Skrip memakai transaksi dan tidak mengubah tabel `ulasan`.
3. Pastikan tidak ada error. Klik **Write Changes** bila tombolnya aktif, lalu **Refresh**. Di tab **Browse Data**, dropdown akan berisi tabel dan view berawalan `m07_`.

Pada database yang diberikan: 109 sampel / 27 destinasi, maksimal lima baris pertama per destinasi menurut id_ulasan. Sampel ini untuk inspeksi awal; bukan sampel acak, representatif, atau bukti anotasi sudah dilakukan. Skrip tidak mengganti isian review saat dijalankan ulang; jalankan pada database sumber yang sama. Sampel tersimpan tidak otomatis disinkronkan jika data sumber berubah.

## Senin — sampel lintas destinasi

**Browse Data → m07_01_rekap_sampel.** Screenshot ID, nama, jumlah sampel, serta cara memilihnya. Selanjutnya **m07_03_periksa_sentimen** memperlihatkan teks ulasan dari sampel yang dipilih. Belum ada label sentimen otomatis.

Caption: “Pemilihan sampel inspeksi lintas destinasi, maksimal lima ulasan pertama per ID menurut urutan database. Pemilihan dilakukan pada [tanggal aktual].”

## Selasa — kategori wisata dan kasus ambigu

**Browse Data → m07_02_periksa_jenis.** Screenshot nama destinasi dan kategori sumber. Status awal semua destinasi adalah **Belum ditinjau**. Baca data/keterangan lokasi, lalu buka tabel **m07_review_destinasi** untuk mengisi status `Sesuai` atau `Perlu ditinjau`, alasan keraguan, kategori usulan bila ada, penilai dan tanggal.

Screenshot view setelah mengisi review aktual. Filter kolom `status_review` ke `Perlu ditinjau` untuk melihat kasus yang benar-benar ditandai. Tidak ada kasus ambigu yang disimpulkan otomatis. Kolom `kategori_usulan` tidak mengganti label sumber.

## Rabu — anotasi sentimen

Buka **m07_03_periksa_sentimen** untuk membaca teks asli dan mencatat id_ulasan. Isian dibuat di tabel **m07_review_sentimen** pada ID yang sama. Pilih `Positif`, `Netral`, `Negatif`, atau `Campuran/ambigu`, lalu isi alasan berdasarkan teks, penilai dan tanggal. Pedoman sentimen masih perlu disepakati; label ini bukan anotasi tervalidasi secara otomatis. Jangan menentukan sentimen hanya dari rating.

Screenshot view **m07_03_periksa_sentimen** setelah isian disimpan. Jika belum dianotasi, tampilkan sebagai persiapan/lembar kosong, bukan hasil uji selesai. Jika ada bimbingan, tambahkan screenshot/foto pertemuan asli beserta lembar catatannya.

## Kamis — keterbatasan waktu kunjungan

Buka **m07_04_periksa_waktu**. Screenshot `id_ulasan`, `tanggal_sumber`, dan `status_waktu`. Baca juga teks asli: tanggal unggah relatif dan waktu kunjungan adalah hal berbeda. Pada tabel **m07_review_waktu**, tandai `Belum diketahui` beserta alasan bila memang tidak ada bukti yang memadai, atau `Ada bukti waktu` dengan kutipan/sumber bukti. Awalnya status `Belum diverifikasi`.

Jangan mengisi musim dari label `rekomendasi_cuaca` atau menebak tanggal kunjungan dari “bulan lalu”. `musim_terverifikasi` tetap kosong kecuali waktu kunjungan, lokasi dan aturan musim didukung bukti. Skrip tidak mengubah atau menghitung musim otomatis.

## Jumat — distribusi label dan bahan bimbingan

Buka Colab **02 Audit/EDA** pada [notebook beroutput](../../../deliverables/lda-v3/Colab_Wisata_v3_Dijalankan.ipynb). Screenshot grafik distribusi dan tabel jenis wisata/cuaca. Grafik asli: [eda_rating_cuaca_jenis.png](../../../deliverables/lda-v3/grafik/eda_rating_cuaca_jenis.png).

Alternatif langsung di database: **m07_05_distribusi_jenis** untuk rekap jumlah ulasan dan destinasi. Lengkapi dengan **m07_05_status_review** serta **m07_02_periksa_jenis** yang difilter ke kasus `Perlu ditinjau`, bila ada hasil review. Catatan pertemuan hanya diisi dari bimbingan yang berlangsung.

Perhatikan satuan pada chart: batang rating/cuaca menghitung ulasan; pie cuaca/jenis menghitung destinasi unik. Grafik bukan hasil validasi label sentimen. Notebook v3 memuat 2.058 ulasan / 27 destinasi; jangan memakai angka historis 79.514/207.

## Cara membuat screenshot terbaca

Tutup panel kanan yang tidak diperlukan, tampilkan 3–5 baris, atur lebar kolom, dan screenshot header bersama isi. Untuk teks panjang, pilih satu baris dan buka tampilan teks sel. Ambil dua screenshot bila daftar kolom terlalu lebar. Pakai **Win + Shift + S**. Jangan menyembunyikan status belum ditinjau untuk mengesankan anotasi selesai.

Isi caption dan tanggal berdasarkan pelaksanaan aktual. Output v3 berasal dari run 12 November 2026, sehingga dicatat sebagai tindak lanjut jika dipakai untuk baris logbook September/Oktober. `NULL` pada label/alasan/penilai adalah isian belum tersedia, bukan kelas sentimen netral.
