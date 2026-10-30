"""
Database Connection Manager
Provides thread-safe connections with WAL mode and SQLite optimization.
"""

import sqlite3
from typing import Optional
from pathlib import Path
from config.settings import config


class DatabaseManager:
    """Manages SQLite connections for studio_apps.db."""

    def __init__(self, db_path: Optional[Path | str] = None):
        self.db_path = str(db_path or config.DB_PATH)

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a robust SQLite connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Performance and concurrency pragmas
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass
            
        return conn


# Global default manager
db_manager = DatabaseManager()
