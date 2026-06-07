@echo off
REM ── Versigent Safe Launch Generator — Windows launcher ──
cd /d "%~dp0"
echo Installing required libraries (first run only)...
python -m pip install -r requirements.txt
echo Starting Safe Launch app...
python -m streamlit run app.py
pause
