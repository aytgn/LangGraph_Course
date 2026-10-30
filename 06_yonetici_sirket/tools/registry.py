"""
Central Tool Registry (Dynamic Tool Management).
"""

from typing import Dict, List, Optional, Any, Callable
from tools.base import StudioTool


class ToolRegistry:
    """
    Singleton registry enabling dynamic tool registration, department-based
    discovery, and listing for UI and architectural inspections.
    """
    _instance = None
    _tools: Dict[str, StudioTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._tools = {}
        return cls._instance

    @classmethod
    def register(cls, tool: StudioTool) -> StudioTool:
        """Register a tool instance."""
        cls._tools[tool.name] = tool
        return tool

    @classmethod
    def get_tool(cls, name: str) -> Optional[StudioTool]:
        """Fetch a tool by unique name."""
        return cls._tools.get(name)

    @classmethod
    def get_tools_for_department(cls, department: str) -> List[StudioTool]:
        """Retrieve all tools assigned to a specific department or available to ALL."""
        return [
            tool for tool in cls._tools.values()
            if tool.department in (department, "ALL")
        ]

    @classmethod
    def list_all_tools(cls) -> List[Dict[str, Any]]:
        """List all registered tools with metadata for inspection."""
        return [tool.to_dict() for tool in cls._tools.values()]

    @classmethod
    def count(cls) -> int:
        """Total number of registered tools."""
        return len(cls._tools)


# Global registry reference
registry = ToolRegistry()
