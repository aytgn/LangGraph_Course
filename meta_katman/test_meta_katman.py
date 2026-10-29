"""
Doğrulama Testi: Meta-Katman ve İkinci Beyin
"""
import os
import sys

# Windows konsol UTF-8 desteği
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Dizin ayarı
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from meta_katman.ikinci_beyin import (
    initialize_vault,
    get_company_vision,
    save_brainstorm_note,
    save_strategic_decision,
    save_operational_directive,
    list_vault_documents
)

def test_vault():
    print("1. İkinci Beyin Kasası Başlatılıyor...")
    initialize_vault()
    
    vision = get_company_vision()
    assert "ŞİRKET VİZYONU" in vision, "Vizyon belgesi okunamadı!"
    print("   [OK] Şirket vizyonu başarıyla okundu.")

    # Beyin fırtınası testi
    sample_chat = [
        {"role": "user", "content": "Ajan şirketine EdTech simülasyonu eklemeliyiz."},
        {"role": "Co-Founder", "content": "Harika bir fikir, üniversiteler ve kurumsal şirketler için laboratuvar olur."},
        {"role": "Skeptic", "content": "B2C satış döngüsü uzun olabilir, B2B kurumsal bootcamp hedefleyelim."}
    ]
    bf_path = save_brainstorm_note(
        title="Test EdTech Fikri",
        summary="EdTech ve bootcamp odaklı ajan laboratuvarı tartışıldı.",
        transcript=sample_chat,
        tags=["test", "edtech"]
    )
    assert os.path.exists(bf_path), f"Dosya oluşturulamadı: {bf_path}"
    print(f"   [OK] Beyin fırtınası kaydedildi: {os.path.basename(bf_path)}")

    # ADR testi
    adr_path = save_strategic_decision(
        title="B2B EdTech Odaklanması",
        context="B2C öğrenci edinme maliyeti yüksek.",
        decision="Bootcamp ve şirket içi Ar-Ge ekiplerine odaklanılacak.",
        consequences="Daha yüksek sepet tutarı, daha kısa satış döngüsü.",
        tags=["adr", "b2b"]
    )
    assert os.path.exists(adr_path), f"ADR oluşturulamadı: {adr_path}"
    print(f"   [OK] Stratejik Karar (ADR) kaydedildi: {os.path.basename(adr_path)}")

    # Direktif testi
    dir_path = save_operational_directive(
        title="EdTech Pazar Analizi",
        task_brief="Pazar araştırması departmanı kurumsal bootcamp talebini incelesin."
    )
    assert os.path.exists(dir_path), f"Direktif kaydedilemedi: {dir_path}"
    print(f"   [OK] Operasyonel Direktif kaydedildi: {os.path.basename(dir_path)}")

    # Listeleme
    docs = list_vault_documents()
    print(f"   [OK] Kasada toplam {len(docs)} belge listelendi:")
    for d in docs:
        print(f"        - [{d['category']}] {d['name']} ({d['size_kb']} KB)")

    print("\nTÜM İKİNCİ BEYİN TESTLERİ BAŞARIYLA TAMAMLANDI! ✅")

if __name__ == "__main__":
    test_vault()
