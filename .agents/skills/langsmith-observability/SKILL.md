---
name: langsmith-observability
description: >-
  Provides configuration rules, tracing patterns, and evaluation workflows for LangSmith.
  Use when instrumenting LangGraph applications with observability, monitoring token costs,
  latency profiling, inspecting execution run trees, and debugging failed agent interactions.
---

# LangSmith Gözlemlenebilirlik, Maliyet ve Akış Takibi

Bu beceri, LangGraph ile inşa edilen ajanların ve otonom şirket yapılarının üretim ortamında izlenmesini, maliyet kontrolünü ve performans optimizasyonunu sağlar.

## 1. Temel Konfigürasyon ve Entegrasyon

LangSmith, LangChain ve LangGraph ile yerel olarak entegredir. Tek yapılması gereken ortam değişkenlerini tanımlamaktır:

```bash
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_PROJECT="otonom-ajan-sirketi"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

Python içinde dinamik yapılandırma:
```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langgraph-course-live"
```

---

## 2. Run Tree & Metadata Etiketleme

Çoklu ajan ve departman çağrılarında graf çalıştırılırken `tags` ve `metadata` ekleyerek LangSmith arayüzünde filtreleme yapma:

```python
config = {
    "configurable": {"thread_id": "session-101"},
    "tags": ["production", "department-tech", "gemini-1.5-flash"],
    "metadata": {
        "user_id": "usr_882",
        "company_tier": "enterprise",
        "project_goal": "full_stack_build"
    }
}

response = app.invoke({"messages": [("user", "Yeni bir API tasarla")]}, config=config)
```

---

## 3. Maliyet ve Gecikme (Latency) Takibi

LangSmith arayüzünde:
- **Token Usage**: Hangi ajanın kaç prompt ve completion token tükettiği.
- **Cost Analysis**: Model bazlı anlık maliyet dökümü.
- **Step Latency**: Hangi alt ajanın veya aracın (Tool) darboğaz oluşturduğunun saniye cinsinden analizi.

---

## 4. Geri Bildirim (Feedback) ve Hata Ayıklama (Run Debugging)

Çalışan bir run'ın ID'sini alarak hata ayıklama veya insan geri bildirimi ekleme:

```python
from langsmith import Client

client = Client()

# Belirli bir run için kalite puanı / feedback kaydet
client.create_feedback(
    run_id="run-id-from-trace",
    key="human-score",
    score=1.0,
    comment="Kod çıktısı başarıyla derlendi."
)
```
