"""SISRE's local visual system; no external fonts or image services."""
import streamlit as st


def apply_styles():
    st.markdown('''<style>
    :root {--ink:#153c43;--teal:#176b60;--muted:#637574;--line:#dfe5de;--paper:#f7f7f0;}
    .stApp {background:var(--paper);}
    .block-container {max-width:1180px;padding-top:1.5rem;padding-bottom:1.4rem;}
    header[data-testid="stHeader"] {background:transparent;}
    [data-testid="stToolbar"],#MainMenu {display:none;}
    h1,h2,h3 {color:var(--ink);letter-spacing:-.045em;}
    h3 {font-size:1.45rem!important;}
    p {line-height:1.5;}
    .sisre-nav {display:flex;align-items:center;justify-content:space-between;padding:0 0 1.1rem;border-bottom:1px solid var(--line);}
    .wordmark {display:flex;gap:11px;align-items:center;font-size:1.35rem;font-weight:800;letter-spacing:-.06em;color:var(--ink);}
    .brand-mark {display:grid;place-items:center;width:33px;height:33px;background:var(--ink);border-radius:11px;color:#e4edb8;font-size:1.3rem;line-height:1;}
    .nav-meta {font-size:.78rem;color:var(--muted);display:flex;gap:16px;align-items:center;}
    .nav-dot {width:5px;height:5px;background:#8b9c77;border-radius:50%;}
    .sisre-hero {position:relative;padding:3.2rem 0 1.2rem;overflow:hidden;}
    .hero-kicker {display:flex;align-items:center;gap:8px;color:var(--teal);font-size:.72rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;}
    .hero-kicker:before {content:"";height:1px;width:24px;background:var(--teal);}
    .sisre-hero h1 {position:relative;z-index:1;font-size:clamp(2.7rem,5vw,4.4rem);line-height:1.08;font-weight:650;max-width:710px;margin:.85rem 0 1rem;padding:0;}
    .sisre-hero h1 em {font-family:Georgia,serif;font-weight:400;color:var(--teal);}
    .sisre-hero p {color:var(--muted);font-size:1rem;margin:0;}
    .hero-art {position:absolute;right:0;top:16px;width:285px;height:240px;opacity:.8;pointer-events:none;}
    [data-testid="stForm"] {background:#fff;border:1px solid #d5dfd6;border-radius:20px;padding:20px 22px 16px;box-shadow:0 8px 28px #153c4306;}
    [data-testid="stTextInput"] input {font-size:1rem;}
    [data-testid="stTextInput"] [data-baseweb="input"] {min-height:50px;border-radius:10px;}
    [data-testid="stFormSubmitButton"] button {min-height:50px;border-radius:10px;font-weight:650;}
    [data-testid="stWidgetLabel"] p {font-size:.76rem;color:var(--muted);font-weight:550;}
    [data-testid="stSelectbox"] [data-baseweb="select"]>div {border-radius:9px;background:#fbfcf8;}
    [data-testid="stPills"] {margin:.1rem 0 .4rem;}
    [data-testid="stPills"] button {font-size:.78rem;border-color:#dbe2d8;}
    [data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:16px!important;}
    .destination-art {position:relative;overflow:hidden;height:130px;border-radius:11px;background:var(--scene-bg);margin-bottom:14px;}
    .destination-art .sun {position:absolute;top:22px;right:37px;width:33px;height:33px;border-radius:50%;background:var(--scene-sun);}
    .destination-art .land {position:absolute;bottom:-63px;left:-12%;width:90%;height:135px;border-radius:50%;background:var(--scene-land);transform:rotate(-12deg);}
    .destination-art .land-back {left:45%;bottom:-50px;background:var(--scene-back);height:135px;transform:rotate(8deg);}
    .destination-art.beach:after {content:"";position:absolute;bottom:20px;left:0;right:0;height:2px;background:#ffffff70;box-shadow:15px 8px 0 #ffffff50,-10px 16px 0 #ffffff40;}
    .destination-art.mountain .land {bottom:-45px;height:140px;border-radius:28px 90px 0 0;transform:rotate(30deg);}
    .destination-art.heritage .land {bottom:-45px;left:26%;width:46%;height:130px;border-radius:85px 85px 0 0;transform:none;}
    .destination-art.heritage .land-back {bottom:-60px;left:9%;width:82%;height:100px;border-radius:12px;}
    .art-tag {position:absolute;left:12px;top:12px;background:#fffffff0;border:1px solid #ffffff70;border-radius:30px;padding:4px 10px;font-size:.65rem;font-weight:600;color:var(--ink);z-index:2;}
    .result-title {font-size:1.12rem;font-weight:650;letter-spacing:-.02em;line-height:1.35;margin:0 0 7px;padding:0;min-height:1.5em;}
    .destination-meta {display:flex;align-items:center;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:.72rem;margin-bottom:15px;}
    .meta-dot {height:3px;width:3px;background:#9baba0;border-radius:50%;}
    .result-index {position:absolute;bottom:10px;right:11px;color:#fff;font-size:.67rem;letter-spacing:.06em;z-index:2;background:#153c4377;padding:2px 7px;border-radius:20px;}
    [data-testid="stExpander"] {border-color:#e7ebe3;border-radius:9px;}
    [data-testid="stExpander"] summary p {font-size:.75rem;color:var(--muted);}
    [data-testid="stLinkButton"] a {border-color:#d5dfd6;border-radius:9px;font-size:.8rem;min-height:38px;}
    [data-testid="stLinkButton"] a:hover {border-color:var(--teal);color:var(--teal);background:#f1f6ef;}
    .results-note {color:var(--muted);font-size:.78rem;}
    .sisre-footer {display:flex;justify-content:space-between;margin-top:2.5rem;padding-top:1.2rem;border-top:1px solid var(--line);font-size:.7rem;color:#74827a;}
    .sisre-footer strong {letter-spacing:.09em;}
    @media(max-width:760px){.hero-art{width:160px;right:-60px;top:20px;opacity:.25}.sisre-hero{padding-top:2.2rem}.sisre-hero h1{font-size:2.7rem}.nav-meta .nav-count,.nav-dot{display:none}.block-container{padding:1.2rem 1.1rem 1.5rem}[data-testid="stForm"]{padding:16px}.destination-art{height:145px}}
    </style>''', unsafe_allow_html=True)


def masthead(count):
    st.markdown(f'''<nav class="sisre-nav" aria-label="SISRE"><div class="wordmark"><span class="brand-mark" aria-hidden="true">≋</span>SISRE</div>
    <div class="nav-meta"><span>Wisata Madura</span><i class="nav-dot"></i><span class="nav-count">{count} destinasi</span></div></nav>''', unsafe_allow_html=True)


def hero():
    st.markdown('''<section class="sisre-hero"><div class="hero-kicker">Jelajahi Madura</div>
    <h1>Madura,<br>mau ke <em>mana?</em></h1><p>Temukan tempat yang pas dengan rencana perjalananmu.</p>
    <svg class="hero-art" viewBox="0 0 280 240" aria-hidden="true"><circle cx="165" cy="85" r="64" fill="#e9edce"/>
    <path d="M20 178 Q75 95 150 156 T300 137" fill="none" stroke="#b3c8b7" stroke-width="1.4"/>
    <path d="M-10 195 Q70 110 149 173 T300 150 M-15 209 Q65 128 150 188 T300 165 M-10 223 Q70 145 150 202 T300 180" fill="none" stroke="#b3c8b7" stroke-width="1.4"/>
    <circle cx="165" cy="86" r="8" fill="#176b60"/><circle cx="165" cy="86" r="18" fill="none" stroke="#176b60" stroke-opacity=".25"/>
    <path d="M165 94 Q148 128 126 141" fill="none" stroke="#176b60" stroke-dasharray="3 5"/>
    </svg></section>''', unsafe_allow_html=True)
