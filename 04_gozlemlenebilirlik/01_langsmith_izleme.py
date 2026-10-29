import os
import sys
import time
import sqlite3
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.callbacks.base import BaseCallbackHandler

class LiveMetricsCallbackHandler(BaseCallbackHandler):
    """Her adımın süresini, çağrılan araçları ve gecikmeleri canlı takip eden callback."""
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("  ⚡ [LLM Başladı]: Yanıt üretiliyor...")

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "Bilinmeyen Araç")
        print(f"  🔧 [Araç Başladı]: {name}")

    def on_tool_end(self, output, **kwargs):
        print(f"  ✔ [Araç Bitti]: Sonuç State'e yazıldı.")
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
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
# 1. LangSmith Ortam Yapılandırması
langsmith_api_key = os.getenv("LANGCHAIN_API_KEY")
cloud_tracing_active = bool(langsmith_api_key and langsmith_api_key.startswith("lsv2_"))

if cloud_tracing_active:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "otonom-ajan-sirketi")
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
else:
    # Geçerli API anahtarı yoksa 401 hatası almamak için bulut aktarımını kapat, yerel metrikleri kullan:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

# ==============================================================================
# 2. Araçlar (Tools)
# ==============================================================================
@tool
def calculate_cost_projection(current_expense: float, months: int) -> str:
    """Belirli bir aylık gider için geleceğe dönük kümülatif maliyet projeksiyonu hesaplar."""
    time.sleep(0.4)  # Ağ gecikmesini simüle etmek için küçük bir gecikme
    total = current_expense * months * 1.08  # %8 enflasyon payı
    return f"{months} aylık tahmini toplam maliyet projeksiyonu: {total:,.2f} TL"

@tool
def audit_system_logs(service_name: str) -> str:
    """Belirtilen mikroservisin sistem sağlık ve hata loglarını denetler."""
    time.sleep(0.3)
    return f"[{service_name.upper()}]: Sistem sağlıklı, 0 kritik hata, CPU: %14, Bellek: 420MB."

tools = [calculate_cost_projection, audit_system_logs]

# ==============================================================================
# 3. Model ve State
# ==============================================================================
llm_with_tools = get_gemini_llm(temperature=0.2, tools=tools)

class ObservabilityState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def agent_node(state: ObservabilityState):
    print("\n--- [AJAN DÜĞÜMÜ: Karar Veriyor] ---")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools=tools)

# ==============================================================================
# 4. Graf Mimarisi & Veritabanı
# ==============================================================================
workflow = StateGraph(ObservabilityState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

db_path = os.path.join(os.path.dirname(__file__), "checkpoints.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

app = workflow.compile(checkpointer=memory)

# Yardımcı: Metin okuyucu
def get_text(content) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)

# ==============================================================================
# 5. Canlı Gözlemlenebilirlik ve Metrik Takip Testi
# ==============================================================================
if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]MODÜL 4: LANGSMITH GÖZLEMLENEBİLİRLİK, MALİYET VE LOG TAKİBİ[/bold cyan]",
        border_style="cyan"
    ))
    
    if cloud_tracing_active:
        console.print("[bold green]✔ LangSmith Cloud Tracing AKTİF![/bold green]")
        console.print(f"👉 Dashboard: https://smith.langchain.com/o/default/projects/p/{os.getenv('LANGCHAIN_PROJECT')}\n")
    else:
        console.print("[bold yellow]ℹ LANGCHAIN_API_KEY .env dosyasında bulunamadı.[/bold yellow]")
        console.print("[dim]Yerel terminal izleyicisi ve çalışma metrikleri aktif ediliyor...[/dim]")
        console.print("[dim](Ücretsiz bulut hesabı için: https://smith.langchain.com adresinden API anahtarı alabilirsiniz.)[/dim]\n")

    soru = (
        "Finans mikroservisimizin sağlık durumunu denetle. "
        "Ayrıca aylık 85.000 TL olan sunucu giderimiz için 6 aylık projeksiyon çıkar."
    )
    console.print(f"[bold white]Kullanıcı Talebi:[/bold white] {soru}\n")

    # ==========================================================================
    # Kurumsal Metadata ve Etiketleme (Tags & Metadata)
    # ==========================================================================
    # LangSmith üzerinde filtreleme, arama ve maliyet merkezlerini ayırma:
    config = {
        "configurable": {"thread_id": "izleme-oturum-101"},
        "tags": ["production", "q4-audit", "infra-team"],
        "metadata": {
            "environment": "production",
            "cost_center": "Engineering-Ops",
            "triggered_by": "Executive-Dashboard"
        },
        # Canlı konsol adımları ve metrik takibi:
        "callbacks": [LiveMetricsCallbackHandler()]
    }

    start_time = time.time()
    
    # Grafı çalıştır
    result = app.invoke({"messages": [HumanMessage(content=soru)]}, config=config)
    
    total_latency = round(time.time() - start_time, 3)

    # ==========================================================================
    # Konsol Metrik ve Maliyet Raporu
    # ==========================================================================
    table = Table(title="📊 Graf Çalışma ve Gözlemlenebilirlik Metrikleri", border_style="green")
    table.add_column("Metrik Adı", style="cyan", no_wrap=True)
    table.add_column("Değer", style="magenta")
    table.add_column("Açıklama", style="dim")

    message_count = len(result["messages"])
    # Yaklaşık token hesabı (ortalama 4 karakter = 1 token varsayımı)
    total_chars = sum(len(get_text(m.content)) for m in result["messages"])
    est_tokens = int(total_chars / 4)
    # Gemini 3.x Flash maliyet katsayısı: ~$0.0001 / 1K token
    est_cost = (est_tokens / 1000) * 0.0001

    table.add_row("Toplam Çalışma Süresi (Latency)", f"{total_latency} saniye", "Tüm LLM + Tool çağrılarının toplamı")
    table.add_row("Üretilen Mesaj Adımı", str(message_count), "Human, AI ve Tool mesajları")
    table.add_row("Tahmini Tüketilen Token", f"~{est_tokens} token", "Prompt + Completion tahmini")
    table.add_row("Tahmini İşlem Maliyeti", f"${est_cost:.6f} USD", "Model tarifesine göre yaklaşık maliyet")
    table.add_row("Kalıcılık Veritabanı", "SQLite (checkpoints.db)", "Tüm konuşma diske kaydedildi")

    console.print(table)

    console.print("\n[bold green]=== AJANIN NİHAİ RAPORU ===[/bold green]")
    console.print(Panel(get_text(result["messages"][-1].content), title="Ajan Yanıtı", border_style="blue"))
