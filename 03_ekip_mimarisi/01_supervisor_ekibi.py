import os
import sys
import sqlite3
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# Kök dizindeki model_factory modülünü içe aktar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm

load_dotenv()

# ==============================================================================
# 1. Uzman Ajanların Araçları (Tools)
# ==============================================================================

# Araştırmacı Ajanın Araçları
@tool
def search_market_data(query: str) -> str:
    """Piyasa ve sektör trendlerini, rakip verilerini simüle edilmiş web kaynağından arar."""
    market_db = {
        "yapay zeka": "2026 Yapay Zeka Pazarı Raporu: Otonom çoklu ajan mimarileri %140 büyüme gösterdi. Kurumsal entegrasyonlar rekor seviyede.",
        "finans": "2026 FinTech Trendleri: API tabanlı otomatik bütçeleme ve akıllı mikro-servisler liderliği ele aldı.",
        "bulut": "2026 Bulut Bilişim: Sunucusuz (serverless) konteynerler ve edge LLM altyapıları standart hale geldi."
    }
    for key, val in market_db.items():
        if key in query.lower():
            return f"[Piyasa Araştırma Sonucu]: {val}"
    return f"[Piyasa Araştırma Sonucu]: '{query}' hakkında güncel piyasa trendi: Sektörde güçlü dijitalleşme ve otomasyon talebi var."

# Geliştirici (Coder) Ajanın Araçları
@tool
def generate_python_snippet(feature_name: str) -> str:
    """Belirtilen özellik için standart ve test edilebilir bir Python kod şablonu üretir."""
    return (
        f"# --- Otomatik Üretilen Kod: {feature_name} ---\n"
        f"def run_{feature_name.replace(' ', '_').lower()}():\n"
        f"    print('🚀 [{feature_name}] modülü başarıyla başlatıldı!')\n"
        f"    return {{'status': 'OK', 'module': '{feature_name}'}}\n"
    )

# ==============================================================================
# 2. State (Şirket Hafızası)
# ==============================================================================
class TeamState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_worker: str       # Supervisor'ın seçtiği sıradaki çalışan
    task_summary: str      # Şirket ortak pano özeti

# ==============================================================================
# 3. Supervisor (Yönetici) ve Karar Şeması
# ==============================================================================
class RouteDecision(BaseModel):
    """Yöneticinin işi kime devredeceğini belirten karar çıktısı."""
    next: Literal["Researcher", "Coder", "FINISH"] = Field(
        description="Görevi devralacak uzman çalışan. Eğer görev eksiksiz tamamlandıysa 'FINISH'."
    )
    reason: str = Field(description="Bu çalışanın seçilme sebebi veya görevin bitiş gerekçesi.")

# ==============================================================================
# 4. Modellerin Hazırlanması
# ==============================================================================
# Yönetici Model (Yapılandırılmış Çıktı / Structured Output ile karar verir)
supervisor_llm = get_gemini_llm(temperature=0.1).with_structured_output(RouteDecision)

# Araştırmacı Ajan Modeli (Arama araçlarıyla donatılmış)
researcher_tools = [search_market_data]
researcher_llm = get_gemini_llm(temperature=0.3, tools=researcher_tools)

# Geliştirici Ajan Modeli (Kod yazma araçlarıyla donatılmış)
coder_tools = [generate_python_snippet]
coder_llm = get_gemini_llm(temperature=0.1, tools=coder_tools)

# ==============================================================================
# 5. Düğümler (Nodes)
# ==============================================================================

def supervisor_node(state: TeamState):
    """Merkezi Yönetici: Konuşma geçmişine bakar ve sıradaki ajanı seçer."""
    print("\n👔 [SUPERVISOR / YÖNETİCİ]: Durumu inceliyor ve görev dağıtımı yapıyor...")
    
    prompt = (
        "Sen bir Yazılım ve Ürün Şirketinin Proje Yöneticisisin (Supervisor).\n"
        "Ekibinde 2 uzman çalışan var:\n"
        "1. 'Researcher': Piyasa araştırması, sektör bilgisi ve kullanıcı ihtiyaçlarını araştırır.\n"
        "2. 'Coder': Araştırma sonuçlarına göre Python kod şablonları ve mimari kod yazar.\n\n"
        "GÖREVİN:\n"
        "- Kullanıcının isteğini ve şu ana kadar yapılan işleri incele.\n"
        "- Eğer henüz araştırma yapılmadıysa 'Researcher'ı seç.\n"
        "- Eğer araştırma tamamlandıysa ve kod gerekiyorsa 'Coder'ı seç.\n"
        "- Hem araştırma hem de kod tamamsa veya kullanıcıya cevap hazırsa 'FINISH' seç.\n"
    )
    
    messages = [HumanMessage(content=prompt)] + state["messages"]
    decision: RouteDecision = supervisor_llm.invoke(messages)
    
    print(f"👉 [YÖNETİCİ KARARI]: Sıradaki Ajan -> '{decision.next}' (Sebep: {decision.reason})")
    return {"next_worker": decision.next}


def researcher_node(state: TeamState):
    """Araştırmacı Uzman Ajan."""
    print("\n🔍 [RESEARCHER / ARAŞTIRMACI]: Piyasa verilerini araştırıyor...")
    system_prompt = (
        "Sen Kıdemli Piyasa Araştırmacısısın. 'search_market_data' aracını kullanarak "
        "kullanıcının talebine dair en güncel pazar ve sektör bilgilerini topla ve 2-3 cümleyle özetle."
    )
    # İlgili araçla çalıştır
    response = researcher_llm.invoke([HumanMessage(content=system_prompt)] + state["messages"])
    
    # Eğer tool çağırdıysa ToolNode'u hemen çalıştırıp yanıtı alalım:
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"   [Araç Çağrıldı]: {response.tool_calls[0]['name']}")
        tool_node = ToolNode(researcher_tools)
        tool_res = tool_node.invoke({"messages": [response]})
        # Sonucu LLM'e verip nihai özetini al
        final_summary = researcher_llm.invoke(state["messages"] + [response] + tool_res["messages"])
        return {"messages": [final_summary]}
        
    return {"messages": [response]}


def coder_node(state: TeamState):
    """Geliştirici Uzman Ajan."""
    print("\n💻 [CODER / GELİŞTİRİCİ]: Çözüm için Python kodunu üretiyor...")
    system_prompt = (
        "Sen Baş Yazılım Mimarı ve Python Geliştiricisisin. State'teki araştırma bulgularını incele. "
        "'generate_python_snippet' aracını kullanarak talebe uygun çalışan, temiz bir Python kodu oluştur."
    )
    response = coder_llm.invoke([HumanMessage(content=system_prompt)] + state["messages"])
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"   [Araç Çağrıldı]: {response.tool_calls[0]['name']}")
        tool_node = ToolNode(coder_tools)
        tool_res = tool_node.invoke({"messages": [response]})
        final_summary = coder_llm.invoke(state["messages"] + [response] + tool_res["messages"])
        return {"messages": [final_summary]}
        
    return {"messages": [response]}

# ==============================================================================
# 6. Graf Mimarisi (Workflow)
# ==============================================================================
workflow = StateGraph(TeamState)

# Düğümleri kaydet
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Coder", coder_node)

# Başlangıç her zaman Supervisor ile olur
workflow.add_edge(START, "supervisor")

# Supervisor'dan uzman ajanlara KOŞULLU YÖNLENDİRME:
# next_worker alanına bakar: "Researcher", "Coder" veya "FINISH" -> END
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_worker"],
    {
        "Researcher": "Researcher",
        "Coder": "Coder",
        "FINISH": END
    }
)

# Her uzman işini bitirdiğinde mutlaka tekrar YÖNETİCİYE geri döner!
workflow.add_edge("Researcher", "supervisor")
workflow.add_edge("Coder", "supervisor")

# ==============================================================================
# 7. SQLite Veritabanı ile Derleme (Persistence)
# ==============================================================================
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
# 8. Canlı Test Senaryosu
# ==============================================================================
if __name__ == "__main__":
    print("=" * 72)
    print(">>> MODÜL 3: MULTI-AGENT SUPERVISOR PATTERN (CANLI TEST) <<<")
    print("=" * 72)
    
    talep = (
        "Yapay zeka sektöründeki güncel durumu araştırıp, "
        "bu alanda çalışan bir 'Ajan İzleme' fonksiyonu için Python kodu yazar mısınız?"
    )
    print(f"Kullanıcı Talebi:\n'{talep}'\n")
    
    config = {"configurable": {"thread_id": "sirket-proje-001"}}
    initial_input = {
        "messages": [HumanMessage(content=talep)],
        "next_worker": "supervisor",
        "task_summary": ""
    }
    
    final_output = app.invoke(initial_input, config=config)
    
    print("\n" + "=" * 72)
    print("=== ŞİRKET EKİBİNİN NİHAİ RAPORU ===")
    print("=" * 72)
    for msg in final_output["messages"]:
        sender = getattr(msg, "name", type(msg).__name__)
        print(f"\n[{sender}]:\n{get_text(msg.content)}")
