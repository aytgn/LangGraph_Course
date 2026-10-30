"""
Enterprise Sidebar Component.
"""

from datetime import datetime
import streamlit as st
from data.repositories.app_repository import app_repository


def render_enterprise_sidebar() -> str:
    """Render the left navigation sidebar and return the selected active_thread."""
    with st.sidebar:
        st.markdown("### 🏢 OTONOM YAZILIM EVİ")
        st.caption("AI Software Studio & Venture Builder • v5.0")

        # Documentation external links
        st.link_button("📖 Sistem Dokümantasyonu (Yeni Sekme) ↗", url="/Sistem_Dokumantasyonu", use_container_width=True)
        st.link_button("📚 LangGraph Başucu Kitabı (Yeni Sekme) ↗", url="/LangGraph_Basucu_Kitabi", use_container_width=True)
        st.divider()

        # Project Switcher (Repository Read)
        all_threads = app_repository.list_thread_ids()
        current_thread = st.session_state.get("active_thread", "")

        if all_threads:
            selected_idx = all_threads.index(current_thread) if current_thread in all_threads else 0
            chosen_thread = st.selectbox(
                "📂 Aktif Proje / Oturum:",
                options=all_threads,
                index=selected_idx,
                help="Her uygulama kendi SQLite checkpoint izolasyonunda saklanır."
            )
            st.session_state.active_thread = chosen_thread
        else:
            st.info("Henüz kayıtlı proje yok.")
            chosen_thread = current_thread

        # Quick New Project Action (Repository Create)
        with st.expander("➕ Yeni Uygulama Projesi Başlat", expanded=False):
            new_title = st.text_input("Proje Kodu / Slug:", value=f"app-{datetime.now().strftime('%m%d-%H%M%S')}")
            if st.button("✨ Projeyi Oluştur", use_container_width=True):
                clean_tid = app_repository.create_thread(new_title)
                st.session_state.active_thread = clean_tid
                st.rerun()

        st.divider()

        # Database Stats Widget (Repository Read)
        stats = app_repository.get_statistics()
        st.markdown("**📊 Stüdyo Sağlık Metrikleri**")
        st.caption(f"• Toplam Proje: **{stats.total_apps}**")
        st.caption(f"• Toplam Checkpoint: **{stats.total_checkpoints}**")
        st.caption(f"• SQLite Boyutu: **{stats.db_size_kb} KB**")
        st.caption(f"• Diskte Paketlenen: **{stats.deployed_apps_count} Uygulama**")

    return st.session_state.active_thread
