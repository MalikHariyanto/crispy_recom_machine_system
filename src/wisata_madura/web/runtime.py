"""Cache boundaries: load once, index once, keep user filters request-local."""
from pathlib import Path
import streamlit as st

from wisata_madura.data import load_bundled_reviews, audit_bundled_reviews
from .services import make_catalog, SearchIndex

ROOT = Path(__file__).resolve().parents[3]


@st.cache_data(show_spinner="Menyiapkan katalog wisata…")
def load_data():
    reviews, manifest = load_bundled_reviews(ROOT / "data")
    return make_catalog(reviews), audit_bundled_reviews(reviews, manifest)


@st.cache_resource(show_spinner="Menyiapkan mesin pencarian…")
def lexical_index():
    catalog, _ = load_data()
    return SearchIndex(catalog)


@st.cache_resource(show_spinner="Memuat BGE-M3. Unduhan pertama dapat memerlukan beberapa menit…")
def semantic_index():
    from wisata_madura.recommendation import BGERecommender
    catalog, _ = load_data()
    return BGERecommender.from_pretrained(catalog)
