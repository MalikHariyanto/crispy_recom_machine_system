# Kode dan hasil eksperimen wisata v2

## Jalankan sendiri
Buka `notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb` di Colab. Biarkan `DATA_PATH=None`. Dataset bawaan tetap dimuat otomatis; tidak perlu upload Excel atau mengetik dataset. Pilih runtime GPU untuk `RUN_DEEP=True` (default), lalu Run all. `RUN_DEEP=False` melewati deep learning, tetapi tetap menjalankan seluruh analisis LDA dan baseline. `RUN_BGE=False` secara default.

ZIP ini berisi folder `data/`, `src/`, `notebooks/`, `docs/`, `tests/`, requirements, serta hasil run. Ekstrak utuh untuk penggunaan lokal; gunakan Python >=3.10 dan kernel virtualenv. Notebook otomatis memasang dependensi. Di Colab, notebook dapat mengambil kode dan data dari branch GitHub jika belum ada folder lokal v2. Restart kernel setelah pernah memuat modul versi lama.

## Perbaikan dan paper
Baca `docs/METODOLOGI_DAN_PAPER.md`: setiap keputusan dan parameter memiliki rujukan fondasi serta penjelasan adaptasi/pilihan lokal. Tidak semua full text bisa diakses dalam lingkungan ini; cakupan pemeriksaan sumber dinyatakan. Angka parameter tidak diklaim diwajibkan atau terbukti optimal oleh paper.

## Hasil run yang disertakan
Notebook `Colab_Wisata_v2_Dijalankan.ipynb` memuat output run aktual. Pada mesin CPU:
- Dataset 79.514 ulasan / 207 destinasi, checksum terverifikasi.
- Train 47.459 ulasan / 130 destinasi; validation 12.473 / 34; test 12.849 / 43. Tidak ada ID/teks identik antarpartisi. Validation tidak memiliki kelas sungai.
- Seluruh 18 LDA selesai. K=2 terpilih; rerata NPMI validation antar-seed sekitar -0,0587, stability Jaccard 0,6600. Hasil berada di batas grid; satu topik memiliki coherence negatif. Ini bukan aspek tervalidasi.
- Dua BiLSTM selesai masing-masing 7 epoch; early stopping dan checkpoint epoch 4 dipulihkan sebelum prediksi test.
- Lima tes regresi lulus, termasuk pemeriksaan bahwa perubahan test tidak mengubah pemilihan K/kosakata dan prediksi sesuai checkpoint terbaik yang tersimpan.
- Tidak menjalankan BGE karena default False; tidak ada evaluasi rekomendasi yang diklaim.

Lihat hasil asli di `hasil-run/`. Model/vectorizer LDA disertakan. Bobot FastText/BiLSTM dan embedding besar tetap tersimpan pada mesin run, dan otomatis dibuat ulang pada folder `models/` ketika menjalankan notebook; tidak disertakan dalam ZIP ini. Berkas `.joblib` hanya dimuat jika berasal dari sumber tepercaya.

Data masih bercampur wilayah; tanpa verifikasi jangan mengklaim hasil khusus Madura. Sentimen dan waktu kunjungan belum tersedia. Jumlah topik bukan jumlah kelas jenis wisata. Perbandingan v1-v2 bukan eksperimen terkontrol karena train v2 lebih kecil akibat validation.
