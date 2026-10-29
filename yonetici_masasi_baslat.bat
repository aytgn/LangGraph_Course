@echo off
title Otonom Ajan Sirketi - Yonetici Masasi
color 0B
chcp 65001 > nul

echo ==============================================================================
echo   👑 OTONOM AJAN SIRKETI - YONETICI MASASI (EXECUTIVE COCKPIT) 👑
echo ==============================================================================
echo.
echo [1/2] Sanal ortam ve bilesenler kontrol ediliyor...
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [HATA] .venv sanal ortami bulunamadi!
    pause
    exit /b
)

echo [2/2] Yonetici Masasi tarayicida baslatiliyor...
echo.
echo Tarayici otomatik acilacaktir (http://localhost:8501)
echo Durdurmak icin bu pencerede Ctrl+C tuslarina basabilirsiniz.
echo ==============================================================================
echo.

.\.venv\Scripts\streamlit.exe run 06_yonetici_sirket\yonetici_masasi.py --theme.base="dark"
pause
