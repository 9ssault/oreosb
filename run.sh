#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "[run.sh] created .env from .env.example — edit TOKEN then rerun"
  exit 1
fi
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -U pip
  .venv/bin/pip install -r requirements.txt
fi
export PYTHONUNBUFFERED=1
while true; do
  .venv/bin/python main.py || true
  code=$?
  echo "[run.sh] exited $code — restart in 4s"
  sleep 4
done
