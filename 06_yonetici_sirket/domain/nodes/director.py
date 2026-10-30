"""
Studio Director Node & Cyclical Routing Engine.
"""

import sys
from pathlib import Path
from langchain_core.messages import AIMessage
from rich.console import Console

# Ensure root directory is on sys.path
_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from model_factory import get_gemini_llm
from domain.state import CompanyState
from domain.schemas import DirectorRouteOutput
from domain.utils import get_clean_user_directive, append_log

console = Console(force_terminal=False, legacy_windows=False)


def studio_director_node(state: CompanyState) -> dict:
    """
    Studio Director evaluates the global project state, cycle count, and feedback
    to route execution cyclically.
    """
    current_cycle = (state.get("cycle_count") or 0) + 1
    console.print(f"\n[bold gold1]👑 [STÜDYO DİREKTÖRÜ - Döngü #{current_cycle}]:[/bold gold1] Durum denetleniyor...")

    user_directive = get_clean_user_directive(state)
    has_prd = bool(state.get("prd_spec"))
    has_arch = bool(state.get("architecture_spec"))
    has_code = bool(state.get("code_files"))
    qa_passed = bool(state.get("qa_passed"))
    qa_issues = state.get("qa_issues") or []
    founder_feedback = state.get("founder_feedback")
    feedback_target = state.get("feedback_target")
    is_deployed = bool(state.get("is_deployed"))

    # Terminal state check
    if is_deployed:
        return {
            "next_step": "END",
            "cycle_count": current_cycle,
            "transition_log": append_log(state, "Studio_Director", "Proje başarıyla tamamlandı", "END")
        }

    # 1. Deterministic Rule-Based Fast Routing (Efficiency & Safety)
    if not has_prd:
        next_target = "Product_Lead"
        reason = "Henüz ürün PRD ve kapsam dokümanı hazırlanmadı. İş CPO'ya devrediliyor."
    elif not has_arch:
        next_target = "System_Architect"
        reason = "PRD onaylandı, teknik altyapı ve dosya mimarisi için CTO'ya devrediliyor."
    elif not has_code:
        next_target = "Lead_Developer"
        reason = "Mimari şema hazır, uygulama kodlaması için Kıdemli Mühendise devrediliyor."
    elif not qa_passed and qa_issues:
        next_target = "Lead_Developer"
        reason = f"QA/AST denetiminde {len(qa_issues)} sorun bulundu! Otomatik düzeltme için koda geri dönülüyor."
    elif not qa_passed and not state.get("code_verified_by_qa"):
        next_target = "QA_Security_Lead"
        reason = "Kod üretildi, AST ve güvenlik denetimi için QA Liderine devrediliyor."
    elif qa_passed and not founder_feedback:
        next_target = "Deployment_Gate"
        reason = "Kod ve QA onaylandı! Kurucu Başkanın onay/revizyon kapısına sunuluyor."
    elif founder_feedback and feedback_target:
        next_target = feedback_target
        reason = f"Kurucu Başkandan revizyon direktifi geldi: '{founder_feedback[:80]}...'. Hedef: {feedback_target}."
    else:
        # LLM based reasoning for complex/unhandled cyclical states
        director_llm = get_gemini_llm(temperature=0.1)
        structured_director = director_llm.with_structured_output(DirectorRouteOutput)

        prompt = f"""Sen Otonom Yazılım Evi'nin Stüdyo Direktörüsün (Studio Director / Managing Partner).
Görevin şirket içindeki canlı proje durumunu inceleyip işi sıradaki en doğru departmana yönlendirmektir.

DÖNGÜ: #{current_cycle}
KURUCU DİREKTİFİ: {user_directive}
PRD VAR MI: {has_prd} (Uygulama: {state.get('app_name', '-')}, Tip: {state.get('app_type', '-')})
MİMARİ VAR MI: {has_arch} (Stack: {state.get('tech_stack', [])})
KOD VAR MI: {has_code} (Dosya Sayısı: {len(state.get('code_files') or {})}, Toplam LOC: {state.get('total_loc', 0)})
QA GEÇTİ Mİ: {qa_passed} (Hatalar: {qa_issues})
KURUCU REVİZYON NOTU: {founder_feedback}
DAĞITILDI MI: {is_deployed}

HEDEF SEÇENEKLERİ:
- 'Product_Lead': PRD veya kapsam eksikse ya da kurucu ürün fikrini değiştirdiyse.
- 'System_Architect': Teknoloji stack'i, mimari veya modül şeması tasarlanacaksa/değişecekse.
- 'Lead_Developer': Sıfırdan kod yazılacaksa veya QA/Kurucu revizyonlarına göre kod düzeltilecekse.
- 'QA_Security_Lead': Kod yazıldıktan sonra AST, sözdizimi ve import denetimi yapılacaksa.
- 'Deployment_Gate': Kod QA'dan başarıyla geçtiyse ve Kurucu Başkan onayına sunulacaksa.
"""
        decision: DirectorRouteOutput = structured_director.invoke([AIMessage(content=prompt)])
        next_target = decision.next_node
        reason = decision.reasoning

    console.print(f"  [cyan]-> Seçilen Rota:[/cyan] [bold green]{next_target}[/bold green] ({reason})")

    return {
        "next_step": next_target,
        "cycle_count": current_cycle,
        "transition_log": append_log(state, "Studio_Director", reason, next_target)
    }


def director_router(state: CompanyState) -> str:
    """LangGraph conditional edge router."""
    return state.get("next_step") or "Studio_Director"
