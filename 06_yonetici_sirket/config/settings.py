"""
Config Layer for 06_yonetici_sirket
Centralized configuration, environment variables, filesystem paths, and defaults.
"""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class StudioConfig:
    """Enterprise Studio Configuration settings."""
    # Filesystem directories
    MODULE_ROOT: Path = Path(__file__).resolve().parent.parent
    PROJECT_ROOT: Path = MODULE_ROOT.parent
    
    OUTPUT_APPS_DIR: Path = MODULE_ROOT / "output_uygulamalar"
    VAULT_DIR: Path = MODULE_ROOT / "meta_bellek"
    DB_PATH: Path = MODULE_ROOT / "studio_apps.db"
    
    # Subdirectories in Vault
    VISION_FILE: Path = VAULT_DIR / "01_sirket_vizyonu.md"
    BRAINSTORM_DIR: Path = VAULT_DIR / "02_beyin_firtinasi_notlari"
    DECISIONS_DIR: Path = VAULT_DIR / "03_stratejik_kararlar"
    DIRECTIVES_DIR: Path = VAULT_DIR / "04_operasyonel_direktifler"
    BACKUP_DIR: Path = VAULT_DIR / ".backups"

    # Execution limits & defaults
    MAX_CYCLES: int = 12
    AST_MAX_FIX_ATTEMPTS: int = 3
    DEFAULT_TIMEOUT_SECONDS: int = 60
    
    def ensure_directories(self) -> None:
        """Ensure all required runtime directories exist."""
        for path in (
            self.OUTPUT_APPS_DIR,
            self.VAULT_DIR,
            self.BRAINSTORM_DIR,
            self.DECISIONS_DIR,
            self.DIRECTIVES_DIR,
            self.BACKUP_DIR,
        ):
            path.mkdir(parents=True, exist_ok=True)


# Global singleton configuration instance
config = StudioConfig()
config.ensure_directories()
