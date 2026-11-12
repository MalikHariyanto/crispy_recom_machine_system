"""Static branding, with no external image or font requests."""
import streamlit as st


def apply_styles():
    st.markdown('''<style>
    .block-container {max-width:1240px; padding-top:2.3rem; padding-bottom:3rem;}
    [data-testid="stSidebar"] {border-right:1px solid #e0e8e3;}
    h1,h2,h3 {letter-spacing:-.04em;}
    h1 {font-size:2.8rem !important;}
    [data-testid="stMetric"] {background:white; border:1px solid #dfe8e2; padding:1rem 1.2rem; border-radius:14px;}
    [data-testid="stMetricLabel"] {color:#62776e;}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:16px !important;}
    .eyebrow {font-size:.73rem;font-weight:700;letter-spacing:.18em;color:#578474;margin-bottom:.65rem;}
    .hero {position:relative;overflow:hidden;background:#153e35;border-radius:24px;padding:2.4rem 2.6rem;margin:0 0 1.7rem;color:#f3f8ed;}
    .hero h1 {max-width:660px;color:#f3f8ed;line-height:1.12;margin:.25rem 0 .75rem;}
    .hero p {max-width:590px;color:#cadacf;line-height:1.7;margin:0;}
    .hero .eyebrow {color:#b9d7ad;}
    .hero:after {content:"";position:absolute;width:330px;height:330px;border:60px solid #67997d24;border-radius:50%;right:-90px;top:-120px;pointer-events:none;}
    .tag {display:inline-block;background:#eaf3ed;color:#28624d;border-radius:6px;padding:4px 8px;font-size:.72rem;margin:0 5px 8px 0;}
    .rank {color:#6b887c;font-size:.75rem;font-weight:700;letter-spacing:.12em;margin-bottom:8px;}
    .card-title {font-size:1.22rem;font-weight:650;line-height:1.35;margin:2px 0 12px;}
    .muted {color:#667b71;font-size:.87rem;line-height:1.65;}
    .footer {border-top:1px solid #dfe8e2;padding-top:1.2rem;margin-top:2rem;color:#73847c;font-size:.75rem;}
    @media(max-width:640px){.hero{padding:1.6rem;} .hero h1{font-size:2rem !important;} .block-container{padding-top:1rem;}}
    </style>''', unsafe_allow_html=True)


def hero():
    st.markdown('''<section class="hero"><div class="eyebrow">MADURA / TRAVEL DISCOVERY</div>
    <h1>Perjalanan berikutnya,<br>dimulai dari rasa penasaran.</h1>
    <p>Jelajahi destinasi lewat cerita wisatawan. Temukan pilihan yang sesuai minat dan kecocokan musim perjalananmu.</p>
    </section>''', unsafe_allow_html=True)
