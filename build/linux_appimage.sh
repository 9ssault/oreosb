#!/usr/bin/env bash
# Optional AppImage packaging (needs appimagetool on PATH)
set -euo pipefail
cd "$(dirname "$0")/.."

./build/linux_bin.sh

APPDIR=dist/OreoSB.AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp dist/linux/OreoSB "$APPDIR/usr/bin/OreoSB"
cp .env.example "$APPDIR/usr/bin/.env.example"
cp config.json "$APPDIR/usr/bin/config.json"

cat > "$APPDIR/OreoSB.desktop" <<'EOF'
[Desktop Entry]
Name=OreoSB
Exec=OreoSB
Icon=oreosb
Type=Application
Categories=Network;
Terminal=true
EOF

cp "$APPDIR/OreoSB.desktop" "$APPDIR/usr/share/applications/"

# placeholder icon (1x1 png) if none
python3 - <<'PY'
from pathlib import Path
try:
    from PIL import Image
    p = Path("dist/OreoSB.AppDir/usr/share/icons/hicolor/256x256/apps/oreosb.png")
    Image.new("RGB", (256, 256), (40, 40, 48)).save(p)
except Exception:
    Path("dist/OreoSB.AppDir/oreosb.png").write_bytes(b"")
PY

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname "$(readlink -f "$0")")
cd "$HERE/usr/bin" || exit 1
exec "$HERE/usr/bin/OreoSB" "$@"
EOF
chmod +x "$APPDIR/AppRun" "$APPDIR/usr/bin/OreoSB"

if command -v appimagetool >/dev/null 2>&1; then
  appimagetool "$APPDIR" dist/OreoSB-x86_64.AppImage
  echo "Built: dist/OreoSB-x86_64.AppImage"
else
  echo "appimagetool not found — AppDir ready at $APPDIR"
  echo "Install appimagetool then re-run, or use dist/linux/OreoSB"
fi
