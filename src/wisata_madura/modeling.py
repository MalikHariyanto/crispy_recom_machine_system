"""04–05 · Model pembanding, distribusi topik LDA, dan metrik klasifikasi."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, hamming_loss
from sklearn.svm import LinearSVC

from .data import TARGETS, ReviewSplit

def _destination_class_weights(train, target):
    counts = train.drop_duplicates("id_destinasi")[target].value_counts()
    return (counts.sum() / (len(counts) * counts)).to_dict()



@dataclass
class TopicFeatures:
    train: np.ndarray
    test: np.ndarray
    keywords: pd.DataFrame
    weather_summary: pd.DataFrame
    sample_size: int
    validation: np.ndarray | None = None


def run_baselines(split: ReviewSplit, seed=42) -> dict:
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), min_df=2, max_features=40_000, sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b",
    )
    train_x = vectorizer.fit_transform(split.train["teks_model"])
    test_x = vectorizer.transform(split.test["teks_model"])
    predictions = {"mayoritas": {}, "tfidf_linear_svc": {}}
    from .protocol import destination_sample_weights
    sample_weights = destination_sample_weights(split.train)
    for target in TARGETS:
        models = {
            "mayoritas": DummyClassifier(strategy="most_frequent"),
            "tfidf_linear_svc": LinearSVC(class_weight=_destination_class_weights(split.train, target), random_state=seed),
        }
        for name, model in models.items():
            model.fit(train_x, split.train[target], sample_weight=sample_weights)
            predictions[name][target] = model.predict(test_x)
    return predictions


def run_lda_only(split: ReviewSplit, topics: TopicFeatures, seed=42) -> dict:
    from .protocol import destination_sample_weights
    predictions = {}
    for target in TARGETS:
        classifier = LogisticRegression(class_weight=_destination_class_weights(split.train, target), max_iter=500, random_state=seed)
        classifier.fit(topics.train, split.train[target], sample_weight=destination_sample_weights(split.train))
        predictions[target] = classifier.predict(topics.test)
    return {"lda_logreg": predictions}


def evaluate_classifiers(test: pd.DataFrame, predictions: dict, label_space=None) -> tuple[pd.DataFrame, pd.DataFrame]:
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
                labels = list(label_space[target]) if label_space is not None else sorted(set(actual) | set(predicted))
                key = {"target": target, "model": model, "unit": unit}
                summary.append({
                    **key,
                    "accuracy": accuracy_score(actual, predicted),
                    "micro_f1": f1_score(actual, predicted, average="micro"),
                    "macro_f1": f1_score(actual, predicted, labels=labels, average="macro", zero_division=0),
                    "macro_f1_present": f1_score(actual, predicted, labels=sorted(set(actual)), average="macro", zero_division=0),
                    "classes_observed": len(set(actual)),
                    "classes_evaluated": len(labels),
                    "hamming_loss": hamming_loss(actual, predicted),
                    "n": len(actual),
                })
                report = classification_report(
                    actual, predicted, labels=labels, output_dict=True, zero_division=0
                )
                details.extend({**key, "kelas": label, **report[label]} for label in labels)
    return pd.DataFrame(summary), pd.DataFrame(details)
