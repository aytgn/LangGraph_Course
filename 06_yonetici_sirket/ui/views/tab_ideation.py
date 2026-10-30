"""
View: Tab 0 - Product & Architecture Discovery Room (CPO, CTO & Technical PM Council).
Includes 1-Click Bridge to Software Factory and Full Second Brain Vault CRUD.
"""

import streamlit as st
from data.repositories.vault_repository import vault_repository
from services.discovery_service import discovery_service


QUICK_TOPICS = [
    "💳 Bireysel abonelik ve tekrarlayan giderleri takip eden yerel SQLite + Streamlit uygulaması tasarlayalım.",
    "📦 KOBİ depoları için kritik stok uyarılı FastAPI + SQLite REST mikroservisi planlayalım.",
    "🔍 Sunucu log dosyalarını ayrıştırıp hata özeti çıkaran modüler bir Python CLI aracı kurgulayalım.",
]


def _handle_ideation_turn(user_msg: str, mode: str, ui_pref: str, db_pref: str) -> None:
    prior_history = list(st.session_state.ideation_chat)
    pref_hint = ""
    if ui_pref != "Otomatik (Konsey Önersin)" or db_pref != "Otomatik (Konsey Önersin)":
        pref_hint = f"\n\n[Kurucu Teknik Tercihi -> Arayüz: {ui_pref} | Veri Katmanı: {db_pref}]"

    enriched_msg = user_msg.strip() + pref_hint
    st.session_state.ideation_chat.append({"role": "user", "content": user_msg.strip()})

    if mode.startswith("🏛️"):
        with st.spinner("🏛️ Ürün & Mimari Konseyi (CPO + CTO + Teknik PM) tartışıyor..."):
            res = discovery_service.run_council_debate(enriched_msg, prior_history)
            st.session_state.ideation_chat.append({"role": "cpo", "content": res["cpo"]})
            st.session_state.ideation_chat.append({"role": "cto", "content": res["cto"]})
            st.session_state.ideation_chat.append({"role": "scribe", "content": res["scribe"]})
    elif mode.startswith("💡"):
        with st.spinner("💡 CPO ürün kapsamını ve MVP özelliklerini değerlendiriyor..."):
            reply = discovery_service.consult_cpo(enriched_msg, prior_history)
            st.session_state.ideation_chat.append({"role": "cpo", "content": reply})
    else:
        with st.spinner("📐 CTO teknoloji yığınını ve modüler mimariyi değerlendiriyor..."):
            reply = discovery_service.consult_cto(enriched_msg, prior_history)
            st.session_state.ideation_chat.append({"role": "cto", "content": reply})


def render_ideation_view(thread_id: str):
    """Render Tab 0: Product & Tech Stack Deliberation, Factory Bridge, and Vault CRUD."""
    st.markdown("#### 💡 Ürün & Mimari Tartışma Odası (CPO • CTO • Teknik PM)")
    st.caption(
        "Ne uygulaması yapacağımızı, hangi problemi çözeceğini (CPO) ve hangi altyapı/teknolojiyle (CTO) "
        "inşa edeceğimizi tartışın; kararlaştırılan şartnameyi tek tıkla Yazılım Fabrikası'na aktarın."
    )

    # Show active bridge notification if recently queued
    queued = st.session_state.get("queued_factory_directive")
    if queued and queued.get("thread_id") == thread_id:
        st.markdown(
            f"""
<div class="bridge-box">
    <div style="font-weight:700; color:#4ade80; font-size:14px;">
        ✅ Mühendislik Şartnamesi Hazırlandı: {queued.get('title', thread_id)} (Proje: <code>{thread_id}</code>)
    </div>
    <div style="font-size:12.5px; color:#cbd5e1; margin-top:4px;">
        Şimdi üst menüden <b>🏭 1. Canlı Yazılım Fabrikası</b> sekmesine geçerek şartnameyi onaylayıp imalatı başlatabilirsiniz.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    col_chat, col_vault = st.columns([3, 2], gap="large")

    with col_chat:
        p1, p2 = st.columns(2)
        with p1:
            ui_pref = st.selectbox(
                "🖥️ Tercih Edilen Uygulama Tipi:",
                options=[
                    "Otomatik (Konsey Önersin)",
                    "Streamlit Web App",
                    "FastAPI REST Service",
                    "CLI & Automation Tool",
                    "Pure Python Package",
                ],
                key="id_ui_pref",
            )
        with p2:
            db_pref = st.selectbox(
                "🗄️ Tercih Edilen Veri Katmanı:",
                options=[
                    "Otomatik (Konsey Önersin)",
                    "SQLite3 (Yerel Kalıcı DB)",
                    "JSON / Dosya Tabanlı",
                    "Bellek İçi (In-Memory)",
                ],
                key="id_db_pref",
            )

        council_mode = st.radio(
            "🗣️ Görüşme Modu:",
            options=[
                "🏛️ Ürün & Mimari Konseyi (CPO + CTO Birlikte)",
                "💡 Sadece CPO (Ürün Amacı & MVP Kapsamı)",
                "📐 Sadece CTO (Teknoloji Yığını & Altyapı)",
            ],
            horizontal=True,
            key="id_council_mode",
        )

        # Quick starter buttons when discussion is empty
        if not st.session_state.ideation_chat:
            st.caption("⚡ Hızlı Tartışma Başlatıcılar:")
            q_cols = st.columns(3)
            q_labels = ["💳 Abonelik App", "📦 Depo Stok API", "🔍 LogAnaliz CLI"]
            for idx, lbl in enumerate(q_labels):
                with q_cols[idx]:
                    if st.button(lbl, key=f"id_quick_{idx}", use_container_width=True):
                        _handle_ideation_turn(QUICK_TOPICS[idx], council_mode, ui_pref, db_pref)
                        st.rerun()

        # Conversation history container
        chat_box = st.container(height=390, border=True)
        with chat_box:
            if not st.session_state.ideation_chat:
                st.info(
                    "👋 Henüz tartışma başlamadı. Aşağıdaki sohbet kutusundan uygulama fikrinizi yazarak "
                    "CPO ve CTO ile kapsam & mimari istişaresi başlatabilirsiniz."
                )
            for msg in st.session_state.ideation_chat:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    with st.chat_message("user", avatar="👑"):
                        st.markdown(f"**Kurucu Başkan:**\n\n{content}")
                elif role == "cpo":
                    with st.chat_message("assistant", avatar="💡"):
                        st.markdown(f"**CPO (Ürün & MVP Lideri):**\n\n{content}")
                elif role == "cto":
                    with st.chat_message("assistant", avatar="📐"):
                        st.markdown(f"**CTO (Baş Sistem Mimarı):**\n\n{content}")
                elif role == "scribe":
                    with st.chat_message("assistant", avatar="📋"):
                        st.markdown(f"**Teknik PM (Uygulama & Mimari Yol Haritası):**\n\n{content}")

        user_prompt = st.chat_input(
            "Uygulama fikrinizi, hedef kitlesini veya altyapı sorunuzu yazın...",
            key="ideation_chat_input",
        )
        if user_prompt and user_prompt.strip():
            _handle_ideation_turn(user_prompt, council_mode, ui_pref, db_pref)
            st.rerun()

        # Action bar: Bridge to Factory, Save ADR, Clear
        b1, b2, b3 = st.columns([2.4, 1.8, 1.1])
        has_chat = len(st.session_state.ideation_chat) > 0
        with b1:
            if st.button(
                "🚀 Fabrikaya Şartname Olarak Aktar",
                type="primary",
                disabled=not has_chat,
                use_container_width=True,
                key="id_btn_bridge",
            ):
                with st.spinner("Teknik PM tartışmayı mühendislik şartnamesine dönüştürüyor ve yeni proje açıyor..."):
                    prefs = f"Tercih Edilen Tip: {ui_pref} | Veri Katmanı: {db_pref}"
                    bridged = discovery_service.bridge_discussion_to_factory(
                        st.session_state.ideation_chat,
                        custom_notes=prefs,
                    )
                    st.session_state.active_thread = bridged["thread_id"]
                    st.session_state.queued_factory_directive = {
                        "thread_id": bridged["thread_id"],
                        "title": bridged["title"],
                        "directive": bridged["directive_text"],
                        "source": "Ürün & Mimari Konseyi",
                    }
                st.rerun()
        with b2:
            if st.button(
                "📝 ADR & Not Kaydet",
                disabled=not has_chat,
                use_container_width=True,
                key="id_btn_adr",
            ):
                with st.spinner("ADR kararı ve keşif notu İkinci Beyin'e kaydediliyor..."):
                    disc_text = "\n\n".join(
                        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.ideation_chat]
                    )
                    adr_path, note_path = discovery_service.finalize_adr_and_note(disc_text)
                    st.success(f"ADR ve Not kaydedildi! (`{adr_path}`)")
        with b3:
            if st.button("🧹 Temizle", disabled=not has_chat, use_container_width=True, key="id_btn_clear"):
                st.session_state.ideation_chat = []
                st.rerun()

    with col_vault:
        st.markdown("##### 🗄️ İkinci Beyin Hafızası (`meta_bellek/` CRUD)")
        st.caption("Şirket manifestosu, ADR kararları, keşif notları ve üretilen şartnameleri okuyun, düzenleyin veya silin:")

        docs = vault_repository.list_all_vault_documents()
        if docs:
            doc_labels = [f"[{d.category}] {d.title} ({d.filename})" for d in docs]
            sel_idx = st.selectbox(
                "📂 İncelenecek Belge:",
                options=list(range(len(docs))),
                format_func=lambda i: doc_labels[i],
                key="vault_doc_select",
            )
            chosen_doc = docs[sel_idx]
            full_text = vault_repository.read_item(chosen_doc.filepath)

            st.caption(f"Son Güncelleme: `{chosen_doc.updated_at}` • Dosya: `{chosen_doc.filename}`")
            edited_doc = st.text_area(
                "Belge İçeriği (Markdown):",
                value=full_text,
                height=340,
                key=f"vault_editor_{chosen_doc.filename}",
            )

            vc1, vc2 = st.columns(2)
            with vc1:
                if st.button("💾 Belgeyi Güncelle", use_container_width=True, key="vault_btn_save"):
                    ok = vault_repository.update_item(chosen_doc.filepath, edited_doc)
                    if ok:
                        st.success("Belge güncellendi!")
                        st.rerun()
                    else:
                        st.error("Belge güncellenemedi.")
            with vc2:
                is_vision = chosen_doc.category == "Vizyon & Manifesto"
                if st.button(
                    "🗑️ Belgeyi Sil",
                    disabled=is_vision,
                    use_container_width=True,
                    key="vault_btn_delete",
                    help="Ana şirket manifestosu silinemez; diğer ADR ve notlar silinebilir.",
                ):
                    if vault_repository.delete_item(chosen_doc.filepath):
                        st.success(f"`{chosen_doc.filename}` silindi.")
                        st.rerun()
        else:
            st.info("İkinci Beyin kasasında henüz belge bulunmuyor.")
