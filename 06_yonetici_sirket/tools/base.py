"""
Base classes and protocols for Studio Tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable


@dataclass
class StudioTool(ABC):
    """Abstract base class representing an executable, discoverable Studio Tool."""
    name: str
    description: str
    department: str = "ALL"  # "QA_Security_Lead", "Deployment_Gate", "Lead_Developer", etc.
    category: str = "General"  # "Verification", "Packaging", "Documentation", "Execution"
    parameters_schema: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the tool logic."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tool metadata for inspection and UI display."""
        return {
            "name": self.name,
            "description": self.description,
            "department": self.department,
            "category": self.category,
            "parameters": self.parameters_schema,
        }
