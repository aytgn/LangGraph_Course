@echo off
chcp 65001 > nul
title LangGraph & Otonom Ajanlar - E-Kitap Okuyucu
echo ============================================================================
echo   📖 ZİNCİRLERDEN OTONOM ŞİRKETLERE: LANGGRAPH E-KİTAP OKUYUCU (VIBE READER)
echo ============================================================================
echo.
echo Karanlık temalı interaktif e-kitap stüdyosu açılıyor...
echo Adres: http://kitap.lvh.me
echo.
cd /d "%~dp0"
start "" "http://kitap.lvh.me"
.\.venv\Scripts\python.exe kitap_okuyucu.py
pause
