"""
Tools Package for AI Software Studio.
Provides dynamic registration, discovery, and execution of engineering tools.
"""

from tools.base import StudioTool
from tools.registry import ToolRegistry, registry

# Import tool modules to trigger automatic registration
import tools.code_verification
import tools.disk_operations
import tools.vault_operations

__all__ = ["StudioTool", "ToolRegistry", "registry"]
