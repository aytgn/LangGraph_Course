"""
================================================================================
🏗️ OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU MOTORU (AI SOFTWARE STUDIO ENGINE)
================================================================================
Araştırma/danışmanlık şablonlarından tamamen arındırılmış; gerçek uygulama
geliştirme yaşam döngüsünü (PRD -> Sistem Mimarisi -> Çok Dosyalı Kodlama <-> QA
Döngüsü -> Kurucu HITL Onayı / Revizyon Döngüsü -> Fiziksel Paketleme) yürüten
döngüsel LangGraph motoru.
================================================================================
"""

import ast
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from rich.console import Console

# Kök dizindeki model_factory modülünü içe aktar
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_CURRENT_DIR)
for _p in (_CURRENT_DIR, _ROOT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

load_dotenv(os.path.join(_ROOT_DIR, ".env"))

from model_factory import get_gemini_llm

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(force_terminal=False, legacy_windows=False)

OUTPUT_APPS_DIR = os.path.join(_CURRENT_DIR, "output_uygulamalar")
os.makedirs(OUTPUT_APPS_DIR, exist_ok=True)


# ==============================================================================
# 1. Yazılım Stüdyosu Ortak Durumu (Cyclical Studio State)
# ==============================================================================
class CompanyState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_step: str

    # 1. Ürün Keşfi & PRD (Product_Lead)
    app_name: Optional[str]
    app_slug: Optional[str]
    app_type: Optional[str]          # "Streamlit Web App" | "FastAPI REST Service" | "CLI & Automation Tool"
    purpose_summary: Optional[str]
    core_features: Optional[List[str]]
    prd_spec: Optional[str]

    # 2. Sistem Mimarisi & Tech Stack (System_Architect)
    tech_stack: Optional[List[str]]
    database_choice: Optional[str]
    entrypoint_file: Optional[str]
    planned_files: Optional[List[str]]
    architecture_spec: Optional[str]

    # 3. Çok Dosyalı Gerçek Kodlama (Lead_Developer)
    code_files: Optional[Dict[str, str]]
    total_loc: Optional[int]
    code_verified_by_qa: bool

    # 4. Kalite Güvence, AST & Güvenlik Döngüsü (QA_Security_Lead)
    qa_passed: bool
    qa_report: Optional[str]
    qa_issues: Optional[List[str]]
    revision_count: int

    # 5. Kurucu Onayı, Revizyon Geri Bildirimi & Fiziksel Paketleme (Deployment_Gate)
    founder_feedback: Optional[str]
    feedback_target: Optional[str]   # "System_Architect" | "Lead_Developer" | None
    is_deployed: bool
    app_folder: Optional[str]
    run_command_hint: Optional[str]

    # 6. Döngüsel Graf Telemetrisi
    cycle_count: int
    transition_log: Optional[List[Dict[str, str]]]


# ==============================================================================
# 2. Yapılandırılmış Çıktı Şemaları (Pydantic Schemas)
# ==============================================================================

class PRDSpecOutput(BaseModel):
    """Ürün Yöneticisi (CPO) tarafından çıkarılan somut ürün şartnamesi."""
    app_name: str = Field(description="Uygulamanın net Türkçe adı (örn: 'Akıllı Abonelik ve Gider Takipçisi')")
    app_slug: str = Field(description="Klasör adı olmaya uygun küçük harfli ASCII slug (örn: 'akilli_abonelik_takipcisi')")
    app_type: Literal["Streamlit Web App", "FastAPI REST Service", "CLI & Automation Tool"] = Field(
        description="Kullanıcı talebine en uygun uygulama arayüz/çalışma tipi."
    )
    purpose_summary: str = Field(description="Uygulamanın hangi problemi nasıl çözdüğünü anlatan 2 cümlelik net amaç özeti.")
    core_features: List[str] = Field(description="Uygulamada eksiksiz kodlanacak 3 ila 5 somut fonksiyonel özellik.")
    prd_markdown: str = Field(
        description=(
            "Kullanıcı hikayelerini, ekran/uç nokta davranışlarını, örnek başlangıç verilerini (seed data) "
            "ve kabul kriterlerini içeren detaylı Markdown PRD belgesi."
        )
    )


class ArchitectureSpecOutput(BaseModel):
    """Sistem Mimarı (CTO) tarafından belirlenen teknoloji yığını ve modül sözleşmesi."""
    tech_stack: List[str] = Field(
        description="Kullanılacak somut teknolojiler (örn: ['Python 3.12', 'Streamlit', 'SQLite3', 'Pandas', 'Altair'])"
    )
    database_choice: str = Field(description="Veri saklama katmanı seçimi ve gerekçesi (örn: 'SQLite3 yerel kalıcı veritabanı')")
    entrypoint_file: str = Field(description="Uygulamayı başlatacak ana dosya adı: Streamlit için 'app.py', FastAPI/CLI için 'main.py'")
    planned_files: List[str] = Field(
        description="Üretilecek modüler Python dosyalarının listesi (örn: ['database.py', 'services.py', 'app.py'])"
    )
    architecture_markdown: str = Field(
        description=(
            "Tablo/Pydantic veri şemalarını, modüller arası fonksiyon imzalarını (hangi dosya hangi sınıfı/fonksiyonu dışa aktaracak) "
            "ve hata yönetimi kurallarını içeren detaylı Markdown Sistem Mimarisi belgesi."
        )
    )


class GeneratedFileItem(BaseModel):
    """Tek bir kaynak kod dosyasının adı ve tam içeriği."""
    filename: str = Field(description="Dosya adı (örn: 'database.py', 'services.py', 'app.py', 'requirements.txt', 'README.md')")
    content: str = Field(description="Dosyanın hiçbir kısaltma veya 'TODO' içermeyen, doğrudan çalışır tam içeriği.")


class CodeBundleOutput(BaseModel):
    """Kıdemli Yazılımcı tarafından üretilen çok dosyalı uygulama paketi."""
    implementation_notes: str = Field(description="Yazılan modüllerin ve uygulanan iş mantığının kısa teknik özeti.")
    files: List[GeneratedFileItem] = Field(
        description="Uygulamanın eksiksiz çalışması için gereken tüm kod, bağımlılık ve doküman dosyaları."
    )


class QAReviewOutput(BaseModel):
    """QA & Güvenlik Lideri değerlendirme şeması."""
    passed: bool = Field(description="Kod tüm PRD özelliklerini karşılıyor, importları tutarlı ve çalışmaya hazırsa True.")
    issues: List[str] = Field(description="Eğer passed=False ise düzeltilmesi gereken somut kod hataları listesi; sorun yoksa boş liste.")
    qa_markdown: str = Field(description="Kod kalitesi, güvenlik, modül uyumu ve özellik kapsama denetimini özetleyen Markdown raporu.")


class DirectorRouteOutput(BaseModel):
    """Stüdyo Direktörünün (Orkestratör) geri bildirim yönlendirme kararı."""
    target_department: Literal["System_Architect", "Lead_Developer"] = Field(
        description="Kurucu geri bildirimi altyapı/teknoloji/veritabanı değişikliği gerektiriyorsa 'System_Architect', özellik/arayüz/kod değişikliği gerektiriyorsa 'Lead_Developer'."
    )
    reason: str = Field(description="Yönlendirme gerekçesi.")


# ==============================================================================
# 3. Yardımcı Fonksiyonlar & Deterministik AST Denetçisi
# ==============================================================================

def get_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)


def sanitize_slug(raw_slug: str) -> str:
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    cleaned = raw_slug.translate(tr_map).lower()
    cleaned = re.sub(r"[^a-z0-9_]", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:48] or f"uygulama_{datetime.now().strftime('%H%M%S')}"


def get_clean_user_directive(state: CompanyState) -> str:
    """Kullanıcının ilk uygulama talebini ve varsa son revizyon taleplerini birleştirir."""
    human_texts = []
    for m in state.get("messages", []):
        if isinstance(m, HumanMessage):
            txt = get_text(m.content).strip()
            if txt:
                human_texts.append(txt)
    if not human_texts:
        return "Modüler bir görev ve not yönetim uygulaması geliştirin."
    return "\n\n[EK KULLANICI NOTU]: ".join(human_texts)


def append_log(state: CompanyState, node: str, action: str, target: str = "") -> List[Dict[str, str]]:
    logs = list(state.get("transition_log") or [])
    cycle = state.get("cycle_count", 0)
    logs.append({
        "cycle": str(cycle),
        "node": node,
        "target": target,
        "action": action,
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    return logs


def run_deterministic_ast_checks(code_files: Dict[str, str], entrypoint: str) -> List[str]:
    """
    Üretilen tüm .py dosyalarını Python AST ile ayrıştırır:
    1. SyntaxError / IndentationError kontrolü yapar.
    2. Yerel modüller arası 'from X import Y' tanımlarının gerçekten var olduğunu doğrular.
    3. Giriş dosyasının (entrypoint) mevcut olduğunu kontrol eder.
    """
    errors: List[str] = []
    if not code_files:
        return ["Hiçbir kod dosyası üretilmedi."]

    if entrypoint and entrypoint not in code_files:
        py_files = [f for f in code_files if f.endswith(".py")]
        if not py_files:
            errors.append(f"Giriş dosyası '{entrypoint}' ve hiçbir .py dosyası bulunamadı.")

    parsed_trees: Dict[str, ast.Module] = {}
    exported_symbols: Dict[str, set] = {}

    for fname, content in code_files.items():
        if not fname.endswith(".py"):
            continue
        try:
            tree = ast.parse(content, filename=fname)
            parsed_trees[fname] = tree
            symbols = set()
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    symbols.add(node.name)
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            symbols.add(t.id)
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    symbols.add(node.target.id)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        symbols.add(alias.asname or alias.name)
            exported_symbols[fname[:-3]] = symbols
        except SyntaxError as exc:
            errors.append(f"{fname} satır {exc.lineno}: SyntaxError - {exc.msg}")

    # Yerel dosyalar arası import tutarlılığı kontrolü
    for fname, tree in parsed_trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                base_mod = node.module.split(".")[0]
                if base_mod in exported_symbols:
                    avail = exported_symbols[base_mod]
                    for alias in node.names:
                        if alias.name != "*" and alias.name not in avail:
                            errors.append(
                                f"{fname}: '{base_mod}.py' içinden '{alias.name}' import edilmeye çalışılıyor "
                                f"ancak '{base_mod}.py' içinde böyle bir sınıf/fonksiyon/değişken tanımlı değil! "
                                f"(Mevcut olanlar: {sorted(list(avail))[:10]})"
                            )
    return errors


def export_application_to_disk(state: CompanyState) -> tuple[str, str]:
    """Onaylanan uygulama dosyalarını fiziksel diske yazar ve baslat.bat üretir."""
    slug = sanitize_slug(state.get("app_slug") or state.get("app_name") or "yeni_uygulama")
    app_dir = os.path.join(OUTPUT_APPS_DIR, slug)
    os.makedirs(app_dir, exist_ok=True)

    code_files = state.get("code_files") or {}
    for fname, content in code_files.items():
        safe_rel = os.path.normpath(fname).lstrip("\\/")
        full_path = os.path.join(app_dir, safe_rel)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    # PRD ve Mimari Dökümanını da klasöre ekle
    spec_doc = (
        f"# 📌 {state.get('app_name', slug)} — Ürün & Mimari Şartnamesi\n\n"
        f"**Uygulama Tipi:** {state.get('app_type', '-')}\n"
        f"**Teknoloji Yığını:** {', '.join(state.get('tech_stack') or [])}\n"
        f"**Veritabanı:** {state.get('database_choice', '-')}\n\n"
        f"---\n\n## 1. Ürün Şartnamesi (PRD)\n{state.get('prd_spec', '')}\n\n"
        f"---\n\n## 2. Sistem Mimarisi\n{state.get('architecture_spec', '')}\n\n"
        f"---\n\n## 3. QA & Güvenlik Raporu\n{state.get('qa_report', '')}\n"
    )
    with open(os.path.join(app_dir, "MIMARI_VE_PRD.md"), "w", encoding="utf-8") as f:
        f.write(spec_doc)

    entrypoint = state.get("entrypoint_file") or ("app.py" if "app.py" in code_files else "main.py")
    if entrypoint not in code_files:
        py_candidates = [k for k in code_files.keys() if k.endswith(".py")]
        if py_candidates:
            entrypoint = py_candidates[0]

    app_type = state.get("app_type") or ""
    entry_code = code_files.get(entrypoint, "")
    app_title = state.get("app_name") or slug

    # Çalıştırma komutu ve baslat.bat üretimi
    venv_scripts = os.path.abspath(os.path.join(_ROOT_DIR, ".venv", "Scripts"))
    if "Streamlit" in app_type or "import streamlit" in entry_code:
        run_hint = f'streamlit run "{entrypoint}" --server.port 8505'
        bat_content = (
            "@echo off\n"
            "chcp 65001 > nul\n"
            f"title {app_title}\n"
            'cd /d "%~dp0"\n'
            "echo ============================================================\n"
            f"echo   🚀 {app_title} BASLATILIYOR (Port: 8505)...\n"
            "echo ============================================================\n"
            f'if exist "{venv_scripts}\\streamlit.exe" (\n'
            f'    "{venv_scripts}\\streamlit.exe" run "{entrypoint}" --server.port 8505\n'
            ") else (\n"
            f'    streamlit run "{entrypoint}" --server.port 8505\n'
            ")\n"
            "pause\n"
        )
    elif "FastAPI" in app_type or "from fastapi" in entry_code or "import fastapi" in entry_code:
        mod_name = os.path.splitext(entrypoint)[0]
        run_hint = f"uvicorn {mod_name}:app --host 127.0.0.1 --port 8080 --reload"
        bat_content = (
            "@echo off\n"
            "chcp 65001 > nul\n"
            f"title {app_title} - FastAPI\n"
            'cd /d "%~dp0"\n'
            "echo ============================================================\n"
            f"echo   ⚡ {app_title} REST API BASLATILIYOR...\n"
            "echo   Swagger UI: http://127.0.0.1:8080/docs\n"
            "echo ============================================================\n"
            'start "" "http://127.0.0.1:8080/docs"\n'
            f'if exist "{venv_scripts}\\uvicorn.exe" (\n'
            f'    "{venv_scripts}\\uvicorn.exe" {mod_name}:app --host 127.0.0.1 --port 8080 --reload\n'
            ") else (\n"
            f"    uvicorn {mod_name}:app --host 127.0.0.1 --port 8080 --reload\n"
            ")\n"
            "pause\n"
        )
    else:
        run_hint = f'python "{entrypoint}"'
        bat_content = (
            "@echo off\n"
            "chcp 65001 > nul\n"
            f"title {app_title} - CLI\n"
            'cd /d "%~dp0"\n'
            "echo ============================================================\n"
            f"echo   🛠️ {app_title} CALISTIRILIYOR...\n"
            "echo ============================================================\n"
            f'if exist "{venv_scripts}\\python.exe" (\n'
            f'    "{venv_scripts}\\python.exe" "{entrypoint}"\n'
            ") else (\n"
            f'    python "{entrypoint}"\n'
            ")\n"
            "echo.\n"
            "pause\n"
        )

    with open(os.path.join(app_dir, "baslat.bat"), "w", encoding="utf-8") as f:
        f.write(bat_content)

    return app_dir, run_hint


# ==============================================================================
# 4. Departman Düğümleri (Autonomous Software Studio Nodes)
# ==============================================================================

director_router_llm = get_gemini_llm(temperature=0.1).with_structured_output(DirectorRouteOutput)
product_llm = get_gemini_llm(temperature=0.35).with_structured_output(PRDSpecOutput)
architect_llm = get_gemini_llm(temperature=0.2).with_structured_output(ArchitectureSpecOutput)
developer_llm = get_gemini_llm(temperature=0.2).with_structured_output(CodeBundleOutput)
qa_llm = get_gemini_llm(temperature=0.1).with_structured_output(QAReviewOutput)


def studio_director_node(state: CompanyState):
    """
    👑 Stüdyo Direktörü (Döngüsel Orkestratör):
    Uygulama geliştirme durumunu inceler; ileri yönlü akışı, QA<->Yazılımcı hata
    düzeltme döngüsünü ve Kurucu geri bildirim döngülerini koordine eder.
    """
    cycle = (state.get("cycle_count") or 0) + 1
    state_with_cycle = {**state, "cycle_count": cycle}

    has_prd = bool(state.get("prd_spec"))
    has_arch = bool(state.get("architecture_spec"))
    has_code = bool(state.get("code_files"))
    code_verified = bool(state.get("code_verified_by_qa"))
    qa_passed = bool(state.get("qa_passed"))
    rev_count = state.get("revision_count") or 0
    founder_fb = (state.get("founder_feedback") or "").strip()
    is_deployed = bool(state.get("is_deployed"))

    console.print(f"\n[bold gold1]👑 [STÜDYO DİREKTÖRÜ - Döngü #{cycle}]:[/bold gold1] Durum denetleniyor...")

    # 1. Dağıtım tamamlandıysa bitir
    if is_deployed:
        closing = AIMessage(
            content=(
                f"🚀 **[STÜDYO TESLİMAT BİLDİRİMİ]:** `{state.get('app_name')}` uygulaması tüm mühendislik ve QA "
                f"süreçlerinden geçerek fiziksel diske inşa edildi!\n\n"
                f"- **Konum:** `{state.get('app_folder')}`\n"
                f"- **Çalıştırma Komutu:** `{state.get('run_command_hint')}` (veya klasördeki `baslat.bat`)"
            )
        )
        logs = append_log(state_with_cycle, "Studio_Director", "Uygulama fiziksel diske paketlendi, süreç tamamlandı.", "FINISH")
        return {"next_step": "FINISH", "cycle_count": cycle, "transition_log": logs, "messages": [closing]}

    # 2. Kurucu Başkan revizyon / değişiklik geri bildirimi verdiyse ilgili departmana geri döndür!
    if founder_fb and has_prd:
        fb_target = state.get("feedback_target")
        if not fb_target:
            route_prompt = (
                f"MEVCUT UYGULAMA: {state.get('app_name')} ({state.get('app_type')})\n"
                f"MEVCUT TEKNOLOJİLER: {state.get('tech_stack')}\n"
                f"KURUCU BAŞKAN REVİZYON TALEBİ: \"{founder_fb}\"\n\n"
                "Bu talep altyapı/framework/veritabanı değişikliği içeriyorsa 'System_Architect', "
                "özellik/arayüz/iş mantığı/kod güncellemesi içeriyorsa 'Lead_Developer' seç."
            )
            decision = director_router_llm.invoke([HumanMessage(content=route_prompt)])
            fb_target = decision.target_department

        logs = append_log(
            state_with_cycle,
            "Studio_Director",
            f"Kurucu revizyon talebi alındı -> '{fb_target}' departmanına geri yönlendirildi.",
            fb_target,
        )
        # Eğer mimariye dönüyorsa mimari sonrası kodun da yeniden üretilmesi gerekir
        updates = {
            "next_step": fb_target,
            "cycle_count": cycle,
            "transition_log": logs,
            "code_verified_by_qa": False,
            "qa_passed": False,
            "feedback_target": None,
        }
        return updates

    # 3. PRD yoksa Ürün Liderine gönder
    if not has_prd:
        logs = append_log(state_with_cycle, "Studio_Director", "Uygulama kapsamı ve PRD çıkarılmak üzere Ürün Liderine yönlendirildi.", "Product_Lead")
        return {"next_step": "Product_Lead", "cycle_count": cycle, "transition_log": logs}

    # 4. Mimari yoksa Sistem Mimarına gönder
    if not has_arch:
        logs = append_log(state_with_cycle, "Studio_Director", "PRD hazır -> Teknoloji yığını ve veri şeması için Sistem Mimarına yönlendirildi.", "System_Architect")
        return {"next_step": "System_Architect", "cycle_count": cycle, "transition_log": logs}

    # 5. Kod henüz yazılmadıysa Kıdemli Yazılımcıya gönder
    if not has_code:
        logs = append_log(state_with_cycle, "Studio_Director", "Mimari onaylandı -> Çok dosyalı uygulama kodlaması için Yazılım Mühendisliğine yönlendirildi.", "Lead_Developer")
        return {"next_step": "Lead_Developer", "cycle_count": cycle, "transition_log": logs}

    # 6. Son üretilen kod henüz QA tarafından denetlenmediyse QA'e gönder
    if not code_verified:
        logs = append_log(state_with_cycle, "Studio_Director", "Kod üretildi -> AST sözdizimi ve kalite denetimi için QA departmanına yönlendirildi.", "QA_Security_Lead")
        return {"next_step": "QA_Security_Lead", "cycle_count": cycle, "transition_log": logs}

    # 7. QA başarısız olduysa ve revizyon hakkı varsa döngüsel olarak Yazılımcıya GERİ GÖNDER!
    if not qa_passed and rev_count < 2:
        logs = append_log(
            state_with_cycle,
            "Studio_Director",
            f"QA denetiminde düzeltilmesi gereken bulgular tespit edildi -> Yazılımcıya geri gönderiliyor (Revizyon #{rev_count + 1}).",
            "Lead_Developer",
        )
        return {
            "next_step": "Lead_Developer",
            "cycle_count": cycle,
            "revision_count": rev_count + 1,
            "transition_log": logs,
        }

    # 8. QA geçti (veya maksimum revizyona ulaşıldı) -> Yönetici Yayına Alma Kapısına (HITL) gönder
    logs = append_log(
        state_with_cycle,
        "Studio_Director",
        "Kod ve QA denetimi tamamlandı -> Kurucu Başkan yayına alma / inceleme onayına (HITL) sunuluyor.",
        "Deployment_Gate",
    )
    return {"next_step": "Deployment_Gate", "cycle_count": cycle, "transition_log": logs}


def product_lead_node(state: CompanyState):
    """💡 Ürün Direktörü (CPO): Fikri somut PRD ve MVP özellik listesine dönüştürür."""
    console.print("\n[bold magenta]💡 [DEPARTMAN 1: ÜRÜN & KAPSAM LİDERİ (CPO)][/bold magenta] PRD hazırlanıyor...")
    directive = get_clean_user_directive(state)

    prompt = (
        "Sen bir Yazılım Evinin Ürün Direktörüsün (CPO).\n"
        "Aşağıdaki kullanıcı/kurucu talebini incele ve hemen kodlanabilecek somut, gerçekçi, "
        "içi dolu bir **Uygulama Ürün Şartnamesi (PRD)** çıkar.\n\n"
        f"KURUCU TALEBİ:\n{directive}\n\n"
        "KURALLAR:\n"
        "- Eğer kullanıcı arayüz belirtmediyse etkileşimli görsel deneyim için 'Streamlit Web App', "
        "mikroservis/API istediyse 'FastAPI REST Service', komut satırı aracı istediyse 'CLI & Automation Tool' seç.\n"
        "- Uygulama açıldığında boş görünmemesi için anlamlı başlangıç örnek verileri (seed data) planla.\n"
        "- Özellikler somut ve doğrudan Python ile gerçeklenebilir olsun."
    )

    prd: PRDSpecOutput = product_llm.invoke([HumanMessage(content=prompt)])
    clean_slug = sanitize_slug(prd.app_slug or prd.app_name)

    msg = AIMessage(
        content=f"💡 **[CPO - Ürün Şartnamesi Hazır]:** `{prd.app_name}` ({prd.app_type})\n\n{prd.purpose_summary}"
    )
    logs = append_log(
        state,
        "Product_Lead",
        f"'{prd.app_name}' ({prd.app_type}) için {len(prd.core_features)} özellikli PRD oluşturuldu.",
        "Studio_Director",
    )

    return {
        "app_name": prd.app_name,
        "app_slug": clean_slug,
        "app_type": prd.app_type,
        "purpose_summary": prd.purpose_summary,
        "core_features": prd.core_features,
        "prd_spec": prd.prd_markdown,
        "messages": [msg],
        "transition_log": logs,
    }


def system_architect_node(state: CompanyState):
    """📐 Sistem Mimarı (CTO): Teknoloji yığınını, veri modellerini ve dosya sözleşmesini tasarlar."""
    console.print("\n[bold cyan]📐 [DEPARTMAN 2: SİSTEM MİMARI & CTO][/bold cyan] Altyapı ve modül şeması tasarlanıyor...")
    founder_fb = (state.get("founder_feedback") or "").strip()

    prompt = (
        "Sen Kıdemli Sistem Mimarı ve CTO'sun.\n"
        f"UYGULAMA ADI: {state.get('app_name')}\n"
        f"UYGULAMA TİPİ: {state.get('app_type')}\n"
        f"TEMEL ÖZELLİKLER: {json.dumps(state.get('core_features') or [], ensure_ascii=False)}\n\n"
        f"PRD BELGESİ:\n{state.get('prd_spec')}\n\n"
        + (f"KURUCU MİMARİ REVİZYON TALEBİ:\n{founder_fb}\n\n" if founder_fb else "")
        + "MİMARİ KURALLAR:\n"
        "1. Yalnızca Python standart kütüphanelerini (`sqlite3`, `json`, `csv`, `datetime`, `math`, `re`, `uuid`, `pathlib`) "
        "ve ortamda kurulu olan paketleri (`streamlit`, `fastapi`, `uvicorn`, `pydantic`, `pandas`, `numpy`, `altair`, `requests`, `httpx`, `rich`, `fpdf2`) kullan! "
        "Kurulu olmayan harici paketler seçme ki uygulama tek tıkla hatasız çalışsın.\n"
        "2. Temiz modüler yapı kur (2 ila 4 Python dosyası: örn. `database.py` veya `models.py`, `services.py`, ve giriş dosyası `app.py` veya `main.py`).\n"
        "3. `architecture_markdown` içinde her dosyanın hangi sınıf/fonksiyon isimlerini dışa aktaracağını NET yaz ki yazılımcı import hatası yapmasın."
    )

    arch: ArchitectureSpecOutput = architect_llm.invoke([HumanMessage(content=prompt)])
    msg = AIMessage(
        content=(
            f"📐 **[CTO - Sistem Mimarisi Hazır]:** Altyapı: `{', '.join(arch.tech_stack)}` | "
            f"Veri Katmanı: `{arch.database_choice}` | Dosyalar: `{', '.join(arch.planned_files)}`"
        )
    )
    logs = append_log(
        state,
        "System_Architect",
        f"Tech Stack ({', '.join(arch.tech_stack[:3])}) ve {len(arch.planned_files)} modüllü mimari tasarlandı.",
        "Studio_Director",
    )

    return {
        "tech_stack": arch.tech_stack,
        "database_choice": arch.database_choice,
        "entrypoint_file": arch.entrypoint_file,
        "planned_files": arch.planned_files,
        "architecture_spec": arch.architecture_markdown,
        # Mimari yenilendiyse kodun da bu mimariye göre üretilmesi için sıfırla (eğer revizyondan geldiyse)
        "code_files": None if founder_fb else state.get("code_files"),
        "founder_feedback": None,
        "code_verified_by_qa": False,
        "messages": [msg],
        "transition_log": logs,
    }


def lead_developer_node(state: CompanyState):
    """💻 Kıdemli Yazılım Mühendisi: Eksiksiz, çok dosyalı, çalışan gerçek Python kodu yazar."""
    console.print("\n[bold deep_sky_blue1]💻 [DEPARTMAN 3: KIDEMLİ YAZILIM MÜHENDİSİ][/bold deep_sky_blue1] Uygulama kodlanıyor...")

    qa_issues = state.get("qa_issues") or []
    founder_fb = (state.get("founder_feedback") or "").strip()
    existing_files = state.get("code_files") or {}

    revision_context = ""
    if qa_issues:
        revision_context += (
            "\n⚠️ ÖNCEKİ KODDA QA/AST DENETİMİNİN BULDUĞU HATALAR (BUNLARI KESİNLİKLE DÜZELT!):\n"
            + "\n".join(f"- {iss}" for iss in qa_issues)
            + "\n"
        )
    if founder_fb:
        revision_context += f"\n👑 KURUCU BAŞKANIN REVİZYON / EK ÖZELLİK TALEBİ (BUNU EKSİKSİZ UYGULA!):\n{founder_fb}\n"

    if existing_files and (qa_issues or founder_fb):
        existing_dump = "\n\n".join(f"--- MEVCUT DOSYA: {k} ---\n{v}" for k, v in existing_files.items())
        revision_context += f"\nMEVCUT KOD DOSYALARI (Bunları temel alıp düzelterek tüm dosyaları eksiksiz döndür):\n{existing_dump}\n"

    prompt = (
        "Sen Kıdemli Full-Stack Python Yazılım Mühendisisin.\n"
        "Aşağıdaki PRD ve Sistem Mimarisine birebir uyarak **GERÇEK, TAM ÇALIŞAN, SIFIR DUMMY** uygulama kodunu üret.\n\n"
        f"UYGULAMA ADI: {state.get('app_name')}\n"
        f"UYGULAMA TİPİ: {state.get('app_type')}\n"
        f"GİRİŞ DOSYASI (ENTRYPOINT): {state.get('entrypoint_file')}\n"
        f"PLANLANAN DOSYALAR: {state.get('planned_files')}\n"
        f"TEKNOLOJİ YIĞINI: {state.get('tech_stack')}\n\n"
        f"--- PRD ---\n{state.get('prd_spec')}\n\n"
        f"--- SİSTEM MİMARİSİ ---\n{state.get('architecture_spec')}\n"
        f"{revision_context}\n"
        "KESİN MÜHENDİSLİK KURALLARI:\n"
        "1. ASLA `pass`, `# TODO`, `...` veya yarım bırakılmış fonksiyon yazma! Tüm hesaplamalar, CRUD işlemleri, filtreler ve grafikler gerçek çalışsın.\n"
        "2. Veritabanı (SQLite3 vb.) kullanılıyorsa ilk açılışta tabloları otomatik oluştur (`CREATE TABLE IF NOT EXISTS`) ve tablo boşsa gerçekçi başlangıç verileri (seed data) ekle ki kullanıcı uygulamayı açtığı anda zengin verilerle etkileşime girebilsin!\n"
        "3. Dosyalar arası `import` ifadelerinin birebir eşleştiğinden emin ol (örn. `from database import init_db` diyorsan `database.py` içinde `def init_db` mutlaka olsun).\n"
        "4. Yalnızca standart kütüphaneler ve kurulu paketleri (`streamlit`, `fastapi`, `uvicorn`, `pydantic`, `pandas`, `numpy`, `altair`, `requests`, `httpx`, `rich`, `fpdf2`) kullan.\n"
        "5. Tüm Python dosyalarının yanı sıra temiz bir `requirements.txt` ve kullanım kılavuzu içeren `README.md` üret."
    )

    bundle: CodeBundleOutput = developer_llm.invoke([HumanMessage(content=prompt)])

    files_dict: Dict[str, str] = {}
    total_lines = 0
    for item in bundle.files:
        fname = item.filename.strip().lstrip("\\/")
        files_dict[fname] = item.content
        if fname.endswith(".py"):
            total_lines += len(item.content.splitlines())

    msg = AIMessage(
        content=(
            f"💻 **[Yazılım Mühendisliği]:** `{ len(files_dict) }` dosya (`{total_lines}` satır Python kodu) üretildi.\n\n"
            f"**Teknik Özet:** {bundle.implementation_notes}"
        )
    )
    logs = append_log(
        state,
        "Lead_Developer",
        f"{len(files_dict)} dosya ({total_lines} satır Python kodu) inşa edildi.",
        "Studio_Director",
    )

    return {
        "code_files": files_dict,
        "total_loc": total_lines,
        "code_verified_by_qa": False,
        "qa_issues": [],
        "founder_feedback": None,
        "messages": [msg],
        "transition_log": logs,
    }


def qa_security_lead_node(state: CompanyState):
    """🛡️ Kalite Güvence & Güvenlik Lideri: Deterministik AST + AI Kod İncelemesi yapar."""
    console.print("\n[bold green]🛡️ [DEPARTMAN 4: QA, AST & GÜVENLİK DENETİMİ][/bold green] Kod inceleniyor...")

    code_files = state.get("code_files") or {}
    entrypoint = state.get("entrypoint_file") or "app.py"

    # 1. Deterministik AST Sözdizimi ve İmport Kontrolü
    ast_errors = run_deterministic_ast_checks(code_files, entrypoint)

    if ast_errors:
        console.print(f"   ❌ [AST Hatası Yakalandı]: {ast_errors}")
        qa_md = (
            "### ❌ Otomatik AST & Modül Uyum Denetimi Başarısız\n\n"
            "Aşağıdaki sözdizimi veya modüller arası import hataları tespit edildi ve düzeltilmek üzere Yazılım Mühendisliğine geri gönderildi:\n\n"
            + "\n".join(f"- `{err}`" for err in ast_errors)
        )
        msg = AIMessage(content=f"🛡️ **[QA Denetimi - Hata Yakalandı]:** {len(ast_errors)} teknik hata bulundu, yazılımcıya geri gönderiliyor.")
        logs = append_log(
            state,
            "QA_Security_Lead",
            f"AST/Import kontrolünde {len(ast_errors)} hata yakalandı -> Döngüsel düzeltme tetiklendi.",
            "Studio_Director",
        )
        return {
            "qa_passed": False,
            "qa_issues": ast_errors,
            "qa_report": qa_md,
            "code_verified_by_qa": True,
            "messages": [msg],
            "transition_log": logs,
        }

    # 2. LLM Kalite, Özellik Kapsama ve Güvenlik Denetimi
    files_dump = "\n\n".join(f"=== DOSYA: {k} ===\n{v}" for k, v in code_files.items())
    prompt = (
        "Sen Kıdemli QA ve Uygulama Güvenliği Denetçisisin.\n"
        "Python AST sözdizimi ve yerel import kontrolleri BAŞARIYLA GEÇTİ.\n"
        "Şimdi kodun PRD'deki temel özellikleri gerçekten uygulayıp uygulamadığını, içi boş dummy fonksiyon olup olmadığını "
        "ve çalışma zamanında (runtime) patlayacak bariz bir mantık hatası olup olmadığını denetle.\n\n"
        f"BEKLENEN ÖZELLİKLER: {state.get('core_features')}\n"
        f"GİRİŞ DOSYASI: {entrypoint}\n\n"
        f"ÜRETİLEN KODLAR:\n{files_dump}\n\n"
        "NOT: Ufak stil tercihleri için kodu reddetme; yalnızca uygulamayı bozacak gerçek bir çalışma zamanı hatası "
        "veya tamamen eksik bırakılmış ana özellik varsa `passed=False` ver."
    )

    review: QAReviewOutput = qa_llm.invoke([HumanMessage(content=prompt)])
    status_icon = "✅" if review.passed else "⚠️"
    msg = AIMessage(
        content=f"🛡️ **[QA & Güvenlik Raporu {status_icon}]:** {'Tüm kontrollerden geçti!' if review.passed else 'Revizyon gerekiyor.'}"
    )
    logs = append_log(
        state,
        "QA_Security_Lead",
        "AST + QA güvenlik denetimi başarıyla geçti." if review.passed else f"QA incelemesinde {len(review.issues)} bulgu tespit edildi.",
        "Studio_Director",
    )

    return {
        "qa_passed": review.passed,
        "qa_issues": review.issues,
        "qa_report": review.qa_markdown,
        "code_verified_by_qa": True,
        "messages": [msg],
        "transition_log": logs,
    }


def deployment_gate_node(state: CompanyState):
    """🚀 Fiziksel Paketleme & Dağıtım Düğümü (Kurucu HITL Onayı Sonrası Çalışır)."""
    console.print("\n[bold orange3]🚀 [DAĞITIM & PAKETLEME][/bold orange3] Uygulama fiziksel diske inşa ediliyor...")

    # Eğer kurucu onay yerine revizyon geri bildirimi bıraktıysa diske yazmadan direktöre dön!
    if (state.get("founder_feedback") or "").strip():
        logs = append_log(
            state,
            "Deployment_Gate",
            "Kurucu Başkan revizyon talep etti -> Döngü yeniden başlatılıyor.",
            "Studio_Director",
        )
        return {"is_deployed": False, "transition_log": logs}

    app_dir, run_hint = export_application_to_disk(state)
    logs = append_log(
        state,
        "Deployment_Gate",
        f"Uygulama '{os.path.basename(app_dir)}' klasörüne ve baslat.bat betiğine dönüştürüldü.",
        "Studio_Director",
    )
    return {
        "is_deployed": True,
        "app_folder": app_dir,
        "run_command_hint": run_hint,
        "transition_log": logs,
    }


# ==============================================================================
# 5. Döngüsel LangGraph Kurulumu & SQLite Kalıcılığı
# ==============================================================================

workflow = StateGraph(CompanyState)

workflow.add_node("Studio_Director", studio_director_node)
workflow.add_node("Product_Lead", product_lead_node)
workflow.add_node("System_Architect", system_architect_node)
workflow.add_node("Lead_Developer", lead_developer_node)
workflow.add_node("QA_Security_Lead", qa_security_lead_node)
workflow.add_node("Deployment_Gate", deployment_gate_node)

workflow.add_edge(START, "Studio_Director")

workflow.add_conditional_edges(
    "Studio_Director",
    lambda state: state["next_step"],
    {
        "Product_Lead": "Product_Lead",
        "System_Architect": "System_Architect",
        "Lead_Developer": "Lead_Developer",
        "QA_Security_Lead": "QA_Security_Lead",
        "Deployment_Gate": "Deployment_Gate",
        "FINISH": END,
    },
)

# Tüm uzman departmanlar işini bitirdiğinde Döngüsel Merkez olan Studio_Director'a döner!
workflow.add_edge("Product_Lead", "Studio_Director")
workflow.add_edge("System_Architect", "Studio_Director")
workflow.add_edge("Lead_Developer", "Studio_Director")
workflow.add_edge("QA_Security_Lead", "Studio_Director")
workflow.add_edge("Deployment_Gate", "Studio_Director")

DB_PATH = os.path.join(_CURRENT_DIR, "studio_apps.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
memory = SqliteSaver(conn)

# KURUCU ONAY & REVİZYON KAPISI (HITL):
# Uygulama diske paketlenmeden hemen önce Kurucu Başkan'ın mimariyi ve kodu incelemesi,
# onaylaması veya geri bildirimle döngüyü geri çevirmesi için duraklatılır!
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Deployment_Gate"],
)


if __name__ == "__main__":
    console.print("[bold green]✅ AI Software Studio Engine hazır![/bold green]")
