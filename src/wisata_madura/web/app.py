"""Application shell: the bundled Madura dataset is loaded automatically."""
import streamlit as st

from .runtime import load_data, dataset_version
from .styles import apply_styles
from .views import explore, catalog_view, insights, about


def main():
    st.set_page_config(page_title="Madura Explore · Temukan perjalananmu", page_icon="🌿", layout="wide")
    apply_styles()
    try:
        catalog, audit = load_data()
    except (ValueError, OSError, KeyError):
        st.error("Dataset belum dapat dimuat. Pastikan folder data/ beserta manifest dan semua bagian CSV tersedia di repository.")
        st.stop()
    with st.sidebar:
        st.markdown("## Madura Explore")
        st.caption("WISATA · CERITA · PENEMUAN")
        st.divider()
        page = st.radio("Navigasi", ["Jelajahi", "Katalog destinasi", "Insight data", "Tentang"], label_visibility="collapsed")
        st.divider()
        st.markdown("**Destinasi wisata Madura**")
        st.caption(f"{len(catalog)} destinasi · {audit['rows']:,} ulasan")
        st.caption("Dataset dimuat otomatis. Langsung cari perjalanan yang sesuai minatmu.")
        st.divider()
        st.caption("Dikembangkan oleh Malik Hariyanto\n\nAsistensi Hibah Penelitian")
    if page == "Jelajahi":
        explore(catalog, dataset_version())
    elif page == "Katalog destinasi":
        catalog_view(catalog)
    elif page == "Insight data":
        insights(catalog, audit)
    else:
        about()
    st.markdown('<div class="footer">MADURA EXPLORE &nbsp; / &nbsp; Jelajahi dengan rasa ingin tahu. '
                'Rencanakan dengan informasi yang tepat.</div>', unsafe_allow_html=True)
