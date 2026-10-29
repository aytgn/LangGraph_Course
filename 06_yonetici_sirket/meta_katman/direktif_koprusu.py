"""
================================================================================
🌉 DİREKTİF KÖPRÜSÜ (STRATEGIC DIRECTIVE BRIDGE)
================================================================================
Meta-Düzlemde (Kurucular Odası & İkinci Beyin) alınan stratejik ve felsefi
kararları, operasyonel çoklu ajan şirketinin (CEO, Araştırma, Mühendislik, Denetim)
hemen yürütebileceği somut görev briflerine dönüştüren köprü mekanizması.
================================================================================
"""

import os
import sys
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from meta_katman.meta_motoru import (
    get_scribe_llm,
    OperationalBriefSynthesis,
    format_history_for_prompt
)
from meta_katman.ikinci_beyin import save_operational_directive


def bridge_meta_to_operational_directive(chat_history: List[Dict[str, str]], custom_notes: str = "") -> Dict[str, str]:
    """
    Meta-Düzlem sohbetini veya kararını, operasyonel şirket CEO'sunun
    anlayacağı net bir yönetim kurulu direktifine dönüştürür.
    
    Döndürdüğü sözlük:
    {
        "title": "Görev Başlığı",
        "directive_text": "CEO'ya aktarılacak nihai görev metni",
        "file_path": "meta_bellek altındaki kaydedilmiş dosya yolu"
    }
    """
    history_str = format_history_for_prompt(chat_history, max_turns=12)

    prompt = (
        "Sen Yönetim Kurulu Genel Sekreterisin (Chief of Staff).\n"
        "Kurucular Odası'nda yapılan aşağıdaki stratejik tartışmayı ve kurucu notunu incele. "
        "Operasyonel Çoklu Ajan Şirketimizin CEO'suna (Supervisor Ajanı) iletilmek üzere "
        "net, aksiyon odaklı ve departmanların (Araştırma Departmanı pazar verisi toplayacak, "
        "Mühendislik Departmanı kod/mimari üretecek, Denetim Departmanı bütçe çıkaracak) "
        "çalıştırabileceği bir operasyonel görev direktifi hazırla.\n\n"
        f"--- TARTIŞMA GEÇMİŞİ ---\n{history_str}\n\n"
        f"--- KURUCU EK NOTU ---\n{custom_notes}\n"
    )

    scribe_model = get_scribe_llm().with_structured_output(OperationalBriefSynthesis)
    brief = scribe_model.invoke(prompt)

    # İkinci Beyin'e direktif olarak kaydet
    file_path = save_operational_directive(
        title=brief.directive_title,
        task_brief=brief.actionable_prompt
    )

    return {
        "title": brief.directive_title,
        "directive_text": brief.actionable_prompt,
        "file_path": file_path
    }
