"""
Config Layer for 06_yonetici_sirket
Centralized configuration, environment variables, filesystem paths, and defaults.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 I/O encoding across Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


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
    MAX_CYCLES: int = 14
    MAX_QA_SELF_HEAL_RETRIES: int = 2
    DEFAULT_TIMEOUT_SECONDS: int = 60

    def initialize(self) -> None:
        """Load root .env and ensure all required runtime directories exist."""
        env_file = self.PROJECT_ROOT / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=False)
        else:
            load_dotenv()

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
config.initialize()
