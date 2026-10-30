"""
Disk and Packaging Operations Tools.
"""

import io
import re
import zipfile
from typing import Dict, Tuple, Any
from config.settings import config
from tools.base import StudioTool
from tools.registry import ToolRegistry


def sanitize_slug(raw_slug: str) -> str:
    """Normalize project name into safe filesystem directory slug."""
    s = (raw_slug or "").strip().lower()
    s = s.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "otonom_uygulama"


class BatchScriptGeneratorTool(StudioTool):
    """Generates a tailored 1-click Windows batch launcher (.bat) for the application."""

    def __init__(self):
        super().__init__(
            name="batch_script_generator",
            description="Uygulama tipine göre (Streamlit port 8505, FastAPI port 8005, CLI) tek tıkla çalışan baslat.bat üretir.",
            department="Deployment_Gate",
            category="Packaging",
            parameters_schema={"app_name": "str", "app_type": "str", "entrypoint": "str"},
        )

    def run(self, app_name: str, app_type: str, entrypoint: str = "app.py") -> Tuple[str, str]:
        """Returns tuple of (bat_content, run_command_hint)."""
        venv_python = str(config.PROJECT_ROOT / ".venv" / "Scripts" / "python.exe")

        if "FastAPI" in app_type:
            mod_name = entrypoint[:-3] if entrypoint.endswith(".py") else "main"
            hint = f"uvicorn {mod_name}:app --reload --port 8005  (Swagger UI: http://127.0.0.1:8005/docs)"
            exec_block = (
                "start \"\" http://127.0.0.1:8005/docs\n"
                f"if exist \"{venv_python}\" (\n"
                f"    \"{venv_python}\" -m uvicorn {mod_name}:app --reload --port 8005\n"
                ") else (\n"
                f"    python -m uvicorn {mod_name}:app --reload --port 8005\n"
                ")"
            )
        elif "Streamlit" in app_type:
            hint = f"streamlit run {entrypoint} --server.port 8505  (Web UI: http://localhost:8505)"
            exec_block = (
                f"if exist \"{venv_python}\" (\n"
                f"    \"{venv_python}\" -m streamlit run \"{entrypoint}\" --server.port 8505\n"
                ") else (\n"
                f"    python -m streamlit run \"{entrypoint}\" --server.port 8505\n"
                ")"
            )
        else:
            hint = f"python {entrypoint}"
            exec_block = (
                f"if exist \"{venv_python}\" (\n"
                f"    \"{venv_python}\" \"{entrypoint}\"\n"
                ") else (\n"
                f"    python \"{entrypoint}\"\n"
                ")"
            )

        bat_content = f"""@echo off
chcp 65001 >nul
title {app_name} - AI Software Studio
cd /d "%~dp0"
echo ============================================================
echo   {app_name}
echo   Mimari Tur: {app_type}
echo ============================================================
echo.
{exec_block}
echo.
pause
"""
        return bat_content, hint


class DiskExportTool(StudioTool):
    """Physically writes code bundle, requirements, PRD doc, and baslat.bat to disk."""

    def __init__(self):
        super().__init__(
            name="disk_export_tool",
            description="Üretilen tüm dosyaları ve çalıştırma betiklerini fiziksel diske (output_uygulamalar) yazar.",
            department="Deployment_Gate",
            category="Packaging",
            parameters_schema={"state": "dict"},
        )
        self.bat_generator = BatchScriptGeneratorTool()

    def run(self, state: Dict[str, Any]) -> Tuple[str, str]:
        """Exports application to disk, returning (app_folder, run_command_hint)."""
        raw_slug = state.get("app_slug") or state.get("app_name") or "uygulama"
        clean_slug = sanitize_slug(raw_slug)
        app_name = state.get("app_name") or "Otonom Uygulama"
        app_type = state.get("app_type") or "Streamlit Web App"
        entrypoint = state.get("entrypoint_file") or "app.py"
        code_files = state.get("code_files") or {}

        target_dir = config.OUTPUT_APPS_DIR / clean_slug
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write source files
        for fname, content in code_files.items():
            safe_rel = fname.strip().lstrip("\\/")
            fpath = target_dir / safe_rel
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8", errors="replace")

        # 2. Write requirements.txt if missing
        req_path = target_dir / "requirements.txt"
        if not req_path.exists():
            techs = state.get("tech_stack") or []
            req_lines = []
            for t in techs:
                t_low = t.lower()
                if "streamlit" in t_low:
                    req_lines.append("streamlit>=1.35.0")
                elif "fastapi" in t_low:
                    req_lines.extend(["fastapi>=0.115.0", "uvicorn>=0.30.0"])
                elif "pydantic" in t_low:
                    req_lines.append("pydantic>=2.7.0")
                elif "pandas" in t_low:
                    req_lines.append("pandas>=2.2.0")
                elif "altair" in t_low:
                    req_lines.append("altair>=5.3.0")
            if not req_lines:
                req_lines = ["pydantic>=2.7.0"]
            req_path.write_text("\n".join(sorted(list(set(req_lines)))) + "\n", encoding="utf-8")

        # 3. Generate and write baslat.bat
        bat_content, run_hint = self.bat_generator.run(app_name, app_type, entrypoint)
        (target_dir / "baslat.bat").write_text(bat_content, encoding="utf-8", errors="replace")

        # 4. Write PRD and Architecture Markdown doc
        prd_path = target_dir / "MIMARI_VE_PRD.md"
        prd_text = f"""# 📘 {app_name} - Sistem Mimarisi & PRD

* **Uygulama Tipi:** {app_type}
* **Giriş Dosyası:** `{entrypoint}`
* **Veritabanı Tercihi:** {state.get('database_choice') or 'SQLite3'}
* **Teknoloji Yığını:** {', '.join(state.get('tech_stack') or [])}

---

## 🎯 Ürün Amacı ve Kapsam
{state.get('prd_spec') or state.get('purpose_summary') or 'Açıklama belirtilmedi.'}

---

## 📐 Mimari ve Modül Yapısı
{state.get('architecture_spec') or 'Modüler mimari şeması.'}

---

## 🧪 QA & Güvenlik Raporu
* **QA Onayı:** {'Evet (Doğrulandı)' if state.get('qa_passed') else 'Bekliyor'}
* **Toplam Satır Sayısı (LOC):** {state.get('total_loc') or 0} satır
"""
        prd_path.write_text(prd_text, encoding="utf-8", errors="replace")

        return str(target_dir), run_hint


class ZipPackagerTool(StudioTool):
    """Packages application code bundle and specs into an in-memory ZIP archive."""

    def __init__(self):
        super().__init__(
            name="zip_packager_tool",
            description="Uygulama kaynak kodlarını ve PRD dokümanını indirilebilir ZIP belleğine paketler.",
            department="Deployment_Gate",
            category="Packaging",
            parameters_schema={"state": "dict"},
        )

    def run(self, state: Dict[str, Any]) -> bytes:
        buf = io.BytesIO()
        code_files = state.get("code_files") or {}
        app_name = state.get("app_name", "Uygulama")
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname, content in code_files.items():
                zf.writestr(fname, content)
            spec_md = (
                f"# {app_name}\n\n"
                f"## PRD & Kapsam\n{state.get('prd_spec', '')}\n\n"
                f"## Mimari Şema\n{state.get('architecture_spec', '')}\n\n"
                f"## QA Raporu\n{state.get('qa_report', '')}\n"
            )
            zf.writestr("MIMARI_VE_PRD.md", spec_md)
        buf.seek(0)
        return buf.getvalue()


# Register packaging tools
ToolRegistry.register(BatchScriptGeneratorTool())
ToolRegistry.register(DiskExportTool())
ToolRegistry.register(ZipPackagerTool())
