"""
QA & Security Lead Node.
Uses ToolRegistry for Deterministic AST & Cross-Import checks + LLM Quality Review.
"""

import sys
from pathlib import Path
from langchain_core.messages import AIMessage, HumanMessage
_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from model_factory import get_gemini_llm
from domain.state import CompanyState
from domain.schemas import QAReviewOutput
from domain.utils import append_log, console
from tools.registry import ToolRegistry


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
    deterministic_errors = ast_suite_tool.run(code_files=code_files, entrypoint=entrypoint) if ast_suite_tool else []

    if deterministic_errors:
        console.print(f"  [bold red]❌ Deterministik AST / Import Denetimi Başarısız ({len(deterministic_errors)} hata):[/bold red]")
        for err in deterministic_errors:
            console.print(f"    - {err}")

        err_bullets = "\n".join(f"- `{e}`" for e in deterministic_errors)
        report_md = (
            f"# ⚠️ QA & AST Denetim Raporu: BAŞARISIZ\n"
            f"* **Uygulama:** {app_name}\n"
            f"* **Durum:** Python Sözdizimi veya Çapraz Modül Import Hatası Bulundu!\n\n"
            f"## 🔴 Kritik Hatalar\n{err_bullets}"
        )
        msg = AIMessage(
            content=(
                f"🛡️ **[QA & AST Denetimi — ❌ Hata Yakalandı]:** `{len(deterministic_errors)}` teknik sözdizimi/import hatası tespit edildi, "
                f"otomatik düzeltme için Kıdemli Yazılımcıya geri gönderiliyor:\n{err_bullets}"
            )
        )
        return {
            "code_verified_by_qa": True,
            "qa_passed": False,
            "qa_report": report_md,
            "qa_issues": deterministic_errors,
            "messages": [msg],
            "transition_log": append_log(
                state, "QA_Security_Lead", f"AST/Import denetimi başarısız ({len(deterministic_errors)} hata)", "Studio_Director"
            ),
        }

    console.print("  [green]✔ Deterministik AST ve Modül Import Denetimi Temiz Geçti.[/green]")

    # 2. LLM Code Quality & Architecture Compliance Review
    code_summary_text = "\n\n".join(
        f"--- DOSYA: {fname} ---\n{content}"
        for fname, content in code_files.items()
    )

    prompt = f"""Sen Otonom Yazılım Evi'nin Baş QA ve Güvenlik Liderisin (Principal QA & AppSec Lead).
Python AST sözdizimi ve çapraz modül import kontrolleri BAŞARIYLA GEÇTİ.
Görevin; üretilen kodun CPO'nun PRD şartnamesine ve CTO'nun mimari ilkelerine uygunluğunu denetlemektir.

UYGULAMA: {app_name}
PRD ÖZETİ:
{prd_spec[:1000]}

MİMARİ ŞARTNAME:
{arch_spec[:1000]}

KOD DOSYALARI:
{code_summary_text[:6000]}

DENETİM KRİTERLERİ:
1. Temel kütüphane çağrıları ve çalışma zamanı akışı doğru mu?
2. Tablo oluşturma ve başlangıç verisi (seed data) yükleme mantığı var mı?
3. Kodda tamamlanmamış ya da geçiştirilmiş blok var mı?

NOT: Ufak stil tercihleri için kodu reddetme; kod çalışabilir ve sağlamsa 'passed: True' ver. Yalnızca gerçek bir çalışma zamanı hatası varsa 'passed: False' ver.
"""
    llm = get_gemini_llm(temperature=0.1)
    structured_qa = llm.with_structured_output(QAReviewOutput)
    res: QAReviewOutput = structured_qa.invoke([HumanMessage(content=prompt)])

    if res.passed:
        console.print(f"  [bold green]✔ QA Onayı Verildi! (Kalite Skoru: {res.overall_quality_score}/100)[/bold green]")
        msg = AIMessage(
            content=(
                f"🛡️ **[QA & Güvenlik Lideri — ✅ Onaylandı]:** Deterministik AST, modül importları ve kod kalitesi denetiminden başarıyla geçti! "
                f"*(Kalite Skoru: **{res.overall_quality_score}/100**)* — Kurucu Başkan incelemesine sunuluyor."
            )
        )
    else:
        console.print(f"  [bold yellow]⚠️ QA Revizyon İstedi ({len(res.identified_issues)} sorun)[/bold yellow]")
        iss_bullets = "\n".join(f"- {i}" for i in res.identified_issues)
        msg = AIMessage(
            content=(
                f"🛡️ **[QA & Güvenlik Lideri — ⚠️ Revizyon Gerekli]:** *(Skor: {res.overall_quality_score}/100)*\n{iss_bullets}"
            )
        )

    return {
        "code_verified_by_qa": True,
        "qa_passed": res.passed,
        "qa_report": res.detailed_report_markdown,
        "qa_issues": res.identified_issues if not res.passed else [],
        "messages": [msg],
        "transition_log": append_log(
            state,
            "QA_Security_Lead",
            f"QA Denetimi: {'ONAYLANDI' if res.passed else 'REVİZYON GEREKLİ'} (Skor: {res.overall_quality_score})",
            "Studio_Director",
        ),
    }
