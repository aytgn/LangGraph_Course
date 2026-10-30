"""
App Repository - Full Enterprise CRUD Operations for Applications & Checkpoints.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from config.settings import config
from data.database import db_manager, DatabaseManager
from data.models import AppProject, CheckpointRecord, DatabaseStats


def _clean_thread_id(raw_id: str) -> str:
    s = (raw_id or "").strip()
    s = s.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    s = s.replace("İ", "i").replace("Ğ", "g").replace("Ü", "u").replace("Ş", "s").replace("Ö", "o").replace("Ç", "c")
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-_")
    return s or f"app-{datetime.now().strftime('%m%d-%H%M%S')}"


class AppRepository:
    """Enterprise Data Access Layer (Repository Pattern) with real SQLite CRUD."""

    def __init__(self, manager: Optional[DatabaseManager] = None):
        self.manager = manager or db_manager
        self._sync_existing_checkpoint_threads()

    def _table_exists(self, conn, table_name: str) -> bool:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cur.fetchone() is not None

    def _sync_existing_checkpoint_threads(self) -> None:
        """Auto-register any thread present in LangGraph checkpoints into studio_projects."""
        if not os.path.exists(self.manager.db_path):
            return
        try:
            conn = self.manager.get_connection()
            if not self._table_exists(conn, "checkpoints"):
                conn.close()
                return

            cur = conn.cursor()
            cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY rowid ASC")
            rows = [r[0] for r in cur.fetchall() if r[0]]
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for tid in rows:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO studio_projects (thread_id, display_name, custom_notes, tags, created_at, updated_at)
                    VALUES (?, '', '', '', ?, ?)
                    """,
                    (tid, now, now),
                )
            conn.commit()
            conn.close()
        except Exception:
            pass

    # =========================================================================
    # CREATE
    # =========================================================================
    def create_project(
        self,
        thread_id: str,
        display_name: str = "",
        custom_notes: str = "",
        tags: str = "",
    ) -> str:
        """Persist a new application project record in SQLite studio_projects."""
        clean_id = _clean_thread_id(thread_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = self.manager.get_connection()
            conn.execute(
                """
                INSERT INTO studio_projects (thread_id, display_name, custom_notes, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    display_name = CASE WHEN excluded.display_name != '' THEN excluded.display_name ELSE studio_projects.display_name END,
                    custom_notes = CASE WHEN excluded.custom_notes != '' THEN excluded.custom_notes ELSE studio_projects.custom_notes END,
                    tags = CASE WHEN excluded.tags != '' THEN excluded.tags ELSE studio_projects.tags END,
                    updated_at = excluded.updated_at
                """,
                (clean_id, display_name.strip(), custom_notes.strip(), tags.strip(), now, now),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
        return clean_id

    def create_thread(self, thread_id: str, display_name: str = "") -> str:
        """Alias for create_project preserving backward compatibility."""
        return self.create_project(thread_id=thread_id, display_name=display_name)

    def touch_project(self, thread_id: str, display_name: str = "") -> None:
        """Update project's updated_at timestamp (or create if missing)."""
        self.create_project(thread_id=thread_id, display_name=display_name)

    # =========================================================================
    # READ
    # =========================================================================
    def list_thread_ids(self) -> List[str]:
        """Fetch all unique project thread IDs ordered by most recently updated."""
        self._sync_existing_checkpoint_threads()
        if not os.path.exists(self.manager.db_path):
            return []
        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT thread_id FROM studio_projects ORDER BY updated_at DESC, rowid DESC")
            rows = [r[0] for r in cur.fetchall() if r[0]]
            conn.close()
            return rows
        except Exception:
            return []

    def _get_project_meta_map(self) -> Dict[str, dict]:
        meta: Dict[str, dict] = {}
        if not os.path.exists(self.manager.db_path):
            return meta
        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT thread_id, display_name, custom_notes, tags, created_at, updated_at FROM studio_projects"
            )
            for row in cur.fetchall():
                meta[row["thread_id"]] = dict(row)
            conn.close()
        except Exception:
            pass
        return meta

    def get_checkpoint_count(self, thread_id: str) -> int:
        """Return the count of state checkpoints for a specific thread."""
        if not os.path.exists(self.manager.db_path):
            return 0
        try:
            conn = self.manager.get_connection()
            if not self._table_exists(conn, "checkpoints"):
                conn.close()
                return 0
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM checkpoints WHERE thread_id = ?", (thread_id,))
            cnt = cur.fetchone()[0]
            conn.close()
            return cnt
        except Exception:
            return 0

    def get_project(self, thread_id: str, app_graph=None, meta_row: Optional[dict] = None) -> Optional[AppProject]:
        """Combine studio_projects metadata and LangGraph state snapshot into AppProject."""
        if meta_row is None:
            meta_row = self._get_project_meta_map().get(thread_id, {})

        custom_display = (meta_row.get("display_name") or "").strip()
        custom_notes = meta_row.get("custom_notes") or ""
        tags = meta_row.get("tags") or ""
        created_at = meta_row.get("created_at") or ""
        updated_at = meta_row.get("updated_at") or ""

        if not app_graph:
            return AppProject(
                thread_id=thread_id,
                name=custom_display or "(Henüz İsimlendirilmedi)",
                custom_notes=custom_notes,
                tags=tags,
                created_at=created_at,
                updated_at=updated_at,
            )

        try:
            cfg = {"configurable": {"thread_id": thread_id}}
            snapshot = app_graph.get_state(cfg)
            if not snapshot or not snapshot.values:
                return AppProject(
                    thread_id=thread_id,
                    name=custom_display or "(Yeni Boş Proje)",
                    custom_notes=custom_notes,
                    tags=tags,
                    created_at=created_at,
                    updated_at=updated_at,
                )

            v = snapshot.values
            c_files = v.get("code_files") or {}
            waiting_hitl = bool(snapshot.next and "Deployment_Gate" in snapshot.next)
            is_deployed = bool(v.get("is_deployed"))
            is_rejected = bool(v.get("is_rejected"))

            if is_deployed:
                status_label = "🚀 Fiziksel Paket Hazır"
            elif is_rejected:
                status_label = "❌ Kod Reddedildi"
            elif waiting_hitl:
                status_label = "🛑 Kurucu Onayı Bekliyor"
            elif v.get("prd_spec") or c_files:
                status_label = "🔄 Geliştiriliyor"
            else:
                status_label = "⚪ Başlangıç"

            effective_name = custom_display or v.get("app_name") or "(Henüz İsimlendirilmedi)"

            return AppProject(
                thread_id=thread_id,
                name=effective_name,
                slug=v.get("app_slug") or "",
                app_type=v.get("app_type") or "Henüz Belirlenmedi",
                status=status_label,
                tech_stack=v.get("tech_stack") or [],
                total_loc=v.get("total_loc") or 0,
                files_count=len(c_files),
                cycle_count=v.get("cycle_count") or 0,
                revision_count=v.get("revision_count") or 0,
                qa_passed=bool(v.get("qa_passed")),
                is_deployed=is_deployed,
                is_rejected=is_rejected,
                rejection_reason=v.get("rejection_reason"),
                app_folder=v.get("app_folder"),
                run_command_hint=v.get("run_command_hint"),
                purpose_summary=v.get("purpose_summary"),
                code_files=c_files,
                qa_report=v.get("qa_report"),
                custom_notes=custom_notes,
                tags=tags,
                created_at=created_at,
                updated_at=updated_at,
            )
        except Exception:
            return AppProject(
                thread_id=thread_id,
                name=custom_display or "(Henüz İsimlendirilmedi)",
                custom_notes=custom_notes,
                tags=tags,
                created_at=created_at,
                updated_at=updated_at,
            )

    def list_all_projects(
        self,
        app_graph=None,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[AppProject]:
        """Fetch all projects with optional status filter and search query."""
        thread_ids = self.list_thread_ids()
        meta_map = self._get_project_meta_map()
        q = (search_query or "").strip().lower()
        projects = []
        for tid in thread_ids:
            proj = self.get_project(tid, app_graph=app_graph, meta_row=meta_map.get(tid, {}))
            if not proj:
                continue
            if status_filter and status_filter != "Tümü" and proj.status != status_filter:
                continue
            if q:
                haystack = f"{proj.thread_id} {proj.name} {proj.app_type} {' '.join(proj.tech_stack)} {proj.tags} {proj.custom_notes}".lower()
                if q not in haystack:
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
        """Compute database size, total projects count, and total checkpoints."""
        self._sync_existing_checkpoint_threads()
        db_path = Path(self.manager.db_path)
        if not db_path.exists():
            return DatabaseStats()
        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()

            cur.execute("SELECT count(*) FROM studio_projects")
            t_cnt = cur.fetchone()[0] or 0

            c_cnt = 0
            if self._table_exists(conn, "checkpoints"):
                cur.execute("SELECT count(*) FROM checkpoints")
                c_cnt = cur.fetchone()[0] or 0

            conn.close()
            size_kb = round(db_path.stat().st_size / 1024, 1)

            deployed_cnt = 0
            if config.OUTPUT_APPS_DIR.exists():
                deployed_cnt = sum(1 for d in config.OUTPUT_APPS_DIR.iterdir() if d.is_dir())

            return DatabaseStats(
                total_apps=t_cnt,
                total_checkpoints=c_cnt,
                db_size_kb=size_kb,
                deployed_apps_count=deployed_cnt,
            )
        except Exception:
            return DatabaseStats()

    # =========================================================================
    # UPDATE
    # =========================================================================
    def update_project_metadata(
        self,
        thread_id: str,
        display_name: Optional[str] = None,
        custom_notes: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> bool:
        """Update project display_name, custom_notes, and tags in studio_projects."""
        try:
            self._sync_existing_checkpoint_threads()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM studio_projects WHERE thread_id = ?", (thread_id,))
            if not cur.fetchone():
                conn.execute(
                    "INSERT INTO studio_projects (thread_id, display_name, custom_notes, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (thread_id, display_name or "", custom_notes or "", tags or "", now, now),
                )
            else:
                fields = ["updated_at = ?"]
                params: list = [now]
                if display_name is not None:
                    fields.append("display_name = ?")
                    params.append(display_name.strip())
                if custom_notes is not None:
                    fields.append("custom_notes = ?")
                    params.append(custom_notes.strip())
                if tags is not None:
                    fields.append("tags = ?")
                    params.append(tags.strip())
                params.append(thread_id)
                conn.execute(
                    f"UPDATE studio_projects SET {', '.join(fields)} WHERE thread_id = ?",
                    tuple(params),
                )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def update_metadata(self, thread_id: str, new_name: Optional[str] = None, notes: Optional[str] = None, tags: Optional[str] = None) -> bool:
        """Backward-compatible alias for update_project_metadata."""
        return self.update_project_metadata(thread_id=thread_id, display_name=new_name, custom_notes=notes, tags=tags)

    # =========================================================================
    # DELETE
    # =========================================================================
    def delete_project(self, thread_id: str, slug: Optional[str] = None, delete_disk: bool = True) -> bool:
        """
        Permanently remove a project from studio_projects, checkpoints, and writes tables,
        and optionally delete its physical directory in output_uygulamalar.
        """
        if not os.path.exists(self.manager.db_path):
            return False

        try:
            conn = self.manager.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM studio_projects WHERE thread_id = ?", (thread_id,))
            if self._table_exists(conn, "checkpoints"):
                cur.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            if self._table_exists(conn, "writes"):
                cur.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
            conn.commit()
            conn.close()

            if delete_disk:
                targets = []
                if slug:
                    targets.append(slug)
                targets.extend([thread_id, thread_id.replace("-", "_")])
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
