"""
Enterprise Design Tokens & CSS Styling for Streamlit UI.
"""

import streamlit as st


def apply_enterprise_theme():
    """Inject modern, high-contrast dark theme CSS into Streamlit page."""
    custom_css = """
<style>
/* Modern Inter / System Font */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Hide default streamlit page nav */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Top App Header & Badges */
.studio-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.studio-title {
    font-size: 24px;
    font-weight: 700;
    color: #f8fafc;
    margin: 0;
}

.studio-subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
}

/* Metric & Status Cards */
.metric-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.metric-val {
    font-size: 22px;
    font-weight: 700;
    color: #38bdf8;
}
.metric-lbl {
    font-size: 12px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Cycle Node Badges */
.node-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}
.node-active {
    background-color: rgba(56, 189, 248, 0.2);
    color: #38bdf8;
    border: 1px solid #38bdf8;
}
.node-passed {
    background-color: rgba(34, 197, 94, 0.2);
    color: #4ade80;
    border: 1px solid #22c55e;
}
.node-waiting {
    background-color: rgba(148, 163, 184, 0.1);
    color: #94a3b8;
    border: 1px solid #475569;
}
.node-error {
    background-color: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid #ef4444;
}

/* HITL Action Box */
.hitl-box {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}
</style>
"""
    st.markdown(custom_css, unsafe_allow_html=True)
