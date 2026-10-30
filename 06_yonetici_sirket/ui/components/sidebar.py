"""
Enterprise Sidebar Component.
Project Switcher, New Project Creator, Sample App Templates & Live Telemetry.
"""

from datetime import datetime
import streamlit as st
from model_factory import TARGET_MODEL, API_KEY_POOL
from data.repositories.app_repository import app_repository
from tools.registry import ToolRegistry


SAMPLE_BLUEPRINTS = {
    "💳 Abonelik & Gider Takipçisi (Streamlit + SQLite)": (
        "Abonelik Takipçisi",
        "Bireysel kullanıcılar için aylık ve yıllık dijital aboneliklerini SQLite3 veritabanında saklayan, "
        "kategori bazlı maliyet analizi sunan, yaklaşan ödemeleri listeleyen ve örnek verilerle hazır gelen "
        "modüler bir Streamlit web uygulaması geliştirin.",
    ),
    "📦 Depo Stok & Barkod Mikroservisi (FastAPI + SQLite)": (
        "Depo Stok API",
        "KOBİ depoları için ürün ekleme, stok giriş/çıkış hareketleri, kritik stok eşiği uyarıları ve "
        "kategori raporlaması sunan, SQLite3 tabanlı ve Swagger arayüzlü modüler bir FastAPI REST servisi geliştirin.",
    ),
    "🔍 Log & Hata Analiz Aracı (CLI + Argparse)": (
        "LogAnaliz CLI",
        "Sunucu log dosyalarını tarayarak ERROR/WARNING dağılımını çıkaran, en sık tekrarlayan hataları "
        "tablo halinde özetleyen ve JSON/Markdown rapor üreten modüler bir Python CLI aracı geliştirin.",
    ),
    "⏱️ Odaklanma & Görev Analitiği (Streamlit + SQLite)": (
        "Odak ve Görev Masası",
        "Yazılımcılar için görev yönetimi (Kanban durumu), çalışma oturumu kaydı ve haftalık üretkenlik "
        "istatistiklerini SQLite3 ile takip eden temiz arayüzlü bir Streamlit uygulaması geliştirin.",
    ),
}


def render_enterprise_sidebar() -> str:
    """Render the left navigation sidebar and return the selected active_thread."""
    with st.sidebar:
        st.markdown("### 🏢 OTONOM YAZILIM EVİ")
        st.caption("AI Software Studio & Venture Builder • v5.1")

        # Documentation external links
        st.link_button("📖 Sistem Dokümantasyonu (Yeni Sekme) ↗", url="/Sistem_Dokumantasyonu", use_container_width=True)
        st.link_button("📚 LangGraph Başucu Kitabı (Yeni Sekme) ↗", url="/LangGraph_Basucu_Kitabi", use_container_width=True)

        st.markdown(
            f"<div style='margin-top:6px;'>"
            f"<span class='node-badge node-active'>🧠 {TARGET_MODEL}</span>"
            f"<span class='node-badge node-passed'>🔑 {len(API_KEY_POOL)} Key</span>"
            f"<span class='node-badge node-waiting'>🛠️ {ToolRegistry.count()} Araç</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        # Project Switcher (Repository Read)
        all_projects = app_repository.list_all_projects()
        all_threads = [p.thread_id for p in all_projects]
        label_map = {
            p.thread_id: (f"{p.name} ({p.thread_id})" if p.name and not p.name.startswith("(") else p.thread_id)
            for p in all_projects
        }

        current_thread = st.session_state.get("active_thread", "")
        if current_thread and current_thread not in all_threads:
            app_repository.create_project(current_thread)
            all_threads.insert(0, current_thread)
            label_map[current_thread] = current_thread

        if all_threads:
            selected_idx = all_threads.index(current_thread) if current_thread in all_threads else 0
            chosen_thread = st.selectbox(
                "📂 Aktif Uygulama Projesi:",
                options=all_threads,
                index=selected_idx,
                format_func=lambda tid: label_map.get(tid, tid),
                help="Her uygulama kendi SQLite kaydı ve LangGraph checkpoint izolasyonunda tutulur.",
            )
            st.session_state.active_thread = chosen_thread
        else:
            chosen_thread = app_repository.create_project(f"app-{datetime.now().strftime('%m%d-%H%M%S')}")
            st.session_state.active_thread = chosen_thread

        # Quick New Project Action (Repository Create)
        with st.expander("➕ Yeni Uygulama Projesi Başlat", expanded=False):
            new_display = st.text_input("Proje Adı (Opsiyonel):", placeholder="Örn: Müşteri Destek Paneli", key="sb_new_display")
            new_slug = st.text_input(
                "Proje Kodu / Slug:",
                value=f"app-{datetime.now().strftime('%m%d-%H%M')}",
                key="sb_new_slug",
            )
            if st.button("✨ Boş Proje Oluştur ve Geç", use_container_width=True, key="sb_btn_create"):
                clean_tid = app_repository.create_project(
                    thread_id=new_slug,
                    display_name=new_display,
                )
                st.session_state.active_thread = clean_tid
                st.session_state.queued_factory_directive = None
                st.rerun()

        # Sample Application Blueprints
        with st.expander("⚡ Hazır Uygulama Şablonları", expanded=False):
            chosen_tpl = st.selectbox("Örnek Şablon Seçin:", options=list(SAMPLE_BLUEPRINTS.keys()), key="sb_tpl_select")
            if st.button("📌 Şablonla Yeni Proje Hazırla", use_container_width=True, key="sb_btn_tpl"):
                short_title, prompt_txt = SAMPLE_BLUEPRINTS[chosen_tpl]
                slug_tid = app_repository.create_project(
                    thread_id=f"tpl-{datetime.now().strftime('%H%M%S')}",
                    display_name=short_title,
                    tags="sablon,mvp",
                )
                st.session_state.active_thread = slug_tid
                st.session_state.queued_factory_directive = {
                    "thread_id": slug_tid,
                    "title": short_title,
                    "directive": prompt_txt,
                    "source": "Hazır Şablon",
                }
                st.rerun()

        st.divider()

        # Database Stats Widget (Repository Read)
        stats = app_repository.get_statistics()
        st.markdown("**📊 Stüdyo Sağlık Metrikleri**")
        st.caption(f"• Kayıtlı Proje: **{stats.total_apps}**")
        st.caption(f"• Toplam Checkpoint: **{stats.total_checkpoints}**")
        st.caption(f"• SQLite Boyutu: **{stats.db_size_kb} KB**")
        st.caption(f"• Diskte Paketlenen: **{stats.deployed_apps_count} Uygulama**")

    return st.session_state.active_thread
