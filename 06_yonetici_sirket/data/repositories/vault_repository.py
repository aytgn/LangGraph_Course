"""
Vault Repository - Full CRUD for Knowledge Base (Second Brain / meta_bellek).
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from config.settings import config
from data.models import VaultItem


class VaultRepository:
    """Manages markdown knowledge files in meta_bellek with full CRUD."""

    def __init__(self, vault_dir: Optional[Path] = None):
        self.vault_dir = vault_dir or config.VAULT_DIR
        self.vision_file = config.VISION_FILE
        self.brainstorm_dir = config.BRAINSTORM_DIR
        self.decisions_dir = config.DECISIONS_DIR
        self.directives_dir = config.DIRECTIVES_DIR

    def get_vision(self) -> str:
        """Read company vision manifesto."""
        if not self.vision_file.exists():
            return "# 🌟 Otonom Yazılım Evi Manifestosu\n(Henüz oluşturulmadı)"
        try:
            return self.vision_file.read_text(encoding="utf-8")
        except Exception as e:
            return f"# Şirket Vizyonu\n(Okuma hatası: {e})"

    def update_vision(self, content: str) -> bool:
        """Update company vision manifesto."""
        try:
            self.vision_file.parent.mkdir(parents=True, exist_ok=True)
            self.vision_file.write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False

    def read_item(self, filepath: str) -> str:
        """Read full markdown text of a vault item safely."""
        p = Path(filepath)
        if p.exists() and p.is_file() and str(p.resolve()).startswith(str(self.vault_dir.resolve())):
            return p.read_text(encoding="utf-8", errors="replace")
        return ""

    def update_item(self, filepath: str, new_content: str) -> bool:
        """Update markdown content of an existing vault item safely."""
        p = Path(filepath)
        if p.exists() and p.is_file() and str(p.resolve()).startswith(str(self.vault_dir.resolve())):
            try:
                p.write_text(new_content, encoding="utf-8")
                return True
            except Exception:
                return False
        return False

    def list_items(self, folder: Path, category_name: str) -> List[VaultItem]:
        """List all markdown items in a subfolder."""
        items = []
        if not folder.exists():
            return items

        for p in sorted(folder.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                content = p.read_text(encoding="utf-8", errors="replace")
                first_line = content.split("\n")[0].replace("#", "").strip() if content else p.name
                items.append(
                    VaultItem(
                        category=category_name,
                        filename=p.name,
                        title=first_line or p.stem,
                        filepath=str(p),
                        updated_at=mtime,
                        content_snippet=content[:200] + "..." if len(content) > 200 else content,
                    )
                )
            except Exception:
                continue
        return items

    def list_all_vault_documents(self) -> List[VaultItem]:
        """List vision manifesto + ADRs + brainstorm notes + directives."""
        docs: List[VaultItem] = []
        if self.vision_file.exists():
            mtime = datetime.fromtimestamp(self.vision_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            txt = self.get_vision()
            docs.append(
                VaultItem(
                    category="Vizyon & Manifesto",
                    filename=self.vision_file.name,
                    title="Şirket Vizyonu & Mühendislik İlkeleri",
                    filepath=str(self.vision_file),
                    updated_at=mtime,
                    content_snippet=txt[:200],
                )
            )
        docs.extend(self.list_items(self.decisions_dir, "Mimari Karar (ADR)"))
        docs.extend(self.list_items(self.brainstorm_dir, "Ürün Keşif Notu"))
        docs.extend(self.list_items(self.directives_dir, "Mühendislik Şartnamesi"))
        return docs

    def list_all_notes(self) -> List[VaultItem]:
        return self.list_items(self.brainstorm_dir, "Ürün Keşif Notu")

    def list_all_adrs(self) -> List[VaultItem]:
        return self.list_items(self.decisions_dir, "Mimari Karar (ADR)")

    def delete_item(self, filepath: str) -> bool:
        """Delete a vault item safely (except main vision manifesto)."""
        p = Path(filepath)
        if p.resolve() == self.vision_file.resolve():
            return False
        if p.exists() and p.is_file() and str(p.resolve()).startswith(str(self.vault_dir.resolve())):
            try:
                p.unlink()
                return True
            except Exception:
                return False
        return False


# Global singleton repository
vault_repository = VaultRepository()
