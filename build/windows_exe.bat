@echo off
setlocal
cd /d "%~dp0.."

echo [OreoSB] Windows EXE build
python -m pip install -U pip pyinstaller
python -m pip install -r requirements.txt

pyinstaller --noconfirm --clean oreosb.spec

if exist dist\OreoSB.exe (
  echo.
  echo Built: dist\OreoSB.exe
  echo Copy .env next to the exe or paste TOKEN in the launcher UI.
) else (
  echo Build failed.
  exit /b 1
)
