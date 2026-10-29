---
name: langgraph-multi-agent-architectures
description: >-
  Provides architectural blueprints, patterns, and code implementations for Multi-Agent Systems,
  Supervisor Patterns, Hierarchical Teams, Subgraphs, and Autonomous Agent Company frameworks in LangGraph.
  Use when designing multi-agent collaboration, delegation workflows, and autonomous enterprise systems.
---

# Çoklu Ajan Mimarileri: Supervisor, Hiyerarşik Ekipler ve Otonom Şirket Mimarisi

Bu beceri, birden fazla uzmanlaşmış ajanın bir arada çalıştığı, hiyerarşik veya eşler arası (peer-to-peer) sistemlerin kurulmasını yönetir.

## Mimari Modeller

```
+-------------------------------------------------------------+
|               Otonom Ajan Şirketi Mimarisi                  |
+-------------------------------------------------------------+
                               |
                               v
                     +-------------------+
                     |  CEO / Supervisor |
                     +-------------------+
                       /       |       \
                      /        |        \
                     v         v         v
         +-------------+  +------------+  +-------------+
         |  Araştırma  |  | Mühendislik|  |    Kalite   |
         | Departmanı  |  | Departmanı |  |   Güvence   |
         |  (Subgraph) |  | (Subgraph) |  | (Subgraph)  |
         +-------------+  +------------+  +-------------+
```

---

## 1. Supervisor (Yönetici) Şablonu

Merkezi bir yönetici düğüm (`supervisor_node`), kullanıcı hedefine göre görevi hangi uzman ajana devredeceğine karar verir.

```python
from typing import Literal
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    next: Literal["Researcher", "Coder", "Reviewer", "FINISH"] = Field(
        description="Görevi devralacak bir sonraki ajan veya iş bittiyse FINISH"
    )

supervisor_prompt = (
    "Sen bir proje yöneticisisin. Aşağıdaki çalışanları yönetiyorsun: Researcher, Coder, Reviewer. "
    "Kullanıcının isteğini incele ve sıradaki adımı belirle. Eğer görev tamamlandıysa FINISH seç."
)
```

---

## 2. Hiyerarşik Ekipler (Hierarchical Teams & Subgraphs)

Büyük projelerde her departman kendi bağımsız alt grafı (`subgraph`) olarak tasarlanır ve ana grafa bir düğüm olarak eklenir.

```python
# Araştırma Departmanı Alt Grafı (Subgraph)
research_builder = StateGraph(ResearchTeamState)
research_builder.add_node("search_agent", search_node)
research_builder.add_node("summarizer_agent", summary_node)
research_subgraph = research_builder.compile()

# Ana Şirket Grafı
company_builder = StateGraph(CompanyState)
company_builder.add_node("ceo_supervisor", ceo_node)
company_builder.add_node("research_department", research_subgraph)
company_builder.add_node("tech_department", tech_subgraph)
```

---

## 3. Otonom Şirket Durum Yönetimi (Company State Design)

Şirket genelinde paylaşılan durum ile departman içi özel durumların ayrıştırılması:

```python
class CompanyState(TypedDict):
    task: str
    company_log: list[str]
    department_outputs: dict[str, Any]
    current_department: str
    is_completed: bool
```
