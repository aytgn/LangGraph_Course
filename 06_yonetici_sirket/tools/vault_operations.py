"""
Vault Operations Tools - ADR, Brainstorm & Engineering Spec Documentation.
"""

import re
from datetime import datetime
from config.settings import config
from tools.base import StudioTool
from tools.registry import ToolRegistry


def _safe_slug(text: str) -> str:
    s = (text or "not").strip().lower()
    s = s.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")[:40] or "belge"


class ADRWriterTool(StudioTool):
    """Generates standardized Architecture Decision Records (ADR)."""

    def __init__(self):
        super().__init__(
            name="adr_writer_tool",
            description="Mimari karar kayıtlarını (ADR) standart markdown formatında meta_bellek altına kaydeder.",
            department="System_Architect",
            category="Documentation",
            parameters_schema={"adr_id": "str", "title": "str", "status": "str", "decision": "str"},
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
        clean_slug = _safe_slug(title)
        safe_id = re.sub(r"[^a-zA-Z0-9\-_]+", "", adr_id or "ADR")
        filename = f"{safe_id}_{clean_slug}.md"
        filepath = config.DECISIONS_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
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
            parameters_schema={"title": "str", "content": "str"},
        )

    def run(self, title: str, content: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _safe_slug(title)
        filename = f"{ts}_{slug}.md"
        filepath = config.BRAINSTORM_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        doc = f"# 💡 {title}\n\n**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{content}\n"
        filepath.write_text(doc, encoding="utf-8")
        return str(filepath)


class OperationalSpecWriterTool(StudioTool):
    """Saves finalized product-to-engineering build specifications."""

    def __init__(self):
        super().__init__(
            name="operational_spec_writer",
            description="Tartışma odasında olgunlaşan uygulama şartnamesini 04_operasyonel_direktifler altına kaydeder.",
            department="Studio_Director",
            category="Documentation",
            parameters_schema={"title": "str", "directive_text": "str"},
        )

    def run(self, title: str, directive_text: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _safe_slug(title)
        filename = f"SPEC_{ts}_{slug}.md"
        filepath = config.DIRECTIVES_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        doc = (
            f"# 🚀 Uygulama Geliştirme Şartnamesi: {title}\n\n"
            f"**Oluşturulma:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n{directive_text}\n"
        )
        filepath.write_text(doc, encoding="utf-8")
        return str(filepath)


# Register tools
ToolRegistry.register(ADRWriterTool())
ToolRegistry.register(BrainstormNoteWriterTool())
ToolRegistry.register(OperationalSpecWriterTool())
