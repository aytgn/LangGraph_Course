import os
import sys
import sqlite3
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

# Kök dizindeki model_factory modülünü içe aktar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm

# 1. Ortam Değişkenleri
load_dotenv()

# 2. Araçlar (Kritik Finansal İşlemler)
@tool
def execute_bank_transfer(recipient: str, amount: float) -> str:
    """Belirtilen alıcıya şirket hesabından banka havalesi yapar. DİKKAT: Gerçek para transferidir!"""
    return f"BAŞARILI: {recipient} hesabına {amount:,.2f} TL tutarındaki havale gönderildi. İşlem Referans No: TRX-99214."

@tool
def check_company_balance() -> str:
    """Şirket ana banka hesabının mevcut bakiyesini döner."""
    return "Şirket Ana Hesap Bakiyesi: 2.450.000 TL"

tools = [execute_bank_transfer, check_company_balance]

# 3. Model: Birincil her zaman 'gemini-3.8-flash', hata verirse 3 alternatifli otomatik yedekleme
llm_with_tools = get_gemini_llm(temperature=0.2, tools=tools)

# 4. State
class FinanceAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 5. Düğümler
def agent_node(state: FinanceAgentState):
    print("\n--- [AJAN DÜĞÜMÜ: Karar Veriyor] ---")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools=tools)

# 6. Graf Mimarisi
workflow = StateGraph(FinanceAgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# 7. Gerçek Veritabanı (SQLite Checkpointer) ve Human-in-the-Loop ile Derleme
# SqliteSaver: Grafın her adımını RAM yerine gerçek bir disk veritabanına (.db) yazar.
# Script kapansa veya sunucu yeniden başlasa bile tüm konuşmalar ve checkpoint'ler korunur!
db_path = os.path.join(os.path.dirname(__file__), "checkpoints.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["tools"]  # Kritik Güvenlik Kilidi: İnsan onayı olmadan araç çalışamaz!
)

# Yardımcı Metin Okuyucu
def get_text(content) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)

# 8. Canlı Test ve Senaryo
if __name__ == "__main__":
    print("=" * 65)
    print(">>> MODÜL 2: PERSISTENCE (HAFIZA) & HUMAN-IN-THE-LOOP (HITL) <<<")
    print("=" * 65)

    # -------------------------------------------------------------
    # ADIM 1: Oturum İzolasyonu (Thread Management)
    # -------------------------------------------------------------
    config_ahmet = {"configurable": {"thread_id": "oturum-ahmet-ceo"}}
    config_mehmet = {"configurable": {"thread_id": "oturum-mehmet-muhasebe"}}

    print("\n[SENARYO 1]: Ahmet (CEO) oturum açıyor ve ajana kendini tanıtıyor...")
    app.invoke({"messages": [HumanMessage(content="Merhaba, ben Ahmet. Şirketin CEO'suyum. Gizli bütçemiz 5 Milyon TL.")]}, config=config_ahmet)

    print("\n[SENARYO 2]: Mehmet (Muhasebe) FARKLI bir oturumda ajana soru soruyor...")
    resp_m = app.invoke({"messages": [HumanMessage(content="Merhaba, ben kimim?")]}, config=config_mehmet)
    print(f"Mehmet'in Oturumunda Ajan Yanıtı: {get_text(resp_m['messages'][-1].content)}")

    print("\n[SENARYO 3]: Ahmet (CEO) ilk oturumuna geri dönüyor...")
    resp_a = app.invoke({"messages": [HumanMessage(content="Ben kimim ve gizli bütçemiz ne kadardı?")]}, config=config_ahmet)
    print(f"Ahmet'in Oturumunda Ajan Yanıtı: {get_text(resp_a['messages'][-1].content)}")

    # -------------------------------------------------------------
    # ADIM 2: Human-in-the-Loop (Kritik İşlemde İnsan Onayı)
    # -------------------------------------------------------------
    print("\n" + "=" * 65)
    print("[SENARYO 4]: Ahmet para transferi emri veriyor (Kritik İşlem)...")
    print("=" * 65)

    emr = "Tedarikçi ABC Ltd şirketine 150.000 TL havale gönder."
    print(f"Ahmet'in Emri: '{emr}'")
    
    # Graf çalıştırılıyor
    app.invoke({"messages": [HumanMessage(content=emr)]}, config=config_ahmet)

    # Graf durdu mu? Anlık State'i kontrol edelim:
    snapshot = app.get_state(config_ahmet)
    print("\n[GÜVENLİK KONTROLÜ - GRAF DURAKLATILDI]")
    print(f"Grafın Durumu: {'DURAKLADI (BEKLEMEDE)' if snapshot.next else 'TAMAMLANDI'}")
    print(f"Sırada Bekleyen Düğüm (Next): {snapshot.next}")
    
    # Modelin çağırmak istediği aracı inceleyelim:
    last_agent_msg = snapshot.values["messages"][-1]
    pending_tool = last_agent_msg.tool_calls[0]
    print(f"Ajanın Çalıştırmak İstediği Araç: '{pending_tool['name']}'")
    print(f"İşlem Detayları: {pending_tool['args']}")

    # -------------------------------------------------------------
    # ADIM 3: İnsanın Kararı (Onay Verme veya Devam Ettirme)
    # -------------------------------------------------------------
    print("\n>>> İNSAN ONAYI: Yönetici işlemi kontrol etti ve ONAY VERDİ! <<<")
    print("Graf kaldığı yerden devam ettiriliyor...")

    # None göndererek grafın bekleyen 'tools' adımından devam etmesini sağlıyoruz:
    resumed_state = app.invoke(None, config=config_ahmet)

    print("\n[İŞLEM TAMAMLANDI - AJANIN SON RAPORU]:")
    print(get_text(resumed_state["messages"][-1].content))

    # -------------------------------------------------------------
    # ADIM 4: Time-Travel (Geçmiş Checkpoint'leri Listeleme)
    # -------------------------------------------------------------
    print("\n" + "=" * 65)
    print("[SENARYO 5]: Time-Travel - Geçmiş Checkpoint Listesi (Zaman Çizelgesi)")
    print("=" * 65)
    history = list(app.get_state_history(config_ahmet))
    print(f"Ahmet'in oturumunda toplam {len(history)} adet checkpoint (zaman damgası) kaydedildi:")
    for i, state in enumerate(history[:4]):  # Son 4 adımı göster
        step_name = state.next if state.next else "Bitiş (END)"
        print(f"  [{i+1}] Checkpoint ID: {state.config['configurable']['checkpoint_id'][:8]}... | Sıradaki: {step_name} | Mesaj Sayısı: {len(state.values['messages'])}")
