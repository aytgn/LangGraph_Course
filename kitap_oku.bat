@echo off
chcp 65001 > nul
cd /d "%~dp0"
if not exist "%~dp0LANGGRAPH_E_KITAP.html" (
    .\.venv\Scripts\python.exe kitap_okuyucu.py --build
)
start "" "%~dp0LANGGRAPH_E_KITAP.html"
exit /b 0
