"""
Cyclical Studio Matrix & Live Transition Trail Component.
Visualizes non-linear back-and-forth loops across software departments.
"""

from typing import List, Dict
import streamlit as st
from services.studio_service import studio_service


NODE_SHORT_LABELS = {
    "Studio_Director": "👑 Direktör",
    "Product_Lead": "💡 CPO",
    "System_Architect": "📐 CTO",
    "Lead_Developer": "💻 Mühendis",
    "QA_Security_Lead": "🛡️ QA/AST",
    "Deployment_Gate": "🚀 Dağıtım Kapısı",
}


def render_cyclical_matrix(thread_id: str):
    """Render cyclical graph state cards and horizontal + detailed transition trail."""
    values, next_nodes, waiting_hitl = studio_service.get_state(thread_id)
    cycle_count = values.get("cycle_count") or 0
    rev_count = values.get("revision_count") or 0
    t_log: List[Dict[str, str]] = values.get("transition_log") or []
    is_deployed = bool(values.get("is_deployed"))
    is_rejected = bool(values.get("is_rejected"))
    next_node = next_nodes[0] if next_nodes else ("END" if (is_deployed or is_rejected) else "Studio_Director")

    dept_defs = [
        ("Studio_Director", "👑 Stüdyo Direktörü", "Merkezi Orkestratör"),
        ("Product_Lead", "💡 Ürün Lideri (CPO)", "PRD & MVP Kapsamı"),
        ("System_Architect", "📐 Sistem Mimarı (CTO)", "Tech Stack & Şema"),
        ("Lead_Developer", "💻 Kıdemli Mühendis", "Çok Dosyalı Kodlama"),
        ("QA_Security_Lead", "🛡️ QA & Güvenlik", "AST & Import Testi"),
        ("Deployment_Gate", "🚀 Dağıtım Kapısı", "Onay / Red / Kurulum"),
    ]

    st.markdown(
        f"##### 🔄 Canlı Stüdyo Graf Matrisi • Döngü `#{cycle_count}` "
        f"{f'• Revizyon `#{rev_count}`' if rev_count else ''}"
    )

    cols = st.columns(6)
    for idx, (code, title, desc) in enumerate(dept_defs):
        with cols[idx]:
            card_cls = "dept-idle"
            badge_cls = "node-waiting"
            badge_txt = "BEKLİYOR"

            if code == "Deployment_Gate" and is_rejected:
                card_cls = "dept-rejected"
                badge_cls = "node-error"
                badge_txt = "❌ REDDEDİLDİ"
            elif code == "Deployment_Gate" and waiting_hitl:
                card_cls = "dept-hitl"
                badge_cls = "node-warn"
                badge_txt = "🛑 KARAR BEKLİYOR"
            elif code == "Deployment_Gate" and is_deployed:
                card_cls = "dept-done"
                badge_cls = "node-passed"
                badge_txt = "✔ İNŞA EDİLDİ"
            elif next_node == code and values:
                card_cls = "dept-active"
                badge_cls = "node-active"
                badge_txt = "⚡ SIRADA"
            elif code == "Studio_Director" and cycle_count > 0:
                card_cls = "dept-done"
                badge_cls = "node-passed"
                badge_txt = f"✔ {cycle_count} TUR"
            elif code == "Product_Lead" and values.get("prd_spec"):
                card_cls = "dept-done"
                badge_cls = "node-passed"
                badge_txt = "✔ PRD HAZIR"
            elif code == "System_Architect" and values.get("architecture_spec"):
                card_cls = "dept-done"
                badge_cls = "node-passed"
                badge_txt = "✔ ŞEMA HAZIR"
            elif code == "Lead_Developer" and values.get("code_files"):
                if rev_count > 0 and not values.get("qa_passed"):
                    card_cls = "dept-loop"
                    badge_cls = "node-active"
                    badge_txt = f"🔄 REV #{rev_count}"
                else:
                    card_cls = "dept-done"
                    badge_cls = "node-passed"
                    badge_txt = f"✔ {len(values.get('code_files') or {})} DOSYA"
            elif code == "QA_Security_Lead" and values.get("code_verified_by_qa"):
                if values.get("qa_passed"):
                    card_cls = "dept-done"
                    badge_cls = "node-passed"
                    badge_txt = "✔ AST GEÇTİ"
                else:
                    card_cls = "dept-rejected"
                    badge_cls = "node-error"
                    badge_txt = "⚠️ HATA BULDU"

            st.markdown(
                f"""
<div class="dept-card {card_cls}">
    <div style="font-size: 11.5px; font-weight: 700; color: #f8fafc;">{title}</div>
    <div style="font-size: 10px; color: #94a3b8; margin: 4px 0;">{desc}</div>
    <div><span class="node-badge {badge_cls}" style="font-size: 10px; margin: 0;">{badge_txt}</span></div>
</div>
""",
                unsafe_allow_html=True,
            )

    if t_log:
        hops = []
        seen_depts = set()
        for entry in t_log[-10:]:
            n = entry.get("node", "")
            c = entry.get("cycle", "1")
            lbl = NODE_SHORT_LABELS.get(n, n)
            is_backloop = n in seen_depts and n != "Studio_Director"
            seen_depts.add(n)
            color = "#c084fc" if is_backloop else "#38bdf8"
            hops.append(f"<span style='color:{color}; font-weight:600;'>{lbl} #{c}</span>")

        if waiting_hitl:
            hops.append("<span style='color:#fbbf24; font-weight:700;'>🛑 Kurucu Karar Kapısı</span>")
        elif is_rejected:
            hops.append("<span style='color:#f87171; font-weight:700;'>❌ Kod Reddedildi</span>")
        elif is_deployed:
            hops.append("<span style='color:#4ade80; font-weight:700;'>✅ Fiziksel Paket Hazır</span>")

        st.markdown(
            f"<div class='trail-box'><b>🧭 Canlı Döngü Rotası:</b> {' ➔ '.join(hops)}</div>",
            unsafe_allow_html=True,
        )

        with st.expander(f"📜 Detaylı Departman Geçiş Günlüğü ({len(t_log)} Kayıt)", expanded=False):
            for entry in reversed(t_log[-15:]):
                ts = entry.get("ts", "--:--:--")
                c_num = entry.get("cycle", "1")
                node = NODE_SHORT_LABELS.get(entry.get("node", ""), entry.get("node", ""))
                act = entry.get("action", "")
                tgt = entry.get("target", "")
                arrow = f" ➔ `{tgt}`" if tgt else ""
                st.markdown(f"- `{ts}` • **Döngü #{c_num}** | **{node}**{arrow}: {act}")
