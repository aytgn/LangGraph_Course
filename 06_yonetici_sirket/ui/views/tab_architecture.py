"""
View: Tab 4 - Architecture, Tool Registry Explorer & PDF Whitepaper.
"""

import pandas as pd
import streamlit as st
from tools.registry import ToolRegistry
from pdf_olusturucu import generate_enterprise_documentation_pdf


def render_architecture_view():
    """Render Tab 4: System Architecture, Tool Registry, and PDF Export."""
    st.markdown("#### 🏛️ Otonom Yazılım Evi Mimarisi & Kayıtlı Araçlar")
    st.caption("Clean Architecture, dinamik Tool Registry ve döngüsel LangGraph sistem organizasyonu.")

    # 1. Registered Tools Table (Dynamic Tool Registry)
    st.markdown("##### 🛠️ Merkezi Kayıtlı Araçlar (Dynamic Tool Registry)")
    st.caption("Ajan departmanlarının kullandığı araçlar sabit kodlanmaz; merkezi ToolRegistry üzerinden dinamik olarak sunulur:")

    all_tools = ToolRegistry.list_all_tools()
    if all_tools:
        tool_rows = []
        for t in all_tools:
            tool_rows.append({
                "Araç Adı": t.get("name"),
                "Departman": t.get("department"),
                "Kategori": t.get("category"),
                "Açıklama": t.get("description"),
            })
        st.dataframe(pd.DataFrame(tool_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Kayıtlı araç bulunamadı.")

    st.divider()

    # 2. System Org Chart
    st.markdown("##### 🏢 Departman Rolleri & Sorumluluk Matrisi")
    st.markdown("""
* **👑 Stüdyo Direktörü (Studio Director):** Merkezi orkestratör; döngü sayısını, QA durumunu ve Kurucu revizyonlarını denetleyerek akışı yönlendirir.
* **💡 Ürün & Kapsam Lideri (CPO):** Ne uygulaması yapılacağını, hedef kitleyi, MVP özelliklerini ve başlangıç verilerini (PRD) belirler.
* **📐 Baş Sistem Mimarı (CTO):** Uygulama tipine en uygun teknoloji yığınını (`Streamlit`, `FastAPI`, `SQLite3`, `CLI`) ve modül sözleşmelerini tasarlar.
* **💻 Kıdemli Mühendis (Lead Developer):** PRD ve mimariye %100 sadık kalarak eksiksiz, çok dosyalı kaynak kodları üretir.
* **🛡️ QA & Güvenlik Lideri (QA Lead):** Deterministik Python AST ayrıştırması, çapraz modül import doğrulaması ve kod kalitesi denetimini yapar.
* **🚀 Dağıtım Kapısı (Deployment Gate):** Kurucu Başkan onayından sonra tüm dosyaları diske yazar, `baslat.bat` ve PRD dokümanını inşa eder.
""")

    st.divider()

    # 3. PDF Whitepaper Export
    st.markdown("##### 📑 Yönetici Teknik Whitepaper'ı (PDF)")
    col_pdf, col_desc = st.columns([1, 2])
    with col_desc:
        st.caption("Tüm stüdyo mimarisini, Clean Architecture katmanlarını ve teknik kılavuzu içeren resmi PDF raporu:")
    with col_pdf:
        try:
            pdf_bytes = generate_enterprise_documentation_pdf()
            st.download_button(
                label="📥 Teknik Whitepaper'ı İndir (PDF)",
                data=pdf_bytes,
                file_name="Otonom_Yazilim_Evi_Teknik_Whitepaper.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF üretim hatası: {e}")
