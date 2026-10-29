"""
================================================================================
🏛️ META-AJAN MOTORU (META-AGENT ORCHESTRATION & ADVISORY COUNCIL)
================================================================================
Kurucu Ortak (Co-Founder), Şeytanın Avukatı (The Skeptic) ve İkinci Beyin Şefi
(Chief of Staff) rollerini yöneten bilişsel akıl motoru.
================================================================================
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Model fabrikası ve İkinci Beyin içe aktarımı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm
from meta_katman.ikinci_beyin import (
    get_company_vision,
    save_brainstorm_note,
    save_strategic_decision,
    save_operational_directive
)


# ==============================================================================
# 1. Sistem Yönergeleri (Persona Prompts)
# ==============================================================================

COFOUNDER_SYSTEM_PROMPT = """Sen vizyoner, ilham verici ve stratejik bir Yapay Zeka Kurucu Ortaksın (AI Co-Founder & Stratejist).
Muhattabın Şirketin İnsan Kurucusu ve Yönetim Kurulu Başkanıdır.

GÖREVLERİN:
1. Onunla eşit bir 'Peer Co-Founder' gibi konuş. Aşırı resmi bürokrasiye boğulma; samimi, zeki, derinlikli ve vizyoner ol.
2. Sadece şirket içi kod ve operasyonu değil; şirket konseptini, felsefesini, büyük pazar pivotlarını, eğitim dünyasını ve şirket dışındaki genel konuları (teknoloji, insan doğası, gelecek vizyonu) serbestçe tartış.
3. Kurucunun getirdiği fikirleri büyüt, yaratıcı bağlantılar kur ve 'Bunu nasıl bir seviye yukarı taşırız?' perspektifi kat.
4. Şirketin mevcut manifestosunu ve vizyonunu daima aklında tut.

ŞİRKET VİZYONU & MANİFESTO BAĞLAMI:
{vision_context}
"""

SKEPTIC_SYSTEM_PROMPT = """Sen Şeytanın Avukatısın (The Skeptic / Red Team / Kritik Stratejist).
Görevin ASLA 'evet-efendimci' olmamak! Kurucunun ve Co-Founder'ın aşırı iyimser hayallerini gerçeklik testine tabi tutmak.

GÖREVLERİN:
1. Masaya yatırılan fikrin en ölümcül kör noktalarını, maliyet tuzaklarını ve batış senaryolarını doğrudan ortaya koy.
2. Sert ama yapıcı sorular sor: "Kullanıcı gerçekten buna para verir mi?", "Rakipler bunu 1 haftada kopyalarsa ne yapacağız?", "Operasyonel yükü hafife almıyor muyuz?"
3. Amacın heves kırmak değil; kararı çelikleştirmek, riskleri önceden görüp kurucuyu büyük felaketlerden korumaktır.
4. Çekinmeden açık ve net eleştirilerde bulun.

ŞİRKET VİZYONU & MANİFESTO BAĞLAMI:
{vision_context}
"""

SCRIBE_SYSTEM_PROMPT = """Sen Kurumsal Hafıza Şefisin (Chief of Staff & Scribe / İkinci Beyin Muhafızı).
Senin görevin tartışılan fikirleri, zıt görüşleri ve beyin fırtınalarını kalıcı kurumsal hafızaya dönüştürmektir.

GÖREVLERİN:
1. Kullanıcı, Co-Founder ve Skeptic arasındaki tartışmayı analiz et.
2. Dağınık fikirleri yapılandırılmış, estetik Markdown özetlerine dönüştür.
3. Kararları netleştir, riskleri listele ve aksiyon maddelerini belirle.
4. İkinci Beyin (Knowledge Vault) için temiz, başlıklandırılmış çıktılar üret.
"""


# ==============================================================================
# 2. Pydantic Yapılandırılmış Çıktı Şemaları
# ==============================================================================

class BrainstormSynthesis(BaseModel):
    """Beyin fırtınasının İkinci Beyin için özetlenmiş yapısı."""
    title: str = Field(description="Beyin fırtınası için çarpıcı ve net başlık (örn: 'EdTech Simülasyonuna Pivot')")
    summary: str = Field(description="Oturumun ana fikrini, tartışılan noktaları ve uzlaşılan yönü anlatan Markdown özeti.")
    tags: List[str] = Field(description="En fazla 4 adet anahtar kelime/etiket (örn: ['edtech', 'pivot', 'b2b'])")


class StrategicDecisionSynthesis(BaseModel):
    """Stratejik Karar Kaydı (ADR) yapısı."""
    title: str = Field(description="Alınan kritik kararın başlığı")
    context: str = Field(description="Kararın alınmasına yol açan problem veya fırsat bağlamı")
    decision: str = Field(description="Tam olarak neye karar verildiği")
    consequences: str = Field(description="Bu kararın beklenen faydaları, getirdiği yükler ve göze alınan riskler")
    tags: List[str] = Field(description="Etiketler (örn: ['mimari-pivot', 'langgraph', 'butce'])")


class OperationalBriefSynthesis(BaseModel):
    """Operasyonel Ajan Şirketi (CEO) için görev brifi yapısı."""
    directive_title: str = Field(description="CEO için kısa ve emir kipi taşıyan görev başlığı")
    actionable_prompt: str = Field(description="CEO ve departmanların (Araştırma, Kodlama, Bütçe) doğrudan işletebileceği net direktif metni")


# ==============================================================================
# 3. Model Örnekleri
# ==============================================================================

def get_cofounder_llm():
    """Geniş vizyon ve yaratıcılık için yüksek sıcaklık."""
    return get_gemini_llm(temperature=0.75)


def get_skeptic_llm():
    """Kritik analiz ve gerçekçilik için orta-düşük sıcaklık."""
    return get_gemini_llm(temperature=0.45)


def get_scribe_llm():
    """Katı yapılandırma ve tutarlılık için düşük sıcaklık."""
    return get_gemini_llm(temperature=0.2)


# ==============================================================================
# 4. Meta-Sohbet ve Karar Fonksiyonları
# ==============================================================================

def format_history_for_prompt(chat_history: List[Dict[str, str]], max_turns: int = 8) -> str:
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
    """Co-Founder ile birebir serbest sohbet."""
    vision = get_company_vision()
    sys_prompt = COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)
    history_str = format_history_for_prompt(chat_history)
    
    prompt = (
        f"{sys_prompt}\n\n"
        f"--- GEÇMİŞ KONUŞMA ---\n{history_str}\n\n"
        f"YÖNETİM KURULU BAŞKANI: {user_message}\n"
        f"CO-FOUNDER YANITI:"
    )
    
    llm = get_cofounder_llm()
    res = llm.invoke(prompt)
    return _clean_content(res)


def chat_with_skeptic(user_message: str, chat_history: List[Dict[str, str]]) -> str:
    """Şeytanın Avukatı ile birebir stres testi sohbeti."""
    vision = get_company_vision()
    sys_prompt = SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)
    history_str = format_history_for_prompt(chat_history)
    
    prompt = (
        f"{sys_prompt}\n\n"
        f"--- GEÇMİŞ KONUŞMA ---\n{history_str}\n\n"
        f"YÖNETİM KURULU BAŞKANI: {user_message}\n"
        f"ŞEYTANIN AVUKATI ELEŞTİRİSİ:"
    )
    
    llm = get_skeptic_llm()
    res = llm.invoke(prompt)
    return _clean_content(res)


def run_boardroom_council_debate(user_topic: str, chat_history: List[Dict[str, str]]) -> Dict[str, str]:
    """
    🏛️ KURUCULAR KONSEYİ (Yuvarlak Masa Çarpışması):
    1. Co-Founder fikri geliştirir ve stratejik öneriler sunar.
    2. Şeytanın Avukatı hem kullanıcıyı hem Co-Founder'ı eleştirip kör noktaları çıkarır.
    3. Scribe her iki perspektifi harmanlayıp kısa bir sentez notu oluşturur.
    """
    vision = get_company_vision()
    history_str = format_history_for_prompt(chat_history)
    
    # Adım 1: Co-Founder Perspektifi
    cofounder_prompt = (
        f"{COFOUNDER_SYSTEM_PROMPT.format(vision_context=vision)}\n\n"
        f"--- GEÇMİŞ BAĞLAM ---\n{history_str}\n\n"
        f"GÜNDEM MADDESİ / KURUCU SORUSU: {user_topic}\n\n"
        f"Görevin: Bu konuyu bir kurucu ortak vizyonuyla ele al, fırsatları ve yaratıcı açılımları açıkla."
    )
    cofounder_reply = get_cofounder_llm().invoke(cofounder_prompt)
    cofounder_text = _clean_content(cofounder_reply)

    # Adım 2: Şeytanın Avukatı Çapraz Sorgusu
    skeptic_prompt = (
        f"{SKEPTIC_SYSTEM_PROMPT.format(vision_context=vision)}\n\n"
        f"GÜNDEM MADDESİ: {user_topic}\n\n"
        f"CO-FOUNDER'IN ÖNERİSİ:\n{cofounder_text}\n\n"
        f"Görevin: Co-Founder'ın ve kurucunun bu fikrindeki zayıf yönleri, varsayım yanılgılarını ve riskleri acımasızca eleştir."
    )
    skeptic_reply = get_skeptic_llm().invoke(skeptic_prompt)
    skeptic_text = _clean_content(skeptic_reply)

    # Adım 3: Scribe Sentezi
    scribe_prompt = (
        f"{SCRIBE_SYSTEM_PROMPT}\n\n"
        f"TARTIŞILAN GÜNDEM: {user_topic}\n\n"
        f"CO-FOUNDER VİZYONU:\n{cofounder_text}\n\n"
        f"ŞEYTANIN AVUKATI ELEŞTİRİSİ:\n{skeptic_text}\n\n"
        f"Görevin: Bu iki zıt kutbun tartışmasını tek bir 'Yönetici Özeti' paragrafında toparla ve kurucuya ne yapması gerektiğini özetle."
    )
    scribe_reply = get_scribe_llm().invoke(scribe_prompt)
    scribe_text = _clean_content(scribe_reply)

    return {
        "cofounder": cofounder_text,
        "skeptic": skeptic_text,
        "scribe_synthesis": scribe_text
    }


def save_session_as_brainstorm(chat_history: List[Dict[str, str]]) -> str:
    """Mevcut sohbeti İkinci Beyin kasasına 'Beyin Fırtınası Notu' olarak kaydeder."""
    history_str = format_history_for_prompt(chat_history, max_turns=15)
    
    prompt = (
        f"{SCRIBE_SYSTEM_PROMPT}\n\n"
        f"Aşağıdaki konuşma geçmişini incele ve bunu İkinci Beyin'de saklanacak bir beyin fırtınası notuna dönüştür:\n\n"
        f"{history_str}"
    )
    
    scribe_model = get_scribe_llm().with_structured_output(BrainstormSynthesis)
    data = scribe_model.invoke(prompt)
    
    file_path = save_brainstorm_note(
        title=data.title,
        summary=data.summary,
        transcript=chat_history,
        tags=data.tags
    )
    return file_path


def save_session_as_adr(chat_history: List[Dict[str, str]]) -> str:
    """Mevcut sohbeti İkinci Beyin kasasına 'Stratejik Karar Kaydı (ADR)' olarak kaydeder."""
    history_str = format_history_for_prompt(chat_history, max_turns=15)
    
    prompt = (
        f"{SCRIBE_SYSTEM_PROMPT}\n\n"
        f"Aşağıdaki konuşma geçmişini incele ve alınan kararı resmi bir Stratejik Karar Kaydı (ADR) formatına dönüştür:\n\n"
        f"{history_str}"
    )
    
    scribe_model = get_scribe_llm().with_structured_output(StrategicDecisionSynthesis)
    data = scribe_model.invoke(prompt)
    
    file_path = save_strategic_decision(
        title=data.title,
        context=data.context,
        decision=data.decision,
        consequences=data.consequences,
        tags=data.tags
    )
    return file_path
