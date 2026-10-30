"""
================================================================================
🏗️ OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU - YÖNETİCİ KOKPİTİ (ENTRYPOINT)
================================================================================
Clean Architecture & Modular Streamlit Presentation Controller.
Katmanlar: config/ • data/ • tools/ • domain/ • services/ • ui/
================================================================================
"""

import os
import sys
from pathlib import Path

# Windows terminal Türkçe ve emoji karakter güvenliği (charmap / cp1252 hatasını engeller)
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Modül ve proje kök dizinlerini sys.path'e ekle
_module_root = Path(__file__).resolve().parent
_project_root = _module_root.parent
for p in (_module_root, _project_root):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st
from data.repositories.app_repository import app_repository
from domain.workflow import studio_app
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


def _status_badge_class(status_text: str) -> str:
    if "Hazır" in status_text:
        return "node-passed"
    if "Onayı Bekliyor" in status_text:
        return "node-warn"
    if "Reddedildi" in status_text:
        return "node-error"
    if "Geliştiriliyor" in status_text:
        return "node-active"
    return "node-waiting"


def main():
    # 1. Sayfa Yapılandırması ve Kurumsal Tema
    st.set_page_config(
        page_title="Otonom Yazılım Evi & Uygulama Stüdyosu",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_enterprise_theme()
    init_session_state()

    # 2. Sol Menü (Proje Seçimi, Yeni Proje, Şablonlar ve Sağlık Metrikleri)
    active_thread = render_enterprise_sidebar()
    sync_thread_state(active_thread)

    # 3. Üst Kurumsal Başlık (Aktif Proje Özeti ile)
    proj = app_repository.get_project(active_thread, app_graph=studio_app)
    proj_title = proj.name if proj and not proj.name.startswith("(") else active_thread
    proj_status = proj.status if proj else "⚪ Başlangıç"
    badge_cls = _status_badge_class(proj_status)

    st.markdown(
        f"""
<div class="studio-header">
    <div>
        <div class="studio-title">🏗️ Otonom Yazılım Evi & Uygulama Stüdyosu</div>
        <div class="studio-subtitle">
            Clean Architecture • Döngüsel LangGraph Fabrikası • Fabrika Sohbet Masası • Onay / Revizyon / Red Kapısı • Tam SQLite CRUD
        </div>
    </div>
    <div style="text-align: right;">
        <div style="margin-bottom: 4px;">
            <span class="node-badge node-active" style="font-size: 12.5px; padding: 5px 10px;">
                📂 {proj_title} (<code>{active_thread}</code>)
            </span>
        </div>
        <span class="node-badge {badge_cls}" style="font-size: 11.5px; padding: 4px 10px;">
            {proj_status}
        </span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 4. Modüler Sekme Görünümleri (Views)
    tab_ideation, tab_factory, tab_workspace, tab_portfolio, tab_architecture = st.tabs([
        "💡 0. Ürün & Mimari Tartışma",
        "🏭 1. Canlı Yazılım Fabrikası",
        "💻 2. Kod Gezgini & Çalıştırma",
        "🗄️ 3. Uygulama Portföyü (CRUD)",
        "🏛️ 4. Stüdyo Mimarisi & Araçlar",
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
