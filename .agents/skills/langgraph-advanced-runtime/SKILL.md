---
name: langgraph-advanced-runtime
description: >-
  Provides patterns and implementation standards for advanced LangGraph runtime features.
  Use when teaching or implementing Persistence (Checkpointers), Time-Travel Debugging,
  State Inspection, and Human-in-the-Loop (HITL) approval or state mutation workflows.
---

# LangGraph İleri Seviye: Persistence, Time-Travel & Human-in-the-Loop

Bu beceri, ajanların hafıza kazanmasını, oturum bazlı çalışmasını, insan onayı almasını ve zamanda geriye giderek hata ayıklanmasını sağlayan runtime mekanizmalarını yönetir.

## 1. Persistence & Checkpointers (Hafıza Yönetimi)

Grafın her adımındaki durumunu diske veya veritabanına kaydeder. Oturumlar `thread_id` ile birbirinden izole edilir.

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "session-user-123"}}

# İlk çağrı
events = app.stream({"messages": [("user", "Adım Ahmet ve finans uzmanıyım.")]}, config=config)

# İkinci çağrı: Ajan önceki mesajları ve adını hatırlar
events = app.stream({"messages": [("user", "Benim uzmanlığım neydi?")]}, config=config)
```

## 2. Human-in-the-Loop (HITL - İnsan Onayı ve Müdahalesi)

Kritik işlemlerden (örn. para transferi, e-posta gönderme, kod çalıştırma) önce ajanın durdurulması ve insandan onay/düzeltme alması.

### Yöntem A: `interrupt_before` ile Derleme
```python
# "action_node" çalıştırılmadan HEMEN ÖNCE grafı durdur
app = workflow.compile(checkpointer=memory, interrupt_before=["action_node"])

# Graf action_node öncesinde durur
app.invoke({"messages": [("user", "1000 TL transfer et")]}, config=config)

# Durumu kontrol et
snapshot = app.get_state(config)
print("Sıradaki bekleyen adım:", snapshot.next)  # ('action_node',)

# İnsan onayladıysa veya state güncellendiyse devam ettir:
app.invoke(None, config=config)
```

### Yöntem B: Dinamik `interrupt()` Fonksiyonu
```python
from langgraph.types import interrupt

def human_approval_node(state: AgentState):
    # Kullanıcıdan girdi beklemek için yürütmeyi duraklatır
    human_response = interrupt({
        "question": "Bu işlemi onaylıyor musunuz?",
        "proposed_action": state.get("pending_action")
    })
    return {"approved": human_response.get("approved", False)}
```

## 3. Time-Travel Debugging & State Forking (Geçmişe Yolculuk)

Ajanın geçmiş adımlarını inceleme, hatalı bir adımdan önceye dönüp state'i manuel olarak değiştirip farklı bir akış başlatma (forking).

```python
# Tüm geçmiş adımları listele
for state in app.get_state_history(config):
    print("Checkpoint ID:", state.config["configurable"]["checkpoint_id"])
    print("Mesaj sayısı:", len(state.values["messages"]))

# Belirli bir adımdaki state'i güncelle ve dallandır (fork)
target_config = {
    "configurable": {
        "thread_id": "session-user-123",
        "checkpoint_id": "target-checkpoint-id-xyz"
    }
}

app.update_state(target_config, {"messages": [("user", "Hayır, tutarı 500 TL yap")]})
# Yeni kararla devam et
app.invoke(None, config=target_config)
```
