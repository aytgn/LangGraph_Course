"""
Domain Utilities for Node Execution & Telemetry.
Includes encoding-safe RobustConsole for Windows and cross-platform terminal streams.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from rich.console import Console
from domain.state import CompanyState

# Ensure UTF-8 I/O for stdout & stderr across Windows environments
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class RobustConsole:
    """
    Wrapper around rich.Console guaranteeing zero crashes on character encoding
    mismatches (e.g. Windows cp1252 / charmap unable to encode emojis like 👑 or 🚀).
    """

    def __init__(self):
        self._console = Console(force_terminal=False, legacy_windows=False)

    def print(self, *args, **kwargs):
        try:
            self._console.print(*args, **kwargs)
        except (UnicodeEncodeError, UnicodeError):
            try:
                safe_args = []
                for a in args:
                    if isinstance(a, str):
                        # Transliterate or replace characters unmappable to target stream
                        safe_args.append(a.encode("ascii", errors="backslashreplace").decode("ascii"))
                    else:
                        safe_args.append(a)
                self._console.print(*safe_args, **kwargs)
            except Exception:
                pass
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._console, name)


# Global singleton console instance for all domain nodes
console = RobustConsole()


def get_text(content: Any) -> str:
    """Safely extract plain string from langchain message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)


def get_clean_user_directive(state: CompanyState) -> str:
    """Extract founder's initial or latest directive from the message history."""
    msgs = state.get("messages") or []
    human_msgs = [
        m for m in msgs
        if isinstance(m, HumanMessage) and not get_text(m.content).strip().startswith("[SORU]")
    ]
    if human_msgs:
        return get_text(human_msgs[0].content)
    if msgs:
        return get_text(msgs[0].content)
    return "Otonom yazılım uygulaması geliştirin."


def append_log(state: CompanyState, node: str, action: str, target: str = "") -> List[Dict[str, str]]:
    """Append a timestamped telemetry transition entry to state transition log."""
    log = list(state.get("transition_log") or [])
    cycle = state.get("cycle_count") or 1
    log.append({
        "cycle": str(cycle),
        "node": node,
        "action": action,
        "target": target,
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    return log
