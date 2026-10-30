"""
Studio Director Node & Cyclical Routing Engine.
"""

import sys
from pathlib import Path
from langchain_core.messages import AIMessage, HumanMessage

_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from config.settings import config
from model_factory import get_gemini_llm
from domain.state import CompanyState
from domain.schemas import DirectorRouteOutput
from domain.utils import append_log, console


def studio_director_node(state: CompanyState) -> dict:
    """
    Studio Director evaluates global project state, QA loops, rejections,
    and Founder revisions to route execution cyclically.
    """
    current_cycle = (state.get("cycle_count") or 0) + 1
    state_with_cycle = {**state, "cycle_count": current_cycle}
    console.print(f"\n[bold gold1]👑 [STÜDYO DİREKTÖRÜ - Döngü #{current_cycle}]:[/bold gold1] Durum denetleniyor...")

    has_prd = bool(state.get("prd_spec"))
    has_arch = bool(state.get("architecture_spec"))
    has_code = bool(state.get("code_files"))
    code_verified = bool(state.get("code_verified_by_qa"))
    qa_passed = bool(state.get("qa_passed"))
    qa_issues = state.get("qa_issues") or []
    rev_count = state.get("revision_count") or 0
    founder_feedback = (state.get("founder_feedback") or "").strip()
    feedback_target = state.get("feedback_target")
    is_deployed = bool(state.get("is_deployed"))
    is_rejected = bool(state.get("is_rejected"))

    # 1. Rejected / Cancelled terminal state
    if is_rejected and not founder_feedback:
        rej_reason = state.get("rejection_reason") or "Kurucu kararıyla kod/dağıtım reddedildi."
        closing_rej = AIMessage(
            content=(
                f"❌ **[STÜDYO BİLDİRİMİ — KOD REDDEDİLDİ]:** `{state.get('app_name') or 'Uygulama'}` "
                f"inşası Kurucu Başkan tarafından reddedildi / durduruldu.\n\n"
                f"- **Reddetme Gerekçesi:** {rej_reason}\n"
                f"- *İstediğiniz zaman aşağıdan yeni bir revizyon direktifi yazarak veya sıfırdan inşa başlatarak devam edebilirsiniz.*"
            )
        )
        return {
            "next_step": "END",
            "cycle_count": current_cycle,
            "transition_log": append_log(state_with_cycle, "Studio_Director", f"Kod reddedildi: {rej_reason}", "END"),
            "messages": [closing_rej],
        }

    # 2. Deployed terminal state (unless Founder sent new post-deployment feedback)
    if is_deployed and not founder_feedback:
        closing_ok = AIMessage(
            content=(
                f"🚀 **[STÜDYO TESLİMAT BİLDİRİMİ]:** `{state.get('app_name')}` uygulaması tüm mühendislik ve QA "
                f"süreçlerinden geçerek fiziksel diske inşa edildi!\n\n"
                f"- **Fiziksel Klasör:** `{state.get('app_folder')}`\n"
                f"- **Çalıştırma Komutu:** `{state.get('run_command_hint')}` *(veya **2. Kod Gezgini & Çalıştırma** sekmesinden tek tıkla başlatın)*"
            )
        )
        return {
            "next_step": "END",
            "cycle_count": current_cycle,
            "transition_log": append_log(state_with_cycle, "Studio_Director", "Uygulama fiziksel diske paketlendi, süreç tamamlandı.", "END"),
            "messages": [closing_ok],
        }

    # 3. Founder Revision / Rewrite Request takes highest priority when PRD exists!
    if founder_feedback and has_prd:
        valid_targets = ("Product_Lead", "System_Architect", "Lead_Developer")
        if feedback_target in valid_targets:
            next_target = feedback_target
            reason = f"Kurucu revizyon/yeniden yazım direktifi alındı -> '{next_target}' birimine yönlendirildi."
        else:
            director_llm = get_gemini_llm(temperature=0.1).with_structured_output(DirectorRouteOutput)
            route_prompt = (
                f"MEVCUT UYGULAMA: {state.get('app_name')} ({state.get('app_type')})\n"
                f"MEVCUT TEKNOLOJİLER: {state.get('tech_stack')}\n"
                f"KURUCU BAŞKAN REVİZYON TALEBİ: \"{founder_feedback}\"\n\n"
                "Bu talep ürün kapsamını temelden değiştiriyorsa 'Product_Lead', "
                "altyapı/framework/veritabanı değişikliği içeriyorsa 'System_Architect', "
                "özellik/arayüz/iş mantığı/kod güncellemesi içeriyorsa 'Lead_Developer' seç."
            )
            decision: DirectorRouteOutput = director_llm.invoke([HumanMessage(content=route_prompt)])
            next_target = decision.next_node if decision.next_node in valid_targets else "Lead_Developer"
            reason = f"Kurucu revizyonu analiz edildi ({decision.reasoning}) -> '{next_target}' seçildi."

        console.print(f"  [cyan]-> Revizyon Rotası:[/cyan] [bold yellow]{next_target}[/bold yellow] ({reason})")
        return {
            "next_step": next_target,
            "cycle_count": current_cycle,
            "is_deployed": False,
            "is_rejected": False,
            "rejection_reason": None,
            "code_verified_by_qa": False,
            "qa_passed": False,
            "feedback_target": None,
            "transition_log": append_log(state_with_cycle, "Studio_Director", reason, next_target),
        }

    # 4. Standard Cyclical Pipeline Progression + QA Self-Healing Loop
    if not has_prd:
        next_target = "Product_Lead"
        reason = "Ürün kapsamı ve PRD hazırlanmak üzere CPO'ya yönlendirildi."
    elif not has_arch:
        next_target = "System_Architect"
        reason = "PRD hazır -> Teknoloji yığını ve modül mimarisi için CTO'ya yönlendirildi."
    elif not has_code:
        next_target = "Lead_Developer"
        reason = "Mimari hazır -> Çok dosyalı uygulama kodlaması için Kıdemli Mühendise yönlendirildi."
    elif not code_verified:
        next_target = "QA_Security_Lead"
        reason = "Kod üretildi -> Deterministik AST ve kalite denetimi için QA Liderine yönlendirildi."
    elif not qa_passed and qa_issues and rev_count < config.MAX_QA_SELF_HEAL_RETRIES:
        next_target = "Lead_Developer"
        reason = (
            f"QA/AST denetiminde {len(qa_issues)} sorun yakalandı -> "
            f"Otomatik düzeltme döngüsü için Yazılımcıya geri gönderiliyor (Tur #{rev_count + 1})."
        )
    else:
        next_target = "Deployment_Gate"
        reason = "Kod ve QA süreci tamamlandı -> Kurucu Başkan Onay / Red / Revizyon Kapısına (HITL) sunuluyor."

    console.print(f"  [cyan]-> Seçilen Rota:[/cyan] [bold green]{next_target}[/bold green] ({reason})")
    return {
        "next_step": next_target,
        "cycle_count": current_cycle,
        "transition_log": append_log(state_with_cycle, "Studio_Director", reason, next_target),
    }


def director_router(state: CompanyState) -> str:
    """LangGraph conditional edge router."""
    return state.get("next_step") or "Studio_Director"
