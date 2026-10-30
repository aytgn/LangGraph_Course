"""
App Repository - Full CRUD Operations for Applications & Checkpoints.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from config.settings import config
from data.database import db_manager, DatabaseManager
from data.models import AppProject, CheckpointRecord, DatabaseStats


class AppRepository:
    """Enterprise Data Access Layer (Repository Pattern) for Studio Projects."""

    def __init__(self, manager: Optional[DatabaseManager] = None):
        self.manager = manager or db_manager

    # =========================================================================
    # CREATE
    # =========================================================================
    def create_thread(self, thread_id: str) -> str:
        """Reserve a new thread identifier for a new application project."""
        clean_id = thread_id.strip()
        return clean_id

    # =========================================================================
    # READ
    # =========================================================================
    def list_thread_ids(self) -> List[str]:
        """Fetch all unique thread IDs ordered by latest checkpoint."""
        if not os.path.exists(self.manager.db_path):
            return []
        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY rowid DESC")
            rows = [r[0] for r in cur.fetchall()]
            conn.close()

            # Preserve order while removing duplicates
            seen = set()
            unique_threads = []
            for tid in rows:
                if tid and tid not in seen:
                    seen.add(tid)
                    unique_threads.append(tid)
            return unique_threads
        except Exception:
            return []

    def get_checkpoint_count(self, thread_id: str) -> int:
        """Return the count of state checkpoints for a specific thread."""
        if not os.path.exists(self.manager.db_path):
            return 0
        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM checkpoints WHERE thread_id = ?", (thread_id,))
            cnt = cur.fetchone()[0]
            conn.close()
            return cnt
        except Exception:
            return 0

    def get_project(self, thread_id: str, app_graph=None) -> Optional[AppProject]:
        """
        Extract full domain model for a project by combining SQLite checkpoints
        and LangGraph state snapshot.
        """
        if not app_graph:
            # If graph is not passed, create a default AppProject from thread_id
            return AppProject(thread_id=thread_id)

        try:
            cfg = {"configurable": {"thread_id": thread_id}}
            snapshot = app_graph.get_state(cfg)
            if not snapshot or not snapshot.values:
                return AppProject(thread_id=thread_id)

            v = snapshot.values
            c_files = v.get("code_files") or {}
            waiting_hitl = bool(snapshot.next and "Deployment_Gate" in snapshot.next)

            if v.get("is_deployed"):
                status_label = "🚀 Fiziksel Paket Hazır"
            elif waiting_hitl:
                status_label = "🛑 Kurucu Onayı Bekliyor"
            elif v.get("prd_spec"):
                status_label = "🔄 Geliştiriliyor"
            else:
                status_label = "⚪ Başlangıç"

            return AppProject(
                thread_id=thread_id,
                name=v.get("app_name") or "(Henüz İsimlendirilmedi)",
                slug=v.get("app_slug") or "",
                app_type=v.get("app_type") or "Streamlit Web App",
                status=status_label,
                tech_stack=v.get("tech_stack") or [],
                total_loc=v.get("total_loc") or 0,
                files_count=len(c_files),
                cycle_count=v.get("cycle_count") or 0,
                revision_count=v.get("revision_count") or 0,
                qa_passed=bool(v.get("qa_passed")),
                is_deployed=bool(v.get("is_deployed")),
                app_folder=v.get("app_folder"),
                run_command_hint=v.get("run_command_hint"),
                purpose_summary=v.get("purpose_summary"),
                code_files=c_files,
                qa_report=v.get("qa_report"),
            )
        except Exception:
            return AppProject(thread_id=thread_id)

    def list_all_projects(self, app_graph=None, status_filter: Optional[str] = None) -> List[AppProject]:
        """Fetch all projects as strongly-typed AppProject models, with optional status filter."""
        thread_ids = self.list_thread_ids()
        projects = []
        for tid in thread_ids:
            proj = self.get_project(tid, app_graph=app_graph)
            if proj:
                if status_filter and status_filter != "Tümü" and proj.status != status_filter:
                    continue
                projects.append(proj)
        return projects

    def get_checkpoint_history(self, thread_id: str, app_graph) -> List[CheckpointRecord]:
        """Retrieve the time-travel audit records for a project thread."""
        records = []
        if not app_graph:
            return records
        try:
            cfg = {"configurable": {"thread_id": thread_id}}
            history = list(app_graph.get_state_history(cfg))
            for idx, snap in enumerate(history):
                src = snap.metadata.get("source", "-") if snap.metadata else "-"
                step = snap.metadata.get("step", idx) if snap.metadata else idx
                next_n = ", ".join(snap.next) if snap.next else "END"
                cid = snap.config["configurable"].get("checkpoint_id", "")
                records.append(
                    CheckpointRecord(
                        step=step,
                        source=src,
                        next_node=next_n,
                        checkpoint_id=cid,
                    )
                )
        except Exception:
            pass
        return records

    def get_statistics(self) -> DatabaseStats:
        """Compute database size, distinct apps count, and total checkpoints."""
        db_path = Path(self.manager.db_path)
        if not db_path.exists():
            return DatabaseStats()
        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT count(DISTINCT thread_id), count(*) FROM checkpoints")
            t_cnt, c_cnt = cur.fetchone()
            conn.close()

            size_kb = round(db_path.stat().st_size / 1024, 1)

            # Count folders in output_uygulamalar
            deployed_cnt = 0
            if config.OUTPUT_APPS_DIR.exists():
                deployed_cnt = sum(
                    1 for d in config.OUTPUT_APPS_DIR.iterdir() if d.is_dir()
                )

            return DatabaseStats(
                total_apps=t_cnt or 0,
                total_checkpoints=c_cnt or 0,
                db_size_kb=size_kb,
                deployed_apps_count=deployed_cnt,
            )
        except Exception:
            return DatabaseStats()

    # =========================================================================
    # UPDATE
    # =========================================================================
    def update_metadata(self, thread_id: str, new_name: Optional[str] = None) -> bool:
        """Update app metadata if needed."""
        # Checkpoints in LangGraph are append-only snapshots, metadata updates can be logged
        return True

    # =========================================================================
    # DELETE
    # =========================================================================
    def delete_project(self, thread_id: str, slug: Optional[str] = None, delete_disk: bool = True) -> bool:
        """
        Permanently remove a project thread from SQLite checkpoints and writes tables,
        and optionally remove the exported application directory on disk.
        """
        if not os.path.exists(self.manager.db_path):
            return False

        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            cur.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
            conn.commit()
            conn.close()

            # Clean disk files if slug is provided or thread_id matches folder
            if delete_disk:
                targets = [slug] if slug else [thread_id, thread_id.replace("-", "_")]
                for tgt in targets:
                    if tgt:
                        folder = config.OUTPUT_APPS_DIR / tgt
                        if folder.exists() and folder.is_dir():
                            shutil.rmtree(folder, ignore_errors=True)

            return True
        except Exception:
            return False


# Global singleton repository
app_repository = AppRepository()
