"""
Views package for Streamlit tabs.
"""

from ui.views.tab_ideation import render_ideation_view
from ui.views.tab_factory import render_factory_view
from ui.views.tab_workspace import render_workspace_view
from ui.views.tab_portfolio import render_portfolio_view
from ui.views.tab_architecture import render_architecture_view

__all__ = [
    "render_ideation_view",
    "render_factory_view",
    "render_workspace_view",
    "render_portfolio_view",
    "render_architecture_view",
]
