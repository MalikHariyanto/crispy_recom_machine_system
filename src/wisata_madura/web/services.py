"""Pure, independently testable web services; no Streamlit or training imports."""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from wisata_madura.recommendation import COMPATIBLE, build_catalog


class SearchIndex:
    """One shared, immutable TF-IDF index; requests only transform their query."""

    def __init__(self, catalog):
        self.catalog = catalog.reset_index(drop=True).copy()
        self.vectorizer = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), max_features=30000)
        self.vectors = self.vectorizer.fit_transform(self.catalog.deskripsi)

    def search(self, preference, candidates, k=6, excluded=()):
        if not preference.strip():
            raise ValueError("Tulis preferensi perjalanan terlebih dahulu.")
        eligible = self.catalog.id_destinasi.isin(candidates) & ~self.catalog.id_destinasi.isin(excluded)
        positions = np.flatnonzero(eligible.to_numpy())
        query = self.vectorizer.transform([preference.strip()])
        scores = linear_kernel(query, self.vectors[positions]).ravel() if len(positions) else np.array([])
        # Zero overlap is not evidence of relevance; never invent a ranking for it.
        order = np.argsort(-scores, kind="stable")
        order = order[scores[order] > 0][:k]
        return self.catalog.iloc[positions[order]].assign(skor_kemiripan=scores[order]).reset_index(drop=True)


def make_catalog(reviews):
    catalog = build_catalog(reviews, reviews_per_destination=12)
    counts = reviews.groupby("id_destinasi").size().rename("jumlah_ulasan")
    return catalog.join(counts, on="id_destinasi")


def filter_catalog(catalog, season="", types=(), name=""):
    mask = pd.Series(True, index=catalog.index)
    if season:
        mask &= catalog.rekomendasi_cuaca.str.casefold().map(lambda label: season.casefold() in COMPATIBLE.get(label, set()))
    if types:
        mask &= catalog.wisata.isin(types)
    if name.strip():
        mask &= catalog.destinasi.str.contains(name.strip(), case=False, regex=False)
    return catalog.loc[mask].copy()
