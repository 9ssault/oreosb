# OreoSB on Android — how to use

Discord selfbots need a real Python runtime (discord.py-self + websocket).  
A pure “click APK and gateway works offline” build is limited without embedding CPython.  
**Working options below, ranked by reliability.**

---

## Option 1 — Termux (works today)

This runs the **same** `main.py` / cogs as desktop.

### Install Termux

1. Install **Termux** from F-Droid (recommended) or GitHub releases  
   https://f-droid.org/en/packages/com.termux/  
   Avoid outdated Play Store forks.

2. Open Termux and run:

```bash
pkg update -y
pkg install -y python git openssl libffi
pip install -U pip

git clone https://github.com/9ssault/oreosb.git
cd oreosb
pip install -r requirements.txt

cp .env.example .env
nano .env
# set: TOKEN=your_user_token
# optional: PREFIX=.

python main.py
```

### Keep it running

```bash
# restart loop
while true; do python main.py; sleep 4; done

# or
chmod +x run.sh
# run.sh expects bash + venv; on Termux simpler:
while true; do python main.py; sleep 4; done
```

### Optional: Termux:Widget / boot

- **Termux:Widget** — one-tap script that `cd ~/oreosb && python main.py`
- **Termux:Boot** — start on device boot (same command)

### Update

```bash
cd ~/oreosb
git pull
pip install -r requirements.txt
```

---

## Option 2 — Briefcase APK (shell UI)

Builds an Android package with a small Toga UI (`android/src/oreosb`).  
**This APK is a launcher shell**, not a full replacement for Termux unless you embed the full bot service yourself.

### On a Linux/macOS PC with Android SDK + JDK 17+

```bash
cd oreosb
pip install briefcase toga
cd android
briefcase create android
briefcase build android
briefcase package android -p apk
```

APK path is printed by Briefcase (under `android/build/...`).  
Install: `adb install -r path/to/app.apk`

Use the UI to store a token hint; **run the real bot with Option 1** for full features.

---

## Option 3 — Dashboard WebView APK

1. On a PC: `npm install && npm run dev` (or host the Vite build) so the UI is on your LAN  
2. Point any WebView APK / Browser to `http://<pc-ip>:3000`  
3. Bot process still runs on the PC (`python main.py` / EXE)

---

## What “works”

| Method | Full cogs / snipers / relogin | Install difficulty |
|--------|------------------------------|--------------------|
| Termux + `python main.py` | Yes | Easy |
| Briefcase APK alone | UI shell only | Hard (SDK) |
| EXE / Linux binary | Yes | Medium (build PC) |
| WebView + PC bot | Yes (bot on PC) | Easy |

**Use Termux on phone for a real selfbot.** Use EXE/Linux on desktop. Use the Briefcase APK only if you want a branded icon/shell.
