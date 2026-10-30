"""
Database Connection Manager
Provides thread-safe connections with WAL mode and schema initialization.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from config.settings import config


class DatabaseManager:
    """Manages SQLite connections and studio metadata tables for studio_apps.db."""

    def __init__(self, db_path: Optional[Path | str] = None):
        self.db_path = str(db_path or config.DB_PATH)
        self._ensure_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a robust SQLite connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass
        return conn

    def _ensure_schema(self) -> None:
        """Ensure the studio_projects CRUD metadata table exists."""
        try:
            conn = self.get_connection()
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS studio_projects (
                    thread_id TEXT PRIMARY KEY,
                    display_name TEXT DEFAULT '',
                    custom_notes TEXT DEFAULT '',
                    tags TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
            conn.close()
        except Exception:
            pass


# Global default manager
db_manager = DatabaseManager()
