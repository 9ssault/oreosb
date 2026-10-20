# OreoSB Android (APK)

Two practical paths:

## A) Termux (recommended on device)

```bash
pkg update && pkg install python git
git clone https://github.com/9ssault/oreosb.git
cd oreosb
pip install -r requirements.txt
cp .env.example .env
# edit TOKEN=
python main.py
```

Or `python launcher.py --cli`.

## B) Build APK with Briefcase (BeeWare)

From a Linux/macOS build machine with JDK + Android SDK:

```bash
pip install briefcase
cd android
briefcase create android
briefcase build android
briefcase package android
# APK under android/build/...
```

`pyproject.toml` in this folder configures the app id `com.oreosb.app` and entry `launcher:gui`.

## C) WebView shell APK (dashboard)

If you run the Node dashboard (`npm run dev` / server on LAN):

1. Point a simple Android WebView app at `http://<pc-ip>:3000`
2. Or use Capacitor/Cordova to wrap the Vite `dist/` after `npm run build`

Selfbot core remains Python; the APK is a control shell or Termux-hosted process.
