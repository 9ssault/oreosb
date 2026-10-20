# Build OreoSB binaries

| Target | Command | Output |
|--------|---------|--------|
| Windows EXE | `build\windows_exe.bat` | `dist\OreoSB.exe` |
| Linux binary | `./build/linux_bin.sh` | `dist/linux/OreoSB` |
| Linux AppImage | `./build/linux_appimage.sh` | `dist/OreoSB-x86_64.AppImage` |
| Android | **Termux** (see `android/README.md`) | full bot on device |
| Android APK shell | Briefcase in `android/` | UI shell APK |

Verify layout:

```bash
chmod +x build/verify.sh && ./build/verify.sh
```

## Windows EXE

1. Python 3.10+ installed (Add to PATH)
2. In repo root:

```bat
build\windows_exe.bat
```

3. Run `dist\OreoSB.exe`
4. Paste user token → **Start**  
   Or put `.env` with `TOKEN=` next to the exe

Headless: `OreoSB.exe --cli`

## Linux binary

```bash
sudo apt install python3-pip python3-tk python3-venv  # if needed
chmod +x build/*.sh
./build/linux_bin.sh
./dist/linux/OreoSB
```

AppImage (optional):

```bash
# install appimagetool first
./build/linux_appimage.sh
```

## Android — how to use (full bot)

**Recommended: Termux**

1. Install Termux from F-Droid  
2. In Termux:

```bash
pkg update -y && pkg install -y python git
git clone https://github.com/9ssault/oreosb.git
cd oreosb
bash android/termux-setup.sh
nano .env   # TOKEN=...
python main.py
```

Details and Briefcase APK shell: **`android/README.md`**

## After any git pull

```bash
git pull
pip install -r requirements.txt   # or rebuild EXE/Linux
```

## Notes

- EXE/Linux embed cogs via `oreosb.spec` + `launcher.py`
- Token never belongs in the APK store listing; use `.env` / launcher UI
- Selfbots violate Discord ToS — expect account risk
