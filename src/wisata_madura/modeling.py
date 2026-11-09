"""04–05 · Model pembanding, distribusi topik LDA, dan metrik klasifikasi."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, hamming_loss
from sklearn.svm import LinearSVC

from .data import TARGETS, ReviewSplit


@dataclass
class TopicFeatures:
    train: np.ndarray
    test: np.ndarray
    keywords: pd.DataFrame
    weather_summary: pd.DataFrame
    sample_size: int


def run_baselines(split: ReviewSplit, seed=42) -> dict:
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), min_df=2, max_features=40_000, sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b",
    )
    train_x = vectorizer.fit_transform(split.train["teks_model"])
    test_x = vectorizer.transform(split.test["teks_model"])
    predictions = {"mayoritas": {}, "tfidf_linear_svc": {}}
    for target in TARGETS:
        models = {
            "mayoritas": DummyClassifier(strategy="most_frequent"),
            "tfidf_linear_svc": LinearSVC(class_weight="balanced", random_state=seed),
        }
        for name, model in models.items():
            model.fit(train_x, split.train[target])
            predictions[name][target] = model.predict(test_x)
    return predictions


def fit_topics(split: ReviewSplit, n_topics=6, per_destination=30, seed=42) -> TopicFeatures:
    # Model bersama menjaga arti tiap dimensi topik tetap sama untuk semua data.
    sample = (
        split.train.sample(frac=1, random_state=seed).groupby("id_destinasi", sort=False)
        .head(per_destination).reset_index(drop=True)
    )
    counts = CountVectorizer(min_df=3, max_features=4_000, token_pattern=r"(?u)\b\w\w+\b")
    sample_counts = counts.fit_transform(sample["teks_model"])
    model = LatentDirichletAllocation(
        n_components=n_topics, max_iter=8, learning_method="online", random_state=seed
    )
    sample_weights = model.fit_transform(sample_counts)
    terms = counts.get_feature_names_out()
    names = [f"topik_{i + 1}" for i in range(n_topics)]
    keywords = pd.DataFrame({
        "topik": names,
        "kata_utama": [", ".join(terms[np.argsort(row)[-8:][::-1]]) for row in model.components_],
    })
    by_destination = (
        pd.DataFrame(sample_weights, columns=names)
        .assign(id_destinasi=sample["id_destinasi"], rekomendasi_cuaca=sample["rekomendasi_cuaca"])
        .groupby(["id_destinasi", "rekomendasi_cuaca"])[names].mean()
    )
    return TopicFeatures(
        train=model.transform(counts.transform(split.train["teks_model"])).astype(np.float32),
        test=model.transform(counts.transform(split.test["teks_model"])).astype(np.float32),
        keywords=keywords,
        weather_summary=by_destination.groupby("rekomendasi_cuaca")[names].mean(),
        sample_size=len(sample),
    )


def run_lda_only(split: ReviewSplit, topics: TopicFeatures, seed=42) -> dict:
    predictions = {}
    for target in TARGETS:
        classifier = LogisticRegression(class_weight="balanced", max_iter=500, random_state=seed)
        classifier.fit(topics.train, split.train[target])
        predictions[target] = classifier.predict(topics.test)
    return {"lda_logreg": predictions}


def evaluate_classifiers(test: pd.DataFrame, predictions: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary, details = [], []
    for model, outputs in predictions.items():
        for target in TARGETS:
            per_destination = (
                test[["id_destinasi", target]].assign(prediksi=outputs[target])
                .groupby("id_destinasi")
                .agg(aktual=(target, "first"), prediksi=("prediksi", lambda s: s.mode().iloc[0]))
            )
            evaluations = (
                ("ulasan", test[target], outputs[target]),
                ("destinasi", per_destination["aktual"], per_destination["prediksi"]),
            )
            for unit, actual, predicted in evaluations:
                labels = sorted(set(actual))
                key = {"target": target, "model": model, "unit": unit}
                summary.append({
                    **key,
                    "accuracy": accuracy_score(actual, predicted),
                    "micro_f1": f1_score(actual, predicted, average="micro"),
                    "macro_f1": f1_score(actual, predicted, labels=labels, average="macro", zero_division=0),
                    "hamming_loss": hamming_loss(actual, predicted),
                    "n": len(actual),
                })
                report = classification_report(
                    actual, predicted, labels=labels, output_dict=True, zero_division=0
                )
                details.extend({**key, "kelas": label, **report[label]} for label in labels)
    return pd.DataFrame(summary), pd.DataFrame(details)
