@echo off
title FLOW 8 Pro Studio Remote
cd /d "%~dp0"

if exist "FLOW8_Remote_Pro.exe" (
    start "" "FLOW8_Remote_Pro.exe"
) else (
    python flow8_desktop.py
)
