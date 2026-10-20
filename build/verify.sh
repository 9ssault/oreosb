#!/usr/bin/env bash
# Quick sanity check that packaging files and Python entrypoints exist
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[verify] repo root: $(pwd)"

need=(
  main.py
  launcher.py
  multi_token.py
  config.json
  requirements.txt
  oreosb.spec
  build/windows_exe.bat
  build/linux_bin.sh
  build/linux_appimage.sh
  android/README.md
  android/pyproject.toml
  cogs/sniper.py
  cogs/nuker.py
  evasion/fingerprint.py
)

fail=0
for f in "${need[@]}"; do
  if [[ -e "$f" ]]; then
    echo "  ok  $f"
  else
    echo "  MISSING $f"
    fail=1
  fi
done

python3 -c "import ast; ast.parse(open('launcher.py').read()); ast.parse(open('main.py').read())" && echo "  ok  launcher/main parse"

if [[ $fail -eq 0 ]]; then
  echo "[verify] packaging layout OK"
  echo "  Windows: build\\windows_exe.bat"
  echo "  Linux:   ./build/linux_bin.sh"
  echo "  Android: android/README.md (Termux recommended)"
else
  echo "[verify] FAILED"
  exit 1
fi
