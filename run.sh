#!/bin/bash
cd "$(dirname "$0")"
while true; do
  python3 main.py
  echo "[run] exit $? — restart 4s"
  sleep 4
done
