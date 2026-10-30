"""
Data Models and Typed Entities for Studio Operations.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class AppProject:
    """Represents an application project managed by the AI Software Studio."""
    thread_id: str
    name: str = "(Henüz İsimlendirilmedi)"
    slug: str = ""
    app_type: str = "Henüz Belirlenmedi"
    status: str = "⚪ Başlangıç"
    tech_stack: List[str] = field(default_factory=list)
    total_loc: int = 0
    files_count: int = 0
    cycle_count: int = 0
    revision_count: int = 0
    qa_passed: bool = False
    is_deployed: bool = False
    is_rejected: bool = False
    rejection_reason: Optional[str] = None
    app_folder: Optional[str] = None
    run_command_hint: Optional[str] = None
    purpose_summary: Optional[str] = None
    code_files: Dict[str, str] = field(default_factory=dict)
    qa_report: Optional[str] = None
    custom_notes: str = ""
    tags: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class CheckpointRecord:
    """Represents a discrete state checkpoint in LangGraph's time-travel audit log."""
    step: int
    source: str
    next_node: str
    checkpoint_id: str
    timestamp: str = ""


@dataclass
class DatabaseStats:
    """Global system health & persistence statistics."""
    total_apps: int = 0
    total_checkpoints: int = 0
    db_size_kb: float = 0.0
    deployed_apps_count: int = 0


@dataclass
class VaultItem:
    """Represents a knowledge artifact in the Second Brain."""
    category: str
    filename: str
    title: str
    filepath: str
    updated_at: str
    content_snippet: str = ""
