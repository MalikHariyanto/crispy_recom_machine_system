"""06–07 · FastText dan BiLSTM dengan keluaran terpisah untuk tiap target."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class DeepConfig:
    seed: int = 42
    embedding_dim: int = 80
    fasttext_epochs: int = 5
    max_tokens: int = 64
    hidden_dim: int = 64
    batch_size: int = 128
    bilstm_epochs: int = 5
    learning_rate: float = 0.001


@dataclass
class EncodedReviews:
    train_tokens: np.ndarray
    test_tokens: np.ndarray
    embeddings: np.ndarray


def _word_hash(word):
    return crc32(word.encode("utf-8"))


def fit_fasttext(split: ReviewSplit, config: DeepConfig) -> EncodedReviews:
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
    test_tokens = encode(test_words)
    return EncodedReviews(train_tokens, test_tokens, np.asarray(vectors, dtype=np.float32))


class ReviewBiLSTM(nn.Module):
    """Representasi urutan bersama dengan satu kepala prediksi per atribut."""

    def __init__(self, embeddings, class_counts, hidden_dim, topic_dim):
        super().__init__()
        self.embedding = nn.Embedding.from_pretrained(
            torch.from_numpy(embeddings), freeze=True, padding_idx=0
        )
        self.sequence = nn.LSTM(
            embeddings.shape[1], hidden_dim, batch_first=True, bidirectional=True
        )
        self.dropout = nn.Dropout(0.2)
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
    return nn.CrossEntropyLoss(weight=torch.as_tensor(weights, dtype=torch.float32, device=device))


def _features(tokens, topics):
    lengths = np.count_nonzero(tokens, axis=1).astype(np.int64)
    return torch.from_numpy(tokens), torch.from_numpy(lengths), torch.from_numpy(topics)


def run_bilstm_variants(
    split: ReviewSplit, topics: TopicFeatures, encoded: EncodedReviews, config: DeepConfig,
) -> tuple[dict, pd.DataFrame]:
    """Latih dua varian pada partisi sama. Data uji hanya dipakai untuk prediksi."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    labels = {target: sorted(split.train[target].unique()) for target in TARGETS}
    train_y = np.column_stack([
        pd.Categorical(split.train[target], categories=labels[target]).codes for target in TARGETS
    ]).astype(np.int64)
    losses = {
        target: _balanced_loss(train_y[:, i], len(labels[target]), device)
        for i, target in enumerate(TARGETS)
    }
    train_set = TensorDataset(*_features(encoded.train_tokens, topics.train), torch.from_numpy(train_y))
    test_set = TensorDataset(*_features(encoded.test_tokens, topics.test))
    test_loader = DataLoader(test_set, batch_size=config.batch_size)
    predictions, history = {}, []
    variants = {"fasttext_bilstm": 0, "fasttext_lda_bilstm": topics.train.shape[1]}

    for variant, topic_dim in variants.items():
        torch.manual_seed(config.seed)
        generator = torch.Generator().manual_seed(config.seed)
        loader = DataLoader(train_set, batch_size=config.batch_size, shuffle=True, generator=generator)
        model = ReviewBiLSTM(
            encoded.embeddings, {target: len(values) for target, values in labels.items()},
            config.hidden_dim, topic_dim,
        ).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
        for epoch in range(1, config.bilstm_epochs + 1):
            model.train()
            total_loss = 0.0
            for tokens, lengths, batch_topics, target_ids in loader:
                optimizer.zero_grad()
                logits = model(tokens.to(device, dtype=torch.long), lengths, batch_topics.to(device))
                target_ids = target_ids.to(device)
                loss = torch.stack([
                    losses[target](logits[target], target_ids[:, i])
                    for i, target in enumerate(TARGETS)
                ]).mean()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                total_loss += loss.item() * len(tokens)
            avg_loss = total_loss / len(train_set)
            history.append({"model": variant, "epoch": epoch, "train_loss": avg_loss, "device": device.type})
            print(f"{variant} | epoch {epoch}/{config.bilstm_epochs} | loss latih {avg_loss:.4f}")

        model.eval()
        outputs = {target: [] for target in TARGETS}
        with torch.inference_mode():
            for tokens, lengths, batch_topics in test_loader:
                logits = model(tokens.to(device, dtype=torch.long), lengths, batch_topics.to(device))
                for target in TARGETS:
                    codes = logits[target].argmax(dim=1).cpu().numpy()
                    outputs[target].extend(np.asarray(labels[target])[codes])
        predictions[variant] = {target: np.asarray(values) for target, values in outputs.items()}

    return predictions, pd.DataFrame(history)
