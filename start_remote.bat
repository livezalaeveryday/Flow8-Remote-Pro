@echo off
title FLOW 8 Pro Studio Remote
cd /d "%~dp0"

echo Starting FLOW 8 Pro Studio Remote...
echo Opening in your browser via http://localhost:8844 ...

python server.py

pause
