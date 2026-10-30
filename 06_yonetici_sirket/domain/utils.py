"""
Domain Utilities for Node Execution & Telemetry.
"""

from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from domain.state import CompanyState


def get_text(content: Any) -> str:
    """Safely extract plain string from langchain message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)


def get_clean_user_directive(state: CompanyState) -> str:
    """Extract founder's directive from the message history."""
    msgs = state.get("messages") or []
    human_msgs = [m for m in msgs if isinstance(m, HumanMessage)]
    if human_msgs:
        return get_text(human_msgs[0].content)
    if msgs:
        return get_text(msgs[0].content)
    return "Otonom yazılım uygulaması geliştirin."


def append_log(state: CompanyState, node: str, action: str, target: str = "") -> List[Dict[str, str]]:
    """Append a telemetry transition entry to state transition log."""
    log = list(state.get("transition_log") or [])
    cycle = state.get("cycle_count") or 1
    log.append({
        "cycle": str(cycle),
        "node": node,
        "action": action,
        "target": target
    })
    return log
