# Referensi dokumentasi minggu 2

Gambar dibuat sebagai ilustrasi konsep/rancangan, bukan tangkapan layar kode atau hasil pelatihan. Arsitektur dan label aktual perlu dicocokkan dengan implementasi. Tanggal kegiatan tetap diisi sesuai pelaksanaan.

- M02-D02 — FastText: paper asli Bojanowski dkk., Enriching Word Vectors with Subword Information: https://aclanthology.org/Q17-1010/ ; tutorial resmi: https://fasttext.cc/docs/en/unsupervised-tutorial.html . Contoh trigram pada gambar disederhanakan; FastText menggunakan penanda batas kata dan dapat menggunakan beberapa panjang n-gram.
- M02-D03 — BiLSTM: paper Bidirectional Recurrent Neural Networks: https://doi.org/10.1109/78.650093 ; dokumentasi LSTM PyTorch (bidirectional): https://docs.pytorch.org/docs/stable/generated/torch.nn.LSTM.html . Dua kepala atribut adalah rancangan ilustratif, bukan arsitektur terverifikasi dari kode proyek.
- M02-D04 — BGE: dokumentasi resmi https://github.com/FlagOpen/FlagEmbedding dan model multilingual https://huggingface.co/BAAI/bge-m3 . Diagram menunjukkan alur konseptual; pemilihan model, instruksi masukan dan normalisasi mengikuti model yang benar-benar digunakan. Tidak menyiratkan hasil fusion BGE-E5.
- M02-D05 — Split per grup destinasi: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html ; F1: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html ; Hamming loss: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.hamming_loss.html . Metrik harus disesuaikan dengan format target sebenarnya.

Yang perlu diambil dari pekerjaan asli: screenshot konfigurasi/kode, nama dan asal label, ukuran data, hasil run, tanggal kegiatan, serta catatan konsultasi. Tautan di atas adalah referensi metode; bukan pengganti bukti pelaksanaan.
