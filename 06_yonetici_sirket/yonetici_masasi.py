"""
================================================================================
🏗️ OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU - YÖNETİCİ KOKPİTİ (ENTRYPOINT)
================================================================================
Clean Architecture & Modular Streamlit Presentation Controller.
Büyük yazılım firmaları standartlarında; sunum, alan mantığı, veri ve araç katmanları
kesin çizgilerle ayrılmış, modüler ve yüksek performanslı kurumsal orkestratör.
================================================================================
"""

import sys
from pathlib import Path

# Modül ve proje kök dizinlerini sys.path'e ekle
_module_root = Path(__file__).resolve().parent
_project_root = _module_root.parent
for p in (_module_root, _project_root):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st
from ui.styles import apply_enterprise_theme
from ui.state import init_session_state, sync_thread_state
from ui.components.sidebar import render_enterprise_sidebar
from ui.views import (
    render_ideation_view,
    render_factory_view,
    render_workspace_view,
    render_portfolio_view,
    render_architecture_view,
)


def main():
    # 1. Sayfa Yapılandırması ve Kurumsal Tema
    st.set_page_config(
        page_title="Otonom Yazılım Evi & Uygulama Stüdyosu",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_enterprise_theme()
    init_session_state()

    # 2. Sol Menü (Proje Seçimi, Metrikler ve Hızlı Aksiyonlar)
    active_thread = render_enterprise_sidebar()
    sync_thread_state(active_thread)

    # 3. Üst Kurumsal Başlık
    st.markdown(
        f"""
<div class="studio-header">
    <div>
        <div class="studio-title">🏗️ Otonom Yazılım Evi & Uygulama Stüdyosu</div>
        <div class="studio-subtitle">
            Döngüsel LangGraph Fabrikası • Deterministik AST/QA • SQLite Kalıcılığı • Kurucu Onay Kapısı
        </div>
    </div>
    <div style="text-align: right;">
        <span class="node-badge node-active" style="font-size: 13px; padding: 6px 12px;">
            Aktif Proje: <b>{active_thread}</b>
        </span>
    </div>
</div>
""",
        unsafe_allow_html=True
    )

    # 4. Modüler Sekme Görünümleri (Views)
    tab_ideation, tab_factory, tab_workspace, tab_portfolio, tab_architecture = st.tabs([
        "💡 0. Ürün & Mimari Tartışma",
        "🏭 1. Canlı Yazılım Fabrikası",
        "💻 2. Kod Gezgini & Çalıştırma",
        "🗄️ 3. Uygulama Portföyü (CRUD)",
        "🏛️ 4. Stüdyo Mimarisi & Araçlar"
    ])

    with tab_ideation:
        render_ideation_view(active_thread)

    with tab_factory:
        render_factory_view(active_thread)

    with tab_workspace:
        render_workspace_view(active_thread)

    with tab_portfolio:
        render_portfolio_view(active_thread)

    with tab_architecture:
        render_architecture_view()


if __name__ == "__main__":
    main()
