# OreoSB packaging

## Windows EXE

```bat
build\windows_exe.bat
```

Output: `dist\OreoSB.exe`  
Run it, paste TOKEN in the UI (or place `.env` beside the exe).

Requires Python 3.10+ on the build machine. Target PC does not need Python.

## Linux binary

```bash
chmod +x build/linux_bin.sh build/linux_appimage.sh
./build/linux_bin.sh
# optional AppImage:
./build/linux_appimage.sh
```

Output:
- `dist/linux/OreoSB`
- `dist/OreoSB-x86_64.AppImage` (if appimagetool installed)

## Android APK

See `android/README.md`.

- **Termux**: run Python core directly on phone  
- **Briefcase**: `android/pyproject.toml` → `briefcase package android`  
- **Dashboard WebView**: wrap Vite build against LAN server

## One-shot deps for builders

```bash
pip install pyinstaller pillow
# Windows: run build\windows_exe.bat
# Linux:   ./build/linux_bin.sh
```
