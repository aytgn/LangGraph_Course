"""
Cyclical Studio Matrix & Live Transition Trail Component.
Visualizes the non-linear back-and-forth loops across software departments.
"""

from typing import List, Dict, Any
import streamlit as st
from services.studio_service import studio_service


def render_cyclical_matrix(thread_id: str):
    """Render cyclical graph state and department transition trail."""
    values, next_nodes, waiting_hitl = studio_service.get_state(thread_id)
    cycle_count = values.get("cycle_count") or 0
    t_log: List[Dict[str, str]] = values.get("transition_log") or []
    is_deployed = values.get("is_deployed")
    next_node = next_nodes[0] if next_nodes else ("END" if is_deployed else "Studio_Director")

    # Departments layout
    dept_defs = [
        ("Studio_Director", "👑 Stüdyo Direktörü", "Merkezi Orkestratör"),
        ("Product_Lead", "💡 Ürün & Kapsam (CPO)", "PRD & MVP Kapsamı"),
        ("System_Architect", "📐 Sistem Mimarı (CTO)", "Tech Stack & Şemalar"),
        ("Lead_Developer", "💻 Kıdemli Mühendis", "Çok Dosyalı Kodlama"),
        ("QA_Security_Lead", "🛡️ QA & Güvenlik Lideri", "AST & Import Denetimi"),
        ("Deployment_Gate", "🚀 Dağıtım Kapısı", "Kurucu Onayı & Paketleme"),
    ]

    st.markdown(f"##### 🔄 Canlı Stüdyo Graf Matrisi • Döngü #{cycle_count}")

    cols = st.columns(6)
    for idx, (code, title, desc) in enumerate(dept_defs):
        with cols[idx]:
            is_active = (next_node == code)
            is_done = False
            if code == "Product_Lead" and values.get("prd_spec"):
                is_done = True
            elif code == "System_Architect" and values.get("architecture_spec"):
                is_done = True
            elif code == "Lead_Developer" and values.get("code_files"):
                is_done = True
            elif code == "QA_Security_Lead" and values.get("qa_passed"):
                is_done = True
            elif code == "Deployment_Gate" and values.get("is_deployed"):
                is_done = True

            css_class = "node-active" if is_active else ("node-passed" if is_done else "node-waiting")
            badge_icon = "⚡ AKTİF" if is_active else ("✔ HAZIR" if is_done else "BEKLİYOR")

            st.markdown(
                f"""
<div class="metric-card" style="padding: 10px; min-height: 110px;">
    <div style="font-size: 11px; font-weight: 700; color: #f8fafc;">{title}</div>
    <div style="font-size: 10px; color: #94a3b8; margin: 4px 0;">{desc}</div>
    <span class="node-badge {css_class}" style="font-size: 10px; margin: 0;">{badge_icon}</span>
</div>
""",
                unsafe_allow_html=True
            )

    # Transition Trail (Log of back-and-forth loops)
    if t_log:
        with st.expander(f"📜 Canlı Döngü ve Geçiş İzi ({len(t_log)} Olay)", expanded=False):
            trail_html = "<div style='display: flex; flex-direction: column; gap: 8px;'>"
            for entry in t_log[-8:]:
                c_num = entry.get("cycle", "1")
                node = entry.get("node", "")
                act = entry.get("action", "")
                tgt = entry.get("target", "")
                arrow = f" ➔ <b>{tgt}</b>" if tgt else ""
                trail_html += f"""
<div style="background: #0f172a; border-left: 3px solid #38bdf8; padding: 6px 12px; border-radius: 4px; font-size: 12px;">
    <span style="color: #f59e0b; font-weight: 600;">Döngü #{c_num}</span> | 
    <span style="color: #38bdf8; font-weight: 600;">{node}</span>{arrow}: 
    <span style="color: #cbd5e1;">{act}</span>
</div>
"""
            trail_html += "</div>"
            st.markdown(trail_html, unsafe_allow_html=True)
