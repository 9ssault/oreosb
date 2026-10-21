# OreoSB APK

## Prebuilt APK (recommended)

1. Open the repo on GitHub → **Actions** → **Build OreoSB APK**
2. Run workflow (**workflow_dispatch**) or wait for a push that touches `android/`
3. Open the finished run → **Artifacts** → download **OreoSB-apk**
4. Unzip → `OreoSB.apk`
5. Install on phone (`adb install -r OreoSB.apk` or file manager)
6. Open app → paste **TOKEN** → **Save** → **Start**

Full cogs/config are bundled via `bundle_assets.sh` into app data.

If the in-APK Python gateway fails on device (native wheels), use **Termux** with the same repo:

```bash
pkg install python git
git clone https://github.com/9ssault/oreosb.git && cd oreosb
pip install -r requirements.txt
cp .env.example .env   # TOKEN=
python main.py
```

## Local build

Needs JDK 17 + Android SDK + `ANDROID_HOME`:

```bash
chmod +x android/bundle_assets.sh android/build_apk.sh
./android/build_apk.sh
```

## What’s inside the APK data bundle

- `main.py`, `multi_token.py`, `config.json`, `.env.example`
- entire `cogs/` and `evasion/`
- token entered in UI written to app `.env`
