"""
Domain State Definitions for LangGraph AI Software Studio.
"""

from typing import Annotated, Sequence, List, Dict, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CompanyState(TypedDict):
    """
    State contract for the Cyclical AI Software Studio.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_step: Optional[str]

    # Application identity & product definition (CPO / Product_Lead)
    app_name: Optional[str]
    app_slug: Optional[str]
    app_type: Optional[str]          # "Streamlit Web App" | "FastAPI REST Service" | "CLI & Automation Tool"
    purpose_summary: Optional[str]
    core_features: Optional[List[str]]
    prd_spec: Optional[str]

    # Technical architecture & stack (CTO / System_Architect)
    tech_stack: Optional[List[str]]
    database_choice: Optional[str]
    entrypoint_file: Optional[str]
    planned_files: Optional[List]
    architecture_spec: Optional[str]

    # Codebase & engineering artifacts (Lead_Developer)
    code_files: Optional[Dict[str, str]]
    total_loc: Optional[int]
    code_verified_by_qa: Optional[bool]

    # QA & AST validation loop (QA_Security_Lead)
    qa_passed: Optional[bool]
    qa_report: Optional[str]
    qa_issues: Optional[List[str]]
    revision_count: Optional[int]

    # Founder feedback, rejection & HITL approval (Deployment_Gate / Founder)
    founder_feedback: Optional[str]
    feedback_target: Optional[str]
    is_rejected: Optional[bool]
    rejection_reason: Optional[str]

    # Deployment output
    is_deployed: Optional[bool]
    app_folder: Optional[str]
    run_command_hint: Optional[str]

    # Cyclical telemetry
    cycle_count: Optional[int]
    transition_log: Optional[List[Dict[str, str]]]
