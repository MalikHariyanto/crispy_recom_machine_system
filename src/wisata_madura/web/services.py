"""Pure, independently testable web services; no Streamlit or training imports."""
from io import BytesIO

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from wisata_madura.data import MADURA_DISTRICTS
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


def read_regions(content, known_ids):
    mapping = pd.read_csv(BytesIO(content), dtype=str, keep_default_na=False)
    if not {"id_destinasi", "kabupaten"}.issubset(mapping):
        raise ValueError("CSV harus memiliki kolom id_destinasi dan kabupaten.")
    mapping = mapping[["id_destinasi", "kabupaten"]].apply(lambda c: c.str.strip())
    if mapping.id_destinasi.eq("").any() or mapping.id_destinasi.duplicated().any():
        raise ValueError("Setiap ID harus terisi dan unik.")
    if set(mapping.id_destinasi) - set(known_ids):
        raise ValueError("Ada ID yang tidak ditemukan dalam dataset.")
    canonical = {s.casefold(): s for s in (*MADURA_DISTRICTS, "Di luar Madura", "")}
    if set(mapping.kabupaten.str.casefold()) - set(canonical):
        raise ValueError("Kabupaten harus Bangkalan, Sampang, Pamekasan, Sumenep, Di luar Madura, atau kosong.")
    mapping["kabupaten"] = mapping.kabupaten.str.casefold().map(canonical)
    return mapping


def filter_catalog(catalog, season="", types=(), name="", verified_only=False, districts=()):
    mask = pd.Series(True, index=catalog.index)
    if season:
        mask &= catalog.rekomendasi_cuaca.str.casefold().map(lambda label: season.casefold() in COMPATIBLE.get(label, set()))
    if types:
        mask &= catalog.wisata.isin(types)
    if name.strip():
        mask &= catalog.destinasi.str.contains(name.strip(), case=False, regex=False)
    if verified_only:
        mask &= catalog.kabupaten.isin(MADURA_DISTRICTS)
    if districts:
        mask &= catalog.kabupaten.isin(districts)
    return catalog.loc[mask].copy()
