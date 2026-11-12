"""Generate the separate exploratory tuning notebook."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
main=json.loads((ROOT/'notebooks/Colab_Audit_Wisata_Madura_Otomatis.ipynb').read_text())
setup=''.join(main['cells'][2]['source'])
cells=[]
def add(kind,text):
 cell=dict(cell_type=kind,metadata={},id=f'tuning-{len(cells)}',source=text.strip().splitlines(keepends=True))
 if kind=='code':cell.update(execution_count=None,outputs=[])
 cells.append(cell)
add('markdown','''# Tuning kelompok destinasi — eksplorasi terdaftar

**Tujuan:** memilih konfigurasi menggunakan validation kelompok; evaluasi independen menunggu data baru.

Dataset 27 destinasi yang pernah digunakan pada eksperimen sebelumnya diperlakukan seluruhnya sebagai **development**. Membagi ulang data yang sama tidak menjadikannya independen kembali. Tidak ada nilai yang disebut final test accuracy di notebook ini.

Alur: input → tetapkan protokol/fold → LDA train-only → embedding train-only → kandidat BiLSTM → ringkasan validation → konfigurasi terpilih → evaluasi eksternal ditunda.

Kelas satu destinasi selalu train-only; tabel cakupan mengungkap kelas yang tidak bisa dievaluasi. Tiga fold dipakai berulang untuk memilih K, checkpoint, dan hiperparameter, sehingga skor validation adalah diagnostik seleksi yang optimistis, bukan estimasi tanpa bias. [Protokol](../docs/TUNING_PROTOCOL.md).''')
add('markdown','## 00 · Setup\n\nInput: repository dan mode. Proses: instalasi. Output: modul, folder run, hash. Gunakan runtime Colab baru. MODE full menjalankan pencarian yang ditetapkan; smoke hanya memeriksa alur.')
setup=setup.replace('hasil_wisata_madura_v3','tuning_kelompok_madura').replace('wisata_madura_v3','wisata_madura_tuning')
add('code',setup)
add('markdown','## 01 · Input development dan protokol sebelum tuning\n\nData dimuat otomatis. Rasio fold/seed/kandidat dan objective disimpan sebelum fitting. Jangan mengganti protokol setelah membaca skor untuk mengklaim evaluasi independen.')
add('code','''import pandas as pd
from IPython.display import display
from wisata_madura.data import load_reviews
if not RUN_DEEP:
    raise ValueError('Tuning memerlukan RUN_DEEP=True dan dependensi deep learning.')
from wisata_madura.tuning import TuningConfig, CANDIDATES, grouped_folds, run_grouped_tuning

manifest=json.loads((repo_root/'data/manifest.json').read_text())
source=repo_root/'data/source'/manifest['source_workbook']
if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['source_workbook_sha256']:
    raise ValueError('Checksum workbook tidak cocok')
reviews=load_reviews(source)
config=TuningConfig() if MODE=='full' else TuningConfig(training_seeds=(42,), max_epochs=2, patience=1, lda_topics=(2,3), lda_iterations=2)
candidates=CANDIDATES if MODE=='full' else CANDIDATES[:1]
folds,assignment=grouped_folds(reviews,config)
display(pd.DataFrame(candidates))
display(assignment)
for i,(train,valid) in enumerate(folds):
    print(f'Fold {i}: train={len(train)} ulasan/{train.id_destinasi.nunique()} ID; validation={len(valid)} ulasan/{valid.id_destinasi.nunique()} ID')
print('Objective: mean destination macro-F1 kedua target, seluruh fold dan seed.')
print('Kelas singleton train-only; hasil ini bukan final test estimate.')''')
add('markdown','''## 02 · Proses tuning kelompok

Pada setiap fold: LDA dan kosakata fit train; K dipilih pada validation. Panjang urutan ditentukan dari kuantil teks train (dibatasi 16–128 token). FastText fit sekali per kombinasi embedding/panjang/seed lalu dipakai ulang. Dua varian BiLSTM menerima salinan embedding awal; fine-tuning tidak mengubah cache atau inisialisasi ablation berikutnya.

Empat kandidat membandingkan kapasitas, regularisasi, learning rate, dan frozen/fine-tuning. Ini pencarian terbatas, bukan bukti optimum global. Parameter tidak diubah berdasarkan skor setelah pencarian ini. Semua percobaan dan checkpoint dicatat, termasuk yang buruk.''')
add('code','''from dataclasses import asdict
print(asdict(config))
summary,selected=run_grouped_tuning(reviews, OUTPUT_DIR/'search', config, candidates)
display(summary.sort_values('validation_macro_f1_mean',ascending=False))
print(json.dumps(selected,indent=2))''')
add('markdown','''## 03 · Output dan batas kesimpulan

Konfigurasi pemenang hanya terbaik dalam kandidat yang diuji menurut objective validation. Pembanding baseline tetap dicantumkan meski lebih baik daripada kandidat deep. Nilai rerata ± SD fold/seed bukan confidence interval. Kelas train-only tidak punya bukti generalisasi. Checkpoint fold bukan model final refit seluruh data.

Simpan protokol dan jangan menamai skor seleksi ini sebagai independent test. Bandingkan seluruh skor dan cakupan kelas, bukan seed terbaik saja.''')
add('code','''display(pd.read_csv(OUTPUT_DIR/'search/class_coverage.csv'))
display(pd.read_csv(OUTPUT_DIR/'search/checkpoints.csv'))
print('Independent evaluation: PENDING. Deployment ready:',selected['deployment_ready'])
import shutil
archive=shutil.make_archive(str(OUTPUT_DIR),'zip',root_dir=OUTPUT_DIR)
print('Output:',OUTPUT_DIR,'| ZIP:',archive)''')
add('markdown','''## 04 · Evaluasi independen (belum dijalankan)

Kumpulkan ulasan dari destinasi baru setelah protokol/model ditetapkan. Jangan menyalin baris, mengganti ID, atau membagi ulang data lama lalu menyebutnya independen. Simpan asal/tanggal pengumpulan; validator hanya memeriksa overlap, bukan membuktikan provenance independen.

Langkah berikutnya adalah membekukan konfigurasi, menentukan aturan refit/epoch dari development, melatih model final, dan baru membuka label evaluasi eksternal. Belum ada data baru pada eksperimen ini, sehingga tidak dibuat skor independen atau model deployment otomatis.''')
add('code','''# Jalankan hanya setelah tersedia dataset BARU dan protokol model final dibekukan:
# from wisata_madura.tuning import validate_independent_data
# external=load_reviews(Path('/content/data_evaluasi_baru.xlsx'))
# validate_independent_data(reviews,external)
# Lolos pemeriksaan overlap belum berarti evaluasi sudah dilakukan.
print('Tidak ada dataset independen yang digunakan atau dinilai pada notebook tuning ini.')''')
notebook=dict(cells=cells,metadata=main['metadata'],nbformat=4,nbformat_minor=5)
(ROOT/'notebooks/Colab_Tuning_Kelompok_Madura.ipynb').write_text(json.dumps(notebook,indent=1,ensure_ascii=False)+'\n')
