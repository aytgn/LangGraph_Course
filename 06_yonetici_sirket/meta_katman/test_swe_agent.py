"""
================================================================================
🧪 OTONOM YAZILIM MÜHENDİSİ (SWE-AGENT) DOĞRULAMA TESTLERİ
================================================================================
Sandbox güvenliği, AST denetimi, Snapshot/Rollback ve Otonom Kodlayıcı döngüsü.
================================================================================
"""

import os
import sys

# Windows UTF-8 desteği
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Dizin ayarı
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from meta_katman.kod_araclari import (
    WorkspaceSecurity,
    CodeSnapshotManager,
    CodeQualityEngine,
    CodeInspector
)
from meta_katman.otonom_kodlayici import (
    plan_and_generate_code_patch,
    execute_approved_code_patch,
    rollback_code_change
)

def test_swe_architecture():
    print("=" * 70)
    print("🚀 SWE-AGENT MİMARİ DOĞRULAMA TESTİ BAŞLATILIYOR")
    print("=" * 70)

    # 1. GÜVENLİK VE SANDBOX TESTLERİ
    print("\n1. Sandbox & Güvenlik Duvarı Test Ediliyor...")
    
    # 1.1 Yasaklı .env dosyası testi
    try:
        WorkspaceSecurity.validate_path(".env")
        assert False, "HATA: .env dosyasının değiştirilmesine izin verildi!"
    except PermissionError as e:
        print(f"   [OK] .env koruması devrede: {e}")

    # 1.2 Path Traversal testi (Proje dışına çıkma)
    try:
        WorkspaceSecurity.validate_path("../../Windows/System32/calc.exe")
        assert False, "HATA: Proje dışına çıkılmasına izin verildi!"
    except PermissionError as e:
        print(f"   [OK] Path Traversal engellendi: {e}")

    # 2. AST VE SÖZDİZİMİ TESTLERİ
    print("\n2. AST ve Sözdizimi Denetim Motoru Test Ediliyor...")
    
    valid_code = "def topla(a: int, b: int) -> int:\n    return a + b\n"
    is_valid, err = CodeQualityEngine.verify_python_syntax(valid_code)
    assert is_valid and err is None, "Geçerli kod hatalı sayıldı!"
    print("   [OK] Geçerli Python kodu AST testinden başarıyla geçti.")

    invalid_code = "def bozuk_fonksiyon(a, b\n    return a +\n"
    is_valid_inv, err_inv = CodeQualityEngine.verify_python_syntax(invalid_code)
    assert not is_valid_inv and err_inv is not None, "Bozuk kod tespit edilemedi!"
    print(f"   [OK] Kasıtlı sözdizimi hatası tam satırıyla tespit edildi:\n        {err_inv.splitlines()[0]}")

    # 3. ATOMİK YAZMA VE SNAPSHOT/ROLLBACK TESTİ
    print("\n3. Atomik Yazma, Snapshot & Rollback Test Ediliyor...")
    dummy_file = os.path.join(project_root, "meta_katman", "temp_dummy_test.py")
    
    # Başlangıç dosyası oluştur
    CodeQualityEngine.apply_atomic_write(dummy_file, "# Versiyon 1\nval = 100\n", take_backup=False)
    assert os.path.exists(dummy_file), "Geçici test dosyası oluşturulamadı."
    print("   [OK] Versiyon 1 dosyası atomik olarak yazıldı.")

    # Versiyon 2 yazarken otomatik snapshot al
    write_res = CodeQualityEngine.apply_atomic_write(dummy_file, "# Versiyon 2\nval = 200\n", take_backup=True)
    assert write_res["backup_path"] is not None, "Yedek dosyası alınamadı!"
    print(f"   [OK] Versiyon 2 yazıldı, otomatik snapshot alındı: {os.path.basename(write_res['backup_path'])}")

    # Geri alma (Rollback) testi
    rollback_res = rollback_code_change(dummy_file)
    assert rollback_res is True, "Rollback başarısız oldu!"
    with open(dummy_file, "r", encoding="utf-8") as f:
        restored_content = f.read()
    assert "val = 100" in restored_content, "Rollback sonrası eski içeriğe dönülemedi!"
    print("   [OK] Rollback başarıyla çalıştı, dosya Versiyon 1'e geri döndü.")

    # 4. DIFF ÜRETİCİ TESTİ
    print("\n4. Renkli Unified Diff Üretici Test Ediliyor...")
    diff_output = CodeQualityEngine.generate_unified_diff(
        old_content="x = 10\ny = 20\n",
        new_content="x = 10\ny = 99\nz = 30\n",
        file_name="test.py"
    )
    assert "-y = 20" in diff_output and "+y = 99" in diff_output and "+z = 30" in diff_output
    print("   [OK] Unified Diff doğru satır silme (-) ve ekleme (+) işaretleriyle üretildi.")

    # Temizlik
    if os.path.exists(dummy_file):
        os.remove(dummy_file)

    print("\n" + "=" * 70)
    print("✅ TÜM SWE-AGENT ALTYAPI TESTLERİ 100% BAŞARIYLA TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    test_swe_architecture()
