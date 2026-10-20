"""OreoSB Android UI — write TOKEN/config and start bot when runtime allows."""
import os
import sys
import json
import threading
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("OREOSB_DATA", str(APP_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

def _write_env(token: str, prefix: str = "."):
    env = DATA_DIR / ".env"
    lines = [
        f"TOKEN={token.strip()}",
        f"PREFIX={prefix.strip() or '.'}",
        "AUTO_RECOVER=0",
    ]
    env.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return env

def _write_config():
    cfg_path = DATA_DIR / "config.json"
    if cfg_path.exists():
        return cfg_path
    cfg = {
        "token": "",
        "prefix": ".",
        "nitro_sniper": True,
        "giveaway_sniper": True,
        "invite_sniper": False,
        "max_joins_per_hour": 5,
        "status_rotate": False,
        "status_interval": 30,
        "statuses": ["Gaming", "Chilling", "Coding", "Watching"],
        "afk_message": "AFK",
        "private_mode": True,
        "delay": [0.4, 2.5],
    }
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return cfg_path

def _start_bot(token: str, prefix: str, status_cb):
    """Attempt to run main bot from packaged or sibling repo files."""
    os.environ["TOKEN"] = token
    os.environ["PREFIX"] = prefix
    _write_env(token, prefix)
    _write_config()
    os.chdir(DATA_DIR)

    # Prefer full repo checkout if present next to data
    candidates = [
        DATA_DIR / "main.py",
        APP_DIR.parent.parent.parent / "main.py",  # repo root when developed
        Path.home() / "oreosb" / "main.py",
        Path("/data/data/com.termux/files/home/oreosb/main.py"),
    ]
    main_py = next((p for p in candidates if p.exists()), None)
    if not main_py:
        status_cb("No main.py — clone repo into data or use Termux path")
        return

    root = main_py.parent
    os.chdir(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    status_cb(f"starting from {root}")
    try:
        import runpy
        runpy.run_path(str(main_py), run_name="__main__")
    except SystemExit:
        status_cb("bot exited")
    except Exception as e:
        status_cb(f"error: {e}")

def main():
    try:
        import toga
        from toga.style import Pack
        from toga.style.pack import COLUMN
    except ImportError:
        print("toga missing — install briefcase/toga or use Termux")
        token = os.getenv("TOKEN") or input("TOKEN: ")
        _start_bot(token, ".", print)
        return

    def startup(app):
        token_in = toga.PasswordInput(placeholder="Discord user TOKEN")
        prefix_in = toga.TextInput(placeholder="Prefix", value=".")
        status = toga.Label("Set TOKEN then Start. Full cogs need main.py+cogs on device.")

        def on_start(widget):
            t = (token_in.value or "").strip()
            if not t:
                status.text = "TOKEN required"
                return
            p = (prefix_in.value or ".").strip()
            status.text = "starting…"

            def cb(msg):
                try:
                    status.text = str(msg)[:120]
                except Exception:
                    pass

            threading.Thread(
                target=_start_bot, args=(t, p, cb), daemon=True
            ).start()

        def on_save(widget):
            t = (token_in.value or "").strip()
            if not t:
                status.text = "TOKEN required"
                return
            _write_env(t, prefix_in.value or ".")
            _write_config()
            status.text = f"saved .env + config.json → {DATA_DIR}"

        box = toga.Box(
            children=[
                toga.Label("OreoSB"),
                token_in,
                prefix_in,
                toga.Button("Save config", on_press=on_save),
                toga.Button("Start bot", on_press=on_start),
                status,
            ],
            style=Pack(direction=COLUMN, margin=14, gap=10),
        )
        return toga.MainWindow(title="OreoSB", content=box)

    app = toga.App("OreoSB", "com.oreosb.app", startup=startup)
    app.main_loop()

if __name__ == "__main__":
    main()
