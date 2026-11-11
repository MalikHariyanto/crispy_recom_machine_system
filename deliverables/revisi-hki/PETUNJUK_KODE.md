# Kode audit dan eksperimen wisata — Malik Hariyanto

Sumber: branch research/audit-wisata-madura, commit d76ed77c7b387ddf1b5000b3ae25ffa7bfa8f6d3.
Notebook dan modul asli sudah memuat dataset lewat kode; tidak perlu upload Excel atau memasukkan data manual.

## Colab (paling mudah)
1. Buka Google Colab, pilih File > Upload notebook, lalu buka Colab_Audit_Wisata_Madura_Otomatis.ipynb.
2. Biarkan DATA_PATH = None dan REGION_PATH = None untuk menjalankan dataset bawaan lengkap.
3. Default RUN_DEEP = True menjalankan FastText dan dua varian BiLSTM; pilih runtime GPU.
   Untuk uji awal yang lebih ringan, set RUN_DEEP = False sebelum menjalankan sel instalasi.
4. RUN_BGE = False secara default. Aktifkan True sebelum sel instalasi jika ingin mengunduh dan mencoba BGE-M3.
5. Jalankan semua sel dari atas. Notebook mengambil kode dan dataset otomatis dari branch sumber jika tidak ada salinan lokal.
6. Ambil keluaran di hasil_wisata_madura/<waktu-run>/.

## Dari ZIP secara lokal
Ekstrak seluruh ZIP; jangan pisahkan notebook dari folder data dan src.
Buat virtualenv Python >=3.10, pasang Jupyter, lalu buka notebook dari direktori paket atau notebooks.
Sel instalasi notebook memasang requirements dan dependensi opsional mengikuti RUN_DEEP/RUN_BGE.

## Bukti pemeriksaan
- Lima checksum bagian data cocok dengan manifest.
- Pemuatan otomatis: 79.514 ulasan, 207 destinasi.
- Split: 61.165 ulasan latih / 12.849 uji; 164 / 43 destinasi; tidak berbagi ID atau teks identik.
- Mayoritas, TF-IDF + Linear SVC, dan LDA + regresi logistik selesai pada seluruh data.
- Angka baseline mereproduksi nilai laporan sampai tiga desimal.
- Pelatihan FastText/BiLSTM dan unduhan/inferensi BGE belum dijalankan pada pemeriksaan ini.

## Batas data dan metode
Paket adalah data siap-model, bukan workbook mentah lengkap. Data tidak dibatasi ke Madura karena belum ada kabupaten tervalidasi.
REGION_PATH hanya pilihan filter wilayah terverifikasi; pengisian manual tidak diperlukan untuk memuat dataset bawaan.
Jangan mengisi wilayah atau sentimen dengan tebakan. Tidak tersedia label sentimen atau musim kunjungan terverifikasi.
Kode rekomendasi yang tersedia memakai BGE-M3, bukan implementasi fusion BGE-E5 pada judul sertifikat HKI.
Precision/Recall rekomendasi memerlukan penilaian relevansi independen; jangan menganggap contoh ranking sebagai ground truth.
