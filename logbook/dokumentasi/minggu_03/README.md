# Bahan dokumentasi minggu 3

Bahan ini dihasilkan dari workbook aktif, bukan bukti pengumpulan pada tanggal rencana minggu 3. Waktu pemeriksaan dan SHA256 workbook tercatat pada sheet `Panduan`.

## File

- `Dokumentasi_Data_Minggu_03.xlsx`: daftar destinasi, sampel ulasan, kamus data, audit sampel, audit dataset penuh, dan detail temuan.
- `dataset_wisata.sqlite`: salinan seluruh 2.058 ulasan dari 27 ID destinasi dalam tabel `ulasan`. Kolom `id_ulasan` ditambahkan sebagai primary key; delapan kolom sumber dipertahankan.
- `struktur_database.sql`: definisi tabel SQLite. Tidak perlu dijalankan jika membuka database yang sudah tersedia.

## Cara screenshot

Gunakan zoom yang membuat tulisan terbaca (sekitar 100–125%), fokus pada area yang diperlukan, dan sertakan judul kolom. Hindari mengecilkan seluruh tabel sampai teks tidak terbaca; ambil dua cuplikan bila terlalu lebar. Jangan mengubah nilai supaya tampak lebih rapi. Caption menyebut sumber, cakupan, dan tanggal pemeriksaan aktual.

### Google Maps untuk daftar destinasi

1. Buka sheet `Daftar_Destinasi`. Klik tautan pencarian suatu destinasi, misalnya Air Terjun Toroan.
2. Pilih tempat yang sesuai. Pada panel Ringkasan/Overview, periksa nama, alamat, kabupaten, dan penanda peta. Tautan pencarian belum membuktikan lokasi yang benar.
3. Ambil screenshot panel nama/alamat dan peta. Salin URL tempat yang sudah dibuka ke `URL_tempat_setelah_diperiksa`; isi kabupaten dan status verifikasi berdasarkan pemeriksaan.
4. Untuk ulasan, buka tab Ulasan/Reviews. Jika memotret contoh, tampilkan isi ulasan, bintang dan tanggal; tutup/crop nama serta foto akun. Ulasan yang terlihat sekarang belum tentu sama dengan ekspor penelitian terdahulu. Catat waktu akses sebenarnya.

### Selasa — daftar destinasi

Screenshot kolom ID, destinasi, jumlah ulasan, kabupaten terverifikasi dan URL tempat pada sheet `Daftar_Destinasi`. Kolom verifikasi masih kosong sampai diperiksa sendiri. Untuk tempat di luar Madura, catat wilayah sebenarnya.

### Rabu — sampel ulasan dan bimbingan

Sheet `Sampel_Ulasan` berisi 109 ulasan dari 27 destinasi, dipilih maksimal lima baris pertama per ID menurut urutan sumber. Ini sampel inspeksi deterministik, bukan sampel acak atau representatif. Filter satu destinasi; screenshot 3–5 baris beserta ID, nama, rating, tanggal dan teks. Nomor `baris_excel` mengacu ke workbook sumber. Untuk pertemuan, gunakan foto/screenshot pertemuan asli dan isi lembar catatan pertemuan sesuai realisasi.

### Kamis — struktur database

1. Pasang DB Browser for SQLite dari https://sqlitebrowser.org/ .
2. Download `dataset_wisata.sqlite`, pilih **Open Database**, lalu buka file tersebut.
3. Pilih **Database Structure** untuk melihat tabel `ulasan`, kolom, dan primary key.
4. Pilih **Browse Data**, pilih tabel `ulasan`, dan tampilkan beberapa baris untuk membuktikan isi data.
5. Untuk penjelasan kolom yang lebih mudah dibaca, screenshot sheet `Kamus_Data` di Excel. Kamus data menjelaskan skema; Browse Data menunjukkan isinya.

Contoh query di tab Execute SQL:

```sql
SELECT id_ulasan, id_destinasi, destinasi, rating, date,
       text_preprocessed, rekomendasi_cuaca, wisata
FROM ulasan
ORDER BY id_ulasan
LIMIT 5;
```

Jika hanya perlu dokumentasi struktur data, Excel sudah cukup. File `.sqlite` disediakan untuk menampilkan database yang benar-benar dibuat dan terisi.

### Jumat — kelengkapan sampel

Buka sheet `Audit_Sampel`. Screenshot kolom Pemeriksaan, Jumlah dan Definisi; lanjutkan ke screenshot kedua jika perlu. Jangan mengganti hasil sampel dengan `Audit_Dataset`, karena cakupannya berbeda.

Hasil pada versi sumber ini: 109 ulasan / 27 destinasi; seluruh delapan kolom tidak kosong; rating di luar rentang 1–5 = 0; duplikat persis tambahan = 0; tanggal relatif = 109; indikasi encoding = 32. Pola encoding merupakan indikasi untuk peninjauan manual, bukan bukti semua 32 teks rusak. Hasil tidak menyatakan data bebas masalah atau mewakili seluruh populasi.

`Detail_Temuan` memuat baris sumber dan penanda untuk seluruh dataset. Gunakan filter pada kolom `temuan` untuk menelusuri kasus. Tanggal relatif juga dicatat sebagai temuan keterbatasan, bukan kesalahan yang harus dihapus. Untuk menelusuri kasus sampel tertentu, cocokkan `baris_excel` dengan sheet `Sampel_Ulasan`.

Aturan audit: kosong = null/teks kosong setelah trim; duplikat persis = baris tambahan dengan delapan kolom sama; teks berulang = ID dan teks normalisasi NFKC/casefold/pemisah sama (teks tidak kosong); tanggal relatif = memuat kata `lalu`; encoding = pola indikatif `ðŸ|â€¦|Ã©|�`; ketidakkonsistenan = satu ID memiliki beberapa nama atau label. Aturan dan angka lengkap tersedia pada kedua sheet audit.

Buat ulang setelah workbook berubah:

```bash
python scripts/prepare_logbook_week3.py
```

Dependensi: pandas dan openpyxl dari requirements proyek. Skrip mengganti bahan dokumentasi pada folder ini menggunakan workbook aktif; data sumber tidak diubah dan skrip tidak melakukan scraping.
