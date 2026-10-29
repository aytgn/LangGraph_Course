@echo off
title Otonom Ajan Holding - Yonetici Kokpiti
cd /d "%~dp0"
echo ====================================================
echo OTONOM AJAN HOLDING YONETICI MASASI BASLATILIYOR...
echo ====================================================
call .\.venv\Scripts\activate.bat
streamlit run 06_yonetici_sirket\yonetici_masasi.py
pause