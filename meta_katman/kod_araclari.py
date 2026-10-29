"""
================================================================================
🛠️ KURUMSAL DOSYA & KOD GÜVENLİK MOTORU (SWE-AGENT TOOLSET)
================================================================================
Devin, Aider ve Claude Engineer standartlarında;
- Path Traversal korumalı Sandbox dosya okuma/yazma,
- Abstract Syntax Tree (AST) ve py_compile ile sıfır sözdizimi hatası denetimi,
- Otomatik zaman damgalı snapshot/yedekleme ve tek tıkla rollback,
- Atomik dosya değiştirme (veri kaybı ve bozulma koruması),
- Standart Unified Diff üretimi.
================================================================================
"""

import os
import sys
import ast
import difflib
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# Kök dizin tespiti
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(PROJECT_ROOT, "meta_bellek", ".backups")


# ==============================================================================
# 1. Sandbox ve Güvenlik Duvarı (Workspace Security)
# ==============================================================================
class WorkspaceSecurity:
    """Ajanın yalnızca izin verilen proje sınırları içinde güvenle çalışmasını sağlar."""
    ALLOWED_ROOT = os.path.abspath(PROJECT_ROOT)
    
    # Güvenlik gereği asla ajan tarafından değiştirilmeyecek hassas dosyalar
    FORBIDDEN_FILES = {
        ".env",
        ".env.example",
        ".git",
        ".gitignore"
    }

    @classmethod
    def validate_path(cls, rel_or_abs_path: str) -> str:
        """
        Verilen yolun proje kök dizini içinde olduğunu ve yasaklı dosya olmadığını
        doğrular. Geçerliyse mutlak yolu (canonical absolute path) döndürür.
        """
        if os.path.isabs(rel_or_abs_path):
            abs_path = os.path.abspath(rel_or_abs_path)
        else:
            abs_path = os.path.abspath(os.path.join(cls.ALLOWED_ROOT, rel_or_abs_path))

        # Path traversal saldırısı kontrolü (örn: ../../Windows)
        if not abs_path.startswith(cls.ALLOWED_ROOT):
            raise PermissionError(
                f"GÜVENLİK İHLALİ: '{rel_or_abs_path}' proje sınırları ({cls.ALLOWED_ROOT}) dışındadır!"
            )

        filename = os.path.basename(abs_path)
        if filename in cls.FORBIDDEN_FILES:
            raise PermissionError(
                f"GÜVENLİK İHLALİ: '{filename}' hassas bir yapılandırma/anahtar dosyasıdır ve ajan tarafından değiştirilemez!"
            )

        return abs_path


# ==============================================================================
# 2. Otomatik Snapshot ve Rollback Yöneticisi (Backup Manager)
# ==============================================================================
class CodeSnapshotManager:
    """Her dosya yazımından önce otomatik yedek alır ve geri alma (rollback) sağlar."""

    @classmethod
    def ensure_backup_dir(cls):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    @classmethod
    def create_snapshot(cls, target_path: str) -> Optional[str]:
        """Hedef dosyanın zaman damgalı .bak kopyasını oluşturur."""
        cls.ensure_backup_dir()
        abs_target = WorkspaceSecurity.validate_path(target_path)

        if not os.path.exists(abs_target):
            return None

        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(abs_target)
        backup_filename = f"{now_str}_{base_name}.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        shutil.copy2(abs_target, backup_path)
        return backup_path

    @classmethod
    def list_snapshots(cls) -> List[Dict[str, str]]:
        """Mevcut tüm kod yedeklerini listeler."""
        cls.ensure_backup_dir()
        snapshots = []
        for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if f.endswith(".bak"):
                p = os.path.join(BACKUP_DIR, f)
                snapshots.append({
                    "filename": f,
                    "path": p,
                    "size_kb": round(os.path.getsize(p) / 1024, 2),
                    "timestamp": datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
                })
        return snapshots

    @classmethod
    def restore_snapshot(cls, snapshot_filename_or_path: str, target_rel_path: str) -> bool:
        """Yedek dosyasını hedef dosyanın üzerine geri yükler (Rollback)."""
        cls.ensure_backup_dir()
        if os.path.isabs(snapshot_filename_or_path):
            snap_path = snapshot_filename_or_path
        else:
            snap_path = os.path.join(BACKUP_DIR, snapshot_filename_or_path)

        if not os.path.exists(snap_path):
            raise FileNotFoundError(f"Yedek dosyası bulunamadı: {snap_path}")

        abs_target = WorkspaceSecurity.validate_path(target_rel_path)
        shutil.copy2(snap_path, abs_target)
        return True


# ==============================================================================
# 3. Kod Kalite ve Sözdizimi Denetim Motoru (AST & Quality Engine)
# ==============================================================================
class CodeQualityEngine:
    """Python kodlarının sözdizimini diske yazılmadan önce kesin olarak doğrular."""

    @classmethod
    def verify_python_syntax(cls, code_str: str) -> Tuple[bool, Optional[str]]:
        """
        Python kodunun geçerli bir Abstract Syntax Tree (AST) oluşturup
        oluşturmadığını denetler. Hata varsa tam hata satırını ve mesajını döner.
        """
        try:
            ast.parse(code_str)
            return True, None
        except SyntaxError as e:
            error_details = (
                f"Sözdizimi Hatası (SyntaxError): '{e.msg}' "
                f"[Satır: {e.lineno}, Sütun: {e.offset}]"
            )
            if e.text:
                error_details += f"\nHatalı Kod Satırı: {e.text.strip()}"
            return False, error_details
        except Exception as e:
            return False, f"Beklenmeyen Ayrıştırma Hatası: {str(e)}"

    @classmethod
    def generate_unified_diff(cls, old_content: str, new_content: str, file_name: str = "target_file") -> str:
        """İki metin arasındaki standart renkli Unified Diff çıktısını üretir."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_name} (Mevcut)",
            tofile=f"b/{file_name} (Önerilen)",
            lineterm=""
        )
        return "".join(diff)

    @classmethod
    def apply_atomic_write(cls, target_path: str, new_content: str, take_backup: bool = True) -> Dict[str, any]:
        """
        Dosyayı atomik olarak diske yazar.
        1. Güvenlik doğrulaması yapar.
        2. Python dosyasıysa AST sözdizimini doğrular (hata varsa yazmayı durdurur).
        3. Otomatik .bak yedeği alır.
        4. Geçici .tmp dosyasına yazıp os.replace ile anında değiştirir (bozulma önleme).
        """
        abs_target = WorkspaceSecurity.validate_path(target_path)
        
        # Python dosyasıysa sözdizimi denetimi
        if abs_target.endswith(".py"):
            is_valid, error = cls.verify_python_syntax(new_content)
            if not is_valid:
                raise ValueError(f"KOD YAZIMI ENGELLENDİ! Sözdizimi hatası tespit edildi:\n{error}")

        backup_file = None
        if take_backup and os.path.exists(abs_target):
            backup_file = CodeSnapshotManager.create_snapshot(abs_target)

        # Atomik yazım (.tmp -> hedef)
        tmp_target = abs_target + ".tmp"
        try:
            with open(tmp_target, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_target, abs_target)
        except Exception as e:
            if os.path.exists(tmp_target):
                os.remove(tmp_target)
            raise IOError(f"Dosya diske yazılırken hata oluştu: {e}")

        return {
            "status": "SUCCESS",
            "file_path": abs_target,
            "rel_path": os.path.relpath(abs_target, PROJECT_ROOT),
            "backup_path": backup_file,
            "bytes_written": len(new_content.encode("utf-8"))
        }


# ==============================================================================
# 4. Proje Dosya Gezgini ve Arama (Workspace Inspector)
# ==============================================================================
class CodeInspector:
    """Çalışma alanındaki dosyaları güvenle okuma, listeleme ve arama aracı."""

    IGNORED_DIRS = {".venv", "__pycache__", ".git", ".idea", ".vscode", ".pytest_cache", ".backups"}

    @classmethod
    def read_workspace_file(cls, rel_path: str, start_line: int = 1, end_line: Optional[int] = None) -> Tuple[str, int]:
        """Dosyayı okur, toplam satır sayısını ve seçili satır aralığını döndürür."""
        abs_path = WorkspaceSecurity.validate_path(rel_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {rel_path}")

        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        if end_line is None or end_line > total_lines:
            end_line = total_lines

        selected_lines = lines[start_line - 1 : end_line]
        return "".join(selected_lines), total_lines

    @classmethod
    def list_project_files(cls, extension: Optional[str] = None) -> List[str]:
        """Proje kök dizinindeki düzenlenebilir dosyaları listeler."""
        valid_files = []
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in cls.IGNORED_DIRS]
            for file in files:
                if file in WorkspaceSecurity.FORBIDDEN_FILES:
                    continue
                if extension and not file.endswith(extension):
                    continue
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, PROJECT_ROOT)
                valid_files.append(rel_p)
        return sorted(valid_files)

    @classmethod
    def search_in_codebase(cls, query: str, extension: Optional[str] = None) -> List[Dict[str, any]]:
        """Proje kod tabanında arama yapar ve eşleşen satırları getirir."""
        matches = []
        files = cls.list_project_files(extension)
        query_lower = query.lower()

        for rel_p in files:
            abs_p = os.path.join(PROJECT_ROOT, rel_p)
            try:
                with open(abs_p, "r", encoding="utf-8", errors="replace") as f:
                    for line_no, line in enumerate(f, start=1):
                        if query_lower in line.lower():
                            matches.append({
                                "file": rel_p,
                                "line_no": line_no,
                                "line_content": line.strip()
                            })
            except Exception:
                continue
        return matches
