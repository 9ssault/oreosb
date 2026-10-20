#!/data/data/com.termux/files/usr/bin/bash
# Run inside Termux after: pkg install git && git clone ... && cd oreosb
set -e
echo "[OreoSB] Termux setup"
pkg update -y
pkg install -y python openssl libffi clang
pip install -U pip
pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit .env and set TOKEN="
fi
echo "Done. Run: python main.py"
