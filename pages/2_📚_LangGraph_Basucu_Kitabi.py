"""
================================================================================
📚 ZİNCİRLERDEN OTONOM ŞİRKETLERE — LANGGRAPH BAŞUCU KİTABI (HARİCİ SAYFA) 📚
================================================================================
Yönetici Kokpiti (yonetici_masasi.py) sağ üst başlığındaki doküman/kitap
tuşundan yeni tarayıcı sekmesinde (external / target="_blank") açılan, ayrı bir
arka plan daemon sürecine ihtiyaç duymayan tam ekran interaktif E-Kitap sayfası.
================================================================================
"""

import os
import sys
import base64
import streamlit as st
import streamlit.components.v1 as components

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from kitap_okuyucu import (
    BOOK_MD_PATH,
    BOOK_PDF_PATH,
    render_standalone_ebook_html,
)

st.set_page_config(
    page_title="Zincirlerden Otonom Şirketlere | LangGraph Başucu Kitabı",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Tam ekran (Chromeless) E-Kitap görünümü: Streamlit kenar boşluklarını ve barlarını gizler
st.markdown(
    """
    <style>
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        #MainMenu,
        footer {
            display: none !important;
        }
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            margin: 0 !important;
            padding: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            overflow: hidden !important;
            background-color: #090d16 !important;
        }
        .block-container, [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100vw !important;
            width: 100vw !important;
            height: 100vh !important;
        }
        .stApp iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: 9999 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def _load_full_ebook_html(md_mtime: float, pdf_mtime: float) -> str:
    pdf_b64 = ""
    if os.path.exists(BOOK_PDF_PATH):
        with open(BOOK_PDF_PATH, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode("ascii")

    return render_standalone_ebook_html(
        pdf_href="./LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.pdf",
        pdf_base64=pdf_b64,
        cockpit_url="/",
    )


md_mtime = os.path.getmtime(BOOK_MD_PATH) if os.path.exists(BOOK_MD_PATH) else 0.0
pdf_mtime = os.path.getmtime(BOOK_PDF_PATH) if os.path.exists(BOOK_PDF_PATH) else 0.0

ebook_html = _load_full_ebook_html(md_mtime, pdf_mtime)
components.html(ebook_html, height=900, scrolling=False)
