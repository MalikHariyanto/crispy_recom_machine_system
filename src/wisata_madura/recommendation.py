"""09 · Katalog, pemeringkatan BGE, dan evaluasi jika penilaian tersedia."""

import numpy as np
import pandas as pd


MODEL_NAME = "BAAI/bge-m3"
REQUIRED_JUDGMENTS = ("query_id", "preferensi", "musim", "id_destinasi")
COMPATIBLE = {
    "kemarau": {"kemarau"},
    "kemarau & penghujan": {"kemarau", "penghujan"},
}


def build_catalog(data: pd.DataFrame, reviews_per_destination=5) -> pd.DataFrame:
    columns = ["id_destinasi", "destinasi", "wisata", "rekomendasi_cuaca"]
    catalog = data[columns].drop_duplicates("id_destinasi").sort_values("id_destinasi")
    snippets = (
        data.loc[data["teks_model"].ne(""), ["id_destinasi", "teks_model"]]
        .drop_duplicates()
        .groupby("id_destinasi", sort=False).head(reviews_per_destination)
        .assign(teks_model=lambda d: d["teks_model"].str.slice(0, 160))
        .groupby("id_destinasi")["teks_model"].agg(" | ".join)
    )
    catalog = catalog.join(snippets.rename("cuplikan"), on="id_destinasi").fillna({"cuplikan": ""})
    catalog["deskripsi"] = (
        catalog["destinasi"] + ". Jenis wisata " + catalog["wisata"]
        + ". Kecocokan cuaca " + catalog["rekomendasi_cuaca"] + ". " + catalog["cuplikan"]
    )
    return catalog.drop(columns="cuplikan").reset_index(drop=True)


class BGERecommender:
    def __init__(self, catalog: pd.DataFrame, encoder):
        if catalog.empty:
            raise ValueError("Katalog destinasi kosong.")
        self.catalog = catalog.reset_index(drop=True)
        self.encoder = encoder
        self.weather = self.catalog["rekomendasi_cuaca"].str.casefold()
        unknown = set(self.weather) - set(COMPATIBLE)
        if unknown:
            raise ValueError(f"Kategori kecocokan cuaca belum dipetakan: {sorted(unknown)}")
        self.vectors = self._encode(self.catalog["deskripsi"].tolist())

    @classmethod
    def from_pretrained(cls, catalog, model_name=MODEL_NAME):
        from sentence_transformers import SentenceTransformer

        return cls(catalog, SentenceTransformer(model_name))

    def _encode(self, text):
        return self.encoder.encode(
            text, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
        )

    def recommend(self, preferensi: str, musim="", k=5, riwayat_ids=()) -> pd.DataFrame:
        preference = preferensi.strip()
        season = musim.strip().casefold()
        if not preference or k < 1:
            raise ValueError("Isi preferensi dan gunakan k minimal 1.")
        if season not in {"", "kemarau", "penghujan"}:
            raise ValueError("Musim dapat dikosongkan atau diisi Kemarau/Penghujan.")

        history_ids = list(dict.fromkeys(map(str, riwayat_ids)))
        history = self.catalog.set_index("id_destinasi")
        missing = set(history_ids) - set(history.index)
        if missing:
            raise ValueError(f"ID riwayat tidak ada dalam katalog: {sorted(missing)}")
        if history_ids:
            visited = history.loc[history_ids[-3:]]
            past_preferences = visited["destinasi"] + " (" + visited["wisata"] + ")"
            preference += ". Riwayat kunjungan: " + ", ".join(past_preferences)

        eligible = ~self.catalog["id_destinasi"].isin(history_ids)
        if season:
            eligible &= self.weather.map(lambda label: season in COMPATIBLE[label])
        candidate_ids = np.flatnonzero(eligible.to_numpy())
        scores = self.vectors[candidate_ids] @ self._encode([preference])[0]
        order = np.argsort(-scores, kind="stable")[:k]
        columns = ["id_destinasi", "destinasi", "wisata", "rekomendasi_cuaca"]
        return (
            self.catalog.iloc[candidate_ids[order]][columns]
            .assign(skor_kemiripan=scores[order])
            .reset_index(drop=True)
        )


def evaluate_recommendations(recommender: BGERecommender, judgments: pd.DataFrame, k=5) -> pd.DataFrame:
    """Hitung Precision@K dan Recall@K dari ID relevan yang dinilai secara independen."""
    missing = set(REQUIRED_JUDGMENTS) - set(judgments.columns)
    if missing:
        raise ValueError(f"Kolom penilaian belum tersedia: {sorted(missing)}")
    data = judgments[list(REQUIRED_JUDGMENTS)].fillna("").astype(str).apply(lambda col: col.str.strip())
    if data.empty or data[["query_id", "preferensi", "id_destinasi"]].eq("").any().any():
        raise ValueError("Penilaian kosong atau memiliki ID/preferensi yang kosong.")
    unknown = set(data["id_destinasi"]) - set(recommender.catalog["id_destinasi"])
    if unknown:
        raise ValueError(f"ID relevan tidak ada di katalog: {sorted(unknown)[:8]}")

    rows = []
    for query_id, group in data.groupby("query_id", sort=False):
        for field in ("preferensi", "musim"):
            if group[field].nunique() != 1:
                raise ValueError(f"Penilaian {query_id} memiliki {field} yang berbeda.")
        example = group.iloc[0]
        relevant = set(group["id_destinasi"])
        ranking = recommender.recommend(example["preferensi"], example["musim"], k=k)
        hits = len(set(ranking["id_destinasi"]) & relevant)
        rows.append({
            "query_id": query_id, "k": k, "precision_at_k": hits / k,
            "recall_at_k": hits / len(relevant), "relevant_count": len(relevant),
            "recommended_count": len(ranking),
        })
    return pd.DataFrame(rows)
