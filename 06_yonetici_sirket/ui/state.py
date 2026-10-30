"""
Session State Manager for Streamlit.
"""

from datetime import datetime
import streamlit as st
from data.repositories.app_repository import app_repository
from services.studio_service import studio_service


def init_session_state():
    """Initialize default session state keys if not present."""
    if "active_thread" not in st.session_state:
        # Pick the latest thread if available, or generate a fresh one
        existing = app_repository.list_thread_ids()
        if existing:
            st.session_state.active_thread = existing[0]
        else:
            st.session_state.active_thread = f"app-{datetime.now().strftime('%m%d-%H%M%S')}"

    if "ideation_chat" not in st.session_state:
        st.session_state.ideation_chat = []

    if "factory_logs" not in st.session_state:
        st.session_state.factory_logs = []

    if "last_synced_thread" not in st.session_state:
        st.session_state.last_synced_thread = None


def sync_thread_state(thread_id: str):
    """Synchronize session state when switching projects."""
    if st.session_state.get("last_synced_thread") != thread_id:
        st.session_state.last_synced_thread = thread_id
        # Reset ephemeral factory logs when switching threads
        st.session_state.factory_logs = []
