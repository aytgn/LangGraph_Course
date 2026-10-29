# Modül 1: Temel Eğitim (DeepLearning.AI Standartları)

Bu modülde sıfırdan LangGraph temellerini kodlayarak öğreneceksiniz.

## Öğrenilecek Konular
1. **State Mantığı**: `TypedDict` ve `Annotated[list, add_messages]` reducer yapısı.
2. **Düğümler (Nodes)**: LLM çağrıları yapan ve State'i güncelleyen fonksiyonlar.
3. **Kenarlar (Edges)**: Normal ve Koşullu (Conditional) yönlendirmeler (`tools_condition`).
4. **Tool Calling & ReAct**: Google Gemini (`gemini-1.5-flash`) ile araç çağıran otonom ajan oluşturma.

## Yapılacak Canlı Pratik
- `01_ilk_ajan.py`: İlk StateGraph ve LLM akışı.
- `02_tool_react_ajani.py`: Hesap makinesi / arama araçlarını kullanan canlı ReAct ajanı.
