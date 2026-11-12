"""Application shell and session-local geographic scope."""
import hashlib

import pandas as pd
import streamlit as st

from wisata_madura.data import MADURA_DISTRICTS
from .runtime import load_data, dataset_version
from .services import filter_catalog, read_regions
from .styles import apply_styles
from .views import explore, catalog_view, insights, about, csv_download


def main():
    st.set_page_config(page_title="Madura Explore · Temukan perjalananmu", page_icon="🌿", layout="wide")
    apply_styles()
    try:
        catalog, audit = load_data()
    except (ValueError, OSError, KeyError):
        st.error("Dataset belum dapat dimuat. Pastikan folder data/ beserta manifest dan semua bagian CSV ikut diunggah.")
        st.stop()
    with st.sidebar:
        st.markdown("## Madura Explore")
        st.caption("WISATA · CERITA · PENEMUAN")
        st.divider()
        page = st.radio("Navigasi", ["Jelajahi", "Katalog destinasi", "Insight data", "Tentang"], label_visibility="collapsed")
        st.divider()
        st.markdown("**Cakupan destinasi**")
        upload = st.file_uploader("CSV verifikasi wilayah", type=["csv"], help="Kolom: id_destinasi, kabupaten. Maksimal 5 MB.")
        region_hash = "bundled"
        catalog = catalog.assign(kabupaten="Belum diverifikasi")
        has_mapping = False
        if upload is not None:
            try:
                content = upload.getvalue()
                mapping = read_regions(content, catalog.id_destinasi)
                catalog = catalog.drop(columns="kabupaten").merge(mapping, on="id_destinasi", how="left")
                catalog["kabupaten"] = catalog.kabupaten.fillna("").replace("", "Belum diverifikasi")
                region_hash = hashlib.sha256(content).hexdigest()
                has_mapping = True
                st.success(f"{catalog.kabupaten.isin(MADURA_DISTRICTS).sum()} destinasi Madura terverifikasi")
            except (ValueError, UnicodeError, pd.errors.ParserError):
                st.error("CSV wilayah tidak valid. Gunakan template dengan ID unik dan nama kabupaten yang sesuai.")
                # Never silently fall back to unverified results after an invalid upload.
                st.stop()
        verified = st.toggle("Hanya Madura terverifikasi", disabled=not has_mapping)
        districts = st.multiselect("Kabupaten", MADURA_DISTRICTS, disabled=not has_mapping, placeholder="Semua kabupaten")
        template = catalog[["id_destinasi", "destinasi"]].assign(kabupaten="")
        with st.expander("Panduan verifikasi wilayah"):
            st.caption("Isi kabupaten dengan Bangkalan, Sampang, Pamekasan, Sumenep, Di luar Madura, atau kosong. "
                       "Periksa lokasi terlebih dahulu; nama tempat saja belum cukup untuk verifikasi.")
            csv_download(template, "Unduh template CSV", "verifikasi_wilayah.csv", "region_template")
        st.divider()
        st.caption("Dikembangkan oleh Malik Hariyanto\n\nAsistensi Hibah Penelitian")
    scope_key = (dataset_version(), region_hash, verified, tuple(sorted(districts)))
    scoped = filter_catalog(catalog, verified_only=verified, districts=districts)
    if page != "Tentang":
        if not verified and not districts:
            st.caption("CAKUPAN DATASET SUMBER · Mencakup lokasi di luar Madura. Gunakan CSV wilayah untuk memverifikasi cakupan.")
        else:
            st.caption("CAKUPAN TERVERIFIKASI · Berdasarkan CSV wilayah yang diunggah pada sesi ini.")
    if scoped.empty and page != "Tentang":
        st.info("Belum ada destinasi dalam cakupan ini. Lengkapi verifikasi wilayah atau ubah filter kabupaten.")
    elif page == "Jelajahi":
        explore(scoped, scope_key)
    elif page == "Katalog destinasi":
        catalog_view(scoped)
    elif page == "Insight data":
        insights(scoped, audit)
    else:
        about()
    st.markdown('<div class="footer">MADURA EXPLORE &nbsp; / &nbsp; Jelajahi dengan rasa ingin tahu. '
                'Rencanakan dengan informasi yang tepat.</div>', unsafe_allow_html=True)
