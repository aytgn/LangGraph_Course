"""
System Architect Node (CTO / Tech Stack Lead).
Responsible for Technical Architecture, Tech Stack Selection, and Module Contracts.
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
from domain.schemas import ArchitectureSpecOutput
from domain.utils import append_log

console = Console(force_terminal=False, legacy_windows=False)


def system_architect_node(state: CompanyState) -> dict:
    """CTO node designs technical architecture and module contracts."""
    console.print("\n[bold magenta]📐 [DEPARTMAN 2: SİSTEM MİMARI & CTO] Altyapı ve modül şeması tasarlanıyor...[/bold magenta]")

    app_name = state.get("app_name") or "Uygulama"
    app_type = state.get("app_type") or "Streamlit Web App"
    prd_spec = state.get("prd_spec") or state.get("purpose_summary") or ""
    founder_feedback = state.get("founder_feedback")

    prompt = f"""Sen şirketin Baş Sistem Mimarı ve CTO'susun (Chief Technology Officer).
Görevin; CPO tarafından hazırlanan PRD'yi inceleyerek en temiz, sürdürülebilir ve hatasız çalışacak teknik mimariyi tasarlamaktır.

UYGULAMA ADI: {app_name}
UYGULAMA TİPİ: {app_type}
PRD ÖZETİ / KAPSAM:
{prd_spec}
{"KURUCU REVİZYON TALEBİ: " + founder_feedback if founder_feedback else ""}

MİMARİ VE TEKNOLOJİ İLKELERİ:
1. Yalnızca Python standart kütüphanelerini (`sqlite3`, `json`, `csv`, `datetime`, `math`, `re`, `uuid`, `pathlib`) ve projemizin sanal ortamında kurulu temel kütüphaneleri (`streamlit`, `fastapi`, `uvicorn`, `pydantic`, `pandas`, `altair`) kullan. Asla gereksiz dış paket veya karmaşık servis uydurma!
2. Çok dosyalı, temiz ve modüler bir mimari planla:
   - Ana giriş dosyası (Streamlit için 'app.py', FastAPI için 'main.py' veya 'app.py', CLI için 'cli.py' veya 'main.py')
   - Veritabanı ve veri erişim dosyası ('database.py' - SQLite bağlantı ve CRUD fonksiyonları)
   - İş mantığı / servis dosyası ('services.py' veya 'logic.py')
3. Modüller arası sözleşmeleri (contracts) kristal netliğinde tanımla: Hangi dosya hangi fonksiyona/sınıfa sahip olacak, giriş dosyası onları nasıl çağıracak?
"""
    llm = get_gemini_llm(temperature=0.2)
    structured_arch = llm.with_structured_output(ArchitectureSpecOutput)
    res: ArchitectureSpecOutput = structured_arch.invoke([AIMessage(content=prompt)])

    console.print(f"  [green]✔ Mimari Tasarlandı:[/green] Stack: {res.tech_stack} | Giriş: {res.entrypoint_file}")

    return {
        "tech_stack": res.tech_stack,
        "database_choice": res.database_choice,
        "entrypoint_file": res.entrypoint_file,
        "planned_files": res.planned_files,
        "architecture_spec": res.architecture_summary_markdown,
        "founder_feedback": None,
        "feedback_target": None,
        "transition_log": append_log(
            state, "System_Architect", f"Mimari tasarlandı: {res.entrypoint_file} ({len(res.planned_files)} dosya)", "Studio_Director"
        )
    }
