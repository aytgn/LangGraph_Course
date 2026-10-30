"""
View: Tab 3 - Application Portfolio (CRUD Data Management).
"""

import pandas as pd
import streamlit as st
from data.repositories.app_repository import app_repository
from domain.workflow import studio_app


def render_portfolio_view(active_thread: str):
    """Render Tab 3: Application Portfolio with full CRUD operations."""
    st.markdown("#### 🗄️ Geliştirilen Uygulamalar Portföyü (CRUD)")
    st.caption("Veritabanındaki (`studio_apps.db`) kayıtlı tüm yazılım projelerini listeleyin, filtreleyin, inceleyin veya silin:")

    stats = app_repository.get_statistics()
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Toplam Uygulama", f"{stats.total_apps} Adet")
    with s2:
        st.metric("Toplam Checkpoint", f"{stats.total_checkpoints} Adım")
    with s3:
        st.metric("SQLite Boyutu", f"{stats.db_size_kb} KB")
    with s4:
        st.metric("Diskte Kurulu", f"{stats.deployed_apps_count} Paket")

    st.divider()

    # Filter by status
    status_filter = st.selectbox(
        "🔍 Duruma Göre Filtrele (READ):",
        options=["Tümü", "🚀 Fiziksel Paket Hazır", "🛑 Kurucu Onayı Bekliyor", "🔄 Geliştiriliyor", "⚪ Başlangıç"],
        index=0
    )

    # Repository Read
    projects = app_repository.list_all_projects(app_graph=studio_app, status_filter=status_filter)

    if projects:
        rows = []
        for p in projects:
            rows.append({
                "Proje Kodu": p.thread_id,
                "Uygulama Adı": p.name,
                "Uygulama Tipi": p.app_type,
                "Teknoloji Yığını": ", ".join(p.tech_stack[:3]) if p.tech_stack else "-",
                "Dosya / Satır": f"{p.files_count} dosya / {p.total_loc} LOC" if p.files_count else "-",
                "Döngü / Revizyon": f"#{p.cycle_count} tur ({p.revision_count} rev)",
                "QA Durumu": "✅ Geçti" if p.qa_passed else ("⚠️ Bekliyor" if p.files_count else "-"),
                "Durum": p.status,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # CRUD Delete / Management Section
        with st.expander("🗑️ Proje Yönetimi & Güvenli Silme (CRUD DELETE)", expanded=False):
            st.warning("Bir projeyi sildiğinizde SQLite veritabanındaki tüm checkpoint kayıtları ve diskteki çıktı dosyaları temizlenir.")
            del_thread = st.selectbox("Silinecek Projeyi Seçin:", options=[p.thread_id for p in projects])
            col_del_btn, col_del_chk = st.columns([1, 2])
            with col_del_chk:
                delete_disk = st.checkbox("Fiziksel disk klasörünü de (`output_uygulamalar`) sil", value=True)
            with col_del_btn:
                if st.button("⚠️ Projeyi Kalıcı Olarak Sil", type="primary", use_container_width=True):
                    # Find slug
                    matching = [p for p in projects if p.thread_id == del_thread]
                    slug = matching[0].slug if matching else None
                    if app_repository.delete_project(del_thread, slug=slug, delete_disk=delete_disk):
                        st.success(f"'{del_thread}' başarıyla silindi!")
                        # Switch active thread if we deleted the current one
                        remaining = app_repository.list_thread_ids()
                        st.session_state.active_thread = remaining[0] if remaining else "app-new"
                        st.rerun()
                    else:
                        st.error("Silme işlemi sırasında hata oluştu.")
    else:
        st.info("Kayıtlı uygulama projesi bulunamadı.")

    # Time-Travel Audit (READ)
    with st.expander("⏱️ Aktif Uygulamanın Checkpoint Zaman Çizelgesi (Time-Travel Audit)", expanded=False):
        history = app_repository.get_checkpoint_history(active_thread, studio_app)
        if history:
            h_rows = [
                {
                    "Adım": rec.step,
                    "Kaynak": rec.source,
                    "Sıradaki Düğüm": rec.next_node,
                    "Checkpoint ID": rec.checkpoint_id[:16] + "..." if rec.checkpoint_id else "-",
                }
                for rec in history
            ]
            st.dataframe(pd.DataFrame(h_rows), use_container_width=True, hide_index=True)
        else:
            st.caption("Bu proje için henüz checkpoint geçmişi bulunmuyor.")
