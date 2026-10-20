#!/usr/bin/env bash
# Copy full OreoSB tree into android app data package for APK builds
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/android/src/oreosb/data"
rm -rf "$DEST"
mkdir -p "$DEST"

copy_list=(
  main.py
  multi_token.py
  launcher.py
  config.json
  requirements.txt
  .env.example
  run.sh
)

for f in "${copy_list[@]}"; do
  if [[ -f "$ROOT/$f" ]]; then
    cp "$ROOT/$f" "$DEST/"
  fi
done

cp -a "$ROOT/cogs" "$DEST/cogs"
cp -a "$ROOT/evasion" "$DEST/evasion"

# empty secrets
: > "$DEST/tokens.txt"
cp "$DEST/.env.example" "$DEST/.env" 2>/dev/null || true

echo "Bundled into $DEST"
find "$DEST" -type f | wc -l
echo "files staged for APK asset packaging"
