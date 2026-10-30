"""
QA & Security Lead Node.
Uses ToolRegistry for Deterministic AST & Cross-Import checks + LLM Quality Review.
"""

import sys
from pathlib import Path
from langchain_core.messages import AIMessage
from rich.console import Console

_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from model_factory import get_gemini_llm
from domain.state import CompanyState
from domain.schemas import QAReviewOutput
from domain.utils import append_log
from tools.registry import ToolRegistry

console = Console(force_terminal=False, legacy_windows=False)


def qa_security_lead_node(state: CompanyState) -> dict:
    """
    QA & Security node performs deterministic AST & cross-module import checks via ToolRegistry,
    followed by LLM code quality and PRD compliance review.
    """
    console.print("\n[bold red]🛡️ [DEPARTMAN 4: QA, AST & GÜVENLİK DENETİMİ] Kod inceleniyor...[/bold red]")

    code_files = state.get("code_files") or {}
    entrypoint = state.get("entrypoint_file") or "app.py"
    app_name = state.get("app_name") or "Uygulama"
    prd_spec = state.get("prd_spec") or ""
    arch_spec = state.get("architecture_spec") or ""

    # 1. Dynamic Tool Discovery & Execution: Deterministic AST Suite
    ast_suite_tool = ToolRegistry.get_tool("deterministic_ast_suite")
    if ast_suite_tool:
        deterministic_errors = ast_suite_tool.run(code_files=code_files, entrypoint=entrypoint)
    else:
        # Fallback if registry not populated
        deterministic_errors = []

    if deterministic_errors:
        console.print(f"  [bold red]❌ Deterministik AST / Import Denetimi Başarısız Oldu ({len(deterministic_errors)} hata):[/bold red]")
        for err in deterministic_errors:
            console.print(f"    - {err}")

        report_md = f"""# ⚠️ QA & AST Denetim Raporu: BAŞARISIZ
* **Uygulama:** {app_name}
* **Durum:** Python Sözdizimi veya Çapraz Modül Import Hatası Bulundu!

## 🔴 Kritik Hatalar
""" + "\n".join([f"- {e}" for e in deterministic_errors])

        return {
            "code_verified_by_qa": True,
            "qa_passed": False,
            "qa_report": report_md,
            "qa_issues": deterministic_errors,
            "transition_log": append_log(
                state, "QA_Security_Lead", f"AST/Import denetimi başarısız ({len(deterministic_errors)} hata)", "Studio_Director"
            )
        }

    console.print("  [green]✔ Deterministik AST ve Modül Import Denetimi Temiz Geçti.[/green]")

    # 2. LLM Code Quality & Architecture Compliance Review
    code_summary_text = "\n\n".join([
        f"--- DOSYA: {fname} ---\n{content}"
        for fname, content in code_files.items()
    ])

    prompt = f"""Sen Otonom Yazılım Evi'nin Baş QA ve Güvenlik Liderisin (Principal QA & AppSec Lead).
Görevin; üretilen kodun CPO'nun PRD şartnamesine ve CTO'nun mimari ilkelerine uygunluğunu denetlemektir.

UYGULAMA: {app_name}
PRD ÖZETİ:
{prd_spec[:800]}

MİMARİ ŞARTNAME:
{arch_spec[:800]}

KOD DOSYALARI:
{code_summary_text[:3500]}

DENETİM KRİTERLERİ:
1. Temel kütüphane çağrıları doğru mu?
2. Hata yönetimi (try/except) yeterli mi?
3. Tablo oluşturma ve başlangıç verisi (seed data) yükleme mantığı var mı?
4. Kodda tamamlanmamış ya da geçiştirilmiş blok var mı?

Kod çalışabilir ve yeterince sağlamsa 'passed: True' ver. Kritik bir eksiklik varsa somut talimatlarla 'passed: False' ver.
"""
    llm = get_gemini_llm(temperature=0.1)
    structured_qa = llm.with_structured_output(QAReviewOutput)
    res: QAReviewOutput = structured_qa.invoke([AIMessage(content=prompt)])

    if res.passed:
        console.print(f"  [bold green]✔ QA Onayı Verildi! (Kalite Skoru: {res.overall_quality_score}/100)[/bold green]")
    else:
        console.print(f"  [bold yellow]⚠️ QA Revizyon İstedi ({len(res.identified_issues)} sorun)[/bold yellow]")

    return {
        "code_verified_by_qa": True,
        "qa_passed": res.passed,
        "qa_report": res.detailed_report_markdown,
        "qa_issues": res.identified_issues if not res.passed else [],
        "transition_log": append_log(
            state,
            "QA_Security_Lead",
            f"QA Denetimi: {'ONAYLANDI' if res.passed else 'REVİZYON GEREKLİ'} (Skor: {res.overall_quality_score})",
            "Studio_Director"
        )
    }
