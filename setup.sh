#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "[setup] creating venv"
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[setup] wrote .env — put TOKEN= in it"
fi
if [ ! -f tokens.txt ]; then
  touch tokens.txt
fi
chmod +x run.sh setup.sh 2>/dev/null || true
echo "[setup] done"
echo "  1. edit .env  (TOKEN=... optional EMAIL/PASSWORD)"
echo "  2. ./run.sh   or  .venv/bin/python main.py"
echo "  3. multi: put tokens in tokens.txt then .venv/bin/python multi_token.py"
