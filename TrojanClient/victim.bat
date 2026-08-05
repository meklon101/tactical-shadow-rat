@echo off
:: Navigate to the current batch file directory
cd /d "%~dp0"

:: Launch victim.py silently in background using Python background execution
start "" pythonw victim.py
