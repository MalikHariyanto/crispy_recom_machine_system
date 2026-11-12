"""Search and recommendation cards. Model and research details stay in notebooks."""
from html import escape
from urllib.parse import quote_plus

import streamlit as st

from .runtime import lexical_index
from .services import filter_catalog
from .styles import hero

PALETTES = (
    ('#dcece6','#edc987','#387969','#8db5a4'),
    ('#e9e9d8','#dca77a','#647b61','#9aaa7e'),
    ('#dfeaf0','#ebcb8a','#537e91','#94b3bd'),
    ('#f1e4d7','#d7b474','#b58468','#cfb59a'),
)
EXAMPLES = ('Pantai pasir putih', 'Wisata sejarah', 'Pemandangan bukit')


def _suggest(value):
    st.session_state['sisre_query'] = value
    st.session_state['sisre_suggested'] = True


def _reset():
    st.session_state.update(sisre_query='',sisre_weather='Semua musim',
                            sisre_category='Semua jenis',sisre_example=None)
    for key in ('sisre_results','sisre_limit'):
        st.session_state.pop(key,None)


def _example_changed():
    value=st.session_state.get('sisre_example')
    if value:
        _suggest(value)


def destination_card(row, index, ranked=False):
    category=str(row.wisata)
    scene='beach' if category=='pantai' else 'mountain' if category in {'pegunungan','hutan/perkebunan','air terjun'} else 'heritage'
    colors=PALETTES[index % len(PALETTES)]
    variables=';'.join(f'--scene-{name}:{color}' for name,color in zip(('bg','sun','land','back'),colors))
    badge=f'<span class="result-index">{index+1:02d}</span>' if ranked else ''
    with st.container(border=True):
        st.markdown(f'''<div class="destination-art {scene}" style="{variables}"><span class="art-tag">{escape(category.title())}</span><span class="sun"></span><span class="land land-back"></span><span class="land"></span>{badge}</div>
        <h4 class="result-title">{escape(str(row.destinasi))}</h4>
        <div class="destination-meta"><span>{escape(str(row.rekomendasi_cuaca))}</span><i class="meta-dot"></i><span>{int(row.jumlah_ulasan):,} ulasan</span></div>''',unsafe_allow_html=True)
        st.link_button('Lihat lokasi ↗','https://www.google.com/maps/search/?api=1&query='+quote_plus(row.destinasi),width='stretch')
        with st.expander('Cuplikan ulasan'):
            snippets=str(row.deskripsi).split('. ',3)[-1].split(' | ')[:2]
            for text in snippets:
                st.write(text)


def explore(catalog, version):
    hero()
    if st.session_state.get('sisre_version') != version:
        st.session_state.pop('sisre_results',None)
        st.session_state['sisre_version']=version
    with st.form('sisre_search',border=True):
        query_col,button_col=st.columns([5,1],vertical_alignment='center')
        with query_col:
            query=st.text_input('Cari wisata di Madura',placeholder='Pantai tenang, wisata sejarah, atau tempat buat keluarga…',
                                label_visibility='collapsed',max_chars=400,key='sisre_query')
        with button_col:
            submitted=st.form_submit_button('Cari',type='primary',icon=':material/search:',width='stretch')
        a,b=st.columns(2)
        weather=a.selectbox('Musim',['Semua musim','Kemarau','Penghujan'],key='sisre_weather')
        category=b.selectbox('Jenis wisata',['Semua jenis',*sorted(catalog.wisata.unique())],key='sisre_category',
                             format_func=lambda x:x.capitalize())
    st.pills('Ide pencarian',EXAMPLES,key='sisre_example',label_visibility='collapsed',on_change=_example_changed)
    suggested=st.session_state.pop('sisre_suggested',False)
    filters=(weather,category)
    if submitted or suggested:
        eligible=filter_catalog(catalog,season='' if weather=='Semua musim' else weather,
                                types=() if category=='Semua jenis' else (category,))
        if not query.strip():
            st.session_state.pop('sisre_results',None)
            st.warning('Tulis tempat atau aktivitas yang kamu cari.')
        else:
            try:
                result=lexical_index().search(query,eligible.id_destinasi,k=len(catalog))
                st.session_state['sisre_results']=(query.strip(),filters,result)
                st.session_state['sisre_limit']=6
            except (ValueError,OSError,RuntimeError):
                st.session_state.pop('sisre_results',None)
                st.error('Pencarian belum berhasil. Coba lagi sebentar.')
    saved=st.session_state.get('sisre_results')
    st.write('')
    if saved:
        searched,applied_filters,results=saved
        heading,action=st.columns([4,1],vertical_alignment='center')
        heading.subheader(f'Hasil untuk “{searched}”')
        action.button('Reset',on_click=_reset,width='stretch')
        labels=[v for v in applied_filters if v not in {'Semua musim','Semua jenis'}]
        st.caption(f'{len(results)} tempat'+(' · '+' · '.join(labels) if labels else ''))
        if results.empty:
            st.info('Belum ada yang cocok. Coba kata lain atau ubah filter.')
            return
    else:
        st.subheader('Jelajahi Madura')
        results=catalog.sort_values(['jumlah_ulasan','destinasi'],ascending=[False,True]).reset_index(drop=True)
    limit=st.session_state.get('sisre_limit',6)
    shown=results.head(limit).reset_index(drop=True)
    for start in range(0,len(shown),3):
        columns=st.columns(3,gap='medium')
        for column,(index,row) in zip(columns,shown.iloc[start:start+3].iterrows()):
            with column:
                destination_card(row,index,ranked=bool(saved))
    if limit<len(results):
        left,center,right=st.columns([1,1,1])
        with center:
            if st.button('Lihat lebih banyak',width='stretch'):
                st.session_state['sisre_limit']=limit+6
                st.rerun()
