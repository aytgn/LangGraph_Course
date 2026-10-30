"""
View: Tab 0 - Product & Architecture Discovery Room (CPO & CTO Deliberation).
"""

import streamlit as st
from services.discovery_service import discovery_service


def render_ideation_view(thread_id: str):
    """Render Tab 0: Ideation, CPO/CTO consulting, and ADR bridge."""
    st.markdown("#### 💡 Ürün & Mimari Tartışma Odası")
    st.caption(
        "Burada ne uygulaması yapacağımızı, hangi somut problemi çözeceğini (CPO) ve "
        "hangi altyapı/teknoloji yığınıyla (CTO) geliştireceğimizi tartışırız."
    )

    col_chat, col_vault = st.columns([3, 2])

    with col_chat:
        st.markdown("**💬 Kurucu - CPO & CTO Tartışma Paneli**")

        # Display discussion history
        for msg in st.session_state.ideation_chat:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                with st.chat_message("user", avatar="👑"):
                    st.markdown(f"**Kurucu Başkan:**\n{content}")
            elif role == "cpo":
                with st.chat_message("assistant", avatar="💡"):
                    st.markdown(f"**CPO (Ürün Vizyoneri):**\n{content}")
            elif role == "cto":
                with st.chat_message("assistant", avatar="📐"):
                    st.markdown(f"**CTO (Baş Mimar):**\n{content}")

        # Input form
        with st.form("ideation_form", clear_on_submit=True):
            user_input = st.text_area(
                "Fikrinizi veya sorunuzu yazın:",
                placeholder="Örn: 'Bireysel abonelik maliyetlerini takip eden yerel bir SQLite Streamlit uygulaması yapalım.'",
                height=100
            )
            col1, col2 = st.columns(2)
            with col1:
                ask_cpo = st.form_submit_button("💡 CPO'ya Danış (Ürün & MVP Kapsamı)", use_container_width=True)
            with col2:
                ask_cto = st.form_submit_button("📐 CTO'ya Danış (Tech Stack & Mimari)", use_container_width=True)

        if ask_cpo and user_input.strip():
            st.session_state.ideation_chat.append({"role": "user", "content": user_input})
            with st.spinner("CPO ürün vizyonunu değerlendiriyor..."):
                reply = discovery_service.consult_cpo(user_input, st.session_state.ideation_chat)
                st.session_state.ideation_chat.append({"role": "cpo", "content": reply})
            st.rerun()

        if ask_cto and user_input.strip():
            st.session_state.ideation_chat.append({"role": "user", "content": user_input})
            # Combine last CPO message as context if available
            cpo_ctx = "\n".join([m["content"] for m in st.session_state.ideation_chat if m["role"] == "cpo"][-2:])
            with st.spinner("CTO teknoloji ve altyapı eleştirisini hazırlıyor..."):
                reply = discovery_service.consult_cto(user_input, cpo_ctx, st.session_state.ideation_chat)
                st.session_state.ideation_chat.append({"role": "cto", "content": reply})
            st.rerun()

    with col_vault:
        st.markdown("**🏛️ İkinci Beyin & Mimari Kararlar (ADR)**")
        st.caption("Tartışılan fikirleri kalıcı ADR kararına dönüştürün ve fabrikaya aktarın:")

        if st.session_state.ideation_chat:
            if st.button("📝 Tartışmayı ADR ve Nota Dönüştür", use_container_width=True):
                with st.spinner("Mühendislik şartnamesi ve ADR üretiliyor..."):
                    disc_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.ideation_chat])
                    adr_path, note_path = discovery_service.finalize_adr_and_note(disc_text)
                    st.success(f"ADR Kaydedildi: `{adr_path}`")
                    st.info(f"Not Kaydedildi: `{note_path}`")

        st.divider()
        st.markdown("**🌟 Şirket Manifestosu & Mühendislik İlkeleri**")
        with st.expander("Manifestoyu İncele / Düzenle", expanded=False):
            vision_text = discovery_service.get_vision_manifesto()
            new_vision = st.text_area("Manifesto:", value=vision_text, height=220)
            if st.button("💾 Manifestoyu Kaydet", use_container_width=True):
                if discovery_service.update_vision_manifesto(new_vision):
                    st.success("Manifesto güncellendi!")
                    st.rerun()
