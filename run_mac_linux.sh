#!/usr/bin/env bash
# ── Versigent Safe Launch Generator — macOS / Linux launcher ──
cd "$(dirname "$0")"
echo "Installing required libraries (first run only)..."
python3 -m pip install -r requirements.txt
echo "Starting Safe Launch app..."
python3 -m streamlit run app.py
