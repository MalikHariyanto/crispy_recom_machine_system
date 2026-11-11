"""LDA: R01–R05 in docs/METODOLOGI_DAN_PAPER.md; adaptations stated there."""
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS

from .modeling import TopicFeatures

# Daftar eksplisit dan tersimpan di audit. Pertahankan negasi untuk interpretasi.
ID_STOPWORDS = frozenset('''yang dan di ke dari ini itu untuk dengan pada adalah ada
juga saya aku kami kita mereka anda nya sih dong deh kok lah pun atau karena
sebagai dalam oleh sudah akan masih jadi saja aja kalau jika maka saat ketika
setelah sebelum hingga sampai setiap para sebuah suatu tersebut yaitu yakni
sini sana disini disana kesini kesana sangat banget sekali lebih paling cukup
bisa dapat buat bagi menurut tentang atas antara bersama melalui selama'''.split())
STOPWORDS = sorted((ID_STOPWORDS | ENGLISH_STOP_WORDS) - {'tidak', 'bukan', 'belum', 'jangan', 'kurang', 'no', 'not', 'nor'})


@dataclass(frozen=True)
class TopicConfig:
    topic_counts: tuple = (2, 4, 6, 8, 10, 12)
    seeds: tuple = (42, 43, 44)
    per_destination: int = 30
    max_features: int = 4000
    min_df: int = 3
    max_iter: int = 20
    top_words: int = 10
    examples_per_topic: int = 5


def top_word_ids(model, top_n):
    return [np.argsort(row)[-top_n:][::-1] for row in model.components_]


def document_npmi(counts, word_ids):
    """Rerata NPMI pasangan kata berdasarkan kehadiran per dokumen, bukan c_v.

    Pasangan yang tidak pernah muncul bersama diberi -1. Pasangan yang selalu
    bersama di seluruh dokumen diberi 0 (tidak informatif). Rentang [-1, 1].
    """
    binary = (counts > 0).astype(np.float64).tocsc()
    n_docs = counts.shape[0]
    if not n_docs:
        raise ValueError('Tidak ada dokumen untuk coherence.')
    result = []
    for ids in word_ids:
        x = binary[:, ids]
        freq = np.asarray(x.sum(axis=0)).ravel()
        joint = (x.T @ x).toarray()
        scores = []
        for i, j in combinations(range(len(ids)), 2):
            p12 = joint[i, j] / n_docs
            if p12 == 0:
                score = -1.0
            elif p12 == 1:
                score = 0.0
            else:
                score = np.log(p12 / ((freq[i] / n_docs) * (freq[j] / n_docs))) / -np.log(p12)
            scores.append(score)
        result.append(float(np.mean(scores)) if scores else -1.0)
    return np.asarray(result)


def topic_stability(left, right):
    """Jaccard top-word sets, matched optimally to ignore topic numbering."""
    if len(left) != len(right) or not left:
        raise ValueError('Stability memerlukan jumlah topik sama dan tidak kosong.')
    similarities = np.array([
        [len(set(a) & set(b)) / len(set(a) | set(b)) for b in right] for a in left
    ])
    rows, columns = linear_sum_assignment(-similarities)
    return float(similarities[rows, columns].mean())


def _sample(frame, config, seed):
    return (frame.sample(frac=1, random_state=seed)
            .groupby('id_destinasi', sort=False).head(config.per_destination).reset_index(drop=True))


def analyze_topics(split, output_dir, config=None):
    config = config or TopicConfig()
    if (not config.topic_counts or any(k < 2 for k in config.topic_counts)
            or len(set(config.seeds)) < 2 or len(set(config.topic_counts)) != len(config.topic_counts)
            or config.top_words < 2 or config.max_iter < 1):
        raise ValueError('Gunakan K unik >=2, >=2 seed unik, top_words>=2, dan max_iter>=1.')
    for frame in (split.validation, split.test):
        if not set(split.train.id_destinasi).isdisjoint(frame.id_destinasi):
            raise ValueError('LDA: ID destinasi train bertumpang tindih.')
        if not set(split.train.teks_model).isdisjoint(frame.teks_model):
            raise ValueError('LDA: teks train bertumpang tindih.')
    output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    train_sample = _sample(split.train, config, config.seeds[0])
    valid_sample = _sample(split.validation, config, config.seeds[0])
    vectorizer = CountVectorizer(
        min_df=config.min_df, max_df=0.90, max_features=config.max_features,
        stop_words=STOPWORDS, token_pattern=r'(?u)\b[^\W\d_]{2,}\b',
    )
    train_x = vectorizer.fit_transform(train_sample.teks_model)
    valid_x = vectorizer.transform(valid_sample.teks_model)
    nonempty = np.asarray(valid_x.sum(axis=1)).ravel() > 0
    if train_x.shape[1] < config.top_words or not nonempty.any():
        raise ValueError('Kosakata/validation terlalu kecil; tinjau min_df, top_words, dan data.')
    rows, models, words = [], {}, {}
    for k in config.topic_counts:
        for seed in config.seeds:
            model = LatentDirichletAllocation(
                n_components=k, max_iter=config.max_iter, learning_method='online',
                random_state=seed, n_jobs=1,
            ).fit(train_x)
            ids = top_word_ids(model, config.top_words)
            coherence = document_npmi(valid_x, ids)
            row = dict(n_topics=k, seed=seed, validation_npmi=float(coherence.mean()),
                       validation_perplexity=float(model.perplexity(valid_x[nonempty])),
                       topic_diversity=len(set(np.concatenate(ids))) / (k * config.top_words),
                       iterations=int(model.n_iter_))
            rows.append(row); models[k, seed] = model; words[k, seed] = ids
            print(f"LDA K={k}, seed={seed}: validation NPMI={row['validation_npmi']:.4f}, "
                  f"perplexity={row['validation_perplexity']:.1f}", flush=True)
    trials = pd.DataFrame(rows)
    selection = trials.groupby('n_topics').agg(
        validation_npmi_mean=('validation_npmi', 'mean'),
        validation_npmi_std=('validation_npmi', 'std'),
        validation_perplexity_mean=('validation_perplexity', 'mean'),
        topic_diversity_mean=('topic_diversity', 'mean'),
    ).reset_index()
    selection['stability_jaccard'] = [
        np.mean([topic_stability(words[k, a], words[k, b]) for a, b in combinations(config.seeds, 2)])
        for k in selection.n_topics
    ]
    selection = selection.sort_values(
        ['validation_npmi_mean', 'stability_jaccard', 'validation_perplexity_mean', 'n_topics'],
        ascending=[False, False, True, True], kind='stable',
    ).reset_index(drop=True)
    selected_k = int(selection.iloc[0].n_topics)
    # Seed utama ditetapkan sebelum pencarian; hindari memilih seed yang kebetulan baik.
    model = models[selected_k, config.seeds[0]]
    ids = words[selected_k, config.seeds[0]]
    terms = vectorizer.get_feature_names_out()
    names = [f'topik_{i + 1}' for i in range(selected_k)]
    keyword_table = pd.DataFrame({'topik': names, 'kata_utama': [', '.join(terms[w]) for w in ids]})
    train_weights = model.transform(train_x)
    quality = keyword_table.assign(
        validation_npmi=document_npmi(valid_x, ids),
        rata_rata_bobot_train=train_weights.mean(axis=0),
        dokumen_dominan_train=np.bincount(train_weights.argmax(axis=1), minlength=selected_k),
    )
    word_weights = model.components_ / model.components_.sum(axis=1, keepdims=True)
    word_table = pd.DataFrame([
        dict(topik=names[i], kata=terms[j], probabilitas=float(word_weights[i, j]), urutan=r + 1)
        for i, group in enumerate(ids) for r, j in enumerate(group)
    ])
    examples = []
    for i, name in enumerate(names):
        # Hanya dokumen yang topik dominannya cocok, sehingga topik lemah bisa <5 contoh.
        dominant = np.flatnonzero(train_weights.argmax(axis=1) == i)
        order = dominant[np.argsort(-train_weights[dominant, i], kind='stable')]
        for row in order[:config.examples_per_topic]:
            r = train_sample.iloc[row]
            examples.append(dict(topik=name, bobot=float(train_weights[row, i]),
                                 id_destinasi=r.id_destinasi, destinasi=r.destinasi,
                                 teks_model=r.teks_model, asal='train_sample'))
    examples = pd.DataFrame(examples)
    document_topics = train_sample[['id_destinasi', 'destinasi']].join(pd.DataFrame(train_weights, columns=names))
    weather_summary = (document_topics.assign(rekomendasi_cuaca=train_sample.rekomendasi_cuaca)
                       .groupby(['id_destinasi', 'rekomendasi_cuaca'])[names].mean()
                       .groupby('rekomendasi_cuaca').mean())
    features = TopicFeatures(
        train=model.transform(vectorizer.transform(split.train.teks_model)).astype(np.float32),
        validation=model.transform(vectorizer.transform(split.validation.teks_model)).astype(np.float32),
        test=model.transform(vectorizer.transform(split.test.teks_model)).astype(np.float32),
        keywords=keyword_table, weather_summary=weather_summary, sample_size=len(train_sample),
    )
    audit = dict(config=asdict(config), selected_topics=selected_k, selected_seed=config.seeds[0],
                 selection_rule='highest mean validation document NPMI; ties stability, perplexity, smaller K',
                 coherence_definition='document-level NPMI; unseen pair=-1; not c_v or sliding-window NPMI',
                 train_sample_reviews=len(train_sample), validation_sample_reviews=len(valid_sample),
                 validation_zero_vocabulary_reviews=int((~nonempty).sum()),
                 vocabulary_size=len(terms), stopwords=STOPWORDS,
                 fit_scope='train sample only; no validation/test fitting; no test model selection',
                 interpretation='Human review required; topic ID is not a validated aspect or sentiment label')
    audit['diagnostics'] = {
        'negative_npmi_topics': quality.loc[quality.validation_npmi.lt(0), 'topik'].tolist(),
        'selected_k_at_grid_boundary': selected_k in (min(config.topic_counts), max(config.topic_counts)),
        'stability_jaccard': float(selection.iloc[0].stability_jaccard),
        'note': 'Relative best within this grid only; human interpretation is still required.',
    }
    tables = {'pencarian_lda': trials, 'pemilihan_topik': selection, 'topik_lda': keyword_table,
              'kualitas_topik': quality, 'bobot_kata_topik': word_table, 'contoh_ulasan_topik': examples,
              'distribusi_topik_dokumen_latih': document_topics,
              'ringkasan_topik_per_label_cuaca': weather_summary.reset_index()}
    for name, table in tables.items(): table.to_csv(output / f'{name}.csv', index=False)
    # Hasil review tidak diisi dengan nama aspek yang diasumsikan benar.
    quality.assign(nama_topik_review='', catatan_review='').to_csv(output / 'template_review_topik.csv', index=False)
    (output / 'audit_lda.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding='utf-8')
    joblib.dump({'vectorizer': vectorizer, 'model': model, 'config': asdict(config)}, output / 'model_lda.joblib')
    plot_topic_analysis(selection, word_table, weather_summary, output)
    return features, tables, audit


def plot_topic_analysis(selection, words, weather, output):
    import matplotlib.pyplot as plt
    output = Path(output)
    ordered = selection.sort_values('n_topics')
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), layout='constrained')
    axes[0].errorbar(ordered.n_topics, ordered.validation_npmi_mean,
                     yerr=ordered.validation_npmi_std, marker='o', capsize=4)
    axes[0].set(title='Coherence validation (document NPMI)', xlabel='Jumlah topik', ylabel='Rerata ± SD antar-seed')
    axes[1].plot(ordered.n_topics, ordered.validation_perplexity_mean, 'o-')
    axes[1].set(title='Perplexity validation', xlabel='Jumlah topik', ylabel='Lebih rendah lebih baik')
    axes[2].plot(ordered.n_topics, ordered.stability_jaccard, 'o-', label='Stability Jaccard')
    axes[2].plot(ordered.n_topics, ordered.topic_diversity_mean, 's-', label='Diversity')
    axes[2].set(xlabel='Jumlah topik', ylim=(0, 1)); axes[2].legend()
    fig.savefig(output / 'pemilihan_topik.png', dpi=160); plt.close(fig)
    names = words.topik.drop_duplicates().tolist()
    fig, axes = plt.subplots((len(names) + 1) // 2, 2, figsize=(12, 3 * ((len(names) + 1) // 2)), squeeze=False, layout='constrained')
    for ax, name in zip(axes.ravel(), names):
        frame = words.loc[words.topik.eq(name)].sort_values('probabilitas')
        ax.barh(frame.kata, frame.probabilitas); ax.set(title=name, xlabel='P(kata | topik)')
    for ax in axes.ravel()[len(names):]: ax.set_visible(False)
    fig.savefig(output / 'kata_utama_topik.png', dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(max(8, len(names)), 3), layout='constrained')
    im = ax.imshow(weather.to_numpy(), aspect='auto', vmin=0, vmax=max(0.01, weather.to_numpy().max()), cmap='YlGnBu')
    ax.set_xticks(range(len(names)), names, rotation=45, ha='right')
    ax.set_yticks(range(len(weather)), weather.index)
    ax.set_title('Rerata bobot topik per atribut cuaca — deskriptif pada train sample')
    fig.colorbar(im, ax=ax, label='Bobot topik')
    fig.savefig(output / 'heatmap_topik_cuaca.png', dpi=160); plt.close(fig)
