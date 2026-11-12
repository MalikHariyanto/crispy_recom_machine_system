"""SISRE: a single search-first recommendation screen."""
import streamlit as st

from .runtime import load_data, dataset_version
from .styles import apply_styles, masthead
from .views import explore


def main():
    st.set_page_config(page_title="SISRE · Wisata Madura", page_icon="🌊", layout="wide")
    apply_styles()
    try:
        catalog, _ = load_data()
        version = dataset_version()
    except (ValueError, OSError, KeyError):
        st.error("Wisata belum bisa dimuat. Coba lagi sebentar.")
        st.stop()
    masthead(len(catalog))
    explore(catalog, version)
    st.markdown('<footer class="sisre-footer"><strong>SISRE</strong><span>Wisata Madura</span></footer>', unsafe_allow_html=True)
