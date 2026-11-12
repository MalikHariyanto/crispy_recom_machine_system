"""FastText/BiLSTM: R07–R13 in docs/METODOLOGI_DAN_PAPER.md."""

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from sklearn.metrics import f1_score
from zlib import crc32

import numpy as np
import pandas as pd
from gensim.models import FastText
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence
from torch.utils.data import DataLoader, TensorDataset

from .data import TARGETS, ReviewSplit
from .modeling import TopicFeatures
from .protocol import destination_sample_weights


@dataclass(frozen=True)
class DeepConfig:
    seed: int = 42
    embedding_dim: int = 80
    fasttext_epochs: int = 5
    max_tokens: int = 64
    hidden_dim: int = 64
    batch_size: int = 128
    bilstm_epochs: int = 15
    patience: int = 3
    min_delta: float = 0.0001
    cpu_threads: int = 2
    learning_rate: float = 0.001
    balance_destinations: bool = True
    dropout: float = 0.2
    freeze_embeddings: bool = True


@dataclass
class EncodedReviews:
    train_tokens: np.ndarray
    test_tokens: np.ndarray
    embeddings: np.ndarray
    validation_tokens: np.ndarray | None = None


def _word_hash(word):
    return crc32(word.encode("utf-8"))


def fit_fasttext(split: ReviewSplit, config: DeepConfig, output_dir=None) -> EncodedReviews:
    train_words = [text.split() for text in split.train["teks_model"]]
    test_words = [text.split() for text in split.test["teks_model"]]
    model = FastText(
        vector_size=config.embedding_dim,
        window=5,
        min_count=2,
        sg=1,
        min_n=3,
        max_n=6,
        bucket=100_000,
        workers=1,
        seed=config.seed,
        hashfxn=_word_hash,
        epochs=config.fasttext_epochs,
    )
    model.build_vocab(corpus_iterable=train_words)
    if not model.wv.key_to_index:
        raise ValueError("Korpus latih terlalu kecil untuk kosakata FastText dengan min_count=2.")
    model.train(corpus_iterable=train_words, total_examples=model.corpus_count, epochs=config.fasttext_epochs)

    # ID nol dipakai untuk padding. Token baru memperoleh vektor subword dari
    # model latih yang sudah dibekukan, termasuk saat token muncul di data uji.
    vectors = [np.zeros(config.embedding_dim, dtype=np.float32)]
    word_ids = {}

    def encode(documents):
        encoded = np.zeros((len(documents), config.max_tokens), dtype=np.int32)
        for row, words in enumerate(documents):
            for col, word in enumerate(words[:config.max_tokens]):
                if word not in word_ids:
                    word_ids[word] = len(vectors)
                    vectors.append(model.wv.get_vector(word))
                encoded[row, col] = word_ids[word]
        return encoded

    train_tokens = encode(train_words)
    validation_tokens = encode([text.split() for text in split.validation.teks_model]) if hasattr(split, 'validation') else None
    test_tokens = encode(test_words)
    embeddings = np.asarray(vectors, dtype=np.float32)
    if output_dir is not None:
        output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
        model.save(str(output / 'fasttext.model'))
        np.save(output / 'embedding_matrix.npy', embeddings)
        (output / 'token_ids.json').write_text(json.dumps(word_ids, ensure_ascii=False), encoding='utf-8')
    return EncodedReviews(train_tokens, test_tokens, embeddings, validation_tokens)


class ReviewBiLSTM(nn.Module):
    """Representasi urutan bersama dengan satu kepala prediksi per atribut."""

    def __init__(self, embeddings, class_counts, hidden_dim, topic_dim, dropout=0.2, freeze_embeddings=True):
        super().__init__()
        self.embedding = nn.Embedding.from_pretrained(
            torch.from_numpy(embeddings).clone(), freeze=freeze_embeddings, padding_idx=0
        )
        self.sequence = nn.LSTM(
            embeddings.shape[1], hidden_dim, batch_first=True, bidirectional=True
        )
        self.dropout = nn.Dropout(dropout)
        self.topic_dim = topic_dim
        self.heads = nn.ModuleDict({
            name: nn.Linear(2 * hidden_dim + topic_dim, count)
            for name, count in class_counts.items()
        })

    def forward(self, tokens, lengths, topics):
        embedded = self.embedding(tokens)
        packed = pack_padded_sequence(embedded, lengths, batch_first=True, enforce_sorted=False)
        _, (hidden, _) = self.sequence(packed)
        features = torch.cat((hidden[-2], hidden[-1]), dim=1)
        if self.topic_dim:
            features = torch.cat((features, topics), dim=1)
        features = self.dropout(features)
        return {name: head(features) for name, head in self.heads.items()}


def _balanced_loss(encoded_labels, n_classes, device):
    counts = np.bincount(encoded_labels, minlength=n_classes)
    weights = len(encoded_labels) / (n_classes * counts)
    return nn.CrossEntropyLoss(weight=torch.as_tensor(weights, dtype=torch.float32, device=device), reduction="none")


def _features(tokens, topics):
    lengths = np.count_nonzero(tokens, axis=1).astype(np.int64)
    return torch.from_numpy(tokens), torch.from_numpy(lengths), torch.from_numpy(topics)


def run_bilstm_variants(
    split, topics: TopicFeatures, encoded: EncodedReviews, config: DeepConfig, output_dir=None,
) -> tuple[dict, pd.DataFrame]:
    """Pilih checkpoint dari validation loss; test baru diprediksi setelah checkpoint dipulihkan."""
    if (not hasattr(split, 'validation') or topics.validation is None
            or encoded.validation_tokens is None):
        raise ValueError('Gunakan validation_split dan notebook terbaru sebelum pelatihan BiLSTM.')
    if config.bilstm_epochs < 1 or config.patience < 1 or config.min_delta < 0:
        raise ValueError('Epoch/patience harus positif dan min_delta nonnegatif.')
    torch.set_num_threads(config.cpu_threads)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    labels = {target: sorted(split.train[target].unique()) for target in TARGETS}

    def encode_labels(frame):
        values = np.column_stack([
            pd.Categorical(frame[target], categories=labels[target]).codes for target in TARGETS
        ]).astype(np.int64)
        if (values < 0).any():
            raise ValueError('Ada label validation yang tidak dipelajari dari train.')
        return values

    train_y, val_y = encode_labels(split.train), encode_labels(split.validation)
    representative = ~split.train.id_destinasi.duplicated().to_numpy()
    losses = {target: _balanced_loss(train_y[representative, i] if config.balance_destinations else train_y[:, i],
                                    len(labels[target]), device)
              for i, target in enumerate(TARGETS)}
    def sample_weights(frame):
        values = destination_sample_weights(frame) if config.balance_destinations else np.ones(len(frame))
        return torch.as_tensor(values, dtype=torch.float32)
    train_set = TensorDataset(*_features(encoded.train_tokens, topics.train), torch.from_numpy(train_y), sample_weights(split.train))
    val_set = TensorDataset(*_features(encoded.validation_tokens, topics.validation), torch.from_numpy(val_y), sample_weights(split.validation))
    test_set = TensorDataset(*_features(encoded.test_tokens, topics.test))
    val_loader = DataLoader(val_set, batch_size=config.batch_size)
    test_loader = DataLoader(test_set, batch_size=config.batch_size)
    predictions, history, checkpoints = {}, [], []

    for variant, topic_dim in {'fasttext_bilstm': 0, 'fasttext_lda_bilstm': topics.train.shape[1]}.items():
        torch.manual_seed(config.seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        generator = torch.Generator().manual_seed(config.seed)
        loader = DataLoader(train_set, batch_size=config.batch_size, shuffle=True, generator=generator)
        model = ReviewBiLSTM(encoded.embeddings, {t: len(v) for t, v in labels.items()},
                             config.hidden_dim, topic_dim, config.dropout, config.freeze_embeddings).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
        best_loss, best_epoch, best_state, stale = float('inf'), 0, None, 0
        for epoch in range(1, config.bilstm_epochs + 1):
            model.train(); total_loss = 0.0
            for tokens, lengths, batch_topics, target_ids, sample_weight in loader:
                optimizer.zero_grad()
                logits = model(tokens.to(device, dtype=torch.long), lengths, batch_topics.to(device))
                target_ids = target_ids.to(device)
                loss = torch.stack([(losses[target](logits[target], target_ids[:, i]) * sample_weight.to(device)).mean()
                                    for i, target in enumerate(TARGETS)]).mean()
                if not torch.isfinite(loss):
                    raise RuntimeError('Loss pelatihan tidak finite; periksa data dan parameter.')
                loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); optimizer.step()
                total_loss += loss.item() * len(tokens)
            model.eval(); val_total = 0.0
            outputs = {target: [] for target in TARGETS}
            with torch.inference_mode():
                for tokens, lengths, batch_topics, target_ids, sample_weight in val_loader:
                    logits = model(tokens.to(device, dtype=torch.long), lengths, batch_topics.to(device))
                    target_ids = target_ids.to(device)
                    loss = torch.stack([(losses[t](logits[t], target_ids[:, i]) * sample_weight.to(device)).mean()
                                        for i, t in enumerate(TARGETS)]).mean()
                    val_total += loss.item() * len(tokens)
                    for t in TARGETS: outputs[t].extend(logits[t].argmax(dim=1).cpu().tolist())
            val_loss = val_total / len(val_set)
            improved = val_loss < best_loss - config.min_delta
            if improved:
                best_loss, best_epoch, stale = val_loss, epoch, 0
                best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            else: stale += 1
            row = dict(model=variant, epoch=epoch, train_loss=total_loss / len(train_set),
                       validation_loss=val_loss, checkpoint_improved=improved, device=device.type)
            for i, t in enumerate(TARGETS):
                row['validation_macro_f1_' + t] = f1_score(
                    val_y[:, i], outputs[t], labels=list(range(len(labels[t]))),
                    average='macro', zero_division=0)
            history.append(row)
            print(f"{variant} | epoch {epoch}/{config.bilstm_epochs} | "
                  f"train={row['train_loss']:.4f} | validation={val_loss:.4f}", flush=True)
            if stale >= config.patience:
                print(f'Early stopping; best epoch={best_epoch}', flush=True); break
        if best_state is None:
            raise RuntimeError('Tidak ada checkpoint valid; periksa loss NaN/infinity.')
        model.load_state_dict(best_state); model.eval()
        outputs = {target: [] for target in TARGETS}
        with torch.inference_mode():
            for tokens, lengths, batch_topics in test_loader:
                logits = model(tokens.to(device, dtype=torch.long), lengths, batch_topics.to(device))
                for target in TARGETS:
                    codes = logits[target].argmax(dim=1).cpu().numpy()
                    outputs[target].extend(np.asarray(labels[target])[codes])
        predictions[variant] = {target: np.asarray(values) for target, values in outputs.items()}
        checkpoints.append(dict(model=variant, best_epoch=best_epoch, best_validation_loss=best_loss,
                                epochs_executed=epoch, device=device.type))
        if output_dir is not None:
            output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
            torch.save(dict(state_dict=best_state, labels=labels, config=asdict(config),
                            topic_dim=topic_dim, best_epoch=best_epoch), output / f'{variant}.pt')
    if output_dir is not None:
        pd.DataFrame(checkpoints).to_csv(Path(output_dir) / 'checkpoint_bilstm.csv', index=False)
    return predictions, pd.DataFrame(history)


def plot_training_history(history, output_dir):
    import matplotlib.pyplot as plt
    variants = history.model.drop_duplicates().tolist()
    fig, axes = plt.subplots(1, len(variants), figsize=(6 * len(variants), 4), squeeze=False, layout='constrained')
    for ax, variant in zip(axes.ravel(), variants):
        frame = history.loc[history.model.eq(variant)]
        ax.plot(frame.epoch, frame.train_loss, 'o-', label='Train')
        ax.plot(frame.epoch, frame.validation_loss, 's-', label='Validation')
        ax.set(title=variant, xlabel='Epoch', ylabel='Weighted loss'); ax.legend()
    fig.savefig(Path(output_dir) / 'kurva_bilstm.png', dpi=160); plt.close(fig)
