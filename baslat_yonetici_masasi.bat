@echo off
title Otonom Ajan Holding - Yonetici Kokpiti
cd /d "C:\Users\aytgn\Desktop\LangGraph_Course"
echo ====================================================
echo OTONOM AJAN HOLDING YONETICI MASASI BASLATILIYOR...
echo ====================================================
call .\.venv\Scripts\activate.bat
streamlit run yonetici_masasi.py
pause