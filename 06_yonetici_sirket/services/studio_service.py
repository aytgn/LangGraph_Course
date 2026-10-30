"""
Studio Service - Orchestrates LangGraph execution, HITL approval, and revisions.
"""

from typing import Dict, Any, Generator, Tuple, Optional
from langchain_core.messages import HumanMessage
from domain.workflow import studio_app
from tools.registry import ToolRegistry


class StudioService:
    """Application Service orchestrating workflow runs and human interactions."""

    def __init__(self, app_instance=None):
        self.app = app_instance or studio_app

    def get_state(self, thread_id: str) -> Tuple[Dict[str, Any], Tuple[str, ...], bool]:
        """Fetch current state values, next nodes, and whether it is paused at HITL."""
        cfg = {"configurable": {"thread_id": thread_id}}
        snap = self.app.get_state(cfg)
        if not snap:
            return {}, (), False
        values = snap.values or {}
        next_nodes = tuple(snap.next) if snap.next else ()
        waiting_hitl = bool(next_nodes and "Deployment_Gate" in next_nodes)
        return values, next_nodes, waiting_hitl

    def run_cycle(self, thread_id: str, input_payload: Any) -> Generator[Dict[str, Any], None, None]:
        """Stream cyclical engine execution updates."""
        cfg = {"configurable": {"thread_id": thread_id}}
        for event in self.app.stream(input_payload, config=cfg, stream_mode="updates"):
            yield event

    def approve_and_deploy(self, thread_id: str) -> Generator[Dict[str, Any], None, None]:
        """Founder approves application at HITL gate, resuming graph to execute Deployment_Gate."""
        cfg = {"configurable": {"thread_id": thread_id}}
        # Resuming with None in LangGraph triggers the paused node
        for event in self.app.stream(None, config=cfg, stream_mode="updates"):
            yield event

    def request_revision(self, thread_id: str, feedback: str, target: str = "Lead_Developer") -> Generator[Dict[str, Any], None, None]:
        """Founder requests revisions at HITL gate, updating state and routing back to target department."""
        cfg = {"configurable": {"thread_id": thread_id}}
        self.app.update_state(
            cfg,
            {
                "founder_feedback": feedback,
                "feedback_target": target,
                "next_step": "Studio_Director",
                "qa_passed": False,
            },
            as_node="Studio_Director"
        )
        for event in self.app.stream(None, config=cfg, stream_mode="updates"):
            yield event

    def generate_zip_bytes(self, state_values: Dict[str, Any]) -> bytes:
        """Create downloadable ZIP archive bytes via ToolRegistry."""
        zip_tool = ToolRegistry.get_tool("zip_packager_tool")
        if zip_tool:
            return zip_tool.run(state_values)
        return b""


studio_service = StudioService()
