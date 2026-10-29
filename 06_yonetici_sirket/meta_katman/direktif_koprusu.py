"""
================================================================================
🌉 ÜRÜN & MİMARİ ŞARTNAME KÖPRÜSÜ (PRODUCT-TO-ENGINEERING SPEC BRIDGE)
================================================================================
Ürün & Mimari Masası'nda tartışılan uygulama fikrini, amacını ve teknoloji
kararlarını; Otonom Yazılım Fabrikası'nın (PRD -> Mimari -> Kodlama -> QA)
doğrudan inşa edebileceği net mühendislik brifine dönüştürür.
================================================================================
"""

import os
import sys
from typing import List, Dict

_current_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_app_dir)
for _p in (_app_dir, _root_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from meta_katman.meta_motoru import (
    get_scribe_llm,
    OperationalBriefSynthesis,
    format_history_for_prompt,
)
from meta_katman.ikinci_beyin import save_operational_directive


def bridge_meta_to_operational_directive(chat_history: List[Dict[str, str]], custom_notes: str = "") -> Dict[str, str]:
    """
    Ürün ve teknoloji tartışmasını, Yazılım Fabrikası için somut bir
    Uygulama Geliştirme Şartnamesine dönüştürür.
    """
    history_str = format_history_for_prompt(chat_history, max_turns=14)

    prompt = (
        "Sen Teknik Ürün Yöneticisisin (Technical PM).\n"
        "Aşağıdaki ürün ve teknoloji tartışmasını inceleyerek Otonom Yazılım Fabrikası'na iletilecek "
        "net ve eksiksiz bir **Uygulama Geliştirme Şartnamesi** hazırla.\n\n"
        "Şartnamede şunlar açıkça yer almalıdır:\n"
        "1. Uygulamanın Adı ve Somut Amacı (Hangi problemi çözüyor?)\n"
        "2. Uygulama Türü ve Tercih Edilen Altyapı (Örn: Streamlit Web Uygulaması / FastAPI REST API / CLI Aracı, SQLite / JSON depolama)\n"
        "3. Uygulanacak Somut MVP Özellikleri ve Veri Akışı\n\n"
        f"--- TARTIŞMA GEÇMİŞİ ---\n{history_str}\n\n"
        f"--- EK TEKNİK NOTLAR ---\n{custom_notes}\n"
    )

    scribe_model = get_scribe_llm().with_structured_output(OperationalBriefSynthesis)
    brief = scribe_model.invoke(prompt)

    file_path = save_operational_directive(
        title=brief.directive_title,
        task_brief=brief.actionable_prompt,
    )

    return {
        "title": brief.directive_title,
        "directive_text": brief.actionable_prompt,
        "file_path": file_path,
    }
