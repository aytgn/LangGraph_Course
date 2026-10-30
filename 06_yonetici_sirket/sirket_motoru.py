"""
AI Software Studio Engine - Enterprise Facade (Geriye Dönük Uyumluluk Katmanı).
Clean Architecture geçişi sonrası tüm çağrıları domain, tools ve config katmanlarına delege eder.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Ensure module path is active
_module_root = str(Path(__file__).resolve().parent)
_project_root = str(Path(__file__).resolve().parent.parent)
for p in (_module_root, _project_root):
    if p not in sys.path:
        sys.path.insert(0, p)

# Re-export configuration paths
from config.settings import config
DB_PATH = str(config.DB_PATH)
OUTPUT_APPS_DIR = str(config.OUTPUT_APPS_DIR)

# Re-export state and schemas
from domain.state import CompanyState
from domain.schemas import (
    PRDSpecOutput,
    ArchitectureSpecOutput,
    CodeBundleOutput,
    QAReviewOutput,
    DirectorRouteOutput,
)

# Re-export compiled workflow
from domain.workflow import studio_app as app
from tools.registry import ToolRegistry
from tools.disk_operations import sanitize_slug


def run_deterministic_ast_checks(code_files: Dict[str, str], entrypoint: str = "app.py") -> List[str]:
    """Backward-compatible AST suite execution."""
    tool = ToolRegistry.get_tool("deterministic_ast_suite")
    if tool:
        return tool.run(code_files, entrypoint)
    return []


def export_application_to_disk(state: Dict[str, Any]) -> Tuple[str, str]:
    """Backward-compatible disk export execution."""
    tool = ToolRegistry.get_tool("disk_export_tool")
    if tool:
        return tool.run(state)
    return "", ""


__all__ = [
    "app",
    "CompanyState",
    "DB_PATH",
    "OUTPUT_APPS_DIR",
    "run_deterministic_ast_checks",
    "export_application_to_disk",
    "sanitize_slug",
    "PRDSpecOutput",
    "ArchitectureSpecOutput",
    "CodeBundleOutput",
    "QAReviewOutput",
    "DirectorRouteOutput",
]
