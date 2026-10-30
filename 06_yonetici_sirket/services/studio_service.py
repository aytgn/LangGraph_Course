"""
Studio Service - Orchestrates LangGraph execution, Factory Chat, HITL Approve/Reject/Revise, and File Updates.
"""

from pathlib import Path
from typing import Dict, Any, Generator, Tuple, Optional, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from model_factory import get_gemini_llm
from data.repositories.app_repository import app_repository
from domain.workflow import studio_app
from domain.utils import get_text, append_log
from tools.registry import ToolRegistry


class StudioService:
    """Application Service orchestrating workflow runs, factory chat, and human decisions."""

    def __init__(self, app_instance=None):
        self.app = app_instance or studio_app

    def get_state(self, thread_id: str) -> Tuple[Dict[str, Any], Tuple[str, ...], bool]:
        """Fetch current state values, next nodes, and whether it is paused at HITL."""
        cfg = {"configurable": {"thread_id": thread_id}}
        try:
            snap = self.app.get_state(cfg)
        except Exception:
            return {}, (), False
        if not snap:
            return {}, (), False
        values = snap.values or {}
        next_nodes = tuple(snap.next) if snap.next else ()
        waiting_hitl = bool(next_nodes and "Deployment_Gate" in next_nodes)
        return values, next_nodes, waiting_hitl

    def get_conversation_messages(self, thread_id: str) -> List[Dict[str, str]]:
        """Return formatted conversation messages for the given project thread."""
        values, _, _ = self.get_state(thread_id)
        msgs = values.get("messages") or []
        result: List[Dict[str, str]] = []
        for m in msgs:
            role = "user" if isinstance(m, HumanMessage) else "assistant"
            txt = get_text(m.content)
            if txt.startswith("[SORU]: "):
                txt = txt[len("[SORU]: "):]
            result.append({"role": role, "content": txt})
        return result

    def chat_with_factory_team(self, thread_id: str, user_message: str) -> str:
        """
        Direct interactive conversation with the Software Factory team (Studio Director,
        CTO & Lead Developer) with full awareness of the active project's PRD, architecture & code.
        Does NOT trigger a full code regeneration loop unless asked via build mode.
        """
        app_repository.touch_project(thread_id)
        values, next_nodes, waiting_hitl = self.get_state(thread_id)

        app_name = values.get("app_name") or "(Henüz oluşturulmadı)"
        app_type = values.get("app_type") or "Belirlenmedi"
        tech_stack = ", ".join(values.get("tech_stack") or []) or "Belirlenmedi"
        code_files = values.get("code_files") or {}
        files_summary = ", ".join(f"{k} ({len(v.splitlines())} satır)" for k, v in code_files.items()) or "Henüz kod üretilmedi"
        prd_excerpt = (values.get("prd_spec") or values.get("purpose_summary") or "Henüz PRD yok")[:1200]
        arch_excerpt = (values.get("architecture_spec") or "Henüz mimari yok")[:1200]
        qa_excerpt = (values.get("qa_report") or "Henüz QA raporu yok")[:800]

        code_snippets = ""
        if code_files:
            code_snippets = "\n\n".join(
                f"--- {fname} ---\n{content[:1500]}" for fname, content in list(code_files.items())[:4]
            )

        status_desc = (
            "Kurucu Onay/Red/Revizyon Kapısında (HITL) bekliyor"
            if waiting_hitl
            else ("Fiziksel diske inşa edildi" if values.get("is_deployed") else ("Kod reddedildi" if values.get("is_rejected") else "Yeni / Geliştirme aşamasında"))
        )

        sys_prompt = f"""Sen Otonom Yazılım Fabrikası'nın Baş Mimarı ve Stüdyo Direktörüsün.
Kurucu Başkan şu anda seninle aktif uygulama projesi hakkında doğrudan görüşüyor.

AKTİF PROJE DURUMU ({thread_id}):
- Uygulama Adı: {app_name} ({app_type})
- Mevcut Durum: {status_desc}
- Teknoloji Yığını: {tech_stack}
- Üretilen Dosyalar: {files_summary}

PRD ÖZETİ:
{prd_excerpt}

MİMARİ ÖZETİ:
{arch_excerpt}

QA ÖZETİ:
{qa_excerpt}

{"KOD ÖNİZLEMESİ:\n" + code_snippets if code_snippets else ""}

GÖREVİN:
Kurucunun sorusunu, kod inceleme yorumunu, mimari danışmasını veya değişiklik fikrini somut, net ve teknik olarak doyurucu şekilde yanıtla.
Eğer kurucu kodda bir değişiklik yapılmasını istiyorsa, nasıl yapılacağını açıkla ve isterse hemen alt kısımdaki 'İnşa / Revizyon Başlat' moduyla veya Onay/Revizyon paneliyle bunu koda uygulayabileceğini belirt."""

        llm = get_gemini_llm(temperature=0.35)
        history_msgs = [SystemMessage(content=sys_prompt)]
        for prev in (values.get("messages") or [])[-6:]:
            if isinstance(prev, HumanMessage):
                history_msgs.append(HumanMessage(content=get_text(prev.content)))
            else:
                history_msgs.append(AIMessage(content=get_text(prev.content)))
        history_msgs.append(HumanMessage(content=user_message))

        resp = llm.invoke(history_msgs)
        reply_text = f"🗣️ **[Fabrika Baş Mimarı & Direktör]:**\n\n{get_text(resp.content)}"

        # Persist conversation in thread state (works for both new and existing threads)
        cfg = {"configurable": {"thread_id": thread_id}}
        self.app.update_state(
            cfg,
            {
                "messages": [
                    HumanMessage(content=f"[SORU]: {user_message}"),
                    AIMessage(content=reply_text),
                ]
            },
        )
        return reply_text

    def start_new_build(self, thread_id: str, directive: str) -> Generator[Dict[str, Any], None, None]:
        """Start a fresh cyclical build from scratch for the given thread."""
        app_repository.touch_project(thread_id)
        cfg = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=directive)],
            "next_step": "Studio_Director",
            "app_name": None,
            "app_slug": None,
            "app_type": None,
            "purpose_summary": None,
            "core_features": None,
            "prd_spec": None,
            "tech_stack": None,
            "database_choice": None,
            "entrypoint_file": None,
            "planned_files": None,
            "architecture_spec": None,
            "code_files": None,
            "total_loc": 0,
            "code_verified_by_qa": False,
            "qa_passed": False,
            "qa_report": None,
            "qa_issues": [],
            "revision_count": 0,
            "founder_feedback": None,
            "feedback_target": None,
            "is_rejected": False,
            "rejection_reason": None,
            "is_deployed": False,
            "app_folder": None,
            "run_command_hint": None,
            "cycle_count": 0,
            "transition_log": [],
        }
        for event in self.app.stream(initial_state, config=cfg, stream_mode="updates"):
            yield event

        vals, _, _ = self.get_state(thread_id)
        if vals.get("app_name"):
            app_repository.touch_project(thread_id, display_name=vals["app_name"])

    def start_or_continue_build(
        self, thread_id: str, directive_or_revision: str, target: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        If thread has no PRD yet, run a brand-new build; otherwise run a cyclical
        revision / feature update on the existing application.
        """
        values, _, _ = self.get_state(thread_id)
        if not values.get("prd_spec"):
            yield from self.start_new_build(thread_id, directive_or_revision)
        else:
            yield from self.request_revision(thread_id, directive_or_revision, target=target)

    def run_cycle(self, thread_id: str, input_payload: Any) -> Generator[Dict[str, Any], None, None]:
        """Low-level stream wrapper preserved for compatibility."""
        app_repository.touch_project(thread_id)
        cfg = {"configurable": {"thread_id": thread_id}}
        for event in self.app.stream(input_payload, config=cfg, stream_mode="updates"):
            yield event

    def approve_and_deploy(self, thread_id: str) -> Generator[Dict[str, Any], None, None]:
        """Founder approves application at HITL gate, resuming graph to execute Deployment_Gate."""
        app_repository.touch_project(thread_id)
        cfg = {"configurable": {"thread_id": thread_id}}
        self.app.update_state(
            cfg,
            {
                "is_rejected": False,
                "rejection_reason": None,
                "founder_feedback": None,
                "messages": [HumanMessage(content="[KURUCU KARARI]: ✅ Mimari ve kod onaylandı, fiziksel paketi inşa edin.")],
            },
        )
        for event in self.app.stream(None, config=cfg, stream_mode="updates"):
            yield event
        app_repository.touch_project(thread_id)

    def request_revision(
        self, thread_id: str, feedback: str, target: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Founder requests revisions (from HITL gate, rejected state, or post-deployment),
        routing cyclically back to the chosen department (or AUTO via Studio_Director).
        """
        app_repository.touch_project(thread_id)
        cfg = {"configurable": {"thread_id": thread_id}}
        _, _, waiting_hitl = self.get_state(thread_id)

        effective_target = None if target in (None, "", "AUTO") else target
        fb_msg = HumanMessage(content=f"[KURUCU REVİZYON TALEBİ]: {feedback.strip()}")

        if waiting_hitl:
            # Advance past paused Deployment_Gate directly back into Studio_Director
            self.app.update_state(
                cfg,
                {
                    "founder_feedback": feedback.strip(),
                    "feedback_target": effective_target,
                    "is_rejected": False,
                    "rejection_reason": None,
                    "is_deployed": False,
                    "qa_passed": False,
                    "code_verified_by_qa": False,
                    "messages": [fb_msg],
                },
                as_node="Deployment_Gate",
            )
            for event in self.app.stream(None, config=cfg, stream_mode="updates"):
                yield event
        else:
            payload = {
                "founder_feedback": feedback.strip(),
                "feedback_target": effective_target,
                "is_rejected": False,
                "rejection_reason": None,
                "is_deployed": False,
                "qa_passed": False,
                "code_verified_by_qa": False,
                "messages": [fb_msg],
            }
            for event in self.app.stream(payload, config=cfg, stream_mode="updates"):
                yield event

        app_repository.touch_project(thread_id)

    def reject_code_and_rewrite(
        self, thread_id: str, reason: str = "", target: str = "Lead_Developer"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Reject generated code completely, wipe code_files, and trigger a fresh
        re-implementation cycle in Lead_Developer (or System_Architect).
        """
        clean_reason = reason.strip() or "Üretilen kod beklentiyi karşılamadı; temiz ve eksiksiz şekilde baştan yazılmalı."
        app_repository.touch_project(thread_id)
        cfg = {"configurable": {"thread_id": thread_id}}
        _, _, waiting_hitl = self.get_state(thread_id)

        rej_msg = HumanMessage(content=f"[KURUCU KARARI — KOD REDDEDİLDİ & YENİDEN YAZIM]: {clean_reason}")
        state_patch = {
            "code_files": None,
            "total_loc": 0,
            "code_verified_by_qa": False,
            "qa_passed": False,
            "qa_issues": [],
            "is_deployed": False,
            "is_rejected": False,
            "rejection_reason": None,
            "founder_feedback": f"Önceki kod reddedildi! Şu gerekçeyle sıfırdan temiz kodla: {clean_reason}",
            "feedback_target": target if target in ("Lead_Developer", "System_Architect", "Product_Lead") else "Lead_Developer",
            "messages": [rej_msg],
        }

        if waiting_hitl:
            self.app.update_state(cfg, state_patch, as_node="Deployment_Gate")
            for event in self.app.stream(None, config=cfg, stream_mode="updates"):
                yield event
        else:
            for event in self.app.stream(state_patch, config=cfg, stream_mode="updates"):
                yield event

        app_repository.touch_project(thread_id)

    def reject_and_cancel_project(self, thread_id: str, reason: str = "") -> bool:
        """
        Reject generated code and cancel physical deployment cleanly so the project
        exits the HITL gate and is persisted in SQLite as '❌ Kod Reddedildi'.
        """
        clean_reason = reason.strip() or "Kurucu Başkan tarafından kod/mimari onaylanmadı ve dağıtım iptal edildi."
        app_repository.touch_project(thread_id)
        cfg = {"configurable": {"thread_id": thread_id}}
        values, _, waiting_hitl = self.get_state(thread_id)

        rej_human = HumanMessage(content=f"[KURUCU KARARI — KOD REDDEDİLDİ]: {clean_reason}")

        if waiting_hitl:
            self.app.update_state(
                cfg,
                {
                    "is_rejected": True,
                    "rejection_reason": clean_reason,
                    "is_deployed": False,
                    "founder_feedback": None,
                    "feedback_target": None,
                    "messages": [rej_human],
                },
                as_node="Deployment_Gate",
            )
            # Deterministically runs Studio_Director's fast rejection branch (no LLM call) -> END
            self.app.invoke(None, config=cfg)
        else:
            closing_ai = AIMessage(
                content=(
                    f"❌ **[STÜDYO BİLDİRİMİ — KOD REDDEDİLDİ]:** Dağıtım iptal edildi.\n"
                    f"- **Gerekçe:** {clean_reason}"
                )
            )
            self.app.update_state(
                cfg,
                {
                    "is_rejected": True,
                    "rejection_reason": clean_reason,
                    "is_deployed": False,
                    "founder_feedback": None,
                    "messages": [rej_human, closing_ai],
                    "transition_log": append_log(values, "Studio_Director", f"Kod reddedildi: {clean_reason}", "END"),
                },
            )
        app_repository.touch_project(thread_id)
        return True

    def save_edited_code_file(self, thread_id: str, filename: str, new_content: str) -> Tuple[bool, List[str]]:
        """
        CRUD UPDATE for generated code files: saves manual code edits into state,
        runs deterministic AST validation via ToolRegistry, and syncs to disk if deployed.
        """
        values, _, _ = self.get_state(thread_id)
        code_files = dict(values.get("code_files") or {})
        code_files[filename] = new_content

        entrypoint = values.get("entrypoint_file") or "app.py"
        ast_tool = ToolRegistry.get_tool("deterministic_ast_suite")
        errors = ast_tool.run(code_files=code_files, entrypoint=entrypoint) if ast_tool else []

        total_loc = sum(
            len([ln for ln in content.splitlines() if ln.strip()])
            for fn, content in code_files.items()
            if fn.endswith(".py")
        )

        cfg = {"configurable": {"thread_id": thread_id}}
        self.app.update_state(
            cfg,
            {
                "code_files": code_files,
                "total_loc": total_loc,
                "qa_passed": len(errors) == 0,
                "qa_issues": errors,
            },
        )

        # Sync to physical folder if already deployed
        app_folder = values.get("app_folder")
        if values.get("is_deployed") and app_folder:
            target_file = Path(app_folder) / filename
            if target_file.parent.exists():
                target_file.write_text(new_content, encoding="utf-8", errors="replace")

        app_repository.touch_project(thread_id)
        return (len(errors) == 0), errors

    def generate_zip_bytes(self, state_values: Dict[str, Any]) -> bytes:
        """Create downloadable ZIP archive bytes via ToolRegistry."""
        zip_tool = ToolRegistry.get_tool("zip_packager_tool")
        if zip_tool:
            return zip_tool.run(state_values)
        return b""


studio_service = StudioService()
