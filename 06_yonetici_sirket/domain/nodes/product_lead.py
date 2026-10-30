"""
Product Lead Node (CPO / Co-Founder).
Responsible for Application Scope, User Flow, Seed Data, and PRD Specification.
"""

import sys
from pathlib import Path
from langchain_core.messages import AIMessage
from rich.console import Console

_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from model_factory import get_gemini_llm
from domain.state import CompanyState
from domain.schemas import PRDSpecOutput
from domain.utils import get_clean_user_directive, append_log

console = Console(force_terminal=False, legacy_windows=False)


def product_lead_node(state: CompanyState) -> dict:
    """CPO node generates PRD specification."""
    console.print("\n[bold yellow]💡 [DEPARTMAN 1: ÜRÜN & KAPSAM LİDERİ (CPO)] PRD hazırlanıyor...[/bold yellow]")

    user_directive = get_clean_user_directive(state)
    founder_feedback = state.get("founder_feedback")

    prompt = f"""Sen vizyoner, pratik ve ürün odaklı bir Baş Ürün Liderisin (CPO / Product Lead).
Şirketimiz teorik raporlar yazan bir danışmanlık firması DEĞİL; doğrudan çalışan uygulamalar geliştiren bir **Yazılım Evi ve Uygulama Stüdyosudur**.

GÖREVİN:
Kullanıcının direktifini incele; kullanıcı için keskin, odaklı ve hemen geliştirilebilir bir MVP Ürün Şartnamesi (PRD) hazırla.

KURUCU BAŞKAN DİREKTİFİ:
{user_directive}
{"KURUCU REVİZYON NOTU: " + founder_feedback if founder_feedback else ""}

KURALLAR:
1. Uygulama tipi için: Görsel kullanıcı etkileşimi ve kontrol panelleri için 'Streamlit Web App', dış sistemlerin bağlanacağı API için 'FastAPI REST Service', komut satırı aracı için 'CLI & Automation Tool' seç.
2. 'app_slug' alanını Türkçe karaktersiz, küçük harfli ve alt çizgili güvenli bir klasör adı yap (Örn: 'abonelik_takipcisi', 'stok_yonetim_api').
3. Kullanıcının ilk açılışta boş ekran görmemesi için zengin başlangıç verilerini (seed data) mutlaka tanımla.
4. Kapsamı şişirme, tek seferde kodlanıp başarıyla çalıştırılabilecek gerçekçi bir MVP belirle.
"""
    llm = get_gemini_llm(temperature=0.3)
    structured_cpo = llm.with_structured_output(PRDSpecOutput)
    res: PRDSpecOutput = structured_cpo.invoke([AIMessage(content=prompt)])

    console.print(f"  [green]✔ PRD Tamamlandı:[/green] {res.app_name} ({res.app_type})")

    return {
        "app_name": res.app_name,
        "app_slug": res.app_slug,
        "app_type": res.app_type,
        "purpose_summary": res.purpose_summary,
        "core_features": res.core_features,
        "prd_spec": res.full_prd_markdown,
        "founder_feedback": None,
        "feedback_target": None,
        "transition_log": append_log(
            state, "Product_Lead", f"PRD hazırlandı: {res.app_name} ({res.app_type})", "Studio_Director"
        )
    }
