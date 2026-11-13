# SISRE — Streamlit

SISRE menampilkan satu halaman pencarian rekomendasi wisata Madura. Dataset bawaan dimuat otomatis: 27 destinasi dan 2.058 ulasan. Tidak ada unggahan file, sidebar riset, pemilihan algoritma, statistik eksperimen, atau ekspor dataset pada layar pengguna.

## Deploy

| Field | Nilai |
|---|---|
| Repository | `MalikHariyanto/crispy_recom_machine_system` |
| Branch | `feat/streamlit-wisata` |
| Main file | `app.py` |
| Python | `3.11` |

Streamlit memasang `requirements.txt`. Bila tampilan lama masih muncul setelah pembaruan, gunakan **Manage app → Reboot app**.

## Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tampilan dan interaksi

Tema ivory, teal, dan ink; tipografi ringkas serta ilustrasi geometris lokal. Cover foto lokal ditampilkan untuk destinasi yang sudah dipetakan di assets/destinations/manifest.json; destinasi tanpa pasangan tetap memakai ilustrasi dekoratif. Foto dan daerah diikat pada ID sekaligus nama destinasi agar metadata tidak tertukar setelah perubahan dataset. Foto dari pengguna dioptimalkan ke WebP, sedangkan nama file sumber tetap dicatat. Sebagian nama generik masih menunggu pemetaan konteks dari pengguna. Input mendukung Enter dan tombol Cari. Filter musim/jenis dikirim bersama query. Saran pencarian langsung mengisi dan menjalankan query; Reset mengembalikan layar awal. Hasil ditampilkan enam kartu per tahap, dengan tombol Lihat lebih banyak. Kartu memuat nama, jenis, kecocokan musim, jumlah ulasan, tautan Maps dan cuplikan ulasan yang dapat dibuka.

Skor numerik dan penjelasan implementasi tidak masuk alur utama. Pencarian tetap memakai indeks TF-IDF dan dataset yang sama; perubahan UI tidak melatih atau mengganti model penelitian. Layar awal menampilkan destinasi menurut jumlah ulasan, bukan ranking personal atau rating kualitas. Hasil query tetap diurutkan menurut kemiripan teks. Label musim adalah atribut dataset, bukan prakiraan cuaca langsung.

## Struktur

- `web/app.py`: shell SISRE.
- `web/views.py`: form pencarian, saran, reset, kartu dan pagination.
- `web/styles.py`: tema dan ilustrasi lokal tanpa permintaan aset eksternal.
- `web/runtime.py`: cache data dan indeks berbasis hash manifest.
- `web/services.py`: mesin pencarian dan filter, terpisah dari presentasi.

Modul riset dan notebook tetap tersedia di repo. Rujukan: [Colab v3](COLAB_V3.md), [tuning kelompok](TUNING_PROTOCOL.md).

## Pengujian UI

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_streamlit_app.py' -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_web_services.py' -v
```

Menguji pencarian, filter, reset, hasil kosong, pagination dan ketiadaan unggahan file/sidebar. Browser juga diperiksa pada viewport desktop/mobile untuk Enter, saran pencarian dan tautan Maps.
