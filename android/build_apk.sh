#!/usr/bin/env bash
# Build OreoSB APK (requires JDK 17+, Android SDK, briefcase)
set -euo pipefail
cd "$(dirname "$0")"

echo "[1/3] bundle cogs + config into app data"
bash bundle_assets.sh

echo "[2/3] briefcase tools"
python3 -m pip install -U pip briefcase toga toga-android

echo "[3/3] create/build/package"
if [[ ! -d build ]]; then
  briefcase create android
fi
briefcase build android
briefcase package android -p apk

echo "Done. Install with: adb install -r <path-to-apk>"
echo "APK is under android/build/ (briefcase prints exact path)"
echo "On device: open OreoSB → paste TOKEN → Save → Start"
echo "If Start cannot find gateway deps, use Termux clone of full repo (see README)."
