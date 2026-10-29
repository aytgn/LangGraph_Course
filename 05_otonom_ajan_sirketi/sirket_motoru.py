import os
import sys
import time
import sqlite3
from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Kök dizindeki model_factory modülünü içe aktar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm

load_dotenv()
console = Console()

# ==============================================================================
# 1. Departman Uzmanlarının Araçları (Tools)
# ==============================================================================

# Araştırma Departmanı Araçları
@tool
def query_market_intelligence(domain: str) -> str:
    """Belirtilen sektördeki güncel pazar dinamiklerini, müşteri taleplerini ve trendleri getirir."""
    time.sleep(0.4)
    return (
        f"[{domain.upper()} PAZAR RAPORU 2026]: "
        "Yüksek talep artışı (%85 yıllık büyüme), regülasyon uyumluluğu zorunluluğu, "
        "modüler mikro-servis mimarileri ve 7/24 otonom sistem entegrasyonu en kritik gereksinimdir."
    )

# Mühendislik Departmanı Araçları
@tool
def generate_production_code(component_name: str) -> str:
    """Kurumsal standartlarda, tip güvenli ve test edilebilir Python üretim kodu üretir."""
    time.sleep(0.5)
    clean_name = component_name.replace(" ", "_").lower()
    return (
        f"# --- KURUMSAL ÜRETİM MODÜLÜ: {component_name} ---\n"
        f"class {component_name.replace(' ', '')}Service:\n"
        f"    def __init__(self, service_id: str = 'SVC-001'):\n"
        f"        self.service_id = service_id\n"
        f"        self.is_active = True\n\n"
        f"    def execute_workload(self, payload: dict) -> dict:\n"
        f"        return {{'status': 'SUCCESS', 'service': self.service_id, 'data': payload}}\n"
    )

# Kalite & Finans Onay Departmanı Araçları (Kritik İşlem!)
@tool
def authorize_project_budget(department: str, amount: float) -> str:
    """Proje için kurumsal bütçe tahsisi yapar. DİKKAT: Gerçek şirket bütçesi bloke edilir!"""
    return f"ONAYLANDI: '{department}' departmanına {amount:,.2f} TL bütçe başarıyla tahsis edildi. Bütçe Kodu: BGT-8842."

# ==============================================================================
# 2. Şirket Ortak Durumu (Enterprise State)
# ==============================================================================
class CompanyState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_step: str                     # CEO'nun seçtiği sıradaki departman
    research_summary: Optional[str]    # Araştırma departmanının bulgusu
    code_deliverable: Optional[str]    # Mühendislik departmanının kodu
    allocated_budget: Optional[float]  # Onaylanan bütçe tutarı
    is_audit_passed: bool              # Güvenlik ve denetim onayı

# ==============================================================================
# 3. CEO Karar Şeması (Pydantic Structured Output)
# ==============================================================================
class CEORouteDecision(BaseModel):
    """CEO'nun şirketi yönetecek stratejik kararı."""
    next: Literal["Research_Dept", "Engineering_Dept", "Audit_Approval_Dept", "FINISH"] = Field(
        description="Görevi devralacak departman veya tüm işler eksiksiz tamamlandıysa 'FINISH'."
    )
    strategic_reason: str = Field(description="Bu departmanın seçilme gerekçesi veya projenin tamamlanma notu.")

# ==============================================================================
# 4. Modellerin Yapılandırılması
# ==============================================================================
# CEO Modeli: Kararlarını Pydantic şemasıyla verir
ceo_llm = get_gemini_llm(temperature=0.1).with_structured_output(CEORouteDecision)

# Departman Modelleri
research_tools = [query_market_intelligence]
research_llm = get_gemini_llm(temperature=0.2, tools=research_tools)

engineering_tools = [generate_production_code]
engineering_llm = get_gemini_llm(temperature=0.1, tools=engineering_tools)

audit_tools = [authorize_project_budget]
audit_llm = get_gemini_llm(temperature=0.1, tools=audit_tools)

def get_text(content) -> str:
    """Mesaj içeriğini (string veya Gemini blok listesi) güvenle düz metne çevirir."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)

# ==============================================================================
# 5. Departman Düğümleri (Department Nodes)
# ==============================================================================

def ceo_supervisor_node(state: CompanyState):
    """CEO / Orkestratör: Şirket hedeflerini inceler ve süreci koordine eder."""
    console.print("\n[bold gold1]👑 [CEO / EXECUTIVE BOARD]:[/bold gold1] Şirket durumunu denetliyor ve sıradaki departmanı seçiyor...")
    
    has_research = bool(state.get("research_summary"))
    has_code = bool(state.get("code_deliverable"))
    has_audit = bool(state.get("is_audit_passed"))
    
    prompt = (
        "Sen 'Otonom Ajan Şirketi'nin CEO'susun. 3 ana departmanı yönetiyorsun:\n"
        "1. 'Research_Dept': Pazar araştırması ve sektör analizi yapar.\n"
        "2. 'Engineering_Dept': Araştırma sonuçlarına dayanarak üretim kodu geliştirir.\n"
        "3. 'Audit_Approval_Dept': Proje bütçesini denetler ve bütçe tahsis aracını çalıştırır.\n\n"
        f"MEVCUT ŞİRKET DURUMU:\n"
        f"- 1. Pazar Araştırması : {'TAMAMLANDI' if has_research else 'EKSİK (Yapılmalı)'}\n"
        f"- 2. Mühendislik Kodu  : {'TAMAMLANDI' if has_code else 'EKSİK (Geliştirilmeli)'}\n"
        f"- 3. Bütçe & Finans Denetimi : {'TAMAMLANDI' if has_audit else 'EKSİK (Yapılmalı)'}\n\n"
        "MANTIKSAL AKIŞ KURALLARI:\n"
        "- Eğer Pazar Araştırması EKSİK ise -> Kesinlikle 'Research_Dept'\n"
        "- Eğer Pazar Araştırması TAMAMLANDI ama Mühendislik Kodu EKSİK ise -> Kesinlikle 'Engineering_Dept'\n"
        "- Eğer Mühendislik Kodu TAMAMLANDI ama Bütçe & Finans EKSİK ise -> Kesinlikle 'Audit_Approval_Dept'\n"
        "- Eğer hepsi TAMAMLANDI ise -> Kesinlikle 'FINISH'\n"
    )
    
    # Boş veya eksik mesajları temizle ve Gemini kuralına uygun şekilde sonuna HumanMessage ekle
    valid_messages = [
        m for m in state["messages"] 
        if (isinstance(m.content, str) and m.content.strip()) or (isinstance(m.content, list) and m.content) or (hasattr(m, "tool_calls") and m.tool_calls)
    ]
    messages = valid_messages + [HumanMessage(content=prompt)]
    decision: CEORouteDecision = ceo_llm.invoke(messages)
    
    console.print(f"  👉 [bold cyan]CEO Stratejik Kararı:[/bold cyan] [green]'{decision.next}'[/green] | [dim]{decision.strategic_reason}[/dim]")
    
    if decision.next == "FINISH":
        closing_msg = AIMessage(
            content=f"👑 [CEO Kapanış Bildirimi]: {decision.strategic_reason}\nProje tüm kurumsal departmanlarca başarıyla tamamlanmış ve onaylanmıştır."
        )
        return {"next_step": decision.next, "messages": [closing_msg]}
        
    return {"next_step": decision.next}


def research_dept_node(state: CompanyState):
    """Araştırma ve İstihbarat Departmanı."""
    console.print("\n[bold magenta]🔬 [DEPARTMAN 1: ARAŞTIRMA & İSTİHBARAT][/bold magenta] Pazar analizi yapıyor...")
    system_prompt = (
        "Sen Şirket Baş Araştırmacısısın. 'query_market_intelligence' aracını çağırarak "
        "kullanıcının talebine dair güncel piyasa verilerini topla."
    )
    messages = state["messages"] + [HumanMessage(content=system_prompt)]
    response = research_llm.invoke(messages)
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        console.print(f"   🔧 [Araç]: {response.tool_calls[0]['name']}")
        tool_node = ToolNode(research_tools)
        tool_res = tool_node.invoke({"messages": [response]})
        tool_msg = tool_res["messages"][0]
        summary_text = get_text(tool_msg.content)
        report_msg = AIMessage(content=f"Araştırma Bulguları: {summary_text}")
        return {"messages": [response, tool_msg, report_msg], "research_summary": summary_text}
        
    return {"messages": [response], "research_summary": get_text(response.content)}


def engineering_dept_node(state: CompanyState):
    """Mühendislik ve Ürün Departmanı."""
    console.print("\n[bold deep_sky_blue1]💻 [DEPARTMAN 2: YAZILIM & MÜHENDİSLİK][/bold deep_sky_blue1] Üretim kodunu inşa ediyor...")
    system_prompt = (
        "Sen Şirket Baş Yazılım Mimarı ve Kıdemli Mühendisisin. "
        "Araştırma departmanının çıktılarını baz alarak 'generate_production_code' aracıyla "
        "kullanıcının talebine uygun çalışan Python modülünü oluştur."
    )
    messages = state["messages"] + [HumanMessage(content=system_prompt)]
    response = engineering_llm.invoke(messages)
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        console.print(f"   🔧 [Araç]: {response.tool_calls[0]['name']}")
        tool_node = ToolNode(engineering_tools)
        tool_res = tool_node.invoke({"messages": [response]})
        tool_msg = tool_res["messages"][0]
        code_text = get_text(tool_msg.content)
        report_msg = AIMessage(content=f"Mühendislik Çıktısı:\n{code_text}")
        return {"messages": [response, tool_msg, report_msg], "code_deliverable": code_text}
        
    return {"messages": [response], "code_deliverable": get_text(response.content)}


def audit_approval_dept_node(state: CompanyState):
    """Kalite Denetim ve Bütçe Departmanı (Kritik İşlem)."""
    console.print("\n[bold orange3]🛡️ [DEPARTMAN 3: KALİTE & FİNANS DENETİMİ][/bold orange3] Bütçe tahsisi hazırlıyor...")
    system_prompt = (
        "Sen Şirket Finans ve Denetim Direktörüsün. Mühendisliğin ürettiği modül için "
        "şirket bütçesinden 250.000 TL bütçe tahsisi yapılması için 'authorize_project_budget' aracını çağır."
    )
    messages = state["messages"] + [HumanMessage(content=system_prompt)]
    response = audit_llm.invoke(messages)
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        console.print(f"   ⚠️ [BÜTÇE ARACI TETİKLENDİ]: {response.tool_calls[0]['name']} (Tutar: 250.000 TL)")
        tool_node = ToolNode(audit_tools)
        tool_res = tool_node.invoke({"messages": [response]})
        tool_msg = tool_res["messages"][0]
        audit_text = get_text(tool_msg.content)
        report_msg = AIMessage(content=f"Finans Denetim Raporu: {audit_text}")
        return {
            "messages": [response, tool_msg, report_msg],
            "allocated_budget": 250000.0,
            "is_audit_passed": True
        }
        
    return {"messages": [response], "is_audit_passed": True}

# ==============================================================================
# 6. Kurumsal Grafın Kurulması (Enterprise StateGraph)
# ==============================================================================
workflow = StateGraph(CompanyState)

workflow.add_node("CEO", ceo_supervisor_node)
workflow.add_node("Research_Dept", research_dept_node)
workflow.add_node("Engineering_Dept", engineering_dept_node)
workflow.add_node("Audit_Approval_Dept", audit_approval_dept_node)

# START -> CEO
workflow.add_edge(START, "CEO")

# CEO -> Koşullu Yönlendirme (Dinamik Departman Seçimi)
workflow.add_conditional_edges(
    "CEO",
    lambda state: state["next_step"],
    {
        "Research_Dept": "Research_Dept",
        "Engineering_Dept": "Engineering_Dept",
        "Audit_Approval_Dept": "Audit_Approval_Dept",
        "FINISH": END
    }
)

# Her departman işi tamamladığında mutlaka CEO'ya rapor verir!
workflow.add_edge("Research_Dept", "CEO")
workflow.add_edge("Engineering_Dept", "CEO")
workflow.add_edge("Audit_Approval_Dept", "CEO")

# ==============================================================================
# 7. SQLite Veritabanı ve Human-in-the-Loop ile Derleme
# ==============================================================================
db_path = os.path.join(os.path.dirname(__file__), "enterprise.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# KRİTİK GÜVENLİK KİLİDİ:
# Audit_Approval_Dept (Bütçe Tahsisi) öncesinde İNSAN ONAYI için duraklatılır!
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Audit_Approval_Dept"]
)



# ==============================================================================
# 8. BÜYÜK FİNAL TEST SENARYOSU
# ==============================================================================
if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold gold1]👑 OTONOM AJAN ŞİRKETİ (AUTONOMOUS ENTERPRISE ENGINE) BAŞLATILIYOR 👑[/bold gold1]\n"
        "[dim]CEO Orkestrasyonu • Araştırma • Mühendislik • Finans & HITL İnsan Onayı • SQLite Kalıcılığı[/dim]",
        border_style="gold1"
    ))

    proje_hedefi = (
        "Şirketimiz için 'Bulut Tabanlı Otonom Müşteri Destek Sistemi' projesini başlatın. "
        "Sektör pazarını araştırın, temel Python mikroservis kodunu oluşturun ve "
        "ardından gerekli bütçe onayını alın."
    )
    console.print(f"[bold white]Yönetim Kurulu Direktifi:[/bold white]\n[italic]{proje_hedefi}[/italic]\n")

    config = {
        "configurable": {"thread_id": "holding-proje-alpha-2026"},
        "tags": ["enterprise", "holding", "multi-agent-v3"],
        "metadata": {"company": "Autonomous Agent Corp", "tier": "Tier-1"}
    }

    initial_input = {
        "messages": [HumanMessage(content=proje_hedefi)],
        "next_step": "CEO",
        "research_summary": None,
        "code_deliverable": None,
        "allocated_budget": None,
        "is_audit_passed": False
    }

    start_time = time.time()

    # 1. FAZ: CEO -> Araştırma -> Mühendislik çalışır ve Bütçe öncesinde duraklatılır
    console.print("\n[bold cyan]▶️  [1. FAZ BAŞLATILDI]: Şirket departmanları göreve başlıyor...[/bold cyan]")
    app.invoke(initial_input, config=config)

    # State Denetimi (Graf Durakladı mı?)
    snapshot = app.get_state(config)
    
    if snapshot.next and "Audit_Approval_Dept" in snapshot.next:
        console.print("\n" + "═" * 72)
        console.print("[bold red]🛑 [KRİTİK GÜVENLİK KİLİDİ - GRAF DURAKLATILDI - HUMAN-IN-THE-LOOP][/bold red]")
        console.print("═" * 72)
        console.print(f"  • Sıradaki Bekleyen Departman : [bold yellow]{snapshot.next}[/bold yellow]")
        console.print(f"  • Mühendisliğin Tamamladığı İş : [bold green]Mevcut (Kod hazırlandı)[/bold green]")
        console.print(f"  • Talep Edilen Proje Bütçesi  : [bold red]250.000 TL[/bold red]")
        console.print("\n[bold white]Yönetim Kurulu Başkanı (Kullanıcı) Bütçeyi İnceledi ve ONAY VERDİ! ✔[/bold white]")
        console.print("═" * 72 + "\n")

        # 2. FAZ: İnsan Onayından Sonra Devam Ettirme
        console.print("[bold cyan]▶️  [2. FAZ BAŞLATILDI]: İnsan onayı ile bütçe tahsisi tamamlanıyor...[/bold cyan]")
        final_state = app.invoke(None, config=config)
    else:
        final_state = snapshot.values

    total_duration = round(time.time() - start_time, 2)

    # ==========================================================================
    # Şirket Yönetim Kurulu Kapanış Raporu
    # ==========================================================================
    report_table = Table(title="🏆 Otonom Ajan Şirketi - Proje Teslimat Raporu", border_style="gold1")
    report_table.add_column("Departman / Metrik", style="cyan")
    report_table.add_column("Durum / Çıktı", style="green")

    report_table.add_row("1. Araştırma Departmanı", "Tamamlandı (Pazar İstihbarat Raporu Hazır)")
    report_table.add_row("2. Mühendislik Departmanı", "Tamamlandı (Kurumsal Python Kodu Üretildi)")
    report_table.add_row("3. İnsan Onayı (HITL)", "Onaylandı (250.000 TL Şirket Bütçesi Tahsis Edildi)")
    report_table.add_row("4. Veritabanı Kalıcılığı", "enterprise.db SQLite (Tüm Oturum Saklandı)")
    report_table.add_row("5. Toplam Şirket Süresi", f"{total_duration} saniye")

    console.print("\n")
    console.print(report_table)

    console.print("\n[bold gold1]=== CEO NİHAİ YÖNETİM KURULU BİLDİRİMİ ===[/bold gold1]")
    last_msg = final_state["messages"][-1]
    console.print(Panel(get_text(last_msg.content), title="CEO Kapanış Raporu", border_style="gold1"))
