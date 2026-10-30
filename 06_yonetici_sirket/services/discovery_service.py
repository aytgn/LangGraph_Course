"""
Discovery Service - Product & Architecture Deliberation Room.
Connects CPO, CTO, and PM personas with Second Brain ADR generation.
"""

from typing import List, Dict, Any, Tuple
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from model_factory import get_gemini_llm
from data.repositories.vault_repository import vault_repository
from tools.registry import ToolRegistry
from domain.schemas import ADRDecisionOutput
from meta_katman.meta_motoru import (
    COFOUNDER_SYSTEM_PROMPT,
    SKEPTIC_SYSTEM_PROMPT,
    SCRIBE_SYSTEM_PROMPT,
)


class DiscoveryService:
    """Orchestrates multi-agent deliberations in the Ideation Room."""

    def __init__(self):
        self.vault = vault_repository

    def get_vision_manifesto(self) -> str:
        return self.vault.get_vision()

    def update_vision_manifesto(self, content: str) -> bool:
        return self.vault.update_vision(content)

    def consult_cpo(self, user_msg: str, chat_history: List[Dict[str, str]]) -> str:
        """Consult AI Co-Founder & CPO on product purpose and MVP scope."""
        vision = self.get_vision_manifesto()
        system = COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)
        llm = get_gemini_llm(temperature=0.4)

        messages = [SystemMessage(content=system)]
        for m in chat_history[-6:]:
            if m.get("role") == "user":
                messages.append(HumanMessage(content=m.get("content", "")))
            elif m.get("role") == "cpo":
                messages.append(AIMessage(content=m.get("content", "")))
        messages.append(HumanMessage(content=user_msg))

        resp = llm.invoke(messages)
        return resp.content if isinstance(resp.content, str) else str(resp.content)

    def consult_cto(self, user_msg: str, cpo_context: str, chat_history: List[Dict[str, str]]) -> str:
        """Consult Principal Architect & CTO on tech stack, feasibility, and database."""
        vision = self.get_vision_manifesto()
        system = SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)
        llm = get_gemini_llm(temperature=0.2)

        prompt = f"""CPO VE KURUCU TARTIŞMASI:
{cpo_context}

KURUCUNUN SON SORUSU / TEKNİK TALEBİ:
{user_msg}
"""
        messages = [SystemMessage(content=system)]
        for m in chat_history[-6:]:
            if m.get("role") == "user":
                messages.append(HumanMessage(content=m.get("content", "")))
            elif m.get("role") == "cto":
                messages.append(AIMessage(content=m.get("content", "")))
        messages.append(HumanMessage(content=prompt))

        resp = llm.invoke(messages)
        return resp.content if isinstance(resp.content, str) else str(resp.content)

    def finalize_adr_and_note(self, discussion_text: str) -> Tuple[str, str]:
        """Convert deliberation into an ADR decision and save note via ToolRegistry."""
        vision = self.get_vision_manifesto()
        system = SCRIBE_SYSTEM_PROMPT
        llm = get_gemini_llm(temperature=0.1)

        structured_adr = llm.with_structured_output(ADRDecisionOutput)
        adr_res: ADRDecisionOutput = structured_adr.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"TARTIŞMA TUTANAĞI:\n{discussion_text}")
        ])

        # Use ADRWriterTool via ToolRegistry
        adr_tool = ToolRegistry.get_tool("adr_writer_tool")
        if adr_tool:
            adr_path = adr_tool.run(
                adr_id=adr_res.adr_id,
                title=adr_res.title,
                status=adr_res.status,
                context=adr_res.context,
                decision=adr_res.decision,
                consequences=adr_res.consequences,
            )
        else:
            adr_path = ""

        # Use BrainstormNoteWriterTool via ToolRegistry
        note_tool = ToolRegistry.get_tool("brainstorm_note_writer")
        if note_tool:
            note_path = note_tool.run(
                title=f"Tartisma_{adr_res.title}",
                content=discussion_text
            )
        else:
            note_path = ""

        return adr_path, note_path


discovery_service = DiscoveryService()
