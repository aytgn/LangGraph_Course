@echo off
chcp 65001 > nul
title LangGraph & LangSmith Vibe Coder Atölyesi
echo ======================================================================
echo   🚀 LANGGRAPH & LANGSMITH INTERAKTIF ATÖLYE ARAYÜZÜ (VIBE CODER UI)
echo ======================================================================
echo.
echo Tarayıcınız açılıyor... (http://localhost:8888)
echo Durdurmak için bu konsol penceresini kapatabilir veya Ctrl + C yapabilirsiniz.
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
jupyter notebook --IdentityProvider.token="" --ServerApp.token="" --ServerApp.password="" --port 8888 04_gozlemlenebilirlik/langsmith_atolyesi.ipynb
pause
