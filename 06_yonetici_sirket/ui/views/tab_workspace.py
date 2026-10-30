"""
View: Tab 2 - Workspace, Multi-File Code Explorer, Live Editor & 1-Click Launcher.
"""

import os
import subprocess
from pathlib import Path
import streamlit as st
from services.studio_service import studio_service
from ui.components.code_explorer import render_code_explorer


def render_workspace_view(thread_id: str):
    """Render Tab 2: Code Explorer, AST-Verified Manual Editor, 1-Click Launch, and ZIP Export."""
    values, next_nodes, waiting_hitl = studio_service.get_state(thread_id)
    c_files = values.get("code_files") or {}
    app_folder = values.get("app_folder")
    entrypoint = values.get("entrypoint_file") or "app.py"
    app_name = values.get("app_name") or "Uygulama"
    is_deployed = bool(values.get("is_deployed"))
    is_rejected = bool(values.get("is_rejected"))

    st.markdown("#### 💻 Üretilen Çok Dosyalı Kod Gezgini, Düzenleyici & Çalıştırma Konsolu")

    if not c_files:
        st.info(
            "Bu proje için henüz kaynak kod üretilmedi. Lütfen **🏭 1. Canlı Yazılım Fabrikası** sekmesinden "
            "uygulama imalatını başlatın."
        )
        return

    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Uygulama", app_name)
    with m2:
        st.metric("Mimari Tipi", values.get("app_type") or "-")
    with m3:
        st.metric("Veri Katmanı", values.get("database_choice") or "-")
    with m4:
        st.metric("Dosya / Satır", f"{len(c_files)} dosya / {values.get('total_loc', 0)} LOC")

    if waiting_hitl and not is_deployed:
        st.warning(
            "🛑 Bu kod şu anda **Kurucu Karar Kapısında** bekliyor. Aşağıdan tüm dosyaları inceleyebilir, "
            "elle düzenleyebilir veya **1. Canlı Yazılım Fabrikası** sekmesinden onaylayıp diske kurabilirsiniz."
        )
    elif is_rejected:
        st.error(f"❌ Bu projenin kodu reddedildi: {values.get('rejection_reason') or ''}")

    # Top Action Bar: Run bat, Open Explorer, Download Zip
    col_run, col_open, col_zip = st.columns(3)

    bat_file = Path(app_folder) / "baslat.bat" if app_folder else None
    has_physical_folder = bool(app_folder and os.path.exists(app_folder))

    with col_run:
        if bat_file and bat_file.exists():
            if st.button(
                "🚀 Uygulamayı Başlat (Yeni Pencere)",
                type="primary",
                use_container_width=True,
                key=f"ws_run_{thread_id}",
            ):
                try:
                    # Empty title "" after 'start' prevents Windows cmd from treating quoted path as window title
                    subprocess.Popen(
                        ["cmd.exe", "/c", "start", "", str(bat_file)],
                        cwd=str(app_folder),
                    )
                    st.success("Uygulama yeni konsol penceresinde başlatıldı!")
                except Exception as e:
                    st.error(f"Başlatma hatası: {e}")
        else:
            st.button(
                "🚀 Uygulamayı Başlat (Önce 1. Sekmeden Onaylayın)",
                disabled=True,
                use_container_width=True,
                key=f"ws_run_disabled_{thread_id}",
            )

    with col_open:
        if has_physical_folder:
            if st.button("📂 Klasörü Aç (Explorer)", use_container_width=True, key=f"ws_open_{thread_id}"):
                try:
                    os.startfile(str(app_folder))
                except Exception as e:
                    st.error(f"Klasör açılamadı: {e}")
        else:
            st.button(
                "📂 Klasörü Aç (Henüz Diske Kurulmadı)",
                disabled=True,
                use_container_width=True,
                key=f"ws_open_disabled_{thread_id}",
            )

    with col_zip:
        zip_bytes = studio_service.generate_zip_bytes(values)
        slug = values.get("app_slug") or thread_id
        st.download_button(
            label="📦 Tüm Paketi ZIP Olarak İndir",
            data=zip_bytes,
            file_name=f"{slug}_studio_bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key=f"ws_zip_{thread_id}",
        )

    if has_physical_folder:
        st.caption(f"📁 Fiziksel Dizin: `{app_folder}` • ⚡ Çalıştırma Komutu: `{values.get('run_command_hint', '')}`")

    st.divider()

    # Sub-tabs for Code, PRD, Architecture, and QA Report
    sub_code, sub_prd, sub_arch, sub_qa = st.tabs([
        "📂 Çok Dosyalı Kaynak Kodu & Düzenleyici",
        "💡 Ürün Şartnamesi (PRD)",
        "📐 Sistem Mimarisi",
        "🛡️ QA & AST Raporu",
    ])

    with sub_code:
        render_code_explorer(
            c_files,
            entrypoint=entrypoint,
            thread_id=thread_id,
            allow_edit=True,
            key_prefix=f"ws_{thread_id}",
        )

    with sub_prd:
        st.markdown(values.get("prd_spec") or "PRD belgesi bulunamadı.")

    with sub_arch:
        st.markdown(f"**Teknoloji Yığını:** `{', '.join(values.get('tech_stack') or [])}`")
        st.markdown(values.get("architecture_spec") or "Sistem mimarisi bulunamadı.")

    with sub_qa:
        if values.get("qa_passed"):
            st.success("✅ Deterministik AST Sözdizimi, Çapraz Modül Import ve QA Denetimi Başarılı!")
        else:
            st.warning("⚠️ QA / AST Denetiminde Açık Bulgular Mevcut")
        st.markdown(values.get("qa_report") or "QA raporu bulunamadı.")
        for issue in values.get("qa_issues") or []:
            st.error(issue)
