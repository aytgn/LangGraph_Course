"""
View: Tab 1 - Cyclical Software Factory, Direct Factory Chat & HITL Approve/Revise/Reject Gate.
"""

import streamlit as st
from services.studio_service import studio_service
from ui.components.cyclical_matrix import render_cyclical_matrix
from ui.components.code_explorer import render_code_explorer
from ui.components.stream_runner import render_live_studio_stream


DEPT_TARGET_OPTIONS = {
    "AUTO": "🤖 Otomatik (Stüdyo Direktörü Seçsin)",
    "Lead_Developer": "💻 Kıdemli Mühendis (Kod & Özellik Değişikliği)",
    "System_Architect": "📐 Sistem Mimarı / CTO (Altyapı & Modül Şeması)",
    "Product_Lead": "💡 Ürün Lideri / CPO (PRD & Kapsam Değişikliği)",
}


def _pick_avatar(role: str, content: str) -> str:
    if role == "user":
        return "👑"
    if "ÜRÜN LİDERİ" in content or "CPO" in content:
        return "💡"
    if "BAŞ SİSTEM MİMARI" in content or "CTO" in content:
        return "📐"
    if "KIDEMLİ MÜHENDİS" in content:
        return "💻"
    if "QA & GÜVENLİK" in content:
        return "🛡️"
    if "DAĞITIM KAPISI" in content:
        return "🚀"
    if "Fabrika Baş Mimarı" in content:
        return "🗣️"
    return "🏢"


def render_factory_view(thread_id: str):
    """Render Tab 1: Cyclical Matrix, HITL Approve/Revise/Reject Gate, and Direct Factory Chat."""
    st.markdown("#### 🏭 Döngüsel Yazılım Fabrikası & İletişim Masası")
    st.caption(
        "PRD ➔ Sistem Mimarisi ➔ Kodlama ➔ Deterministik AST/QA ➔ Kurucu Karar Kapısı (Onayla / Revize Et / Reddet) "
        "ve Fabrika Ekibiyle Doğrudan Görüşme alanı."
    )

    # 1. Cyclical Graph Matrix & Live Hop Trail
    render_cyclical_matrix(thread_id)

    values, next_nodes, waiting_hitl = studio_service.get_state(thread_id)
    is_deployed = bool(values.get("is_deployed"))
    is_rejected = bool(values.get("is_rejected"))
    has_prd = bool(values.get("prd_spec"))
    c_files = values.get("code_files") or {}

    # 2. Queued Specification Banner (from Tab 0 Bridge or Sidebar Sample Template)
    queued = st.session_state.get("queued_factory_directive")
    if queued and queued.get("thread_id") == thread_id:
        st.markdown(
            f"""
<div class="bridge-box">
    <div style="font-size:15px; font-weight:700; color:#4ade80;">
        📋 Üretime Hazır Uygulama Şartnamesi ({queued.get('source', 'Konsey')}): {queued.get('title', '')}
    </div>
    <div style="font-size:12.5px; color:#cbd5e1; margin-top:4px;">
        Şartnameyi aşağıdan inceleyip düzenleyebilir ve tek tıkla otonom yazılım fabrikasını başlatabilirsiniz.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        edited_spec = st.text_area(
            "Uygulama Geliştirme Şartnamesi:",
            value=queued.get("directive", ""),
            height=130,
            key=f"queued_spec_editor_{thread_id}",
        )
        qc1, qc2 = st.columns([3, 1])
        with qc1:
            if st.button(
                "⚡ Şartnameyi Onayla ve Otonom İmalatı Başlat",
                type="primary",
                use_container_width=True,
                key=f"btn_run_queued_{thread_id}",
            ):
                st.session_state.queued_factory_directive = None
                render_live_studio_stream(
                    studio_service.start_new_build(thread_id, edited_spec),
                    status_title="🏗️ Otonom Yazılım Fabrikası Şartnameyi İcra Ediyor...",
                )
                st.rerun()
        with qc2:
            if st.button("✖ Kuyruktan Kaldır", use_container_width=True, key=f"btn_cancel_queued_{thread_id}"):
                st.session_state.queued_factory_directive = None
                st.rerun()

    st.divider()

    # 3. Human-in-the-Loop (HITL) Decision Gate: APPROVE / REVISE / REJECT
    if waiting_hitl:
        app_name = values.get("app_name") or "Uygulama"
        app_type = values.get("app_type") or "Python App"
        total_loc = values.get("total_loc") or 0
        qa_ok = bool(values.get("qa_passed"))

        st.markdown(
            """
<div class="hitl-box">
    <div style="font-size: 16px; font-weight: 800; color: #fbbf24; margin-bottom: 6px;">
        🛑 KURUCU BAŞKAN KARAR KAPISI (ONAYLA • REVİZYON İSTE • KODU REDDET)
    </div>
    <div style="color: #e2e8f0; font-size: 13px;">
        Üretilen kaynak kodları hemen aşağıdaki önizleme kutusundan inceleyebilir, alt kısımdaki sohbet masasından 
        fabrika ekibine sorular sorabilir; ardından <b>Onaylayıp Diske Kurabilir</b>, <b>Revizyon İsteyebilir</b> 
        veya <b>Kodu Reddedebilirsiniz</b>.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Uygulama Adı", app_name)
        with m2:
            st.metric("Mimari Tipi", app_type)
        with m3:
            st.metric("Kod Boyutu", f"{len(c_files)} dosya / {total_loc} LOC")
        with m4:
            st.metric("AST / QA Denetimi", "✅ Başarılı" if qa_ok else "⚠️ Uyarı Var")

        # Inline Quick Code, QA & Architecture Preview right inside HITL Gate
        with st.expander("🔍 Karar Öncesi Hızlı İnceleme (Üretilen Kodlar, QA Raporu ve Mimari)", expanded=False):
            p_tab1, p_tab2, p_tab3 = st.tabs(["📂 Üretilen Kodlar", "🛡️ QA & AST Raporu", "📐 PRD & Mimari"])
            with p_tab1:
                render_code_explorer(
                    c_files,
                    entrypoint=values.get("entrypoint_file") or "app.py",
                    thread_id=thread_id,
                    allow_edit=False,
                    key_prefix=f"hitl_{thread_id}",
                )
            with p_tab2:
                st.markdown(values.get("qa_report") or "QA raporu bulunamadı.")
                if values.get("qa_issues"):
                    for iss in values["qa_issues"]:
                        st.warning(iss)
            with p_tab3:
                st.markdown(values.get("prd_spec") or "")
                st.markdown("---")
                st.markdown(values.get("architecture_spec") or "")

        # 3 Explicit Side-by-Side Decision Panels: Approve | Revise | Reject
        col_approve, col_revise, col_reject = st.columns(3, gap="medium")

        with col_approve:
            with st.container(border=True):
                st.markdown("##### ✅ 1. Onayla & Diske Kur")
                st.caption(
                    f"Tüm kaynak kodları, `requirements.txt`, `MIMARI_VE_PRD.md` ve tek tıkla çalıştırılabilir "
                    f"`baslat.bat` paketini `output_uygulamalar/{values.get('app_slug', 'app')}` dizinine inşa eder."
                )
                if st.button(
                    "🚀 Kodu Onayla ve Diske İnşa Et",
                    type="primary",
                    use_container_width=True,
                    key=f"hitl_approve_{thread_id}",
                ):
                    render_live_studio_stream(
                        studio_service.approve_and_deploy(thread_id),
                        status_title="🚀 Fiziksel Uygulama Paketi Diske İnşa Ediliyor...",
                    )
                    st.rerun()

        with col_revise:
            with st.container(border=True):
                st.markdown("##### 🔄 2. Revizyon İste")
                rev_target = st.selectbox(
                    "Hedef Departman:",
                    options=list(DEPT_TARGET_OPTIONS.keys()),
                    format_func=lambda k: DEPT_TARGET_OPTIONS[k],
                    key=f"hitl_rev_target_{thread_id}",
                )
                rev_text = st.text_area(
                    "Değişiklik / Ek Özellik Talimatı:",
                    placeholder="Örn: Kategoriye göre filtreleme ve CSV dışa aktarma butonu ekle.",
                    height=85,
                    key=f"hitl_rev_text_{thread_id}",
                )
                if st.button(
                    "🔁 Departmana Revizyon Gönder",
                    use_container_width=True,
                    key=f"hitl_rev_btn_{thread_id}",
                ):
                    if rev_text.strip():
                        render_live_studio_stream(
                            studio_service.request_revision(thread_id, rev_text, rev_target),
                            status_title="🔄 Fabrika Revizyon Döngüsünü Çalıştırıyor...",
                        )
                        st.rerun()
                    else:
                        st.warning("Lütfen revizyon talimatınızı yazın.")

        with col_reject:
            with st.container(border=True):
                st.markdown("##### ❌ 3. Kodu Reddet")
                rej_reason = st.text_area(
                    "Reddetme Gerekçesi:",
                    placeholder="Örn: Kod yapısı beklentiyi karşılamadı / yanlış yaklaşım kullanıldı...",
                    height=85,
                    key=f"hitl_rej_reason_{thread_id}",
                )
                if st.button(
                    "♻️ Kodu Reddet & Sıfırdan Yazdır",
                    use_container_width=True,
                    key=f"hitl_rej_rewrite_{thread_id}",
                    help="Mevcut kodu tamamen siler ve Kıdemli Mühendise sıfırdan temiz kod yazdırır.",
                ):
                    render_live_studio_stream(
                        studio_service.reject_code_and_rewrite(thread_id, rej_reason, target="Lead_Developer"),
                        status_title="♻️ Eski Kod Silindi — Sıfırdan Temiz Kodlama Başlatılıyor...",
                    )
                    st.rerun()

                if st.button(
                    "🛑 Kodu Reddet & İnşayı İptal Et",
                    use_container_width=True,
                    key=f"hitl_rej_cancel_{thread_id}",
                    help="Fiziksel kurulumu iptal eder ve projeyi '❌ Kod Reddedildi' durumuna alır.",
                ):
                    studio_service.reject_and_cancel_project(thread_id, rej_reason)
                    st.rerun()

        st.divider()

    elif is_rejected:
        reason_txt = values.get("rejection_reason") or "Kurucu Başkan tarafından reddedildi."
        st.markdown(
            f"""
<div class="reject-box">
    <div style="font-size:15px; font-weight:700; color:#f87171;">
        ❌ BU UYGULAMANIN KODU REDDEDİLDİ VE DAĞITIM İPTAL EDİLDİ
    </div>
    <div style="font-size:13px; color:#fecaca; margin-top:4px;">
        <b>Reddetme Gerekçesi:</b> {reason_txt}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        rc1, rc2 = st.columns([2, 3])
        with rc1:
            if st.button(
                "♻️ Bu Projeyi Sıfırdan Yeniden Kodlat",
                type="primary",
                use_container_width=True,
                key=f"btn_rebuild_rejected_{thread_id}",
            ):
                render_live_studio_stream(
                    studio_service.reject_code_and_rewrite(thread_id, reason_txt, target="Lead_Developer"),
                    status_title="♻️ Proje Yeniden Kodlanıyor...",
                )
                st.rerun()
        with rc2:
            st.caption("Veya hemen aşağıdaki iletişim masasından fabrika ekibiyle görüşüp yeni talimat verebilirsiniz.")
        st.divider()

    elif is_deployed:
        dc1, dc2 = st.columns([3.5, 1.5])
        with dc1:
            st.success(
                f"🎉 **Fiziksel Uygulama Paketi Hazır!** Dizin: `{values.get('app_folder')}` — "
                "**💻 2. Kod Gezgini & Çalıştırma** sekmesinden tek tıkla başlatabilir veya aşağıdaki masadan yeni özellik/revizyon isteyebilirsiniz."
            )
        with dc2:
            if st.button(
                "❌ Kodu Reddet / İptal İşaretle",
                use_container_width=True,
                key=f"btn_post_reject_{thread_id}",
                help="Onaylanmış paketi reddedildi statüsüne çeker.",
            ):
                studio_service.reject_and_cancel_project(thread_id, "Kurucu tarafından dağıtım sonrası reddedildi.")
                st.rerun()

    # 4. ALWAYS-VISIBLE SOFTWARE FACTORY CONVERSATION & OPERATION CONSOLE
    st.markdown("##### 💬 Yazılım Fabrikası İletişim & Operasyon Masası")
    st.caption(
        "Fabrika Baş Mimarı ve mühendislik ekibiyle doğrudan sohbet edebilir, kod/mimari hakkında soru sorabilir "
        "ya da doğrudan uygulama imalat / revizyon döngüsü başlatabilirsiniz."
    )

    conv_messages = studio_service.get_conversation_messages(thread_id)
    feed_container = st.container(height=360, border=True)
    with feed_container:
        if not conv_messages:
            with st.chat_message("assistant", avatar="🗣️"):
                st.markdown(
                    "**Fabrika Baş Mimarı & Stüdyo Direktörü:**\n\n"
                    f"Hoş geldiniz Kurucu Başkan! Şu anda **`{thread_id}`** projesindeyiz. Aşağıdaki konsoldan:\n"
                    "- **💬 Fabrika Ekibiyle Görüş** modunu seçerek kod üretmeden teknik istişare yapabilir ve soru sorabilirsiniz,\n"
                    "- **⚡ Otonom İmalat / Geliştirme Döngüsü Çalıştır** modunu seçerek doğrudan çok dosyalı yazılım üretimini başlatabilirsiniz."
                )
        else:
            for m in conv_messages:
                role = m["role"]
                txt = m["content"]
                with st.chat_message(role, avatar=_pick_avatar(role, txt)):
                    st.markdown(txt)

    # Mode selector + optional department target right above chat_input
    mc1, mc2 = st.columns([3.2, 1.8])
    default_mode_idx = 0 if has_prd else 1
    with mc1:
        action_mode = st.radio(
            "Gönderim Modu:",
            options=[
                "💬 Fabrika Ekibiyle Görüş (Soru Sor & Teknik İstişare)",
                "⚡ Otonom İmalat / Geliştirme Döngüsü Çalıştır",
            ],
            index=default_mode_idx,
            horizontal=True,
            key=f"factory_action_mode_{thread_id}",
        )
    selected_target = "AUTO"
    with mc2:
        if action_mode.startswith("⚡") and has_prd:
            selected_target = st.selectbox(
                "Hedef Departman (Revizyon):",
                options=list(DEPT_TARGET_OPTIONS.keys()),
                format_func=lambda k: DEPT_TARGET_OPTIONS[k],
                key=f"factory_build_target_{thread_id}",
            )
        elif action_mode.startswith("💬"):
            st.caption("💡 Bu modda mevcut kod bozulmaz; Baş Mimar projeyi inceleyip yanıt verir.")
        else:
            st.caption("⚡ Bu modda CPO ➔ CTO ➔ Mühendis ➔ AST/QA imalat hattı çalışır.")

    placeholder_txt = (
        "Fabrika Baş Mimarına kod, mimari veya teknik yaklaşım hakkında sorunuzu yazın..."
        if action_mode.startswith("💬")
        else (
            "Uygulamada yapılmasını istediğiniz revizyonu veya yeni özelliği yazın..."
            if has_prd
            else "Geliştirilmesini istediğiniz uygulamanın amacını ve özelliklerini yazın..."
        )
    )

    user_factory_msg = st.chat_input(placeholder_txt, key="factory_chat_input")
    if user_factory_msg and user_factory_msg.strip():
        if action_mode.startswith("💬"):
            with st.spinner("🗣️ Fabrika Baş Mimarı projeyi inceleyerek yanıtlıyor..."):
                studio_service.chat_with_factory_team(thread_id, user_factory_msg.strip())
            st.rerun()
        else:
            render_live_studio_stream(
                studio_service.start_or_continue_build(
                    thread_id,
                    user_factory_msg.strip(),
                    target=selected_target,
                ),
                status_title="🏗️ Otonom Yazılım Fabrikası Döngüsü Çalışıyor...",
            )
            st.rerun()
