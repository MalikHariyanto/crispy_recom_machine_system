"""Small output helpers shared by notebook stages; no training side effects."""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd

from .data import TARGETS


class StageTrace:
    def __init__(self, output):
        self.output = Path(output)
        self.rows = []

    def record(self, section, inputs, process, outputs):
        self.rows.append(dict(section=section, input=inputs, proses=process, output=outputs))
        table = pd.DataFrame(self.rows)
        table.to_csv(self.output/'alur_input_proses_output.csv', index=False)
        return table.tail(1)


def export_predictions(test, predictions, output):
    frames = []
    for model, heads in predictions.items():
        frame = test[['id_destinasi', 'destinasi', *TARGETS]].copy()
        for target in TARGETS:
            frame['prediksi_'+target] = heads[target]
        frame['model'] = model
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    result.to_csv(Path(output)/'prediksi_test.csv', index=False)
    return result


def summarize_seed_metrics(metrics, output):
    keys = ['model', 'target', 'unit']
    summary = metrics.groupby(keys).agg(
        runs=('seed','nunique'), macro_f1_mean=('macro_f1','mean'),
        macro_f1_std=('macro_f1','std'), accuracy_mean=('accuracy','mean'),
        hamming_loss_mean=('hamming_loss','mean'), n=('n','first'),
    ).reset_index()
    summary.to_csv(Path(output)/'ringkasan_metrik_seed.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(14,5), layout='constrained')
    for ax, target in zip(axes, TARGETS):
        part = summary.loc[summary.target.eq(target) & summary.unit.eq('destinasi')]
        ax.barh(part.model, part.macro_f1_mean, xerr=part.macro_f1_std.fillna(0), color='#167C66', capsize=3)
        ax.set(title=target, xlabel='Macro-F1 (seluruh kelas; rerata ± SD seed)', xlim=(0,1))
    fig.savefig(Path(output)/'perbandingan_model.png', dpi=160, bbox_inches='tight')
    return summary, fig


def save_run_manifest(output, metadata):
    output = Path(output)
    (output/'audit_dataset.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    files = sorted(p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and '.matplotlib' not in p.parts)
    (output/'daftar_output.txt').write_text('\n'.join(files), encoding='utf-8')
    return files


def plot_pipeline_flow(reviews, split, lda_audit, deep_config, output):
    """Render the input/process/output diagram from this run's real metadata."""
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(12, 11), layout='constrained')
    ax.set(xlim=(0,100), ylim=(-3,108)); ax.axis('off')
    def box(x,y,w,h,text,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.5',
                                   linewidth=1.3,edgecolor='#356859',facecolor=color))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=11,linespacing=1.6)
    def arrow(a,b):
        ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#356859','lw':1.5})
    ax.text(50,105,'INPUT → PROSES → OUTPUT',ha='center',fontsize=19,fontweight='bold',color='#153e35')
    box(10,91,80,9,f'INPUT: teks ulasan + dua label atribut\n{len(reviews):,} ulasan / {reviews.id_destinasi.nunique()} destinasi Madura','#EAF3ED')
    arrow((50,90),(50,84))
    box(10,75,80,9,'PROSES: audit, normalisasi, deduplikasi\nRating hanya untuk eksplorasi; bukan fitur classifier','#FFF2D9')
    arrow((50,74),(50,68))
    counts=' | '.join(f'{name}: {len(frame):,} ulasan / {frame.id_destinasi.nunique()} ID'
                     for name,frame in [('Train',split.train),('Val',split.validation),('Test',split.test)])
    box(5,58,90,10,'Split kelompok ID destinasi\n'+counts,'#FFF2D9')
    arrow((35,57),(26,51)); arrow((65,57),(74,51))
    k=lda_audit['selected_topics']
    box(4,30,44,21,f'LDA (fit train saja)\nCountVectorizer → pencarian K / seed\nSeleksi NPMI validation → K={k}\nKeluaran: distribusi topik ({k} fitur)','#FFF2D9')
    embedding = (f'FastText (fit train saja)\nSkip-gram + subword 3–6\nEmbedding {deep_config.embedding_dim} dimensi, frozen\nToken IDs + matriks embedding'
                 if deep_config else 'Embedding/BiLSTM dilewati\nRUN_DEEP=False')
    box(52,30,44,21,embedding,'#FFF2D9')
    arrow((26,29),(40,24)); arrow((74,29),(60,24))
    model = (f'MODELING: BiLSTM ({deep_config.hidden_dim} hidden/arah) + concatenation LDA\nDua kepala klasifikasi: cuaca / jenis wisata\nCheckpoint validation; ablation dengan/tanpa LDA'
             if deep_config else 'MODELING: pembanding mayoritas, TF-IDF+SVC, LDA+logreg')
    box(6,12,88,12,model,'#FFF2D9')
    arrow((50,11),(50,7))
    box(6,-1,88,8,'OUTPUT: prediksi atribut test, metrik + support per kelas\nGrafik, analisis topik, checkpoint, audit, dan ZIP','#EAF3ED')
    path=Path(output)/'alur_pipeline.png'
    fig.savefig(path,dpi=160,bbox_inches='tight',facecolor='white')
    return fig
