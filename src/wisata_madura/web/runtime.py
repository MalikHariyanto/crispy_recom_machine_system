"""Cache boundaries keyed by dataset version, not only application code."""
import hashlib
from pathlib import Path
import streamlit as st

from wisata_madura.data import load_bundled_reviews, audit_bundled_reviews
from .services import make_catalog, SearchIndex

ROOT = Path(__file__).resolve().parents[3]


def dataset_version():
    return hashlib.sha256((ROOT / "data/manifest.json").read_bytes()).hexdigest()


@st.cache_data(show_spinner="Menyiapkan katalog wisata…", max_entries=2)
def _load_data(version):
    reviews, manifest = load_bundled_reviews(ROOT / "data")
    return make_catalog(reviews), audit_bundled_reviews(reviews, manifest)


def load_data():
    return _load_data(dataset_version())


@st.cache_resource(show_spinner="Menyiapkan mesin pencarian…", max_entries=2)
def _lexical_index(version):
    catalog, _ = _load_data(version)
    return SearchIndex(catalog)


def lexical_index():
    return _lexical_index(dataset_version())


@st.cache_resource(show_spinner="Memuat BGE-M3. Unduhan pertama dapat memerlukan beberapa menit…", max_entries=1)
def _semantic_index(version):
    from wisata_madura.recommendation import BGERecommender
    catalog, _ = _load_data(version)
    return BGERecommender.from_pretrained(catalog)


def semantic_index():
    return _semantic_index(dataset_version())
