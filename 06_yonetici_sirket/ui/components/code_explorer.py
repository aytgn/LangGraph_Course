"""
Multi-File Code Explorer & Syntax Viewer Component.
"""

from typing import Dict
import streamlit as st


def render_code_explorer(code_files: Dict[str, str], entrypoint: str = "app.py"):
    """Render tabs for each generated code file with syntax highlighting."""
    if not code_files:
        st.info("Bu proje için henüz kod üretilmedi.")
        return

    filenames = sorted(list(code_files.keys()))
    # Put entrypoint first if present
    if entrypoint in filenames:
        filenames.remove(entrypoint)
        filenames.insert(0, entrypoint)

    tabs = st.tabs([f"📄 {fname}" for fname in filenames])
    for idx, fname in enumerate(filenames):
        with tabs[idx]:
            code = code_files[fname]
            loc = len([l for l in code.split("\n") if l.strip()])
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.caption(f"Dosya: `{fname}` • Satır Sayısı: **{loc}**")
            with col_b:
                st.download_button(
                    label="💾 İndir",
                    data=code,
                    file_name=fname,
                    mime="text/plain",
                    key=f"dl_{fname}_{idx}",
                    use_container_width=True
                )
            
            lang = "python" if fname.endswith(".py") else ("markdown" if fname.endswith(".md") else "text")
            st.code(code, language=lang, line_numbers=True)
