import os
import sys
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Kök dizindeki model_factory modülünü içe aktar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm

# 1. Ortam Değişkenleri
load_dotenv()

# 2. Araçlar (Tools) Tanımlama
# @tool dekoratörü ile Python fonksiyonlarını LLM'in çağırabileceği araçlara dönüştürüyoruz.
# Fonksiyonun docstring'i (açıklaması) çok önemlidir, çünkü LLM hangi aracı ne zaman seçeceğini buradan anlar!

@tool
def calculate_growth_rate(current_revenue: float, previous_revenue: float) -> str:
    """İki dönem arasındaki gelir büyüme oranını yüzde olarak hesaplar."""
    if previous_revenue == 0:
        return "Önceki dönem geliri 0 olamaz."
    rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
    return f"Gelir büyüme oranı: %{rate:.2f}"

@tool
def get_company_stock_price(ticker: str) -> str:
    """Belirtilen hisse senedi kodunun (ticker) anlık sembolik fiyatını getirir."""
    # Gerçek API entegrasyonu simülasyonu
    stocks = {
        "GOOGL": "$178.50",
        "AAPL": "$230.10",
        "MSFT": "$425.00"
    }
    ticker_upper = ticker.upper()
    price = stocks.get(ticker_upper, "Bilinmiyor (Veri bulunamadı)")
    return f"{ticker_upper} hisse fiyatı: {price}"

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Belirtilen para birimleri arasında döviz çevrimi yapar (örn: USD -> TRY)."""
    # Sembolik döviz kurları (1 birim baz dövizin karşılığı)
    rates = {
        ("USD", "TRY"): 34.50,
        ("EUR", "TRY"): 37.80,
        ("TRY", "USD"): 1 / 34.50
    }
    pair = (from_currency.upper(), to_currency.upper())
    rate = rates.get(pair)
    if rate:
        converted = amount * rate
        return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()} (Kur: {rate})"
    return f"Döviz kuru bulunamadı: {from_currency} -> {to_currency}"

@tool
def get_company_employee_count(company_name: str) -> str:
    """Belirtilen küresel şirketin toplam çalışan sayısını ve merkezini döner."""
    company_data = {
        "apple": "Apple: Dünya çapında yaklaşık 161.000 çalışan (Merkez: Cupertino, Kaliforniya)",
        "google": "Google (Alphabet): Dünya çapında yaklaşık 182.000 çalışan (Merkez: Mountain View, Kaliforniya)",
        "microsoft": "Microsoft: Dünya çapında yaklaşık 221.000 çalışan (Merkez: Redmond, Washington)"
    }
    info = company_data.get(company_name.lower())
    if info:
        return info
    return f"{company_name} için çalışan bilgisi sistemde kayıtlı değil."

tools = [
    calculate_growth_rate,
    get_company_stock_price,
    convert_currency,
    get_company_employee_count
]

# 3. Model: Birincil her zaman 'gemini-3.8-flash', hata verirse 3 alternatifli otomatik yedekleme
llm_with_tools = get_gemini_llm(temperature=0, tools=tools)

# 4. State Tanımı
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 5. Düğümler (Nodes)
def agent_node(state: AgentState):
    """Karar verici LLM düğümü."""
    print("\n--- [AJAN DÜĞÜMÜ: Düşünüyor / Karar Veriyor] ---")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# LangGraph'ın hazır ToolNode'u: LLM bir araç çağırdığında onu otomatik çalıştırır
tool_node = ToolNode(tools=tools)

# 6. Grafı İnşa Etme (Workflow)
workflow = StateGraph(AgentState)

# Düğümleri ekle
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# Kenarları ekle
workflow.add_edge(START, "agent")

# KOŞULLU KENAR (Conditional Edge):
# tools_condition, LLM'in son mesajında tool çağrısı olup olmadığını kontrol eder:
# - Tool çağrısı varsa -> 'tools' düğümüne gider.
# - Tool çağrısı yoksa -> '__end__' düğümüne gider (Cevap hazır).
workflow.add_conditional_edges(
    "agent",
    tools_condition
)

# DÖNGÜSEL KENAR (Cyclic Edge):
# Araç çalıştığında sonuç State'e eklenir ve mutlaka tekrar 'agent' düğümüne döner!
# Böylece model araç çıktısını okuyup son kullanıcıya açıklama yapabilir.
workflow.add_edge("tools", "agent")

# 7. Grafı Derle
app = workflow.compile()

# Yardımcı: Metin okuyucu
def get_text_content(content) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in content]
        return " ".join(parts)
    return str(content)

# 8. Çalıştırma
if __name__ == "__main__":
    print(">>> 2. Ders: ReAct ve Koşullu Yönlendirme Testi Başlıyor...\n")
    
    # Test Sorusu: Çok adımlı akıl yürütme (Multi-step Reasoning)
    # Ajanın önce hisse fiyatını bulması ($230.10), ardından bunu TRY'ye çevirmesi ve çalışan sayısını sorgulaması gerekir!
    soru = (
        "Apple (AAPL) hisse fiyatı şu an kaç dolar? "
        "Bu hisse fiyatının Türk Lirası (TRY) karşılığı nedir? "
        "Ayrıca Apple şirketinde kaç kişi çalışıyor?"
    )
    
    print(f"Kullanıcı Sorusu: {soru}")
    initial_input = {"messages": [HumanMessage(content=soru)]}
    
    # Stream ile grafın adımlarını canlı canlı izleyelim!
    for chunk in app.stream(initial_input, stream_mode="values"):
        last_msg = chunk["messages"][-1]
        msg_type = type(last_msg).__name__
        
        # Eğer model bir araç çağırmışsa:
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                print(f"\n[Araç Çağrısı Tetiklendi]: {tc['name']} -> Argümanlar: {tc['args']}")
        elif msg_type == "ToolMessage":
            print(f"[Araç Sonucu Döndü]: {last_msg.content}")
        elif msg_type == "AIMessage" and not last_msg.tool_calls:
            print(f"\n[Ajanın Nihai Cevabı]:\n{get_text_content(last_msg.content)}")
