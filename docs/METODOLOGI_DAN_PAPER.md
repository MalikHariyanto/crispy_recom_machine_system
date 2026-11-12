# Landasan metode dan batas eksperimen — pipeline v3

Dataset aktif: **2.058 ulasan / 27 destinasi Madura**, sesuai konfirmasi pemilik data. Tugasnya klasifikasi dua atribut destinasi (cuaca dan jenis wisata) serta eksplorasi topik. Tidak ada klaim sentimen, kausalitas musim, atau bias nol. Paper mendukung gagasan metode; **angka hiperparameter lokal bukan nilai optimal yang dibuktikan paper**.

## Pemetaan keputusan ke literatur

| Keputusan | Landasan | Adaptasi lokal dan batas |
|---|---|---|
| Train/validation/test per ID destinasi; cegah teks identik lintas bagian | R06, R17 | Prinsip evaluasi kelompok dan pencegahan leakage. V3 memakai kandidat split metadata dengan rasio nominal 64/16/20 ulasan, bukan algoritma yang diklaim persis dari R06. |
| 2.048 kandidat, seed=42, stratifikasi wisata, penalti distribusi cuaca | R06, R18 | Desain lokal ditetapkan sebelum fitting. Objektif = L1 selisih proporsi ulasan + 0,1 × L1 selisih jumlah destinasi per label cuaca / jumlah destinasi. Tidak memakai fitur terlatih/skor model. Setelah deduplikasi aktual 1.168/268/426 ulasan dan 16/5/6 destinasi. |
| Kelas singleton tetap di train; laporkan cakupan kelas | R06, R16, R17 | Tidak mungkin membagi satu destinasi ke tiga partisi tanpa leakage. Kelas tanpa support holdout tidak punya bukti generalisasi. |
| CountVectorizer train-only → LDA bersama | R01, R02, R17 | LDA menerima count, tidak menerima embedding sebagai count. Satu model bersama menjaga arti dimensi topik konsisten. |
| Online LDA max_iter=20, n_jobs=1 | R02 | Konfigurasi biaya lokal, bukan bukti konvergensi. Iterasi dicatat. |
| Grid K=(2,4,6,8,10,12), seeds=(42,43,44) | R03, R04, R13 | Grid lokal. Seleksi rerata validation NPMI; seri memakai stability, perplexity, K lebih kecil. Model akhir seed42 tetap, tidak memilih seed kebetulan terbaik. |
| NPMI berbasis dokumen validation | R03 | Adaptasi document-level, bukan c_v/sliding-window atau replikasi persis R03. Pasangan tidak bersama=-1; selalu bersama=0. K terbaik dalam grid tetap bisa memiliki coherence negatif. |
| Stability Jaccard + Hungarian matching, diversity, perplexity | R01, R03, R04 | Diagnostik tambahan; kestabilan antar-seed bukan bukti semantik benar. Tidak mereplikasi seluruh resampling/rank agreement R04. |
| Stopword Indonesia/Inggris eksplisit, negasi dipertahankan | R05 | Hanya jalur LDA; teks olahan sumber tetap mempunyai keterbatasan provenance. min_df=3, max_df=.90, max_features=4.000 adalah pilihan lokal. |
| Maksimal 30 ulasan train per destinasi untuk fit LDA | R03–R05 | Sampling lokal untuk biaya dan dominasi kelompok. Validation sample dibatasi dengan aturan sama; tidak melakukan fit pada validation. |
| FastText skip-gram, subword karakter3–6, window5 | R07 | Fit train saja. Kata baru dari holdout memperoleh vektor subword model beku, bukan pelatihan ulang. |
| Embedding80, min_count2, bucket100.000, epoch5, workers1, frozen | R07, R13 | Parameter lokal untuk biaya dan repeatability. Registry token holdout hanya indexing vektor beku; tidak digunakan memperbarui embedding train. |
| BiLSTM hidden64 per arah, max64 token, dua kepala softmax | R08 | Arsitektur lokal. Kepala cuaca/jenis memprediksi masing-masing satu kelas; bukan multilabel sentimen. |
| Concatenation hidden BiLSTM + distribusi topik | R01, R08 | Adaptasi fitur lokal yang wajib diuji dengan ablation tanpa LDA. Paper fondasi tidak menjamin gabungan menaikkan skor. |
| Adam lr.001, batch128, dropout.20, gradient clip1 | R09, R10, R12 | Pilihan lokal; tidak diklaim hasil tuning terbaik. |
| Bobot sampel invers jumlah ulasan per destinasi, normalisasi mean1 | R06, R15 | Setiap destinasi mempunyai total bobot sama. Formula engineering lokal, bukan algoritma persis R06/R15. Tidak menghapus semua bias representasi korpus. |
| Bobot kelas invers frekuensi destinasi train | R15 | SVC/logreg dan loss deep memakai bobot dari train saja. Validation memakai bobot kelas train dan bobot unit destinasi validation. |
| Early stopping validation loss, maksimal15 epoch, patience3, min_delta.0001 | R11, R18 | Checkpoint terbaik dipulihkan sebelum prediksi test. Test tidak menentukan epoch/parameter/seed. |
| Tiga seed embedding/BiLSTM; klasik satu run | R13 | Embedding fit sekali/seed dan dipakai dua ablation. Klasik tidak diulang menjadi tiga observasi identik. Kolom runs menunjukkan jumlah sebenarnya. Tiga seed satu split bukan cross-validation atau confidence interval. |
| Macro-F1 seluruh kelas + macro_f1_present, support per kelas | R16 | Kelas tanpa test support ditampilkan sebagai nol; metrik pendamping hanya kelas yang hadir. Denominator berbeda harus disebut. Enam destinasi test membatasi kesimpulan. |
| Accuracy, micro-F1, Hamming loss per target | R16 | Untuk satu label per atribut: micro-F1=accuracy dan Hamming=1−accuracy. Bukan bukti independen. Voting destinasi memakai mayoritas; seri diurutkan label. |
| Mayoritas, TF-IDF+SVC, LDA+logreg, FastText-BiLSTM, FastText-LDA-BiLSTM | R01, R07, R08, R14 | Semua memakai split sama. TF-IDF1–2gram min_df2 max40.000; logreg max_iter500. Pembanding lokal, bukan klaim tuning tuntas. |

## Cara membaca hasil

1. K terbaik masih dapat memiliki NPMI negatif; lihat contoh dan isi nama topik melalui review manusia.
2. Semua model dan seed yang ditetapkan dilaporkan. Jangan memilih ulang split atau seed setelah melihat test.
3. Kelas train-only tidak memiliki evaluasi generalisasi. Support nol tidak boleh disebut akurasi kelas.
4. Bobot kelompok/kelas membantu dominasi data, bukan menjamin bebas bias atau memperbaiki label yang salah.
5. V3 mengubah protokol split dan metrik dibanding v2. Perbedaan skor tidak boleh diatribusikan hanya pada tambahan LDA.
6. Dataset sepenuhnya Madura sesuai pemilik data. Asal anotasi cuaca dan preprocessing sumber tetap harus dijelaskan; label cuaca bukan prakiraan cuaca langsung.
7. BGE/Streamlit terpisah dari classifier ini; validasi ranking memerlukan relevansi independen.

## Daftar paper

- **R01.** Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). *Latent Dirichlet Allocation*. JMLR, 3, 993–1022. https://www.jmlr.org/papers/v3/blei03a.html
- **R02.** Hoffman, M. D., Blei, D. M., & Bach, F. (2010). *Online Learning for Latent Dirichlet Allocation*. NeurIPS 23. https://papers.nips.cc/paper/3902-online-learning-for-latent-dirichlet-allocation
- **R03.** Lau, J. H., Newman, D., & Baldwin, T. (2014). *Machine Reading Tea Leaves: Automatically Evaluating Topic Coherence and Topic Model Quality*. EACL, 530–539. https://doi.org/10.3115/v1/E14-1056 ; Aletras, N., & Stevenson, M. (2013). *Evaluating Topic Coherence Using Distributional Semantics*. IWCS, 13–22. https://aclanthology.org/W13-0102/
- **R04.** Greene, D., O'Callaghan, D., & Cunningham, P. (2014). *How Many Topics? Stability Analysis for Topic Models*. ECML PKDD. https://arxiv.org/abs/1404.4606 — kode penulis: https://github.com/derekgreene/topic-stability
- **R05.** Denny, M. J., & Spirling, A. (2018). *Text Preprocessing for Unsupervised Learning: Why It Matters, When It Misleads, and What to Do About It*. Political Analysis, 26(2), 168–189. https://doi.org/10.1017/pan.2017.44
- **R06.** Roberts, D. R., et al. (2017). *Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure*. Ecography, 40, 913–929. https://doi.org/10.1111/ecog.02881
- **R07.** Bojanowski, P., Grave, E., Joulin, A., & Mikolov, T. (2017). *Enriching Word Vectors with Subword Information*. TACL, 5, 135–146. https://doi.org/10.1162/tacl_a_00051
- **R08.** Hochreiter, S., & Schmidhuber, J. (1997). *Long Short-Term Memory*. Neural Computation, 9(8), 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735 ; Schuster, M., & Paliwal, K. K. (1997). *Bidirectional recurrent neural networks*. IEEE Transactions on Signal Processing, 45(11), 2673–2681. https://doi.org/10.1109/78.650093
- **R09.** Kingma, D. P., & Ba, J. (2015). *Adam: A Method for Stochastic Optimization*. ICLR. https://arxiv.org/abs/1412.6980
- **R10.** Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. (2014). *Dropout: A Simple Way to Prevent Neural Networks from Overfitting*. JMLR, 15, 1929–1958. https://www.jmlr.org/papers/v15/srivastava14a.html
- **R11.** Prechelt, L. (1998). *Early Stopping — But When?* In Neural Networks: Tricks of the Trade, 55–69. https://doi.org/10.1007/3-540-49430-8_3
- **R12.** Pascanu, R., Mikolov, T., & Bengio, Y. (2013). *On the difficulty of training recurrent neural networks*. ICML, PMLR 28(3), 1310–1318. https://proceedings.mlr.press/v28/pascanu13.html
- **R13.** Reimers, N., & Gurevych, I. (2017). *Reporting Score Distributions Makes a Difference: Performance Study of LSTM-networks for Sequence Tagging*. EMNLP. https://aclanthology.org/D17-1035/
- **R14.** Salton, G., & Buckley, C. (1988). *Term-weighting approaches in automatic text retrieval*. Information Processing & Management, 24(5), 513–523. https://doi.org/10.1016/0306-4573(88)90021-0 ; Joachims, T. (1998). *Text Categorization with Support Vector Machines: Learning with Many Relevant Features*. ECML. https://doi.org/10.1007/BFb0026683

- **R15.** Elkan, C. (2001). *The Foundations of Cost-Sensitive Learning*. IJCAI, 973–978. Pembobotan kelas lokal merupakan penerapan gagasan biaya yang tidak setara, bukan bukti bobot invers frekuensi optimal untuk dataset ini.
- **R16.** Sokolova, M., & Lapalme, G. (2009). *A systematic analysis of performance measures for classification tasks*. Information Processing & Management, 45(4), 427–437. https://doi.org/10.1016/j.ipm.2009.03.002

- **R17.** Kapoor, S., & Narayanan, A. (2023). *Leakage and the reproducibility crisis in machine-learning-based science*. Patterns, 4(9), 100804. https://doi.org/10.1016/j.patter.2023.100804
- **R18.** Cawley, G. C., & Talbot, N. L. C. (2010). *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation*. JMLR, 11, 2079–2107. https://www.jmlr.org/papers/v11/cawley10a.html

## Bukti akses pada 12 November 2026

Tinjauan **terarah**, bukan systematic review lengkap atau klaim telah membaca semua jurnal yang relevan. Log URL, status akses, ukuran, dan hash materi yang berhasil diperoleh: [literature_access_2026-11-12.json](literature_access_2026-11-12.json).

- Metadata resmi ACL R03 diperiksa (judul/penulis/DOI). Abstrak dan metadata R07 serta R13 diperiksa pada XML resmi ACL Anthology. Abstrak R07 menjelaskan representasi skip-gram berbasis karakter n-gram dan kata yang tidak muncul saat training; R13 menekankan variasi skor akibat seed dan pelaporan distribusi hasil.
- Dokumentasi scikit-learn yang merujuk Blei/Hoffman diperiksa untuk LDA/count/online variational learning. Ini sumber implementasi, **bukan pembacaan full text R01/R02**.
- README repositori penulis Greene dkk. diperiksa: kestabilan terhadap perturbasi untuk pemilihan jumlah topik; protokol v3 Jaccard/seed adalah adaptasi, bukan replika kodenya.
- Implementasi Gensim `direct_confirmation_measure.py` diperiksa sebagai pembanding formula PMI/NPMI; estimator dokumen lokal dinyatakan berbeda dari sliding window.
- README resmi fastText dan implementasi PyTorch LSTM v2.5.1 diperiksa untuk konsistensi API. Keduanya bukan pengganti jurnal fondasi.
- Akses langsung JMLR, NeurIPS, ACL, arXiv, PMLR, dan DOI yang dicoba gagal melalui proxy lingkungan. Tidak ada klaim full text R01–R18 seluruhnya dibaca pada sesi ini. Rujukan lain merupakan dasar bibliografis yang perlu pembacaan lanjutan jika mensyaratkan review full text.

Metadata implementasi yang dapat ditelusuri:
- https://github.com/acl-org/acl-anthology/blob/master/data/xml/E14.xml
- https://github.com/acl-org/acl-anthology/blob/master/data/xml/Q17.xml
- https://github.com/acl-org/acl-anthology/blob/master/data/xml/D17.xml
- https://github.com/scikit-learn/scikit-learn/blob/main/doc/modules/decomposition.rst
- https://github.com/derekgreene/topic-stability
- https://github.com/facebookresearch/fastText
- https://github.com/piskvorky/gensim/blob/develop/gensim/topic_coherence/direct_confirmation_measure.py
- https://github.com/pytorch/pytorch/blob/v2.5.1/torch/nn/modules/rnn.py
