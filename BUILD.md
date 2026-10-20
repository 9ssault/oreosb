# Build OreoSB binaries

| Target | Command | Output |
|--------|---------|--------|
| Windows EXE | `build\windows_exe.bat` | `dist\OreoSB.exe` |
| Linux binary | `./build/linux_bin.sh` | `dist/linux/OreoSB` |
| Linux AppImage | `./build/linux_appimage.sh` | `dist/OreoSB-x86_64.AppImage` |
| Android APK | see `android/README.md` | Briefcase or Termux |

## Windows

1. Install Python 3.10+ from python.org (check “Add to PATH”)
2. Open cmd in repo root
3. `build\windows_exe.bat`
4. Run `dist\OreoSB.exe` → enter token → Start

## Linux

```bash
sudo apt install python3-pip python3-tk python3-venv  # debian/ubuntu
./build/linux_bin.sh
./dist/linux/OreoSB
```

AppImage needs [appimagetool](https://github.com/AppImage/appimagetool).

## Android

Selfbot networking is Python. On phone use **Termux**:

```bash
pkg install python git
git clone https://github.com/9ssault/oreosb.git && cd oreosb
pip install -r requirements.txt
cp .env.example .env   # TOKEN=
python main.py
```

For a packaged APK shell: `android/` + BeeWare Briefcase (JDK + Android SDK required on the build PC).

## Notes

- EXE/Linux builds embed `cogs/`, `evasion/`, `main.py` via `oreosb.spec`
- Launcher writes `.env` next to the binary when you save a token
- Headless: `OreoSB --cli` or `python launcher.py --cli`
