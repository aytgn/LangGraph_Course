"""
View: Tab 4 - Architecture, Dynamic Tool Registry Explorer & PDF Whitepaper.
"""

import pandas as pd
import streamlit as st
from tools.registry import ToolRegistry
from pdf_olusturucu import generate_enterprise_documentation_pdf


def render_architecture_view():
    """Render Tab 4: Clean Architecture Layers, Tool Registry, and PDF Export."""
    st.markdown("#### 🏛️ Kurumsal Clean Architecture Katmanları & Dinamik Araç Kayıt Defteri")
    st.caption(
        "`06_yonetici_sirket` modülü; `config`, `data`, `tools`, `domain`, `services` ve `ui` olmak üzere "
        "6 bağımsız kurumsal katman ve merkezi `ToolRegistry` üzerine inşa edilmiştir."
    )

    # 1. Clean Architecture Layer Overview
    l_cols = st.columns(3)
    layers = [
        ("1️⃣ Presentation (`ui/`)", "`views/`, `components/`, `styles.py`, `state.py` — Sıfır iş mantığı barındıran modüler Streamlit görünüm katmanı."),
        ("2️⃣ Application (`services/`)", "`StudioService` & `DiscoveryService` — Fabrika sohbeti, HITL onay/revizyon/red ve konsey köprüsü orkestrasyonu."),
        ("3️⃣ Domain (`domain/`)", "`CompanyState`, Pydantic şemalar, `StudioWorkflowBuilder` ve 6 uzman departman düğümü (`nodes/`)."),
        ("4️⃣ Dynamic Tools (`tools/`)", "`StudioTool` soyut sınıfı ve `ToolRegistry` — AST denetimi, paketleme ve kasa araçlarının dinamik yönetimi."),
        ("5️⃣ Persistence (`data/`)", "`DatabaseManager`, `AppRepository` & `VaultRepository` — SQLite WAL ve tam CRUD veri erişim katmanı."),
        ("6️⃣ Configuration (`config/`)", "`StudioConfig` — Kök `.env` yükleme, dizin hazırlama ve öz-iyileştirme / döngü limitleri."),
    ]
    for idx, (title, desc) in enumerate(layers):
        with l_cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(desc)

    st.divider()

    # 2. Registered Tools Table (Dynamic Tool Registry)
    st.markdown(f"##### 🛠️ Merkezi Kayıtlı Araçlar (`ToolRegistry` — {ToolRegistry.count()} Aktif Araç)")
    all_tools = ToolRegistry.list_all_tools()
    if all_tools:
        dept_filter = st.selectbox(
            "Departmana Göre Araç Filtrele:",
            options=["Tümü"] + sorted(list({t.get("department", "ALL") for t in all_tools})),
            key="arch_dept_filter",
        )
        filtered_tools = [
            t for t in all_tools if dept_filter == "Tümü" or t.get("department") == dept_filter
        ]
        tool_rows = [
            {
                "Araç Kodu": t.get("name"),
                "Sorumlu Departman": t.get("department"),
                "Kategori": t.get("category"),
                "Açıklama": t.get("description"),
            }
            for t in filtered_tools
        ]
        st.dataframe(pd.DataFrame(tool_rows), use_container_width=True, hide_index=True)

    st.divider()

    # 3. PDF Whitepaper Export
    st.markdown("##### 📑 Yönetici Teknik Whitepaper'ı (PDF)")
    col_pdf, col_desc = st.columns([1.2, 2.5])
    with col_desc:
        st.caption(
            "Stüdyo mimarisini, Clean Architecture katmanlarını, döngüsel LangGraph akışını ve güvenlik kapılarını "
            "içeren resmi PDF dokümanını indirebilirsiniz."
        )
    with col_pdf:
        try:
            pdf_bytes = generate_enterprise_documentation_pdf()
            st.download_button(
                label="📥 Teknik Whitepaper'ı İndir (PDF)",
                data=pdf_bytes,
                file_name="Otonom_Yazilim_Evi_Teknik_Whitepaper.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="arch_pdf_dl",
            )
        except Exception as e:
            st.error(f"PDF üretim hatası: {e}")
