"""
Live LangGraph Stream Runner Component.
Displays real-time department transitions inside Streamlit st.status.
"""

from typing import Dict, Any, Generator
import streamlit as st


def render_live_studio_stream(
    event_generator: Generator[Dict[str, Any], None, None],
    status_title: str = "🔄 Otonom Yazılım Fabrikası Çalışıyor...",
) -> None:
    """Consume a StudioService stream generator and render live department updates."""
    with st.status(status_title, expanded=True) as status_box:
        for event in event_generator:
            if not isinstance(event, dict):
                continue
            for node_name, node_out in event.items():
                if "factory_logs" in st.session_state:
                    st.session_state.factory_logs.append(f"Adım: {node_name}")

                if node_name == "__interrupt__":
                    st.warning(
                        "🛑 **Kurucu Onay / Red / Revizyon Kapısına (HITL Gate)** ulaşıldı! "
                        "Aşağıdaki panelden kodu inceleyip onaylayabilir, revizyon isteyebilir veya reddedebilirsiniz."
                    )
                    continue

                if not isinstance(node_out, dict):
                    continue

                if node_name == "Studio_Director":
                    nxt = node_out.get("next_step", "")
                    cyc = node_out.get("cycle_count", "")
                    st.write(f"👑 **Stüdyo Direktörü (Döngü #{cyc})** ➔ Sıradaki hedef: `{nxt}`")
                elif node_name == "Product_Lead":
                    st.write(
                        f"💡 **Ürün Lideri (CPO):** `{node_out.get('app_name', 'Uygulama')}` "
                        f"({node_out.get('app_type', '-')}) için PRD ve MVP kapsamı hazırlandı."
                    )
                elif node_name == "System_Architect":
                    files_cnt = len(node_out.get("planned_files") or [])
                    st.write(
                        f"📐 **Baş Sistem Mimarı (CTO):** Teknoloji yığını ve **{files_cnt} modüllük** "
                        "mimari sözleşme tasarlandı."
                    )
                elif node_name == "Lead_Developer":
                    f_cnt = len(node_out.get("code_files") or {})
                    loc = node_out.get("total_loc", 0)
                    st.write(
                        f"💻 **Kıdemli Mühendis:** **{f_cnt} kaynak dosya** (**{loc} satır Python kodu**) üretildi."
                    )
                elif node_name == "QA_Security_Lead":
                    if node_out.get("qa_passed"):
                        st.write("🛡️ **QA & Güvenlik Lideri:** ✅ Deterministik AST ve çapraz modül denetimi **BAŞARILI**!")
                    else:
                        issues = node_out.get("qa_issues") or []
                        st.write(
                            f"🛡️ **QA & Güvenlik Lideri:** ⚠️ **{len(issues)} sorun** tespit edildi — "
                            "düzeltme için Kıdemli Mühendise geri yönlendiriliyor..."
                        )
                elif node_name == "Deployment_Gate":
                    if node_out.get("is_deployed"):
                        st.write(
                            f"🚀 **Dağıtım Kapısı:** Fiziksel uygulama paketi inşa edildi ➔ `{node_out.get('app_folder', '')}`"
                        )
                    else:
                        st.write("🛑 **Dağıtım Kapısı:** İşlem atlandı (revizyon veya reddetme koruması).")

        status_box.update(label="✅ Stüdyo Döngü Adımı Tamamlandı!", state="complete", expanded=False)
