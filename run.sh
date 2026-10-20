#!/bin/bash
# auto-restart so relogin can apply new token
cd "$(dirname "$0")"
while true; do
  python3 main.py
  code=$?
  echo "[run.sh] exited $code — restart in 4s"
  sleep 4
done
