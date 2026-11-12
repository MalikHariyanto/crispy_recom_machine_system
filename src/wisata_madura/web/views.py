"""UI composition. All searches operate on the same shared catalog index."""
from html import escape
from importlib.util import find_spec
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

from .runtime import lexical_index, semantic_index
from .services import filter_catalog
from .styles import hero


def csv_download(data, label, filename, key):
    st.download_button(label, data.to_csv(index=False).encode("utf-8-sig"), filename,
                       "text/csv", key=key, width="stretch")


def destination_card(row, rank=None):
    with st.container(border=True):
        if rank is not None:
            st.markdown(f'<div class="rank">PILIHAN {rank:02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{escape(str(row.destinasi))}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="tag">{escape(str(row.wisata))}</span>'
                    f'<span class="tag">{escape(str(row.rekomendasi_cuaca))}</span>', unsafe_allow_html=True)
        st.caption(f"{int(row.jumlah_ulasan):,} ulasan dalam dataset · {row.kabupaten}")
        if rank is not None:
            st.caption(f"Skor kemiripan: {row.skor_kemiripan:.3f} · bukan rating kualitas")
        with st.expander("Lihat cuplikan ulasan"):
            # Catalog descriptions include normalized review text, not editorial copy.
            snippets = row.deskripsi.split(". ", 3)[-1].split(" | ")[:3]
            st.caption("Teks ulasan yang sudah diproses; ejaan mengikuti dataset.")
            for text in snippets:
                st.write(text)
        st.link_button("Cari di Google Maps ↗", "https://www.google.com/maps/search/?api=1&query=" + quote_plus(row.destinasi),
                       width="stretch")


def card_grid(data, ranked=False):
    for start in range(0, len(data), 3):
        columns = st.columns(3)
        for col, (index, row) in zip(columns, data.iloc[start:start + 3].iterrows()):
            with col:
                destination_card(row, index + 1 if ranked else None)


def explore(catalog, scope_key):
    hero()
    metrics = st.columns(3)
    metrics[0].metric("Destinasi dalam cakupan", f"{len(catalog):,}")
    metrics[1].metric("Ulasan wisatawan", f"{catalog.jumlah_ulasan.sum():,}")
    metrics[2].metric("Kategori wisata", catalog.wisata.nunique())
    st.write("")
    st.subheader("Mau perjalanan seperti apa?")
    st.caption("Ceritakan suasana, aktivitas, atau nama tempat yang ingin kamu temukan.")
    with st.form("search"):
        preference = st.text_input("Preferensi perjalanan", placeholder="Contoh: pantai pasir putih untuk bersantai bersama keluarga",
                                   max_chars=800)
        a, b, c = st.columns([1, 1.4, 1])
        season = a.selectbox("Musim perjalanan", ["Semua musim", "Kemarau", "Penghujan"])
        types = b.multiselect("Jenis wisata", sorted(catalog.wisata.unique()), placeholder="Semua kategori")
        k = c.select_slider("Jumlah rekomendasi", [3, 6, 9, 12], value=6)
        with st.expander("Personalisasi & metode pencarian"):
            names = dict(zip(catalog.id_destinasi, catalog.destinasi))
            visited = st.multiselect("Destinasi yang sudah dikunjungi (dikeluarkan dari hasil)", list(names),
                                    format_func=lambda x: names[x], placeholder="Pilih destinasi yang pernah dikunjungi")
            methods = ["TF-IDF · pencocokan kata"]
            if find_spec("sentence_transformers"):
                methods.append("BGE-M3 · pencarian semantik")
            method = st.selectbox("Metode", methods)
            st.caption("TF-IDF mencocokkan kata dalam nama, jenis wisata, dan cuplikan ulasan. "
                       "BGE-M3 tersedia bila dependensi semantik dipasang oleh pengelola.")
        submitted = st.form_submit_button("Temukan destinasi →", type="primary", width="stretch")
    if submitted:
        if not preference.strip():
            st.warning("Tulis preferensi perjalanan terlebih dahulu.")
        else:
            eligible = filter_catalog(catalog, season="" if season == "Semua musim" else season, types=types)
            try:
                if method.startswith("BGE"):
                    with st.spinner("Mencocokkan preferensi dengan destinasi…"):
                        engine = semantic_index()
                        excluded = set(engine.catalog.id_destinasi) - set(eligible.id_destinasi)
                        result = engine.recommend(preference, "" if season == "Semua musim" else season,
                                                  k, sorted(excluded | set(visited)))
                        result = result.merge(catalog[["id_destinasi", "deskripsi", "jumlah_ulasan", "kabupaten"]], on="id_destinasi")
                else:
                    result = lexical_index().search(preference, eligible.id_destinasi, k, visited)
                    result = result.merge(catalog[["id_destinasi", "kabupaten"]], on="id_destinasi")
                st.session_state["search_result"] = (scope_key, preference, method, result)
            except (ValueError, OSError, ImportError, RuntimeError):
                st.session_state.pop("search_result", None)
                st.error("Pencarian belum berhasil. Coba TF-IDF atau periksa ketersediaan model BGE pada server.")
    saved = st.session_state.get("search_result")
    if saved and saved[0] == scope_key:
        _, query, method, result = saved
        st.subheader("Pilihan untuk perjalananmu")
        st.write(f'Preferensi: “{query}”')
        st.caption(f"{len(result)} hasil · {method} · urutan berdasarkan kemiripan teks")
        if result.empty:
            st.info("Belum ada hasil yang cocok. Gunakan kata lain atau longgarkan filter jenis wisata dan musim.")
        else:
            card_grid(result, ranked=True)
            csv_download(result.drop(columns="deskripsi"), "Unduh hasil rekomendasi", "rekomendasi_wisata.csv", "ranking_csv")
    else:
        st.subheader("Mulai menjelajah")
        st.caption("Pratinjau katalog, diurutkan berdasarkan jumlah ulasan; bukan peringkat rekomendasi.")
        card_grid(catalog.sort_values(["jumlah_ulasan", "destinasi"], ascending=[False, True]).head(3).reset_index(drop=True))


def catalog_view(catalog):
    st.markdown('<div class="eyebrow">DESTINATION DIRECTORY</div>', unsafe_allow_html=True)
    st.title("Katalog destinasi")
    st.write("Kenali pilihan tempat dan telusuri ulasan sebelum menentukan perjalanan.")
    a, b, c = st.columns([2, 1, 1])
    name = a.text_input("Cari nama destinasi", placeholder="Ketik nama tempat…")
    types = b.multiselect("Kategori wisata", sorted(catalog.wisata.unique()), placeholder="Semua kategori")
    season = c.selectbox("Kecocokan musim", ["Semua", "Kemarau", "Penghujan"])
    filtered = filter_catalog(catalog, season="" if season == "Semua" else season, types=types, name=name)
    sort = st.selectbox("Urutkan", ["Ulasan terbanyak", "Nama A–Z"])
    filtered = filtered.sort_values(["jumlah_ulasan", "destinasi"], ascending=[False, True]) if sort == "Ulasan terbanyak" else filtered.sort_values("destinasi")
    st.caption(f"{len(filtered)} destinasi ditemukan")
    if filtered.empty:
        st.info("Tidak ada destinasi untuk filter ini. Coba nama atau kategori lain.")
        return
    pages = max(1, (len(filtered) + 8) // 9)
    page = st.selectbox("Halaman", range(1, pages + 1), format_func=lambda x: f"{x} dari {pages}")
    card_grid(filtered.iloc[(page - 1) * 9:page * 9].reset_index(drop=True))
    cols = ["id_destinasi", "destinasi", "wisata", "rekomendasi_cuaca", "jumlah_ulasan", "kabupaten"]
    csv_download(filtered[cols], "Unduh katalog sesuai filter", "katalog_wisata.csv", "catalog_csv")


def insights(catalog, audit):
    st.markdown('<div class="eyebrow">DATA OBSERVATORY</div>', unsafe_allow_html=True)
    st.title("Di balik rekomendasi")
    st.write("Ringkasan data untuk memahami cakupan dan batas rekomendasi.")
    a, b, c = st.columns(3)
    a.metric("Destinasi dalam cakupan", len(catalog))
    b.metric("Ulasan dalam cakupan", f"{catalog.jumlah_ulasan.sum():,}")
    c.metric("Median ulasan / destinasi", f"{catalog.jumlah_ulasan.median():.0f}" if len(catalog) else "0")
    a, b = st.columns(2)
    with a:
        st.subheader("Jenis destinasi")
        st.bar_chart(catalog.groupby("wisata").size().rename("Destinasi"), color="#167C66", horizontal=True)
    with b:
        st.subheader("Kecocokan cuaca")
        st.bar_chart(catalog.groupby("rekomendasi_cuaca").size().rename("Destinasi"), color="#A3B878", horizontal=True)
    st.subheader("Kualitas dataset sumber")
    st.caption("Angka berikut dihitung dari seluruh dataset bawaan, sebelum filter wilayah.")
    quality = pd.DataFrame({"Indikator": ["Ulasan sumber", "Baris duplikat persis", "Teks model kosong", "Tanggal relatif", "Indikasi masalah encoding"],
                            "Jumlah": [audit["rows"], audit["exact_duplicate_rows"], audit["empty_normalized_text_rows"],
                                       audit["relative_date_rows"], audit["potential_encoding_error_rows"]]})
    st.dataframe(quality, hide_index=True, width="stretch")
    st.info("Jumlah ulasan bukan rating. Label cuaca berasal dari dataset dan bukan prakiraan cuaca langsung. "
            "Verifikasi lokasi, jam operasional, dan kondisi terkini sebelum berkunjung.")


def about():
    st.markdown('<div class="eyebrow">RESEARCH & TRANSPARENCY</div>', unsafe_allow_html=True)
    st.title("Tentang Madura Explore")
    st.write("Antarmuka eksplorasi destinasi dari penelitian rekomendasi wisata Malik Hariyanto.")
    with st.container(border=True):
        st.subheader("Dari ulasan menjadi pilihan")
        st.markdown("1. **Katalog:** nama, kategori, kecocokan cuaca, dan maksimal 12 cuplikan ulasan per destinasi.\n"
                    "2. **Penyaringan:** musim, kategori, wilayah terverifikasi, dan riwayat kunjungan.\n"
                    "3. **Pencocokan:** TF-IDF dengan kemiripan kosinus, atau BGE-M3 bila diaktifkan.\n"
                    "4. **Hasil:** pilihan berdasarkan kemiripan teks, dengan tautan pencarian lokasi dan ekspor CSV.")
    a, b = st.columns(2)
    with a:
        st.subheader("Cara membaca hasil")
        st.write("Skor menunjukkan kemiripan preferensi dengan deskripsi destinasi. Skor bukan probabilitas, "
                 "rating kualitas, atau jaminan kepuasan. Skor TF-IDF dan BGE tidak dapat dibandingkan langsung.")
    with b:
        st.subheader("Cakupan geografis")
        st.write("Dataset sumber mencakup lokasi di luar Madura dan belum memiliki kabupaten terverifikasi. "
                 "Unggah CSV verifikasi wilayah melalui sidebar untuk membatasi katalog pada lokasi yang sudah diperiksa.")
    st.subheader("Hubungan dengan penelitian")
    st.write("Notebook tetap menjadi tempat pelatihan LDA, FastText, dan BiLSTM serta evaluasi eksperimen. "
             "Aplikasi ini tidak melatih ulang model saat digunakan dan tidak menampilkan metrik eksperimen sebagai metrik pencarian. "
             "Tanpa penilaian relevansi independen, akurasi rekomendasi belum dapat disimpulkan.")
    st.link_button("Buka kode & metodologi ↗", "https://github.com/MalikHariyanto/crispy_recom_machine_system/tree/feat/streamlit-wisata")
