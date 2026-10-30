"""
View: Tab 2 - Workspace, Code Explorer & 1-Click Launcher.
"""

import os
import subprocess
from pathlib import Path
import streamlit as st
from services.studio_service import studio_service
from ui.components.code_explorer import render_code_explorer


def render_workspace_view(thread_id: str):
    """Render Tab 2: Code Explorer, 1-Click Launch, and Package Download."""
    values, next_nodes, waiting_hitl = studio_service.get_state(thread_id)
    c_files = values.get("code_files") or {}
    app_folder = values.get("app_folder")
    entrypoint = values.get("entrypoint_file") or "app.py"
    app_name = values.get("app_name") or "Uygulama"

    st.markdown("#### 💻 Üretilen Çok Dosyalı Kod ve Çalıştırma Konsolu")

    if not c_files:
        st.info("Bu proje için henüz kaynak kod üretilmedi. Lütfen '1. Canlı Yazılım Fabrikası' sekmesinden imalatı başlatın.")
        return

    # Top Action Bar: Run bat, Download Zip
    col_run, col_zip, col_folder = st.columns([2, 2, 3])

    with col_run:
        bat_file = Path(app_folder) / "baslat.bat" if app_folder else None
        if bat_file and bat_file.exists():
            if st.button("🚀 Uygulamayı Başlat (Yeni Pencere)", type="primary", use_container_width=True):
                try:
                    subprocess.Popen(
                        ["cmd.exe", "/c", "start", str(bat_file)],
                        shell=True,
                        cwd=str(app_folder)
                    )
                    st.success("Uygulama ayrı konsol penceresinde başlatıldı!")
                except Exception as e:
                    st.error(f"Başlatma hatası: {e}")
        else:
            st.button("🚀 Uygulamayı Başlat (Henüz Kurulmadı)", disabled=True, use_container_width=True)

    with col_zip:
        zip_bytes = studio_service.generate_zip_bytes(values)
        slug = values.get("app_slug") or "uygulama"
        st.download_button(
            label="📦 Tüm Paketi ZIP Olarak İndir",
            data=zip_bytes,
            file_name=f"{slug}_studio_bundle.zip",
            mime="application/zip",
            use_container_width=True
        )

    with col_folder:
        if app_folder and os.path.exists(app_folder):
            st.caption(f"📁 Fiziksel Dizin: `{app_folder}`")
            st.caption(f"⚡ Komut: `{values.get('run_command_hint', '')}`")

    st.divider()

    # Code Explorer Tabs
    render_code_explorer(c_files, entrypoint=entrypoint)

    # Technical Specs Markdown Expander
    with st.expander("📘 Uygulama Mimari & PRD Şartnamesi (MIMARI_VE_PRD.md)", expanded=False):
        st.markdown(f"### {app_name} - Şartname")
        st.markdown(f"**Uygulama Tipi:** {values.get('app_type')}")
        st.markdown(f"**Veritabanı:** {values.get('database_choice')}")
        st.markdown(f"**Teknoloji Yığını:** {', '.join(values.get('tech_stack') or [])}")
        st.markdown("---")
        st.markdown(values.get("prd_spec") or "PRD belirtilmedi.")
        st.markdown("---")
        st.markdown(values.get("architecture_spec") or "Mimari belirtilmedi.")
