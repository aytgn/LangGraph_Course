"""
View: Tab 3 - Application Portfolio (Full Enterprise SQLite CRUD Management).
Supports CREATE, READ (Search + Status Filter), UPDATE (Rename/Tags/Notes), and DELETE.
"""

from datetime import datetime
import pandas as pd
import streamlit as st
from data.repositories.app_repository import app_repository
from domain.workflow import studio_app


def render_portfolio_view(active_thread: str):
    """Render Tab 3: Application Portfolio with real SQLite CRUD operations."""
    st.markdown("#### 🗄️ Geliştirilen Uygulamalar Portföyü (Tam CRUD Yönetimi)")
    st.caption(
        "`studio_apps.db` üzerindeki tüm uygulama projelerini arayın, filtreleyin, tek tıkla masaya yükleyin, "
        "yeniden adlandırın/etiketleyin veya disk paketiyle birlikte kalıcı olarak silin."
    )

    stats = app_repository.get_statistics()
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Kayıtlı Proje", f"{stats.total_apps} Adet")
    with s2:
        st.metric("Toplam Checkpoint", f"{stats.total_checkpoints} Adım")
    with s3:
        st.metric("SQLite Boyutu", f"{stats.db_size_kb} KB")
    with s4:
        st.metric("Diskte Kurulu", f"{stats.deployed_apps_count} Paket")

    st.divider()

    # READ: Search & Filter Controls
    f_col1, f_col2 = st.columns([2.2, 1.8])
    with f_col1:
        search_q = st.text_input(
            "🔎 Proje Ara (READ):",
            placeholder="Proje kodu, uygulama adı, teknoloji, etiket veya not ara...",
            key="pf_search_q",
        )
    with f_col2:
        status_filter = st.selectbox(
            "📌 Duruma Göre Filtrele (READ):",
            options=[
                "Tümü",
                "🚀 Fiziksel Paket Hazır",
                "🛑 Kurucu Onayı Bekliyor",
                "❌ Kod Reddedildi",
                "🔄 Geliştiriliyor",
                "⚪ Başlangıç",
            ],
            index=0,
            key="pf_status_filter",
        )

    projects = app_repository.list_all_projects(
        app_graph=studio_app,
        status_filter=status_filter,
        search_query=search_q,
    )

    if projects:
        rows = []
        for p in projects:
            rows.append({
                "Aktif": "⭐" if p.thread_id == active_thread else "",
                "Proje Kodu": p.thread_id,
                "Uygulama Adı": p.name,
                "Durum": p.status,
                "Mimari Tipi": p.app_type,
                "Dosya / Satır": f"{p.files_count} dosya / {p.total_loc} LOC" if p.files_count else "-",
                "Döngü": f"#{p.cycle_count} ({p.revision_count} rev)",
                "Etiketler": p.tags or "-",
                "Notlar": (p.custom_notes[:45] + "...") if len(p.custom_notes) > 45 else (p.custom_notes or "-"),
                "Güncelleme": p.updated_at or "-",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Quick Project Switcher
        sw1, sw2 = st.columns([3, 1.5])
        with sw1:
            switch_tid = st.selectbox(
                "🎯 Masaya Yüklenecek Projeyi Seçin:",
                options=[p.thread_id for p in projects],
                format_func=lambda tid: next((f"{x.name} ({x.thread_id}) — {x.status}" for x in projects if x.thread_id == tid), tid),
                key="pf_switch_select",
            )
        with sw2:
            st.write("")
            if st.button("📂 Seçili Projeyi Masaya Yükle", type="primary", use_container_width=True, key="pf_btn_switch"):
                st.session_state.active_thread = switch_tid
                st.rerun()
    else:
        st.info("Filtre kriterlerine uygun uygulama projesi bulunamadı.")

    st.divider()

    # Explicit CRUD Management Tabs (CREATE / UPDATE / DELETE)
    st.markdown("##### ⚙️ Kurumsal Veri Yönetimi İşlemleri (CREATE • UPDATE • DELETE)")
    crud_create, crud_update, crud_delete = st.tabs([
        "➕ Yeni Proje Oluştur (CREATE)",
        "✏️ Proje Bilgilerini Güncelle (UPDATE)",
        "🗑️ Projeyi Kalıcı Sil (DELETE)",
    ])

    all_unfiltered = app_repository.list_all_projects(app_graph=studio_app)

    with crud_create:
        with st.form("pf_create_form", clear_on_submit=True):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_slug = st.text_input("Proje Kodu (Thread ID):", value=f"proje-{datetime.now().strftime('%m%d-%H%M')}")
                c_tags = st.text_input("Etiketler (virgülle):", placeholder="Örn: saas, sqlite, mvp")
            with c_col2:
                c_name = st.text_input("Görünür Proje Adı:", placeholder="Örn: Müşteri Fatura Takip Sistemi")
                c_notes = st.text_input("Yönetici Notu:", placeholder="Örn: Q4 iç operasyon aracı")
            if st.form_submit_button("✨ Projeyi Veritabanına Kaydet ve Aktif Et", type="primary", use_container_width=True):
                new_tid = app_repository.create_project(
                    thread_id=c_slug,
                    display_name=c_name,
                    custom_notes=c_notes,
                    tags=c_tags,
                )
                st.session_state.active_thread = new_tid
                st.success(f"`{new_tid}` projesi oluşturuldu ve aktif masaya yüklendi!")
                st.rerun()

    with crud_update:
        if all_unfiltered:
            upd_tid = st.selectbox(
                "Güncellenecek Projeyi Seçin:",
                options=[p.thread_id for p in all_unfiltered],
                format_func=lambda tid: next((f"{x.name} ({x.thread_id})" for x in all_unfiltered if x.thread_id == tid), tid),
                key="pf_upd_select",
            )
            sel_proj = next((x for x in all_unfiltered if x.thread_id == upd_tid), all_unfiltered[0])
            u_col1, u_col2 = st.columns(2)
            with u_col1:
                u_name = st.text_input(
                    "Yeni Görünür Uygulama Adı:",
                    value= "" if sel_proj.name.startswith("(") else sel_proj.name,
                    key=f"pf_u_name_{upd_tid}",
                )
                u_tags = st.text_input("Etiketler:", value=sel_proj.tags, key=f"pf_u_tags_{upd_tid}")
            with u_col2:
                u_notes = st.text_area("Yönetici Notları:", value=sel_proj.custom_notes, height=105, key=f"pf_u_notes_{upd_tid}")

            if st.button("💾 Proje Metadata Bilgilerini Güncelle (SQLite UPDATE)", type="primary", use_container_width=True, key="pf_btn_update"):
                if app_repository.update_project_metadata(
                    thread_id=upd_tid,
                    display_name=u_name,
                    custom_notes=u_notes,
                    tags=u_tags,
                ):
                    st.success(f"`{upd_tid}` projesinin veritabanı kayıtları güncellendi!")
                    st.rerun()
                else:
                    st.error("Güncelleme sırasında bir hata oluştu.")
        else:
            st.info("Güncellenecek proje bulunmuyor.")

    with crud_delete:
        if all_unfiltered:
            st.warning(
                "Dikkat: Silinen projenin `studio_projects`, `checkpoints` ve `writes` tablolarındaki kayıtları kalıcı olarak kaldırılır."
            )
            del_thread = st.selectbox(
                "Silinecek Projeyi Seçin:",
                options=[p.thread_id for p in all_unfiltered],
                format_func=lambda tid: next((f"{x.name} ({x.thread_id}) — {x.status}" for x in all_unfiltered if x.thread_id == tid), tid),
                key="pf_del_select",
            )
            d_col1, d_col2 = st.columns([2, 1.2])
            with d_col1:
                delete_disk = st.checkbox(
                    "Fiziksel disk klasörünü de (`output_uygulamalar`) temizle",
                    value=True,
                    key="pf_del_disk_chk",
                )
            with d_col2:
                if st.button("⚠️ Projeyi Kalıcı Olarak Sil", type="primary", use_container_width=True, key="pf_btn_delete"):
                    matching = [p for p in all_unfiltered if p.thread_id == del_thread]
                    slug = matching[0].slug if matching else None
                    if app_repository.delete_project(del_thread, slug=slug, delete_disk=delete_disk):
                        remaining = app_repository.list_thread_ids()
                        if st.session_state.get("active_thread") == del_thread:
                            st.session_state.active_thread = remaining[0] if remaining else app_repository.create_project("app-yeni")
                        st.success(f"`{del_thread}` başarıyla silindi!")
                        st.rerun()
                    else:
                        st.error("Silme işlemi sırasında hata oluştu.")
        else:
            st.info("Silinecek proje bulunmuyor.")

    # Time-Travel Audit (READ)
    with st.expander(f"⏱️ Aktif Uygulamanın (`{active_thread}`) Checkpoint Zaman Çizelgesi (Time-Travel Audit)", expanded=False):
        history = app_repository.get_checkpoint_history(active_thread, studio_app)
        if history:
            h_rows = [
                {
                    "Adım": rec.step,
                    "Kaynak": rec.source,
                    "Sıradaki Düğüm": rec.next_node,
                    "Checkpoint ID": rec.checkpoint_id[:18] + "..." if rec.checkpoint_id else "-",
                }
                for rec in history
            ]
            st.dataframe(pd.DataFrame(h_rows), use_container_width=True, hide_index=True)
        else:
            st.caption("Bu proje için henüz LangGraph checkpoint geçmişi oluşmadı.")
