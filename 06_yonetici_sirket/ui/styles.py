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
    padding: 18px 24px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}

.studio-title {
    font-size: 23px;
    font-weight: 800;
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
    padding: 14px;
    text-align: center;
}
.metric-val {
    font-size: 20px;
    font-weight: 700;
    color: #38bdf8;
}
.metric-lbl {
    font-size: 11px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Cyclical Department Cards */
.dept-card {
    background: #141c2c;
    border-radius: 10px;
    padding: 11px 10px;
    border: 1px solid #283548;
    text-align: center;
    min-height: 106px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.dept-done { border-color: #10b981; background: rgba(16, 185, 129, 0.08); }
.dept-active { border-color: #38bdf8; background: rgba(56, 189, 248, 0.12); box-shadow: 0 0 12px rgba(56, 189, 248, 0.16); }
.dept-loop { border-color: #a855f7; background: rgba(168, 85, 247, 0.12); }
.dept-hitl { border-color: #f59e0b; background: rgba(245, 158, 11, 0.14); }
.dept-rejected { border-color: #ef4444; background: rgba(239, 68, 68, 0.14); }
.dept-idle { border-color: #334155; opacity: 0.85; }

/* Horizontal Graph Hop Trail */
.trail-box {
    background: #0d1320;
    border: 1px solid #243247;
    border-radius: 10px;
    padding: 10px 14px;
    margin-top: 8px;
    font-size: 12.5px;
    color: #cbd5e1;
    line-height: 1.75;
}

/* Cycle Node Badges */
.node-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 4px;
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
.node-warn {
    background-color: rgba(245, 158, 11, 0.2);
    color: #fbbf24;
    border: 1px solid #f59e0b;
}
.node-waiting {
    background-color: rgba(148, 163, 184, 0.12);
    color: #94a3b8;
    border: 1px solid #475569;
}
.node-error {
    background-color: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid #ef4444;
}

/* HITL, Reject & Bridge Boxes */
.hitl-box {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.13) 0%, rgba(217, 119, 6, 0.05) 100%);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
}

.reject-box {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.14) 0%, rgba(185, 28, 28, 0.05) 100%);
    border: 1.5px solid #ef4444;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
}

.bridge-box {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(14, 165, 233, 0.08) 100%);
    border: 1.5px solid #10b981;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
}
</style>
"""
    st.markdown(custom_css, unsafe_allow_html=True)
