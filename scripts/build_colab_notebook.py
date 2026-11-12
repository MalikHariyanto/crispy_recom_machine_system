"""Generate the canonical teaching notebook from one maintained source."""
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
cells = []
def md(text):
    cells.append(dict(cell_type='markdown', metadata={}, source=dedent(text).strip().splitlines(keepends=True)))
def code(text):
    cells.append(dict(cell_type='code', metadata={}, execution_count=None, outputs=[], source=dedent(text).strip().splitlines(keepends=True)))
def section(title, inputs, process, outputs, explanation=''):
    md(f'## {title}\n\n**Input:** {inputs}\n\n**Proses:** {process}\n\n**Output:** {outputs}\n\n{explanation}')

md('''
# Wisata Madura — Input → Proses → Output (v3)
**Malik Hariyanto · Asistensi Hibah Penelitian**

Notebook pembelajaran: **input data → audit/EDA → split → pemodelan topik LDA → embedding FastText → modeling BiLSTM → evaluasi → output**.

Dataset terbaru: **2.058 ulasan, 27 destinasi Madura**. Semua angka split, jumlah topik, dimensi, dan metrik ditampilkan dari run aktual. Angka 79.514/207 dan K=2 pada diagram lama bukan konstanta eksperimen ini.

Jalankan dari atas. Bagian 00–05 tidak melatih BiLSTM; bagian 06–07 melatih embedding dan classifier; test dilaporkan di bagian 08. **LDA menghasilkan distribusi topik, FastText menghasilkan embedding, dan BiLSTM memprediksi dua atribut:** kecocokan cuaca serta jenis wisata. Bukan klasifikasi sentimen atau validasi musim kunjungan.

[Landasan paper dan batas adaptasi](https://github.com/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/docs/METODOLOGI_DAN_PAPER.md) · [Panduan v3](https://github.com/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/docs/COLAB_V3.md).
''')
section('00 · Setup dan konfigurasi', 'Repository, pilihan mode, seed yang ditetapkan sebelum eksperimen.', 'Pasang dependensi; tetapkan anggaran komputasi dan folder run.', 'Modul siap dipakai, konfigurasi eksplisit, hash kode.',
'''`MODE="full"`: grid LDA 6 K × 3 seed, BiLSTM hingga 15 epoch × 3 seed. GPU Colab disarankan. `MODE="smoke"`: tes alur cepat, **bukan hasil penelitian final**. Hiperparameter adalah pilihan lokal, bukan nilai optimal yang dijamin jurnal. Gunakan runtime baru jika pernah mengimpor versi kode sebelumnya.''')
code('''
from pathlib import Path
from datetime import datetime
import subprocess, sys, os, hashlib, json

MODE = "full"  # "full" atau "smoke"
RUN_DEEP = True
SEED = 42
DATA_PATH = None  # None: dataset Madura otomatis, tanpa upload.
OUTPUT_DIR = Path("hasil_wisata_madura_v3") / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
BRANCH = "feat/streamlit-wisata"
REPOSITORY = "https://github.com/MalikHariyanto/crispy_recom_machine_system.git"
if MODE not in {"full", "smoke"}:
    raise ValueError("MODE harus full atau smoke")
checkout = Path.cwd() / "wisata_madura_v3"
repo_root = next((p for p in (Path.cwd(), Path.cwd().parent, checkout)
                  if (p / "src/wisata_madura/protocol.py").is_file()), None)
if repo_root is None:
    if checkout.exists():
        raise FileExistsError("Folder wisata_madura_v3 berisi versi lama. Ganti nama folder atau mulai runtime baru.")
    subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPOSITORY, str(checkout)], check=True)
    repo_root = checkout
requirements = ["-r", str(repo_root / "requirements-wisata.txt")]
if RUN_DEEP:
    requirements += ["gensim>=4.4,<5", "torch>=2.2,<3"]
subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", *requirements], check=True)
if any(name.startswith("wisata_madura") for name in sys.modules):
    raise RuntimeError("Modul pernah diimpor. Restart runtime agar kode dan hasil tidak mencampur versi.")
sys.path.insert(0, str(repo_root / "src"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str((OUTPUT_DIR / ".matplotlib").resolve()))
source_commit = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
source_dirty = bool(subprocess.check_output(["git", "-C", str(repo_root), "status", "--porcelain"], text=True).strip())
source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (repo_root / "src/wisata_madura").glob("*.py")}
print("Mode:", MODE, "| Source:", source_commit, "| Output:", OUTPUT_DIR)
''')
section('01 · INPUT: dataset dan label', 'Workbook dataset_madura_bersih.xlsx dan manifest paket data.', 'Validasi checksum, skema, label per ID; normalisasi ringan teks.', 'DataFrame reviews dengan rating, teks_model, dan dua label.',
'''Kolom `rating` dipakai untuk EDA, **tidak dimasukkan sebagai fitur classifier**. Teks model berasal dari preprocessing sumber; audit tidak membuktikan bahwa seluruh teks/label sumber bebas kesalahan. Cakupan Madura sesuai konfirmasi pemilik data.''')
code('''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from wisata_madura.data import load_reviews, load_bundled_reviews, audit_reviews, TARGETS
from wisata_madura.protocol import SplitConfig, make_experiment_split
from wisata_madura.reporting import StageTrace

trace = StageTrace(OUTPUT_DIR)
if DATA_PATH is None:
    bundled, data_manifest = load_bundled_reviews(repo_root / "data")
    workbook_path = repo_root / "data/source" / data_manifest["source_workbook"]
    if hashlib.sha256(workbook_path.read_bytes()).hexdigest() != data_manifest["source_workbook_sha256"]:
        raise ValueError("Checksum workbook tidak cocok dengan manifest")
    reviews = load_reviews(workbook_path)
    columns = ["id_destinasi", "destinasi", *TARGETS, "teks_model"]
    pd.testing.assert_frame_equal(reviews[columns], bundled[columns])
else:
    workbook_path = Path(DATA_PATH)
    reviews = load_reviews(workbook_path)
    data_manifest = None
print(f"INPUT: {len(reviews):,} ulasan / {reviews.id_destinasi.nunique()} destinasi")
display(reviews[["destinasi", "rating", "teks_model", *TARGETS]].head())
display(trace.record("01 Input", workbook_path.name, "validasi + normalisasi", f"reviews {reviews.shape}"))
''')
section('02 · INPUT: audit dan eksplorasi data', 'reviews sebelum split.', 'Hitung kualitas data; grafik rating, cuaca, jenis wisata, panjang teks.', 'audit, tabel CSV, grafik PNG.',
'''Batang rating/cuaca menghitung ulasan. Pie cuaca/jenis menghitung **destinasi unik** agar tempat ramai tidak dihitung berkali-kali. EDA seluruh data bersifat deskriptif; aturan pemilihan model tetap berdasarkan train/validation.''')
code('''
from wisata_madura.visualization import plot_dataset_overview, plot_partition_overview

audit = audit_reviews(reviews, workbook_path)
figures, eda_tables = plot_dataset_overview(reviews, OUTPUT_DIR)
display(pd.Series(audit))
for figure in figures:
    display(figure)
    plt.close(figure)
for name in ("rating", "cuaca_ulasan", "cuaca_destinasi", "jenis_destinasi"):
    display(eda_tables[name].round(2))
display(trace.record("02 Audit/EDA", f"{len(reviews)} ulasan", "audit + agregasi per unit", "EDA PNG/CSV + audit"))
''')
section('03 · PROSES: bersihkan dan bagi data', 'reviews dan SplitConfig yang ditetapkan sebelum fitting.', 'Split kelompok ID destinasi dengan kandidat berbasis metadata; buang teks identik lintas partisi.', 'split.train, split.validation, split.test; cakupan kelas; grafik pembagian.',
'''R06/R17: pemisahan kelompok mencegah kebocoran destinasi; teks identik juga diperiksa. Kandidat split dipilih menggunakan ukuran kelompok dan distribusi label, **tanpa skor model atau fitur hasil belajar**. Target nominal 64/16/20 untuk ulasan; tidak dipaksakan tepat karena kelompok tidak boleh dipecah. Kelas satu destinasi tetap train-only; lihat tabel cakupan. Perubahan protokol berarti hasil v3 tidak dapat dibandingkan dengan v2 seolah hanya arsitektur yang berubah.''')
code('''
split_config = SplitConfig(seed=SEED, candidates=2048)
split = make_experiment_split(reviews, split_config, OUTPUT_DIR)
partition_figure, partition_table = plot_partition_overview(split, OUTPUT_DIR)
display(partition_table.round(2))
display(partition_figure)
plt.close(partition_figure)
display(pd.DataFrame(split.audit["class_coverage"]))
print("Pembersihan:", {k: split.audit[k] for k in ("input_reviews", "empty_removed", "duplicates_within_destination_removed", "cross_partition_text_removed")})
print("Tujuan metadata split:", split.audit["metadata_objective"])
print("Kelas train-only tidak punya bukti generalisasi test. Rasio aktual ada pada tabel di atas.")
display(trace.record("03 Split", f"{len(reviews)} ulasan", "kelompok ID + metadata; tanpa skor", str(split.audit["partition_reviews"])))
''')
section('04 · PROSES: pemodelan topik LDA', 'Teks train untuk fit; teks validation untuk seleksi K.', 'CountVectorizer → LDA kandidat K/seed → NPMI validation → K terpilih.', 'topics (distribusi topik train/validation/test), tabel kata, contoh, model_lda.joblib.',
'''R01–R05: LDA menerima **count kata**, bukan embedding FastText. Kosakata, stopword, dan LDA tidak di-fit pada validation/test. NPMI yang dipakai berbasis dokumen, **bukan c_v**. Perplexity/diversity/stability adalah diagnostik tambahan. K yang menang dalam grid tidak membuktikan topiknya koheren; skor negatif dan topik lemah tetap dilaporkan. Transform test memakai model beku dan tidak menentukan pemilihan K.''')
code('''
from wisata_madura.topics import TopicConfig, analyze_topics
from dataclasses import asdict
from IPython.display import Image

topic_config = TopicConfig(
    topic_counts=(2,4,6,8,10,12) if MODE == "full" else (2,3),
    seeds=(42,43,44) if MODE == "full" else (42,43),
    max_iter=20 if MODE == "full" else 2,
)
topics, topic_tables, lda_audit = analyze_topics(split, OUTPUT_DIR, topic_config)
display(topic_tables["pemilihan_topik"].round(4))
print("K terpilih dari run ini:", lda_audit["selected_topics"])
print("Bentuk fitur LDA:", topics.train.shape, topics.validation.shape, topics.test.shape)
display(Image(filename=str(OUTPUT_DIR / "pemilihan_topik.png")))
display(trace.record("04 LDA", f"train={len(split.train)}, validation={len(split.validation)}", "fit count/LDA di train; seleksi validation", f"K={lda_audit['selected_topics']}; theta={topics.train.shape}"))
''')
section('05 · PROSES: pelajari dan interpretasikan keluaran LDA', 'Model dan topic_tables hasil section 04.', 'Baca bobot kata, contoh ulasan, diagnosis topik lemah.', 'Bahan interpretasi dan template_review_topik.csv.',
'''ID topik tidak otomatis berarti aspek atau sentimen. Isi nama topik secara manual setelah membaca contoh. Rerata cuaca adalah deskripsi, bukan hubungan sebab-akibat. Model LDA dipakai ulang; section ini tidak melatih LDA lagi.''')
code('''
display(topic_tables["topik_lda"])
display(topic_tables["kualitas_topik"])
display(topic_tables["contoh_ulasan_topik"])
display(Image(filename=str(OUTPUT_DIR / "kata_utama_topik.png")))
display(Image(filename=str(OUTPUT_DIR / "heatmap_topik_cuaca.png")))
print("Diagnosis:", lda_audit["diagnostics"])
''')
section('06 · PROSES: embedding FastText', 'Teks train dan seed yang sudah ditentukan.', 'Tokenisasi → skip-gram subword 3–6 → token IDs dan matriks embedding beku.', 'EncodedReviews per seed, fasttext.model, embedding_matrix.npy, token_ids.json.',
'''R07/R13: FastText dilatih **sekali per seed pada train**, lalu dipakai bersama oleh kedua ablation BiLSTM. Validation/test hanya di-encode dengan FastText beku; kata baru memakai subword. Penambahan ID token holdout hanya lookup vektor beku, bukan fit embedding. Mode full memakai tiga seed untuk variasi embedding+BiLSTM, bukan tiga split atau tiga dataset.''')
code('''
encoded_by_seed = {}
deep_configs = {}
training_seeds = (42,43,44) if MODE == "full" else (42,)
if RUN_DEEP:
    from wisata_madura.neural import DeepConfig, fit_fasttext, run_bilstm_variants, plot_training_history
    for training_seed in training_seeds:
        config = DeepConfig(seed=training_seed, bilstm_epochs=15 if MODE == "full" else 2,
                            patience=3 if MODE == "full" else 1, balance_destinations=True)
        deep_configs[training_seed] = config
        seed_dir = OUTPUT_DIR / "models" / f"seed_{training_seed}"
        encoded = fit_fasttext(split, config, seed_dir)
        encoded_by_seed[training_seed] = encoded
        print(f"Seed {training_seed}: token train={encoded.train_tokens.shape}; embedding={encoded.embeddings.shape}")
        print("Contoh 12 token IDs:", encoded.train_tokens[0, :12])
        print("PAD ID 0; embedding frozen; dimensi:", config.embedding_dim)
    display(trace.record("06 Embedding", f"{len(split.train)} ulasan train", "FastText train-only, satu kali per seed", f"{len(encoded_by_seed)} embedding beku"))
else:
    print("RUN_DEEP=False: embedding/BiLSTM dilewati; bukan eksperimen arsitektur lengkap.")
''')
section('07 · PROSES: modeling classifier dan ablation', 'Fitur LDA dan embedding beku; label train; validation untuk checkpoint.', 'Pembanding klasik + BiLSTM tanpa LDA + BiLSTM dengan concatenation LDA.', 'Prediksi test per seed/model (belum dievaluasi), riwayat loss, checkpoint terbaik.',
'''R08–R16: dua kepala klasifikasi (cuaca/jenis), dropout, Adam, clipping, early stopping. Bobot kelas dihitung dari **destinasi train**; bobot sampel mengimbangi jumlah ulasan per destinasi. Validation loss memakai bobot kelas train dan bobot unit destinasi validation. Ini mengurangi dominasi kelompok, bukan menjamin bebas bias. Pembanding klasik fit sekali, bukan diulang untuk menggandakan jumlah seed. Kedua ablation deep berbagi embedding dan partisi; checkpoint dipilih dari validation, tidak dari test.''')
code('''
from wisata_madura.modeling import run_baselines, run_lda_only, evaluate_classifiers

predictions_by_seed = {SEED: run_baselines(split, seed=SEED)}
predictions_by_seed[SEED].update(run_lda_only(split, topics, seed=SEED))
history_frames = []
if RUN_DEEP:
    for training_seed in training_seeds:
        seed_dir = OUTPUT_DIR / "models" / f"seed_{training_seed}"
        deep_predictions, history = run_bilstm_variants(
            split, topics, encoded_by_seed[training_seed], deep_configs[training_seed], seed_dir)
        predictions_by_seed.setdefault(training_seed, {}).update(deep_predictions)
        history.assign(seed=training_seed).to_csv(seed_dir / "riwayat_bilstm.csv", index=False)
        plot_training_history(history, seed_dir)
        history_frames.append(history.assign(seed=training_seed))
        display(pd.read_csv(seed_dir / "checkpoint_bilstm.csv"))
        display(Image(filename=str(seed_dir / "kurva_bilstm.png")))
    all_history = pd.concat(history_frames, ignore_index=True)
    all_history.to_csv(OUTPUT_DIR / "riwayat_bilstm_semua_seed.csv", index=False)
display(trace.record("07 Modeling", "LDA + embedding + label train/validation", "fit classifier, early stopping validation", f"seed/model: { {seed: list(p) for seed,p in predictions_by_seed.items()} }"))
''')
section('08 · OUTPUT: evaluasi test dan prediksi atribut', 'Prediksi semua model yang telah ditentukan; label test.', 'Accuracy/micro-F1/macro-F1/Hamming loss per ulasan dan destinasi; ringkasan semua seed.', 'Metrik, dukungan per kelas, prediksi CSV, perbandingan_model.png.',
'''Tidak memilih seed, split, K, atau arsitektur terbaik dari skor test. **Macro-F1 utama memakai seluruh kelas dataset** (kelas tanpa support test ikut bernilai nol); `macro_f1_present` hanya kelas yang muncul di test. Kolom jumlah kelas dan support wajib dibaca. Untuk satu label per atribut, micro-F1=accuracy dan Hamming loss=1−accuracy; bukan tiga bukti independen. Deep full: tiga seed, klasik: satu run; SD seed bukan confidence interval. Dengan hanya beberapa destinasi test dan kelas train-only, tidak ada klaim generalisasi semua kategori. Voting destinasi memakai mayoritas; seri diurutkan label, bukan diputuskan dengan label aktual.''')
code('''
from wisata_madura.reporting import export_predictions, summarize_seed_metrics
label_space = {target: sorted(reviews[target].unique()) for target in TARGETS}
metric_frames, detail_frames = [], []
for training_seed, predictions in predictions_by_seed.items():
    metrics, details = evaluate_classifiers(split.test, predictions, label_space=label_space)
    metric_frames.append(metrics.assign(seed=training_seed))
    detail_frames.append(details.assign(seed=training_seed))
    prediction_dir = OUTPUT_DIR / "predictions" / f"seed_{training_seed}"
    prediction_dir.mkdir(parents=True, exist_ok=True)
    export_predictions(split.test, predictions, prediction_dir)
metrics = pd.concat(metric_frames, ignore_index=True)
per_class = pd.concat(detail_frames, ignore_index=True)
metrics.to_csv(OUTPUT_DIR / "metrik_klasifikasi.csv", index=False)
per_class.to_csv(OUTPUT_DIR / "metrik_per_kelas.csv", index=False)
summary, figure = summarize_seed_metrics(metrics, OUTPUT_DIR)
display(summary.loc[summary.unit.eq("destinasi")].round(4))
display(figure)
plt.close(figure)
display(per_class.loc[per_class.unit.eq("destinasi")])
display(trace.record("08 Evaluasi", "prediksi tetap + label test", "nilai semua run; tidak memilih pemenang seed", f"{len(metrics)} baris metrik + prediksi CSV"))
''')
section('09 · OUTPUT: provenance, konfigurasi, dan unduhan', 'Audit, parameter, hash kode, seed, seluruh keluaran run.', 'Simpan manifest dan ringkasan kontrak Input–Proses–Output.', 'audit_dataset.json, daftar_output.txt, tabel alur, arsip ZIP.',
'''Folder keluaran smoke tidak boleh dikutip sebagai eksperimen penuh. BGE/Streamlit adalah tahap rekomendasi terpisah dari klasifikasi atribut pada notebook ini. Kualitas ranking memerlukan penilaian relevansi independen; skor klasifikasi tidak membuktikan kualitas rekomendasi.''')
code('''
from importlib.metadata import version
from wisata_madura.reporting import save_run_manifest, plot_pipeline_flow
import shutil
flow_figure = plot_pipeline_flow(reviews, split, lda_audit, next(iter(deep_configs.values()), None), OUTPUT_DIR)
display(flow_figure)
plt.close(flow_figure)
packages = ["numpy", "pandas", "scikit-learn", "openpyxl", "matplotlib"]
if RUN_DEEP:
    packages += ["gensim", "torch"]
audit.update(dict(pipeline_version="3.0", mode=MODE, run_deep=RUN_DEEP,
                  geography="Madura; owner-confirmed dataset", source_commit=source_commit, source_working_tree_dirty=source_dirty,
                  source_module_sha256=source_hashes, split=split.audit, lda=lda_audit,
                  deep_config={str(seed): asdict(config) for seed,config in deep_configs.items()},
                  packages={package: version(package) for package in packages},
                  metric_label_space=label_space))
display(pd.DataFrame(trace.rows))
files = save_run_manifest(OUTPUT_DIR, audit)
archive = shutil.make_archive(str(OUTPUT_DIR), "zip", root_dir=OUTPUT_DIR)
print("OUTPUT:", OUTPUT_DIR.resolve())
print("Arsip:", archive)
print("\\n".join(files))
# Opsional unduh di Google Colab:
# from google.colab import files
# files.download(archive)
''')

notebook = dict(cells=cells, metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
                language_info=dict(name='python'), colab=dict(provenance=[])), nbformat=4, nbformat_minor=5)
for i, cell in enumerate(cells):
    cell['id'] = f'section-{i:02d}'
path = ROOT/'notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb'
path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False)+'\n', encoding='utf-8')
legacy = dict(notebook, cells=[dict(cell_type='markdown', id='legacy-link', metadata={}, source=[
    '# Notebook utama sudah dipusatkan\n',
    'Gunakan [Colab v3 Input–Proses–Output](https://colab.research.google.com/github/MalikHariyanto/crispy_recom_machine_system/blob/feat/streamlit-wisata/notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb).\n',
    'Implementasi tidak diduplikasi di notebook ini agar pembaruan metode tetap konsisten.\n'])])
(ROOT/'notebooks/Colab_Audit_Wisata_Madura.ipynb').write_text(json.dumps(legacy, indent=1, ensure_ascii=False)+'\n')
print(path)
