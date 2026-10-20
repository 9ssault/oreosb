#!/usr/bin/env python3
"""OreoSB desktop launcher — starts main.py with optional TOKEN from UI."""
import os
import sys
import subprocess
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

def _ensure_env(token: str, prefix: str = "."):
    env_path = ROOT / ".env"
    lines = []
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("TOKEN=") or line.startswith("PREFIX="):
                continue
            lines.append(line)
    lines.insert(0, f"TOKEN={token.strip()}")
    lines.append(f"PREFIX={prefix.strip() or '.'}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def run_bot():
    py = sys.executable
    main = ROOT / "main.py"
    if not main.exists():
        print("main.py missing")
        return
    subprocess.call([py, str(main)])

def cli():
    token = os.getenv("TOKEN", "").strip()
    if not token:
        token = input("TOKEN: ").strip()
    if not token:
        print("TOKEN required")
        sys.exit(1)
    _ensure_env(token)
    run_bot()

def gui():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except Exception:
        print("tkinter unavailable — CLI mode")
        cli()
        return

    root = tk.Tk()
    root.title("OreoSB")
    root.geometry("420x220")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=16)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="User token").grid(row=0, column=0, sticky="w")
    token_var = tk.StringVar(value=os.getenv("TOKEN", ""))
    ttk.Entry(frm, textvariable=token_var, width=48, show="*").grid(row=1, column=0, columnspan=2, pady=4)

    ttk.Label(frm, text="Prefix").grid(row=2, column=0, sticky="w")
    prefix_var = tk.StringVar(value=os.getenv("PREFIX", "."))
    ttk.Entry(frm, textvariable=prefix_var, width=8).grid(row=3, column=0, sticky="w", pady=4)

    status = tk.StringVar(value="idle")
    ttk.Label(frm, textvariable=status).grid(row=4, column=0, sticky="w", pady=8)

    def start():
        t = token_var.get().strip()
        if not t:
            messagebox.showerror("OreoSB", "TOKEN required")
            return
        _ensure_env(t, prefix_var.get())
        status.set("running…")
        threading.Thread(target=run_bot, daemon=True).start()

    ttk.Button(frm, text="Start", command=start).grid(row=5, column=0, sticky="w")
    ttk.Button(frm, text="Quit", command=root.destroy).grid(row=5, column=1, sticky="e")

    root.mainloop()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        cli()
    else:
        gui()
