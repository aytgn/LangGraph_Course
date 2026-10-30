"""
Session State Manager for Streamlit.
"""

from datetime import datetime
import streamlit as st
from data.repositories.app_repository import app_repository


def init_session_state():
    """Initialize default session state keys if not present."""
    if "active_thread" not in st.session_state:
        existing = app_repository.list_thread_ids()
        if existing:
            st.session_state.active_thread = existing[0]
        else:
            fresh_tid = app_repository.create_project(
                f"app-{datetime.now().strftime('%m%d-%H%M%S')}",
                display_name="Yeni Uygulama Projesi",
            )
            st.session_state.active_thread = fresh_tid

    if "ideation_chat" not in st.session_state:
        st.session_state.ideation_chat = []

    if "queued_factory_directive" not in st.session_state:
        st.session_state.queued_factory_directive = None

    if "factory_logs" not in st.session_state:
        st.session_state.factory_logs = []

    if "last_synced_thread" not in st.session_state:
        st.session_state.last_synced_thread = None


def sync_thread_state(thread_id: str):
    """Synchronize session state when switching projects."""
    if st.session_state.get("last_synced_thread") != thread_id:
        st.session_state.last_synced_thread = thread_id
        st.session_state.factory_logs = []
