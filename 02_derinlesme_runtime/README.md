# Modül 2: Derinleşme (LangGraph Academy Standartları)

Bu modülde ajanlarımıza oturum hafızası, insan onayı ve zamanda geriye yolculuk özellikleri ekleyeceğiz.

## Öğrenilecek Konular
1. **Persistence (Hafıza)**: `MemorySaver` ve veritabanı tabanlı checkpointer'lar.
2. **Thread İzolasyonu**: Birden fazla kullanıcının farklı oturumlarını (`thread_id`) yönetme.
3. **Human-in-the-Loop (HITL)**: `interrupt_before` ve `interrupt()` ile insandan onay alma.
4. **Time-Travel Debugging**: Geçmiş adımları listeleme, checkpoint bazlı dallandırma (`forking`) ve state güncelleme (`update_state`).

## Yapılacak Canlı Pratik
- `01_hafizali_ajan.py`: Konuşmaları hatırlayan sürekli ajan.
- `02_insan_onayli_islem.py`: Kritik işlemde durup insandan onay bekleyen akış.
