"""
Lead Developer Node (Senior Full-Stack Engineer).
Responsible for Multi-File Implementation, Code Generation, and Bug Fixes.
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
from domain.schemas import CodeBundleOutput
from domain.utils import append_log

console = Console(force_terminal=False, legacy_windows=False)


def lead_developer_node(state: CompanyState) -> dict:
    """Lead Developer writes or revises clean, multi-file code."""
    console.print("\n[bold blue]💻 [DEPARTMAN 3: KIDEMLİ YAZILIM MÜHENDİSİ] Uygulama kodlanıyor...[/bold blue]")

    app_name = state.get("app_name") or "Uygulama"
    app_type = state.get("app_type") or "Streamlit Web App"
    entrypoint = state.get("entrypoint_file") or "app.py"
    prd_spec = state.get("prd_spec") or ""
    arch_spec = state.get("architecture_spec") or ""
    planned_files = state.get("planned_files") or []
    existing_code = state.get("code_files") or {}
    qa_issues = state.get("qa_issues") or []
    founder_feedback = state.get("founder_feedback")

    is_fixing = bool(qa_issues or founder_feedback)
    action_type = "Düzeltme & Revizyon" if is_fixing else "İlk Kodlama"

    prompt = f"""Sen dünya standartlarında kıdemli bir Tam Yığın Yazılım Mühendisisin (Staff Full-Stack Engineer).
Görevin; CPO'nun hazırladığı PRD'ye ve CTO'nun mimari sözleşmelerine %100 sadık kalarak uygulamanın ÇALIŞAN, EKSİKSİZ, ÇOK DOSYALI kodunu üretmektir.

UYGULAMA: {app_name} ({app_type})
ANA GİRİŞ: {entrypoint}
PLANLANAN DOSYALAR: {planned_files}

PRD ŞARTNAMESİ:
{prd_spec}

MİMARİ ŞARTNAME:
{arch_spec}

{"=== ÖNCEKİ KODLAR VE QA/KURUCU GERİ BİLDİRİMLERİ ===" if is_fixing else ""}
{"TESPİT EDİLEN QA HATALARI (BUNLARI MUTLAKA ÇÖZ!): " + str(qa_issues) if qa_issues else ""}
{"KURUCU REVİZYON TALEBİ: " + str(founder_feedback) if founder_feedback else ""}
{"MEVCUT KOD DOSYALARI: " + str(list(existing_code.keys())) if is_fixing else ""}

KODLAMA VE KALİTE İLKELERİ (ÇOK ÖNEMLİ):
1. ASLA eksik kod, yarım fonksiyon veya '# burada diğer kodlar yer alacak' gibi geçiştirmeler yapma! Her dosya baştan sona eksiksiz, syntax hatasız ve çalışır olmalı.
2. Veritabanı (SQLite3 vb.) kullanılıyorsa ilk açılışta tabloları otomatik oluştur ('CREATE TABLE IF NOT EXISTS') ve tablo boşsa gerçekçi başlangıç verileri (seed data) ekle!
3. Modüller arası import'lara ÇOK DİKKAT ET: Örneğin 'from database import get_db, init_db' yazıyorsan, 'database.py' içinde hem 'get_db' hem de 'init_db' fonksiyonlarının tanımlandığından kesinlikle emin ol!
4. Streamlit için 'st.set_page_config' çağrısını yalnızca ana giriş dosyasının en başında yap.
5. Kullanıcı deneyimini modern kıl: Başlıklar, metrik kartları, tablolar ve formlar ekle.
"""
    llm = get_gemini_llm(temperature=0.2)
    structured_dev = llm.with_structured_output(CodeBundleOutput)
    res: CodeBundleOutput = structured_dev.invoke([AIMessage(content=prompt)])

    code_dict = {}
    total_loc = 0
    for f in res.files:
        code_dict[f.filename] = f.content
        loc = len([line for line in f.content.split("\n") if line.strip()])
        total_loc += loc
        console.print(f"  [cyan]  📄 {f.filename}:[/cyan] {loc} satır kod")

    rev_count = (state.get("revision_count") or 0) + (1 if is_fixing else 0)

    return {
        "code_files": code_dict,
        "total_loc": total_loc,
        "code_verified_by_qa": False,
        "qa_passed": False,
        "qa_issues": [],
        "revision_count": rev_count,
        "founder_feedback": None,
        "feedback_target": None,
        "transition_log": append_log(
            state, "Lead_Developer", f"{action_type} tamamlandı ({len(code_dict)} dosya, {total_loc} LOC)", "Studio_Director"
        )
    }
