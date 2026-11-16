@echo off
title AI Documentary & Story Generator
cd /d "%~dp0"
echo ===================================================
echo     Starting AI Documentary & Story Generator
echo ===================================================
echo.
python -m streamlit run app.py --server.headless=false
pause
