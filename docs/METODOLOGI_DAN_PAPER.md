# Landasan metode dan batas eksperimen — pipeline v2

Dokumen ini memetakan setiap keputusan metode dan kelompok parameter ke literatur. **Paper mendukung gagasan metode, bukan membuktikan nilai parameter lokal paling baik untuk dataset ini.** Ini eksperimen klasifikasi dua atribut destinasi dan eksplorasi topik, bukan klasifikasi sentimen atau analisis musim kunjungan tervalidasi.

## Protokol dan inisialisasi

| Keputusan/parameter | Landasan paper | Implementasi dan batas adaptasi |
|---|---|---|
| Pisahkan train/validation/test menurut ID destinasi; cegah teks identik antarbagian | R06 | Mengikuti prinsip evaluasi data berkelompok. Pemilihan destinasi distratifikasi menurut jenis wisata. Tidak mengklaim mengimplementasikan seluruh strategi CV pada paper. Test awal dipertahankan; validation diambil dari train awal. |
| Rasio test=0,20; validation=0,20 dari sisa; seed=42/142 | R06, R13 | Angka lokal untuk menyediakan validation dan mempertahankan test sebelumnya; bukan rasio atau seed yang diwajibkan paper. Proporsi ulasan mengikuti ukuran destinasi. |
| LDA bag-of-words dengan CountVectorizer | R01 | LDA memodelkan count kata; bukan memasukkan FastText atau TF-IDF langsung sebagai count. Fitur LDA kemudian dapat digabungkan dengan BiLSTM. |
| `learning_method=online`, iterasi=20, `n_jobs=1` | R02 | Online variational learning didukung R02. Angka iterasi dan paralelisme membatasi biaya, bukan bukti konvergensi. `iterations` dicatat; perlu uji sensitivitas bila memperluas penelitian. |
| Kandidat K=(2,4,6,8,10,12), seeds=(42,43,44) | R03, R04, R13 | Pencarian rentang lokal, bukan angka rekomendasi universal. K=2 disertakan karena rentang awal 4–12 memilih batas bawah pada pemeriksaan validation. Test tidak dipakai memperluas grid. Tiga seed adalah diagnosis awal, bukan cukup untuk semua klaim kestabilan. |
| Pemilihan K berdasarkan rerata validation NPMI | R03 | Adaptasi: NPMI berdasarkan kehadiran kata pada **dokumen** validation, bukan c_v atau sliding window/persis protokol paper. Pasangan tidak pernah bersama=-1; bersama pada seluruh dokumen=0 (tidak informatif). Tidak menamai skor sebagai c_v. |
| Perplexity validation dan diversity top words | R01–R03 | Perplexity adalah diagnosis probabilistik; tidak dipakai sebagai satu-satunya bukti keterbacaan. Diversity = jumlah kata unik di seluruh top lists / seluruh slot kata, bukan ukuran relevansi manusia. |
| Stability top-word Jaccard dengan pencocokan optimal | R04 | Terinspirasi pengujian kestabilan dan pencocokan topik. Di sini gangguan berupa seed, memakai Jaccard biasa dan Hungarian matching; bukan reproduksi lengkap protokol resampling/rank agreement R04. |
| Aturan seri: stability, perplexity, K lebih kecil; seed model akhir tetap seed utama | R03, R04, R13 | Aturan rekayasa eksperimen yang dinyatakan eksplisit. Tidak memilih seed yang kebetulan memperoleh skor tertinggi. Model akhir tetap fit pada train saja. |
| Stopword Indonesia eksplisit + EnglishStopWords, pertahankan negasi | R05 | Pilihan preprocessing perlu diperiksa pada korpus. Daftar lokal disimpan ke audit; belum divalidasi sebagai stoplist optimal. Hanya jalur LDA yang mendapat stoplist tambahan; teks FastText/TF-IDF tidak diubah oleh langkah ini. |
| `min_df=3`, `max_df=0,90`, maksimum 4.000 kata, token huruf >=2 | R01, R05 | Penyaringan lokal untuk mengurangi kata sangat jarang/umum dan membatasi memori. Bukan nilai baku paper. Model sumber sudah memakai teks olahan; versi ini tidak mengklaim memperbaiki seluruh preprocessing sumber. |
| Maksimal 30 ulasan train per destinasi; top-10 kata; 5 contoh per topik | R03–R05 | Sampling seimbang per destinasi adalah desain lokal untuk mengurangi dominasi destinasi dengan banyak ulasan dan mengendalikan biaya. Contoh dipilih dari dokumen dengan topik dominan sesuai; tidak semua topik pasti punya lima contoh. |
| Heatmap atribut cuaca, rerata per destinasi | R03–R05 | Ringkasan deskriptif dari train sample, bukan uji kausal atau analisis perubahan musim kunjungan. Topik tidak otomatis menjadi aspek tervalidasi. |
| FastText skip-gram + subword ngram 3–6, window=5 | R07 | Dasar representasi subword dari R07. Gensim melatih model hanya pada train. Validation/test baru memperoleh vektor dari model beku; tidak ada fit pada keduanya. |
| Dimensi embedding=80, min_count=2, bucket=100.000, epoch FastText=5, workers=1 | R07, R13 | Konfigurasi lokal untuk biaya dan repeatability; berbeda dari sebagian konfigurasi asli paper. Tidak diklaim optimal. |
| BiLSTM satu lapis, hidden=64 per arah, urutan maksimum 64 token, embedding frozen | R07, R08 | Arsitektur lokal berdasarkan representasi urutan dua arah. Dua kepala softmax memprediksi dua atribut, bukan multilabel sentimen. Panjang/dimensi/freeze adalah pilihan baseline yang perlu diuji lebih lanjut. |
| Gabungkan hidden BiLSTM dengan distribusi topik melalui concatenation | R01, R08 | Adaptasi fitur lokal: menggabungkan dua representasi. Paper fondasi tidak membuktikan gabungan ini meningkatkan kualitas. Harus dibandingkan dengan varian tanpa LDA pada split sama. |
| Adam lr=0,001, batch=128 | R09 | Adam didukung R09; batch=128 merupakan pilihan lokal. Tidak mengeklaim jadwal optimizer terbaik. |
| Dropout=0,20 | R10 | Regularisasi dropout didukung R10; angka lokal 0,20 bukan hasil tuning validation pada eksperimen ini. |
| Gradient clipping norma=1 | R12 | Prinsip penanganan gradien pada RNN didukung R12; ambang 1 adalah pengaturan lokal. |
| Bobot kelas proporsional invers frekuensi train; loss rata-rata dua kepala | R15 | Tujuannya memberi perhatian lebih pada kelas jarang. Rumus dan pembobotan adalah pilihan lokal, bukan rumus yang diklaim disalin persis dari R15; R15 mendukung gagasan biaya klasifikasi yang tidak setara. Validation memakai bobot yang dihitung dari train saja. |
| Maksimum 15 epoch, patience=3, min_delta=0,0001; pilih validation loss terendah | R11 | Early stopping dan pemilihan checkpoint dari validation didukung R11; batas lokal belum dituning. Test diprediksi setelah checkpoint terbaik dipulihkan. |
| Seed dan deterministik cuDNN; CPU threads=2 | R13 | Membantu repeatability/biaya. Tidak menjamin hasil identik lintas versi/perangkat. Pencarian LDA multi-seed **bukan** pengulangan multi-seed BiLSTM. |
| Mayoritas, TF-IDF+Linear SVC, LDA+regresi logistik, dua varian BiLSTM | R01, R07, R08, R14 | Pembanding lokal pada train dan test yang sama. TF-IDF 1–2gram, min_df=2, max_features=40.000; SVC berbobot kelas; regresi logistik max_iter=500. Nilai ini baseline lokal, belum dituning. |
| Macro-F1, micro-F1, accuracy, Hamming loss per atribut dan suara terbanyak destinasi | R06, R13, R16 | Micro-F1 = accuracy dan Hamming loss = 1-accuracy untuk tugas satu label per contoh ini. Kelas langka dan test 43 destinasi membatasi kesimpulan. Voting adalah agregasi lokal; tidak mengklaim seluruh metrik independen. |
| Grafik, contoh, CSV, hash kode, model/vectorizer, checkpoint | R03–R05, R13 | Mendukung penelaahan dan reproduksibilitas. Grafik sendiri bukan validasi metode. Nama aspek dan kebenaran label tetap perlu penilaian manusia. |

## Cara membaca hasil

1. Bandingkan `pemilihan_topik.csv` dan grafik: K terpilih adalah terbaik **dalam grid dan protokol ini**, bukan jumlah topik yang terbukti benar.
2. Baca `kualitas_topik.csv`: skor negatif berarti kata topik kurang sering muncul bersama menurut ukuran ini; jangan menutupinya karena model sudah dipilih.
3. Baca `contoh_ulasan_topik.csv` sebelum memberi nama pada `template_review_topik.csv`.
4. Kestabilan dekat 0 menunjukkan kesamaan rendah; tidak ada ambang kelulusan universal yang diklaim di sini.
5. `kurva_bilstm.png` dan `checkpoint_bilstm.csv` menunjukkan generalisasi pada validation, bukan jaminan generalisasi ke semua wilayah.
6. Bandingkan kelima model pada `metrik_klasifikasi.csv`. Tambahan LDA boleh memperburuk hasil; laporkan apa adanya.
7. V2 memakai train lebih kecil karena validation dipisahkan. Jangan mengatribusikan selisih angka v1/v2 hanya pada perbaikan LDA.
8. Data campuran wilayah, asal label cuaca belum diverifikasi, tanpa sentimen dan tanggal kunjungan absolut. BGE tetap opsional dan belum merupakan fusion BGE-E5. Referensi fondasi tidak menggantikan bukti dataset ini.

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

## Bukti sumber dan keterbatasan akses

Pada sesi perbaikan ini, metadata R03, R07, dan R13 diperiksa pada data resmi ACL Anthology di GitHub (`acl-org/acl-anthology`, E14.xml, W13.xml, Q17.xml, D17.xml). R01/R02 diperiksa melalui rujukan implementasi scikit-learn; R04 melalui repositori kode penulis; R07 juga melalui repositori resmi fastText. Formula NPMI dibandingkan dengan implementasi konfirmasi langsung Gensim. Tautan publisher, ACL, DOI, dan arXiv langsung ditolak kebijakan jaringan lingkungan, sehingga **tidak diklaim seluruh full text paper dibaca pada sesi ini**. Rujukan lain dicantumkan sebagai fondasi bibliografis; tidak diklaim seluruh setting lokal direplikasi atau divalidasi oleh paper tersebut.

Sumber pemeriksaan yang dapat ditelusuri:
- https://github.com/acl-org/acl-anthology/blob/master/data/xml/E14.xml
- https://github.com/acl-org/acl-anthology/blob/master/data/xml/W13.xml
- https://github.com/acl-org/acl-anthology/blob/master/data/xml/Q17.xml
- https://github.com/scikit-learn/scikit-learn/blob/main/doc/modules/decomposition.rst
- https://github.com/derekgreene/topic-stability
- https://github.com/facebookresearch/fastText
- https://github.com/piskvorky/gensim/blob/develop/gensim/topic_coherence/direct_confirmation_measure.py
