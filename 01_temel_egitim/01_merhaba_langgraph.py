import os
import sys
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Kök dizindeki model_factory modülünü içe aktar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm

# 1. Ortam Değişkenlerini Yükle
load_dotenv()

# 2. State (Graf Hafızası) Tanımı
class CourseState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    lesson_topic: str

# 3. Model: Birincil her zaman 'gemini-3.8-flash', hata verirse 3 alternatifli otomatik yedekleme
llm = get_gemini_llm(temperature=0.3)

# 4. Node (Düğüm) Fonksiyonu
# Node bir fonksiyondur: State'i parametre olarak alır, State'te güncellenecek alanları dict olarak döndürür.
def instructor_node(state: CourseState):
    print("\n--- [EĞİTMEN DÜĞÜMÜ ÇALIŞTI] ---")
    response = llm.invoke(state["messages"])
    # Döndürülen sözlük, State'teki 'messages' listesine eklenir (add_messages sayesinde)
    return {"messages": [response]}

def get_text_content(content) -> str:
    """Mesaj içeriğini string olarak güvenli bir şekilde döner."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in content]
        return " ".join(parts)
    return str(content)

# 4.1 Node (Düğüm) Fonksiyonu - Aytu
def critic_node(state: CourseState):
    """LLM'den gelen son mesaja critique (eleştiri) yazar."""
    print("\n--- [ELEŞTİRMEN DÜĞÜMÜ ÇALIŞTI] ---")
    last_message = get_text_content(state["messages"][-1].content)
    
    critic_prompt = (
        "Aşağıdaki eğitmen yanıtını değerlendir. Konuyla ilgili ve motive edici mi? "
        "Bir öğrenci koçu olarak 1-2 cümlelik yapıcı ve enerjik bir geri bildirim ekle.\n\n"
        f"Eğitmen Yanıtı: {last_message}"
    )
    
    response = llm.invoke([HumanMessage(content=critic_prompt)])
    return {"messages": [response]}

# 5. Grafı İnşa Etme (Workflow)
workflow = StateGraph(CourseState)

# Düğümleri ekle
workflow.add_node("instructor", instructor_node)
workflow.add_node("critic", critic_node)

# Kenarları (Edges) ekle: START -> instructor -> critic -> END
workflow.add_edge(START, "instructor")
workflow.add_edge("instructor", "critic")   # 1. Düzeltme: instructor'dan critic'e geçiş
workflow.add_edge("critic", END)            # 2. Düzeltme: critic'ten END'e geçiş

# 6. Grafı Derleme (Compile)
app = workflow.compile()

# 7. Çalıştırma (Invoke)
if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[UYARI] GOOGLE_API_KEY bulunamadı! Lütfen .env dosyanıza ekleyin.")
        print("Örnek: GOOGLE_API_KEY=\"AIzaSy...\"\n")
    else:
        print(">>> 1. Ders: LangGraph İlk Graf Çalıştırılıyor...")
        initial_input = {
            "messages": [HumanMessage(content="Merhaba! LangGraph öğrenmeye başladım. 1 cümleyle bana hoş geldin de.")],
            "lesson_topic": "LangGraph Temelleri"
        }
        
        # Grafı çalıştır ve sonucu al
        final_state = app.invoke(initial_input)
        
        print("\n" + "="*50)
        print("=== GRAF ÇALIŞMA SONUCU (STATE İÇERİĞİ) ===")
        print("="*50)
        roles = ["Öğrenci (User)", "Eğitmen (Instructor)", "Eleştirmen (Critic)"]
        for i, msg in enumerate(final_state["messages"]):
            role = roles[i] if i < len(roles) else f"Adım {i+1}"
            print(f"\n[{role}]:\n{get_text_content(msg.content)}")
