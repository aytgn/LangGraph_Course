"""
Streamlit UI presentation layer package.
"""

from ui.styles import apply_enterprise_theme
from ui.state import init_session_state, sync_thread_state
from ui.components import render_enterprise_sidebar, render_cyclical_matrix, render_code_explorer
from ui.views import (
    render_ideation_view,
    render_factory_view,
    render_workspace_view,
    render_portfolio_view,
    render_architecture_view,
)

__all__ = [
    "apply_enterprise_theme",
    "init_session_state",
    "sync_thread_state",
    "render_enterprise_sidebar",
    "render_cyclical_matrix",
    "render_code_explorer",
    "render_ideation_view",
    "render_factory_view",
    "render_workspace_view",
    "render_portfolio_view",
    "render_architecture_view",
]
