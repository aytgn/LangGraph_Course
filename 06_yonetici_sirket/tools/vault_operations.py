"""
Vault Operations Tools - ADR & Brainstorm Documentation.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import config
from tools.base import StudioTool
from tools.registry import ToolRegistry


class ADRWriterTool(StudioTool):
    """Generates standardized Architecture Decision Records (ADR)."""

    def __init__(self):
        super().__init__(
            name="adr_writer_tool",
            description="Mimari karar kayıtlarını (ADR) standart markdown formatında meta_bellek altına kaydeder.",
            department="System_Architect",
            category="Documentation",
            parameters_schema={"adr_id": "str", "title": "str", "status": "str", "decision": "str"}
        )

    def run(self, adr_id: str, title: str, status: str, context: str, decision: str, consequences: str) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        content = f"""# {adr_id}: {title}

**Tarih:** {date_str}
**Durum:** {status}
**Karar Vericiler:** Baş Sistem Mimarı (CTO) & Kurucu Başkan

---

## 1. Bağlam ve Problem
{context}

## 2. Alınan Mimari Karar
{decision}

## 3. Sonuçlar ve Etkiler
{consequences}
"""
        clean_slug = title.lower().replace(" ", "_").replace("/", "_")
        filename = f"{adr_id}_{clean_slug}.md"
        filepath = config.DECISIONS_DIR / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)


class BrainstormNoteWriterTool(StudioTool):
    """Saves ideation and brainstorming session notes."""

    def __init__(self):
        super().__init__(
            name="brainstorm_note_writer",
            description="Ürün Keşif ve tartışma odası notlarını meta_bellek altına kaydeder.",
            department="Product_Lead",
            category="Documentation",
            parameters_schema={"title": "str", "content": "str"}
        )

    def run(self, title: str, content: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = title.lower().replace(" ", "_")[:30]
        filename = f"{ts}_{slug}.md"
        filepath = config.BRAINSTORM_DIR / filename
        doc = f"# 💡 {title}\n\n**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{content}\n"
        filepath.write_text(doc, encoding="utf-8")
        return str(filepath)


# Register tools
ToolRegistry.register(ADRWriterTool())
ToolRegistry.register(BrainstormNoteWriterTool())
