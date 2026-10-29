---
name: langgraph-fundamentals
description: >-
  Provides patterns, architectural rules, and code templates for foundational LangGraph concepts.
  Use when teaching, designing, or implementing StateGraph, Nodes, Edges, Conditional Edges,
  ToolNode, Reducers (add_messages), and basic ReAct agent workflows with Google Gemini.
---

# LangGraph Temelleri: State, Node & Edge Mimarisi

Bu beceri, LangGraph'ın en temel yapı taşlarını inşa etme, öğretme ve kodlama kurallarını kapsar.

## Temel Bileşenler

```
+---------+         +------------------+         +--------------+
|  START  | ------> | Node: Assistant  | ------> | Edge/Router  |
+---------+         +------------------+         +--------------+
                                                        |
                                          [Tool Call?]  |  [Sonuç Hazır?]
                                          +-------------+-------------+
                                          |                           |
                                          v                           v
                                  +---------------+             +-----------+
                                  |   ToolNode    |             |    END    |
                                  +---------------+             +-----------+
                                          |
                                          +---------------------------> (Geri Dönüş: Assistant)
```

### 1. State Tanımı (Durum Yönetimi)
LangGraph'ta state, graf boyunca taşınan ve her düğüm tarafından güncellenebilen veri yapısıdır.

```python
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' bir reducer'dır. Eski mesajların üzerine yazmak yerine yeni mesajları listeye ekler.
    messages: Annotated[list[BaseMessage], add_messages]
    sender: str
```

### 2. Düğümler (Nodes)
Düğümler girdi olarak geçerli State'i alır ve geriye State'in güncellenmesini istedikleri alanlarını bir `dict` olarak döndürür:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def assistant_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response], "sender": "assistant"}
```

### 3. Kenarlar (Edges) ve Koşullu Yönlendirme (Conditional Edges)
- **Normal Edge**: Akışın doğrudan A düğümünden B düğümüne gitmesini sağlar (`workflow.add_edge("node_a", "node_b")`).
- **Koşullu Edge**: State'in durumuna bakarak sonraki düğümü dinamik olarak seçer:

```python
from langgraph.prebuilt import tools_condition

# tools_condition: Son mesaj bir tool_call içeriyorsa "tools" düğümüne, içermiyorsa END'e yönlendirir.
workflow.add_conditional_edges(
    "assistant",
    tools_condition,
    {"tools": "tools", "__end__": "__end__"}
)
```

### 4. Grafa Derleme (Compilation) & Çalıştırma
```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(AgentState)
workflow.add_node("assistant", assistant_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "assistant")
workflow.add_conditional_edges("assistant", tools_condition)
workflow.add_edge("tools", "assistant")

app = workflow.compile()
```
