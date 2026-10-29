"""
================================================================================
🧠 İKİNCİ BEYİN (SECOND BRAIN / KNOWLEDGE VAULT YÖNETİCİSİ)
================================================================================
Meta-katmandaki tüm stratejik fikirleri, kurucu ortak beyin fırtınalarını,
karar kayıtlarını (ADR) ve şirket vizyonunu kalıcı Markdown dosyaları olarak
saklayan ve yöneten bilgi kasası (Vault Manager).
================================================================================
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional

# Kök dizin ve Vault yolu
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(PROJECT_ROOT, "meta_bellek")

VISION_FILE = os.path.join(VAULT_DIR, "01_sirket_vizyonu.md")
BRAINSTORM_DIR = os.path.join(VAULT_DIR, "02_beyin_firtinasi_notlari")
DECISIONS_DIR = os.path.join(VAULT_DIR, "03_stratejik_kararlar")
DIRECTIVES_DIR = os.path.join(VAULT_DIR, "04_operasyonel_direktifler")


DEFAULT_VISION_CONTENT = """# 🌟 OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU MANİFESTOSU

**Son Güncelleme:** {date}
**Kurucu & Başkan:** Yönetim Kurulu Başkanı
**Odak Alanı:** Otonom Uygulama Geliştirme, Yazılım Mimarisi & Dijital Ürün İnşası

---

## 1. Varoluş Amacımız (Core Identity)
Biz teorik raporlar üreten bir danışmanlık ya da araştırma firması değiliz.
Biz, gerçek dünya problemlerini çözen somut yazılımlar, web uygulamaları, mikroservis API'leri ve otomasyon araçları tasarlayıp çalışan koda dönüştüren bir **Yapay Zeka Yazılım Evi (AI Software Studio & Venture Builder)**'ız.

## 2. Mühendislik ve Ürün İlkelerimiz
1. **Önce Ürün Amacı & MVP:** Ne uygulaması yapacağımızı, kimin hangi derdini çözeceğini netleştirmeden kod yazmayız.
2. **Doğru İşe Doğru Altyapı (Pragmatic Tech Stack):** İhtiyaca göre `Streamlit`, `FastAPI`, `SQLite`, `Pydantic` ve `CLI` mimarilerini pragmatik biçimde seçeriz.
3. **Sıfır Dummy / Gerçek Çalışan Kod:** Sahte şablonlar üretmeyiz; gerçek veri modellerine, iş mantığına ve fiziksel çalıştırma betiğine sahip uygulamalar inşa ederiz.
4. **Döngüsel Kalite Güvence (QA Loop) & Kurucu Onayı:** Her kod AST ve QA döngüsünden geçer, nihai paketleme Kurucu Başkan onayıyla mühürlenir.
""".format(date=datetime.now().strftime("%Y-%m-%d"))


def initialize_vault() -> None:
    """İkinci Beyin dizinlerini ve başlangıç manifestosunu oluşturur."""
    for folder in [VAULT_DIR, BRAINSTORM_DIR, DECISIONS_DIR, DIRECTIVES_DIR]:
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(VISION_FILE):
        with open(VISION_FILE, "w", encoding="utf-8") as f:
            f.write(DEFAULT_VISION_CONTENT)


def get_company_vision() -> str:
    """Şirket vizyonu ve manifesto metnini döndürür."""
    initialize_vault()
    try:
        with open(VISION_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"# Şirket Vizyonu\n(Okuma hatası: {e})"


def update_company_vision(content: str) -> bool:
    """Şirket vizyonunu günceller."""
    initialize_vault()
    try:
        with open(VISION_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def _slugify(text: str) -> str:
    """Dosya adları için metni güvenli formata dönüştürür."""
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    text = text.translate(tr_map).lower()
    text = re.sub(r"[^a-z0-9_\-]", "", text)
    return text[:40].strip("_")


def save_brainstorm_note(title: str, summary: str, transcript: List[Dict[str, str]], tags: Optional[List[str]] = None) -> str:
    """
    Beyin fırtınası oturumunu tarihli ve etiketli Markdown dosyası olarak kaydeder.
    Dönen değer oluşturulan dosya yoludur.
    """
    initialize_vault()
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    slug = _slugify(title) or "beyin_firtinasi"
    filename = f"{timestamp_str}_{slug}.md"
    file_path = os.path.join(BRAINSTORM_DIR, filename)

    tags_str = ", ".join([f"#{t.strip('#')}" for t in (tags or ["strateji", "beyin-fırtınası"])])

    lines = [
        f"# 💡 BEYİN FIRTINASI: {title.upper()}",
        f"",
        f"- **Tarih:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Etiketler:** {tags_str}",
        f"- **Durum:** İncelendi / Kaydedildi",
        f"",
        f"---",
        f"",
        f"## 📌 Oturum Özeti ve Ana Fikirler",
        f"{summary}",
        f"",
        f"---",
        f"",
        f"## 💬 Tartışma Transkripti",
        f""
    ]

    for item in transcript:
        speaker = item.get("role", "Bilinmeyen")
        content = item.get("content", "")
        avatar = "👔" if speaker in ["user", "Yönetici"] else ("🤝" if "Co-Founder" in speaker else ("⚡" if "Skeptic" in speaker else "🤖"))
        lines.append(f"### {avatar} {speaker}\n{content}\n")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return file_path


def save_strategic_decision(title: str, context: str, decision: str, consequences: str, tags: Optional[List[str]] = None) -> str:
    """
    Mimari & Stratejik Karar Kaydı (ADR - Architecture & Decision Record) oluşturur.
    """
    initialize_vault()
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M")
    slug = _slugify(title) or "stratejik_karar"
    
    # Mevcut karar sayısına göre numara ver
    existing = [f for f in os.listdir(DECISIONS_DIR) if f.endswith(".md")]
    seq_num = len(existing) + 1
    filename = f"ADR-{seq_num:03d}_{slug}.md"
    file_path = os.path.join(DECISIONS_DIR, filename)

    tags_str = ", ".join([f"#{t.strip('#')}" for t in (tags or ["karar", "adr", "pivot"])])

    content = f"""# 🏛️ STRATEJİK KARAR KAYDI: {title.upper()} (ADR-{seq_num:03d})

- **Kayıt Tarihi:** {now.strftime('%Y-%m-%d %H:%M')}
- **Durum:** ✅ ONAYLANDI & YÜRÜRLÜKTE
- **Etiketler:** {tags_str}

---

## 1. Bağlam ve Karşılaşılan Durum (Context)
{context}

## 2. Alınan Karar (Decision)
{decision}

## 3. Doğuracağı Sonuçlar ve Riskler (Consequences & Risks)
{consequences}

## 4. Denetim İmzası
- **Onaylayan:** Yönetim Kurulu Başkanı
- **Sentezleyen:** AI Chief of Staff & Co-Founder
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def save_operational_directive(title: str, task_brief: str) -> str:
    """
    CEO Ajanına gönderilecek operasyonel direktif brifini kaydeder.
    """
    initialize_vault()
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    slug = _slugify(title) or "operasyonel_direktif"
    filename = f"DIR_{timestamp_str}_{slug}.md"
    file_path = os.path.join(DIRECTIVES_DIR, filename)

    content = f"""# 🎯 OPERASYONEL DİREKTİF BRİFİ

- **Tarih:** {now.strftime('%Y-%m-%d %H:%M:%S')}
- **Kaynak:** Meta-Düzlem Strateji Masası
- **Hedef:** Operasyonel Ajan Şirketi CEO'su

---

## Direktif Başlığı
{title}

## Görev ve Beklenen Çıktılar
{task_brief}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def list_vault_documents() -> List[Dict[str, str]]:
    """İkinci Beyin kasasındaki tüm Markdown belgelerini meta verileriyle listeler."""
    initialize_vault()
    documents = []

    # 1. Vizyon
    if os.path.exists(VISION_FILE):
        documents.append({
            "category": "🌟 Vizyon & Manifesto",
            "name": "01_sirket_vizyonu.md",
            "path": VISION_FILE,
            "rel_path": os.path.relpath(VISION_FILE, PROJECT_ROOT),
            "size_kb": round(os.path.getsize(VISION_FILE) / 1024, 2),
            "modified": datetime.fromtimestamp(os.path.getmtime(VISION_FILE)).strftime("%Y-%m-%d %H:%M")
        })

    # 2. Beyin Fırtınaları
    for f in sorted(os.listdir(BRAINSTORM_DIR), reverse=True):
        if f.endswith(".md"):
            p = os.path.join(BRAINSTORM_DIR, f)
            documents.append({
                "category": "💡 Beyin Fırtınaları",
                "name": f,
                "path": p,
                "rel_path": os.path.relpath(p, PROJECT_ROOT),
                "size_kb": round(os.path.getsize(p) / 1024, 2),
                "modified": datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
            })

    # 3. Stratejik Kararlar (ADR)
    for f in sorted(os.listdir(DECISIONS_DIR), reverse=True):
        if f.endswith(".md"):
            p = os.path.join(DECISIONS_DIR, f)
            documents.append({
                "category": "🏛️ Stratejik Kararlar (ADR)",
                "name": f,
                "path": p,
                "rel_path": os.path.relpath(p, PROJECT_ROOT),
                "size_kb": round(os.path.getsize(p) / 1024, 2),
                "modified": datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
            })

    # 4. Operasyonel Direktifler
    for f in sorted(os.listdir(DIRECTIVES_DIR), reverse=True):
        if f.endswith(".md"):
            p = os.path.join(DIRECTIVES_DIR, f)
            documents.append({
                "category": "🎯 Operasyonel Direktifler",
                "name": f,
                "path": p,
                "rel_path": os.path.relpath(p, PROJECT_ROOT),
                "size_kb": round(os.path.getsize(p) / 1024, 2),
                "modified": datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
            })

    return documents


def read_document_content(file_path: str) -> str:
    """Verilen dosya yolundaki Markdown içeriğini okur."""
    if not os.path.exists(file_path):
        return f"Dosya bulunamadı: {file_path}"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Okuma hatası: {e}"
