"""
Discovery Service - Product & Architecture Deliberation Room.
Connects CPO, CTO, and Technical PM personas with Second Brain Vault & Factory Bridge.
"""

from datetime import datetime
from typing import List, Dict, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from model_factory import get_gemini_llm
from data.repositories.vault_repository import vault_repository
from data.repositories.app_repository import app_repository
from domain.schemas import ADRDecisionOutput
from domain.utils import get_text
from tools.registry import ToolRegistry
from tools.disk_operations import sanitize_slug
from meta_katman.meta_motoru import (
    COFOUNDER_SYSTEM_PROMPT,
    SKEPTIC_SYSTEM_PROMPT,
    SCRIBE_SYSTEM_PROMPT,
    OperationalBriefSynthesis,
)


def _format_deliberation_history(chat_history: List[Dict[str, str]], max_turns: int = 12) -> str:
    recent = chat_history[-max_turns:] if len(chat_history) > max_turns else chat_history
    role_names = {
        "user": "KURUCU BAŞKAN",
        "cpo": "CPO (ÜRÜN LİDERİ)",
        "cto": "CTO (BAŞ MİMAR)",
        "scribe": "TEKNİK PM (YOL HARİTASI)",
    }
    lines = []
    for m in recent:
        r = role_names.get(m.get("role", "user"), m.get("role", "USER").upper())
        lines.append(f"{r}: {m.get('content', '')}")
    return "\n\n".join(lines)


class DiscoveryService:
    """Orchestrates multi-agent deliberations in Tab 0 and bridges specs to Tab 1 Factory."""

    def __init__(self):
        self.vault = vault_repository

    def get_vision_manifesto(self) -> str:
        return self.vault.get_vision()

    def update_vision_manifesto(self, content: str) -> bool:
        return self.vault.update_vision(content)

    def consult_cpo(self, user_msg: str, prior_history: List[Dict[str, str]]) -> str:
        """Consult AI Co-Founder & CPO on product purpose and MVP scope."""
        vision = self.get_vision_manifesto()
        system = COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)
        history_str = _format_deliberation_history(prior_history)
        llm = get_gemini_llm(temperature=0.5)

        prompt = (
            f"--- ÖNCEKİ TARTIŞMA GEÇMİŞİ ---\n{history_str or '(Yeni oturum)'}\n\n"
            f"KURUCU BAŞKANIN YENİ MESAJI:\n{user_msg}"
        )
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=prompt)])
        return get_text(resp.content)

    def consult_cto(self, user_msg: str, prior_history: List[Dict[str, str]]) -> str:
        """Consult Principal Architect & CTO on tech stack, feasibility, and database."""
        vision = self.get_vision_manifesto()
        system = SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)
        history_str = _format_deliberation_history(prior_history)
        llm = get_gemini_llm(temperature=0.25)

        prompt = (
            f"--- ÖNCEKİ TARTIŞMA GEÇMİŞİ (CPO & KURUCU DAHİL) ---\n{history_str or '(Yeni oturum)'}\n\n"
            f"KURUCU BAŞKANIN YENİ MESAJI / TEKNİK SORUSU:\n{user_msg}"
        )
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=prompt)])
        return get_text(resp.content)

    def run_council_debate(self, user_msg: str, prior_history: List[Dict[str, str]]) -> Dict[str, str]:
        """Run joint CPO + CTO + Technical PM Scribe council deliberation."""
        vision = self.get_vision_manifesto()
        history_str = _format_deliberation_history(prior_history)

        # 1. CPO
        cpo_llm = get_gemini_llm(temperature=0.55)
        cpo_prompt = (
            f"{COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)}\n\n"
            f"--- GEÇMİŞ BAĞLAM ---\n{history_str}\n\n"
            f"KURUCU GÜNDEMİ: {user_msg}\n\n"
            "Uygulamanın amacını, kullanıcı akışını ve en kritik MVP özelliklerini somutlaştır."
        )
        cpo_reply = get_text(cpo_llm.invoke(cpo_prompt).content)

        # 2. CTO
        cto_llm = get_gemini_llm(temperature=0.25)
        cto_prompt = (
            f"{SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)}\n\n"
            f"KURUCU GÜNDEMİ: {user_msg}\n\n"
            f"CPO'NUN ÜRÜN ÖNERİSİ:\n{cpo_reply}\n\n"
            "Bu ürünü hangi Python framework'ü (Streamlit / FastAPI / CLI), hangi veri katmanı (SQLite3 / JSON) "
            "ve hangi modüler dosya şemasıyla kurmamız gerektiğini belirle; aşırı karmaşıklığı buda."
        )
        cto_reply = get_text(cto_llm.invoke(cto_prompt).content)

        # 3. Technical PM Synthesis
        pm_llm = get_gemini_llm(temperature=0.15)
        pm_prompt = (
            f"{SCRIBE_SYSTEM_PROMPT}\n\n"
            f"GÜNDEM: {user_msg}\n\n"
            f"CPO VİZYONU:\n{cpo_reply}\n\n"
            f"CTO MİMARİ KARARI:\n{cto_reply}\n\n"
            "Ortaya çıkan uygulama kapsamını ve teknoloji yığınını net bir 'Uygulama & Mimari Yol Haritası' olarak sentezle."
        )
        pm_reply = get_text(pm_llm.invoke(pm_prompt).content)

        return {"cpo": cpo_reply, "cto": cto_reply, "scribe": pm_reply}

    def bridge_discussion_to_factory(
        self, chat_history: List[Dict[str, str]], custom_notes: str = ""
    ) -> Dict[str, str]:
        """
        Convert Tab 0 product & tech stack discussion into a concrete engineering
        specification, register a new project in SQLite, and return ready build payload.
        """
        history_str = _format_deliberation_history(chat_history, max_turns=16)
        prompt = (
            "Sen Teknik Ürün Yöneticisisin (Technical PM).\n"
            "Aşağıdaki ürün ve teknoloji tartışmasını inceleyerek Otonom Yazılım Fabrikası'na iletilecek "
            "net ve eksiksiz bir **Uygulama Geliştirme Şartnamesi** hazırla.\n\n"
            "Şartnamede şunlar açıkça yer almalıdır:\n"
            "1. Uygulamanın Adı ve Somut Amacı\n"
            "2. Uygulama Türü ve Tercih Edilen Altyapı (Streamlit / FastAPI / CLI, SQLite3 / JSON)\n"
            "3. Uygulanacak Somut MVP Özellikleri ve Veri Akışı\n\n"
            f"--- TARTIŞMA GEÇMİŞİ ---\n{history_str}\n\n"
            f"--- EK TEKNİK TERCİHLER ---\n{custom_notes}\n"
        )
        llm = get_gemini_llm(temperature=0.15).with_structured_output(OperationalBriefSynthesis)
        brief: OperationalBriefSynthesis = llm.invoke(prompt)

        spec_tool = ToolRegistry.get_tool("operational_spec_writer")
        spec_path = spec_tool.run(title=brief.directive_title, directive_text=brief.actionable_prompt) if spec_tool else ""

        base_slug = sanitize_slug(brief.directive_title)[:26]
        new_tid = f"{base_slug}-{datetime.now().strftime('%H%M%S')}"
        clean_tid = app_repository.create_project(
            thread_id=new_tid,
            display_name=brief.directive_title,
            custom_notes="Tartışma Odası konsey kararıyla oluşturuldu.",
            tags="konsey,mvp",
        )

        return {
            "thread_id": clean_tid,
            "title": brief.directive_title,
            "directive_text": brief.actionable_prompt,
            "spec_path": spec_path,
        }

    def finalize_adr_and_note(self, discussion_text: str) -> Tuple[str, str]:
        """Convert deliberation into an ADR decision and save note via ToolRegistry."""
        llm = get_gemini_llm(temperature=0.1)
        structured_adr = llm.with_structured_output(ADRDecisionOutput)
        adr_res: ADRDecisionOutput = structured_adr.invoke([
            SystemMessage(content=SCRIBE_SYSTEM_PROMPT),
            HumanMessage(content=f"TARTIŞMA TUTANAĞI:\n{discussion_text}"),
        ])

        adr_tool = ToolRegistry.get_tool("adr_writer_tool")
        adr_path = (
            adr_tool.run(
                adr_id=adr_res.adr_id,
                title=adr_res.title,
                status=adr_res.status,
                context=adr_res.context,
                decision=adr_res.decision,
                consequences=adr_res.consequences,
            )
            if adr_tool
            else ""
        )

        note_tool = ToolRegistry.get_tool("brainstorm_note_writer")
        note_path = (
            note_tool.run(title=f"Tartisma_{adr_res.title}", content=discussion_text)
            if note_tool
            else ""
        )
        return adr_path, note_path


discovery_service = DiscoveryService()
