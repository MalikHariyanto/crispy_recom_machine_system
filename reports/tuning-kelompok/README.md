# Hasil pencarian parameter kelompok

Pencarian penuh dijalankan pada CPU: 3 fold destinasi × 2 seed × 4 kandidat × 2 ablation deep. LDA dipilih di masing-masing fold dari K2/4/6 dan dua seed; maksimal15 epoch BiLSTM dengan early stopping. Protokol dan fingerprint disimpan sebelum fitting. Seluruh20 tes lulus.

**Skor ini untuk pemilihan parameter, bukan evaluasi independen.** Seluruh dataset lama diperlakukan sebagai development. Belum ada data baru yang tidak tersentuh; model final refit dan evaluasi independen belum dilakukan. Data fold memiliki ukuran tidak sama karena destinasi besar tidak dipecah; lihat assignment/cakupan sebelum menilai rerata/SD. Kelas singleton tetap train-only.

| Metode | Rerata validation destination macro-F1 kedua target |
|---|---:|
| TF-IDF + Linear SVC (baseline) | 0,3629 |
| Wider FastText–BiLSTM | 0,2533 |
| Compact FastText–LDA–BiLSTM | 0,2528 |
| Wider FastText–LDA–BiLSTM | 0,2475 |

Kandidat deep terpilih: embedding128, hidden64, lr.001, dropout.3, frozen embedding, panjang berdasarkan kuantil95% train (batas16–128). Terpilih hanya berarti terbaik dalam kandidat deep yang dicoba. **Baseline TF-IDF+SVC masih lebih tinggi**, sehingga tidak ada klaim bahwa konfigurasi deep tersebut terbaik secara umum atau layak mengganti aplikasi. Klasik tiga unit fold; deep enam unit fold/seed. Selisih kecil antar-deep tidak membuktikan signifikansi.

`selected_configuration.json` menyimpan pemenang deep, metode validation terbaik secara keseluruhan, dan `deployment_ready=false`. Semua percobaan, termasuk yang rendah, ada di tabel metrik. Tidak ada penyesuaian grid untuk mengejar hasil test. Pembaruan setelah pencarian hanya memperjelas bahwa pemilihan deep tidak mengalahkan baseline.

Notebook [tuning kelompok](../../notebooks/Colab_Tuning_Kelompok_Madura.ipynb); [protokol dan langkah evaluasi independen](../../docs/TUNING_PROTOCOL.md). Biner checkpoint setiap fold tidak disalin ke GitHub; notebook tetap menyimpannya dalam folder run/ZIP.
