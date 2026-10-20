# OreoSB APK — full tree + how to build

This package stages **main.py, multi_token.py, config.json, .env.example, cogs/, evasion/** into the Android app data folder, then builds an APK with BeeWare Briefcase.

## What you need on the build PC

- Linux or macOS (Windows WSL2 OK)
- **Python 3.10+**
- **JDK 17+**
- **Android SDK** (cmdline-tools + platform-tools + a platform + build-tools)
- `ANDROID_HOME` set

```bash
# example Debian/Ubuntu hints
sudo apt install openjdk-17-jdk
# install Android commandline tools from Google, then:
# sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

## Build the APK

From repo root:

```bash
chmod +x android/bundle_assets.sh android/build_apk.sh
./android/build_apk.sh
```

Or step by step:

```bash
cd android
bash bundle_assets.sh          # copies cogs, config, main, evasion → src/oreosb/data
pip install briefcase toga toga-android
briefcase create android       # first time only
briefcase build android
briefcase package android -p apk
```

Install:

```bash
adb install -r path/to/OreoSB-*.apk
```

## Use the APK

1. Open **OreoSB**
2. Paste **user token**
3. Set prefix if needed (default `.`)
4. **Save config** → writes `.env` + `config.json` under app data
5. **Start bot** → runs `main.py` if the Python stack can import `discord`

Bundled under app data after `bundle_assets.sh`:

- `main.py` `multi_token.py` `launcher.py`
- `config.json` `.env.example` `requirements.txt`
- `cogs/` (all modules)
- `evasion/`

## If Start fails on device

Android still needs native wheels for aiohttp/discord. If imports fail inside the APK:

**Fallback that always works — Termux (same files):**

```bash
pkg install python git
git clone https://github.com/9ssault/oreosb.git && cd oreosb
pip install -r requirements.txt
cp .env.example .env   # TOKEN=
python main.py
```

Or copy the staged `android/src/oreosb/data` tree into Termux home and run `python main.py` there after `pip install -r requirements.txt`.

## Contents checklist

| Item | In APK data bundle |
|------|--------------------|
| cogs/* | yes (`bundle_assets.sh`) |
| evasion/* | yes |
| config.json | yes |
| .env.example | yes |
| main.py / multi_token | yes |
| TOKEN at runtime | user enters in UI → `.env` |
