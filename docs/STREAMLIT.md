# Madura Explore — deployment dan struktur

Antarmuka web untuk katalog dan rekomendasi destinasi. Aplikasi langsung membaca dataset bawaan (27 destinasi, 2.058 ulasan; sumber `data/source/dataset_madura_bersih.xlsx`); tidak perlu menjalankan notebook atau mengunggah workbook terlebih dahulu.

## Streamlit Community Cloud

Pilih **Create app → Deploy a public app from GitHub**, lalu isi:

| Field | Nilai |
|---|---|
| Repository | `MalikHariyanto/crispy_recom_machine_system` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version (Advanced settings) | `3.11` |

Streamlit memasang `requirements.txt` dari root. Tidak perlu secrets, API key, database, atau model eksternal untuk pencarian TF-IDF. Jangan pilih `main` selama perubahan belum digabungkan. Sertakan folder `src/`, `.streamlit/`, dan seluruh `data/` saat memindahkan aplikasi.

## Menjalankan lokal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Buka `http://localhost:8501`. Pada Windows, aktivasi dengan `.venv\Scripts\activate`.

## Struktur

```text
app.py                              # entry point deployment
.streamlit/config.toml              # tema dan batas unggahan
requirements.txt                    # dependensi web ringan
src/wisata_madura/web/
  app.py                            # navigasi dan cakupan sesi
  views.py                          # halaman dan komponen UI
  styles.py                         # identitas visual lokal
  services.py                       # indeks TF-IDF dan validasi filter/CSV
  runtime.py                        # cache data dan resource model
src/wisata_madura/                   # modul riset tetap tersedia
notebooks/                          # pelatihan dan evaluasi eksperimen
```

Cache data dan indeks memakai hash manifest; pembaruan dataset juga membatalkan hasil pencarian sesi versi lama. Data dimuat melalui loader riset yang memvalidasi checksum manifest. Katalog dan ringkasan audit disimpan dengan `st.cache_data`. Indeks TF-IDF dibangun satu kali dengan `st.cache_resource`; query baru hanya ditransformasi terhadap indeks tersebut. CSV wilayah dan filter tidak mengubah indeks global. Hasil pencarian disimpan per sesi, dipertahankan saat berpindah halaman, dan disembunyikan ketika cakupan wilayah berubah. Katalog memakai pagination sembilan kartu per halaman. Aset visual tidak membutuhkan layanan eksternal.

## Perilaku rekomendasi

- TF-IDF: unigram/bigram, pembobotan sublinear, maksimum 30.000 fitur, kemiripan kosinus. Deskripsi memuat nama, jenis, cuaca, dan maksimal 12 cuplikan ulasan per destinasi. Bukan model klasifikasi yang dilatih pada notebook.
- Musim, kategori, wilayah, dan riwayat kunjungan membatasi kandidat sebelum pemeringkatan.
- TF-IDF tidak mengembalikan hasil dengan skor nol. Query tanpa kata yang cocok memunculkan saran mengubah preferensi/filter.
- Riwayat pada TF-IDF berfungsi sebagai pengecualian destinasi. BGE juga memakai hingga tiga kunjungan terakhir sebagai konteks, mengikuti modul riset.
- Skor bukan rating kualitas atau probabilitas. Jumlah ulasan bukan rating.
- Katalog menyertakan lokasi di luar Madura. Unggah CSV verifikasi dengan `id_destinasi,kabupaten`; hanya nilai Bangkalan, Sampang, Pamekasan, Sumenep, Di luar Madura, atau kosong yang diterima. Template dapat diunduh dari sidebar. Baris dengan wilayah kosong/tidak dipetakan tetap belum terverifikasi. CSV salah menghentikan pemuatan halaman sampai diperbaiki.
- Label cuaca adalah atribut dataset, bukan prakiraan cuaca saat ini. Cuplikan adalah teks ulasan yang telah diproses, bukan deskripsi redaksi atau verifikasi fasilitas.
- Insight menampilkan statistik aktual; tidak mengarang akurasi rekomendasi atau mengambil angka eksperimen sebagai kinerja pencarian web.

## BGE-M3 opsional

Instal `sentence-transformers>=3,<6` pada server, lalu restart aplikasi. Pilihan BGE muncul otomatis di form **Personalisasi & metode pencarian**. Model `BAAI/bge-m3` baru diunduh/dimuat setelah pengguna memilihnya dan mencari; indeks vektor di-cache. Mode ini membutuhkan akses Hugging Face, penyimpanan dan RAM jauh lebih besar daripada TF-IDF. Untuk deployment Cloud ringan, pertahankan dependensi default. Validasi fungsi BGE memerlukan lingkungan dengan model tersedia; pengujian web default tidak mengunduh atau menguji kualitas BGE.

Pelatihan LDA, FastText, dan BiLSTM tetap di notebook. Tidak ada pelatihan otomatis saat pengguna membuka halaman.

## Pengujian

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_web_services.py' -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_streamlit_app.py' -v
```

Tes memeriksa pemeringkatan, kandidat/wilayah/riwayat, skor nol, validasi CSV, navigasi seluruh halaman, dan rerun pencarian menggunakan dataset asli. Tes pipeline penelitian tetap dapat dijalankan dengan dependensi riset lengkap.

## Pratinjau

Screenshot berikut menggunakan dataset terbaru: 27 destinasi dan 2.058 ulasan.

![Halaman jelajah](images/streamlit-home.png)

![Hasil rekomendasi](images/streamlit-results.png)

## Validasi implementasi

- Enam tes web (service + Streamlit AppTest) lulus dengan dataset bawaan.
- Chromium/Playwright: pencarian aktual, katalog tanpa hasil, rendering viewport mobile, unggah CSV valid, filter wilayah terverifikasi, dan penolakan CSV tidak valid lulus.
- Empat tes pipeline riset lama juga lulus. Tes checkpoint BiLSTM belum dapat dijalankan pada lingkungan web karena `torch` tidak dipasang. Dependensi pelatihan sengaja tidak menjadi dependensi web default.
- BGE-M3 belum diuji dengan unduhan model; mode deploy default yang divalidasi adalah TF-IDF.

Pembaruan dataset 12 November 2026: tes kesetaraan Excel–bundle, kompatibilitas sheet, enam tes web, serta dua tes split/pemilihan model riset lulus. Browser memverifikasi angka 27 destinasi/2.058 ulasan dan pencarian langsung. Workbook sumber tersimpan di `data/source/`; rebuild dengan `python scripts/build_dataset_bundle.py data/source/dataset_madura_bersih.xlsx` (memerlukan `openpyxl` dari dependensi riset). Hasil riset/laporan lama tetap merupakan artefak dataset sebelumnya, bukan evaluasi ulang dataset ini.
