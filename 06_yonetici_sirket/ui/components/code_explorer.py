"""
Multi-File Code Explorer, Syntax Viewer & Inline AST-Verified Editor Component.
"""

from typing import Dict, Optional
import streamlit as st
from services.studio_service import studio_service


def render_code_explorer(
    code_files: Dict[str, str],
    entrypoint: str = "app.py",
    thread_id: Optional[str] = None,
    allow_edit: bool = False,
    key_prefix: str = "ws",
):
    """Render tabs for each generated code file with syntax highlighting and optional live editor."""
    if not code_files:
        st.info("Bu proje için henüz kaynak kod üretilmedi.")
        return

    filenames = sorted(list(code_files.keys()))
    if entrypoint in filenames:
        filenames.remove(entrypoint)
        filenames.insert(0, entrypoint)

    tabs = st.tabs([f"📄 {fname}" for fname in filenames])
    for idx, fname in enumerate(filenames):
        with tabs[idx]:
            code = code_files[fname]
            loc = len([line for line in code.split("\n") if line.strip()])
            col_a, col_b = st.columns([4, 1])
            with col_a:
                entry_tag = " • ⭐ Giriş Noktası (Entrypoint)" if fname == entrypoint else ""
                st.caption(f"Dosya: `{fname}` • Satır Sayısı: **{loc} LOC**{entry_tag}")
            with col_b:
                st.download_button(
                    label="💾 Dosyayı İndir",
                    data=code,
                    file_name=fname,
                    mime="text/plain",
                    key=f"{key_prefix}_dl_{fname}_{idx}",
                    use_container_width=True,
                )

            if fname.endswith(".py"):
                lang = "python"
            elif fname.endswith(".md"):
                lang = "markdown"
            elif fname.endswith(".json"):
                lang = "json"
            else:
                lang = "text"

            st.code(code, language=lang, line_numbers=True)

            if allow_edit and thread_id:
                with st.expander(f"✏️ `{fname}` Dosyasını Elle Düzenle & AST Doğrula (CRUD UPDATE)", expanded=False):
                    edited_text = st.text_area(
                        "Dosya İçeriği:",
                        value=code,
                        height=280,
                        key=f"{key_prefix}_edit_{thread_id}_{fname}_{idx}",
                    )
                    if st.button(
                        f"💾 `{fname}` Değişikliğini Kaydet ve AST Testinden Geçir",
                        key=f"{key_prefix}_save_{thread_id}_{fname}_{idx}",
                        use_container_width=True,
                    ):
                        passed, errors = studio_service.save_edited_code_file(thread_id, fname, edited_text)
                        if passed:
                            st.success(f"`{fname}` güncellendi ve deterministik AST doğrulamasından başarıyla geçti!")
                            st.rerun()
                        else:
                            st.warning(
                                f"`{fname}` kaydedildi ancak AST denetçisi {len(errors)} sözdizimi/import uyarısı buldu:"
                            )
                            for err in errors:
                                st.error(err)
