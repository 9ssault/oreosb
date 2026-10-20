#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[OreoSB] Linux binary build"
python3 -m pip install -U pip pyinstaller
python3 -m pip install -r requirements.txt

pyinstaller --noconfirm --clean oreosb.spec

mkdir -p dist/linux
if [[ -f dist/OreoSB ]]; then
  cp dist/OreoSB dist/linux/OreoSB
  chmod +x dist/linux/OreoSB
  cp .env.example dist/linux/.env.example
  cp config.json dist/linux/config.json
  cat > dist/linux/README.txt <<'EOF'
OreoSB Linux binary
1. Copy .env.example to .env and set TOKEN=
2. ./OreoSB
Or run with --cli for headless.
EOF
  echo "Built: dist/linux/OreoSB"
else
  echo "Build failed"
  exit 1
fi
