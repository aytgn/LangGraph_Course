@echo off
chcp 65001 > nul
title Abonelik ve Gider Takipçisi
cd /d "%~dp0"
echo ============================================================
echo   🚀 Abonelik ve Gider Takipçisi BASLATILIYOR (Port: 8505)...
echo ============================================================
if exist "c:\Users\aytgn\Desktop\LangGraph_Course\.venv\Scripts\streamlit.exe" (
    "c:\Users\aytgn\Desktop\LangGraph_Course\.venv\Scripts\streamlit.exe" run "app.py" --server.port 8505
) else (
    streamlit run "app.py" --server.port 8505
)
pause
