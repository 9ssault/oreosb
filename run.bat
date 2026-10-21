@echo off
cd /d "%~dp0"
:loop
python main.py
echo exited %ERRORLEVEL% — restart in 4s
timeout /t 4 /nobreak >nul
goto loop
