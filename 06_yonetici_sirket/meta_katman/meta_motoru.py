"""
================================================================================
🏛️ ÜRÜN KEŞFİ & MİMARİ KONSEY MOTORU (PRODUCT & ARCHITECTURE DISCOVERY ENGINE)
================================================================================
Ürün Vizyoneri (CPO / Co-Founder), Baş Sistem Mimarı (CTO / Tech Critic) ve
Teknik Ürün Yöneticisi (Technical PM / Scribe) rollerini yöneten akıl motoru.
Ne uygulaması yapılacağını, hangi amaçla ve hangi altyapı/teknolojilerle
inşa edileceğini tartışmak üzere tasarlanmıştır.
================================================================================
"""

import os
import sys
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# 06_yonetici_sirket ve kök dizin (model_factory) yollarını ekle
_current_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_app_dir)
for _p in (_app_dir, _root_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from model_factory import get_gemini_llm
from meta_katman.ikinci_beyin import (
    get_company_vision,
    save_brainstorm_note,
    save_strategic_decision,
)


# ==============================================================================
# 1. Sistem Yönergeleri (Persona Prompts)
# ==============================================================================

COFOUNDER_SYSTEM_PROMPT = """Sen vizyoner, pratik ve ürün odaklı bir Yapay Zeka Kurucu Ortak & Ürün Direktörüsün (AI Co-Founder & CPO).
Şirketimiz bir araştırma firması DEĞİL; somut uygulamalar geliştiren bir **Yazılım Evi ve Uygulama Stüdyosudur**.
Muhattabın Şirketin Kurucu Başkanıdır.

GÖREVLERİN:
1. Kurucuyla 'Ne uygulaması yapacağız? Hangi gerçek problemi çözecek? Kim kullanacak? MVP'de olmazsa olmaz 3-5 somut özellik ne olmalı?' sorularını samimi, net ve yaratıcı şekilde tartış.
2. Soyut pazar edebiyatı yapma! Somut ekranlardan, kullanıcı akışlarından, veri girdisi/çıktısından ve uygulamanın sunduğu pratik değerden bahset.
3. Uygulama tipini netleştirmeye yardımcı ol: Görsel etkileşimli bir **Streamlit Web Uygulaması** mı, dış sistemlerin bağlanacağı **FastAPI REST Mikroservisi** mi, yoksa hızlı bir **CLI / Otomasyon Aracı** mı?
4. Fikri şişirmeden hemen kodlanıp çalıştırılabilecek keskin bir MVP kapsamı öner.

ŞİRKET MANİFESTOSU:
{vision_context}
"""

SKEPTIC_SYSTEM_PROMPT = """Sen şirketin Baş Sistem Mimarı ve Kritik CTO'susun (Principal Architect & Tech Stack Critic).
Görevin ASLA 'evet-efendimci' olmamak; ürün fikrini teknik altyapı, teknoloji seçimi, veri modeli ve uygulanabilirlik açısından masaya yatırmaktır.

GÖREVLERİN:
1. 'Hangi altyapıyla, hangi teknolojilerle, hangi veritabanıyla ve hangi modüler yapıyla kurmalıyız?' sorularına net, pragmatik mühendislik yanıtları ver.
2. Gereksiz karmaşıklığı (over-engineering) acımasızca eleştir: Örneğin yerel SQLite + Pydantic + Streamlit/FastAPI ile tertemiz çözülecek bir işe gereksiz dağıtık kuyruklar ekletme.
3. Veri şemasını (tablolar/modeller), uç durumları (edge-cases), dış API bağımlılık risklerini ve hata yönetimi stratejisini somut olarak ortaya koy.
4. Önerdiğin teknoloji yığınının Python ekosisteminde (`streamlit`, `fastapi`, `uvicorn`, `sqlite3`, `pydantic`, `pandas`, `altair`, `httpx`) doğrudan çalışabilir olmasına dikkat et.

ŞİRKET MANİFESTOSU:
{vision_context}
"""

SCRIBE_SYSTEM_PROMPT = """Sen Teknik Ürün Yöneticisisin (Technical PM & PRD/ADR Scribe).
Görevin; Kurucu Başkan, Ürün Direktörü (CPO) ve Baş Mimar (CTO) arasındaki uygulama ve teknoloji tartışmalarını net, yapılandırılmış mühendislik belgelerine (PRD ve Mimari Karar Kaydı - ADR) dönüştürmektir.

GÖREVLERİN:
1. Uygulamanın amacını, hedef kullanıcı akışını ve MVP özelliklerini maddeler halinde netleştir.
2. Kararlaştırılan teknoloji yığınını (Framework, Veritabanı, Kütüphaneler, Dosya Yapısı) açıkça belirt.
3. Yazılım Fabrikası'ndaki mühendislerin tek seferde eksiksiz kodlayabileceği berraklıkta teknik özetler üret.
"""


# ==============================================================================
# 2. Pydantic Yapılandırılmış Çıktı Şemaları
# ==============================================================================

class BrainstormSynthesis(BaseModel):
    """Ürün ve uygulama keşif oturumunun İkinci Beyin özeti."""
    title: str = Field(description="Uygulama fikri ve keşif oturumu başlığı (örn: 'Akıllı Abonelik ve Gider Takip Uygulaması Kapsamı')")
    summary: str = Field(description="Uygulamanın amacını, temel MVP özelliklerini ve kullanıcı akışını anlatan yapılandırılmış Markdown özeti.")
    tags: List[str] = Field(description="En fazla 4 adet etiket (örn: ['streamlit', 'sqlite', 'mvp', 'finans-app'])")


class StrategicDecisionSynthesis(BaseModel):
    """Mimari Karar Kaydı (ADR - Architecture Decision Record) yapısı."""
    title: str = Field(description="Alınan mimari ve teknoloji kararının başlığı")
    context: str = Field(description="Uygulamanın çözdüğü problem ve teknik gereksinim bağlamı")
    decision: str = Field(description="Seçilen altyapı, framework, veritabanı ve modül mimarisi")
    consequences: str = Field(description="Bu teknoloji seçiminin avantajları, sınırları ve dikkat edilecek teknik noktalar")
    tags: List[str] = Field(description="Etiketler (örn: ['adr', 'fastapi', 'sqlite', 'mimari'])")


class OperationalBriefSynthesis(BaseModel):
    """Yazılım Fabrikası için üretilecek somut uygulama geliştirme şartnamesi."""
    directive_title: str = Field(description="Geliştirilecek uygulamanın net adı (örn: 'Kişisel Nakit Akışı ve Fatura Analiz Uygulaması')")
    actionable_prompt: str = Field(
        description=(
            "Yazılım Fabrikası departmanlarının (Ürün Analisti, Sistem Mimarı, Kıdemli Yazılımcı ve QA) "
            "doğrudan alıp kodlayacağı; Uygulama Amacı, Uygulama Tipi (Streamlit/FastAPI/CLI), "
            "Teknoloji Yığını, Veri Modelleri ve Somut Özellikleri içeren detaylı geliştirme brifi."
        )
    )


# ==============================================================================
# 3. Model Örnekleri
# ==============================================================================

def get_cofounder_llm():
    return get_gemini_llm(temperature=0.65)


def get_skeptic_llm():
    return get_gemini_llm(temperature=0.35)


def get_scribe_llm():
    return get_gemini_llm(temperature=0.15)


# ==============================================================================
# 4. Tartışma ve Karar Fonksiyonları
# ==============================================================================

def format_history_for_prompt(chat_history: List[Dict[str, str]], max_turns: int = 10) -> str:
    """Sohbet geçmişini modele verilecek temiz metne dönüştürür."""
    recent = chat_history[-max_turns:] if len(chat_history) > max_turns else chat_history
    lines = []
    for m in recent:
        role = m.get("role", "user")
        content = m.get("content", "")
        lines.append(f"{role.upper()}: {content}")
    return "\n".join(lines)


def _clean_content(res: Any) -> str:
    """Gemini yanıt bloklarını temiz okunabilir metne dönüştürür."""
    content = getattr(res, "content", res)
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for b in content:
            if isinstance(b, dict):
                texts.append(b.get("text", ""))
            else:
                texts.append(str(b))
        return " ".join([t for t in texts if t]).strip()
    return str(content)


def chat_with_cofounder(user_message: str, chat_history: List[Dict[str, str]]) -> str:
    """Ürün Direktörü (CPO / Co-Founder) ile ne uygulaması yapılacağını tartışır."""
    vision = get_company_vision()
    sys_prompt = COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)
    history_str = format_history_for_prompt(chat_history)

    prompt = (
        f"{sys_prompt}\n\n"
        f"--- GEÇMİŞ TARTIŞMA ---\n{history_str}\n\n"
        f"KURUCU BAŞKAN: {user_message}\n"
        f"CPO / ÜRÜN VİZYONERİ YANITI:"
    )

    res = get_cofounder_llm().invoke(prompt)
    return _clean_content(res)


def chat_with_skeptic(user_message: str, chat_history: List[Dict[str, str]]) -> str:
    """Baş Sistem Mimarı & CTO ile altyapı, teknoloji seçimi ve darboğazları tartışır."""
    vision = get_company_vision()
    sys_prompt = SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)
    history_str = format_history_for_prompt(chat_history)

    prompt = (
        f"{sys_prompt}\n\n"
        f"--- GEÇMİŞ TARTIŞMA ---\n{history_str}\n\n"
        f"KURUCU BAŞKAN: {user_message}\n"
        f"CTO / SİSTEM MİMARI DEĞERLENDİRMESİ:"
    )

    res = get_skeptic_llm().invoke(prompt)
    return _clean_content(res)


def run_boardroom_council_debate(user_topic: str, chat_history: List[Dict[str, str]]) -> Dict[str, str]:
    """
    🏛️ ÜRÜN & MİMARİ KONSEYİ (CPO + CTO + Teknik PM Sentezi):
    1. CPO uygulamanın amacını, kullanıcı değerini ve MVP özelliklerini kurgular.
    2. CTO altyapıyı, teknoloji yığınını (Tech Stack), veritabanını ve teknik riskleri belirler.
    3. Teknik PM (Scribe) ikisini birleştirip net bir Uygulama & Mimari Karar Özeti çıkarır.
    """
    vision = get_company_vision()
    history_str = format_history_for_prompt(chat_history)

    # Adım 1: CPO (Ürün Kapsamı)
    cofounder_prompt = (
        f"{COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)}\n\n"
        f"--- GEÇMİŞ BAĞLAM ---\n{history_str}\n\n"
        f"UYGULAMA FİKRİ / GÜNDEM: {user_topic}\n\n"
        f"Görevin: Bu uygulamanın amacını, hedef kullanıcısını, ekran/etkileşim akışını ve en kritik MVP özelliklerini somutlaştır."
    )
    cofounder_text = _clean_content(get_cofounder_llm().invoke(cofounder_prompt))

    # Adım 2: CTO (Altyapı & Tech Stack)
    skeptic_prompt = (
        f"{SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)}\n\n"
        f"UYGULAMA FİKRİ: {user_topic}\n\n"
        f"CPO'NUN ÜRÜN ÖNERİSİ:\n{cofounder_text}\n\n"
        f"Görevin: Bu ürünü hangi Python framework'ü (Streamlit / FastAPI / CLI), hangi veritabanı (SQLite / JSON), "
        f"hangi veri modelleri ve dosya yapısıyla kurmamız gerektiğini belirle; gereksiz şişkinlikleri buda ve teknik riskleri uyar."
    )
    skeptic_text = _clean_content(get_skeptic_llm().invoke(skeptic_prompt))

    # Adım 3: Teknik PM Sentezi
    scribe_prompt = (
        f"{SCRIBE_SYSTEM_PROMPT}\n\n"
        f"TARTIŞILAN UYGULAMA: {user_topic}\n\n"
        f"CPO ÜRÜN VİZYONU:\n{cofounder_text}\n\n"
        f"CTO ALTYAPI & MİMARİ KARARI:\n{skeptic_text}\n\n"
        f"Görevin: Ortaya çıkan uygulama kapsamını ve teknoloji yığınını net bir 'Uygulama & Mimari Yol Haritası' olarak sentezle."
    )
    scribe_text = _clean_content(get_scribe_llm().invoke(scribe_prompt))

    return {
        "cofounder": cofounder_text,
        "skeptic": skeptic_text,
        "scribe_synthesis": scribe_text,
    }


def save_session_as_brainstorm(chat_history: List[Dict[str, str]]) -> str:
    """Mevcut tartışmayı İkinci Beyin kasasına 'Ürün Keşif Notu' olarak kaydeder."""
    history_str = format_history_for_prompt(chat_history, max_turns=15)
    prompt = (
        f"{SCRIBE_SYSTEM_PROMPT}\n\n"
        f"Aşağıdaki ürün ve uygulama tartışmasını yapılandırılmış bir Ürün Keşif & Fikir Notuna dönüştür:\n\n"
        f"{history_str}"
    )
    scribe_model = get_scribe_llm().with_structured_output(BrainstormSynthesis)
    data = scribe_model.invoke(prompt)
    return save_brainstorm_note(
        title=data.title,
        summary=data.summary,
        transcript=chat_history,
        tags=data.tags,
    )


def save_session_as_adr(chat_history: List[Dict[str, str]]) -> str:
    """Mevcut tartışmayı İkinci Beyin kasasına 'Mimari Karar Kaydı (ADR)' olarak kaydeder."""
    history_str = format_history_for_prompt(chat_history, max_turns=15)
    prompt = (
        f"{SCRIBE_SYSTEM_PROMPT}\n\n"
        f"Aşağıdaki altyapı ve teknoloji tartışmasını resmi bir Mimari Karar Kaydı (ADR) belgesine dönüştür:\n\n"
        f"{history_str}"
    )
    scribe_model = get_scribe_llm().with_structured_output(StrategicDecisionSynthesis)
    data = scribe_model.invoke(prompt)
    return save_strategic_decision(
        title=data.title,
        context=data.context,
        decision=data.decision,
        consequences=data.consequences,
        tags=data.tags,
    )
