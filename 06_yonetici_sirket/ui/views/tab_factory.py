"""
View: Tab 1 - Cyclical Software Factory & Human-in-the-Loop Gate.
"""

from langchain_core.messages import HumanMessage
import streamlit as st
from domain.state import CompanyState
from services.studio_service import studio_service
from ui.components.cyclical_matrix import render_cyclical_matrix


def render_factory_view(thread_id: str):
    """Render Tab 1: Software Factory Execution & HITL Approval/Revision."""
    st.markdown("#### 🏭 Döngüsel Yazılım Fabrikası (Cyclical LangGraph Studio)")
    st.caption("PRD ➔ Sistem Mimarisi ➔ Kodlama ➔ AST/QA Doğrulama ➔ HITL Kurucu Onayı döngüsü.")

    # 1. Cyclical Graph Matrix Widget
    render_cyclical_matrix(thread_id)

    st.divider()

    values, next_nodes, waiting_hitl = studio_service.get_state(thread_id)
    is_deployed = bool(values.get("is_deployed"))

    # 2. Human-in-the-Loop (HITL) Gate
    if waiting_hitl:
        st.markdown(
            f"""
<div class="hitl-box">
    <div style="font-size: 16px; font-weight: 700; color: #f59e0b; margin-bottom: 8px;">
        🛑 KURUCU BAŞKAN ONAY VE REVİZYON KAPISI (HITL GATE)
    </div>
    <div style="color: #cbd5e1; font-size: 13px;">
        Uygulama kodlandı ve QA/AST denetiminden başarıyla geçti! 
        Şimdi kodu inceleyebilir, doğrudan <b>fiziksel diske paketlenmesini onaylayabilir</b> ya da 
        <b>revizyon talimatı vererek</b> fabrikayı yeniden çalıştırabilirsiniz.
    </div>
</div>
""",
            unsafe_allow_html=True
        )

        app_name = values.get("app_name") or "Uygulama"
        app_type = values.get("app_type") or "Streamlit Web App"
        total_loc = values.get("total_loc") or 0
        c_files = values.get("code_files") or {}

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Uygulama Adı", app_name)
        with c2:
            st.metric("Mimari Tipi", app_type)
        with c3:
            st.metric("Toplam Satır (LOC)", f"{total_loc} satır ({len(c_files)} dosya)")

        # Approval & Revision Actions
        col_approve, col_revise = st.columns([1, 1])
        with col_approve:
            if st.button("🚀 Kodu Onayla ve Diske İnşa Et", type="primary", use_container_width=True):
                with st.spinner("Uygulama diske paketleniyor ve baslat.bat üretiliyor..."):
                    for ev in studio_service.approve_and_deploy(thread_id):
                        st.session_state.factory_logs.append(f"Deploy Event: {list(ev.keys())}")
                st.success("Tebrikler! Uygulama başarıyla paketlendi. '2. Kod Gezgini & Çalıştırma' sekmesinden başlatabilirsiniz.")
                st.rerun()

        with col_revise:
            with st.expander("🔄 Revizyon / Ekstra Özellik İste", expanded=False):
                rev_text = st.text_area("İstediğiniz değişiklik veya hata düzeltmesi:", placeholder="Örn: 'Veritabanına kategori filtresi ekle ve grafik çizdir.'")
                rev_target = st.selectbox(
                    "Geri Gönderilecek Departman:",
                    options=["Lead_Developer", "System_Architect", "Product_Lead"],
                    index=0
                )
                if st.button("Revizyonu Başlat", use_container_width=True) and rev_text.strip():
                    with st.spinner("Fabrika revizyon döngüsü için uyandırılıyor..."):
                        for ev in studio_service.request_revision(thread_id, rev_text, rev_target):
                            st.session_state.factory_logs.append(f"Revision Event: {list(ev.keys())}")
                    st.rerun()

    # 3. New Application Build Form
    elif not is_deployed and not values.get("prd_spec"):
        st.markdown("**🚀 Yeni Uygulama İmalat Direktifi Verin:**")
        with st.form("start_build_form"):
            directive = st.text_area(
                "Uygulama Hedefi ve İhtiyaçlar:",
                value="Bireysel kullanıcılar için aylık dijital aboneliklerini SQLite3 veritabanında saklayan, toplam maliyeti hesaplayan ve kategori özetleri sunan modüler bir Streamlit web uygulaması geliştirin.",
                height=90
            )
            submit = st.form_submit_button("⚡ Otonom İmalat Döngüsünü Başlat", type="primary", use_container_width=True)

        if submit and directive.strip():
            initial_state = {
                "messages": [HumanMessage(content=directive)],
                "next_step": "Studio_Director",
                "app_name": None,
                "app_slug": None,
                "app_type": None,
                "purpose_summary": None,
                "core_features": None,
                "prd_spec": None,
                "tech_stack": None,
                "database_choice": None,
                "entrypoint_file": None,
                "planned_files": None,
                "architecture_spec": None,
                "code_files": None,
                "total_loc": 0,
                "code_verified_by_qa": False,
                "qa_passed": False,
                "qa_report": None,
                "qa_issues": [],
                "revision_count": 0,
                "founder_feedback": None,
                "feedback_target": None,
                "is_deployed": False,
                "app_folder": None,
                "run_command_hint": None,
                "cycle_count": 0,
                "transition_log": [],
            }
            with st.spinner("Stüdyo motoru döngüsel grafı icra ediyor (PRD ➔ Mimari ➔ Kodlama ➔ AST/QA)..."):
                for event in studio_service.run_cycle(thread_id, initial_state):
                    node_name = list(event.keys())[0] if event else "Node"
                    st.session_state.factory_logs.append(f"Döngü Adımı: {node_name}")
            st.rerun()

    elif is_deployed:
        st.success(f"🎉 Bu proje tamamlandı ve kuruldu! Dizin: `{values.get('app_folder')}`")
        st.caption("Çalıştırmak veya kodları incelemek için '2. Kod Gezgini & Çalıştırma' sekmesine geçin.")
