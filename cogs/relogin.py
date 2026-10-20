import asyncio
import aiohttp
import json
import os
import base64
from pathlib import Path
import discord
from discord.ext import commands, tasks

API = "https://discord.com/api/v10"

async def _super_props() -> str:
    try:
        from evasion.fingerprint import get_super_properties
        return await get_super_properties("electron")
    except Exception:
        props = {
            "os": "Windows",
            "browser": "Discord Client",
            "release_channel": "stable",
            "client_build_number": 373069,
            "client_event_source": None,
        }
        return base64.b64encode(json.dumps(props).encode()).decode()

class Relogin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")
        self._recovering = False
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()

    async def _headers(self, token=None):
        t = token or getattr(self.bot.http, "token", None) or ""
        return {
            "Authorization": t,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/138.0.7204.92 Electron/36.2.1 Safari/537.36",
            "X-Super-Properties": await _super_props(),
        }

    async def validate(self, token: str) -> bool:
        if not token:
            return False
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{API}/users/@me", headers=await self._headers(token), timeout=10) as r:
                    return r.status == 200
        except Exception:
            return False

    async def login_email(self, email: str, password: str):
        payload = {
            "login": email,
            "password": password,
            "undelete": False,
            "login_source": None,
            "gift_code_sku_id": None,
        }
        headers = await self._headers("")
        headers.pop("Authorization", None)
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                    data = await r.json(content_type=None)
                    if r.status == 200 and isinstance(data, dict) and data.get("token"):
                        return data["token"]
                    if isinstance(data, dict) and (data.get("mfa") or data.get("ticket")):
                        print("[RELOGIN] 2FA/ticket required — cannot auto")
                        return None
                    print("[RELOGIN] login failed", r.status, str(data)[:200])
                    return None
        except Exception as e:
            print("[RELOGIN] login error", e)
            return None

    def save_token(self, token: str):
        env = Path(".env")
        lines = []
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("TOKEN="):
                    lines.append(f"TOKEN={token}")
                else:
                    lines.append(line)
        else:
            lines = [f"TOKEN={token}", "PREFIX=."]
        if not any(l.startswith("TOKEN=") for l in lines):
            lines.insert(0, f"TOKEN={token}")
        env.write_text("\n".join(lines) + "\n")
        cfg = Path("config.json")
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text())
                data["token"] = token
                cfg.write_text(json.dumps(data, indent=2))
            except Exception:
                pass
        print("[RELOGIN] token saved to .env")

    async def recover(self, reason: str = "unknown"):
        if self._recovering:
            return
        self._recovering = True
        print(f"[RELOGIN] recover triggered: {reason}")
        try:
            if not self.email or not self.password:
                print("[RELOGIN] EMAIL/PASSWORD not set — cannot auto-reset")
                return
            new = await self.login_email(self.email, self.password)
            if not new:
                print("[RELOGIN] could not obtain new token")
                return
            self.save_token(new)
            print("[RELOGIN] new token acquired — closing for restart")
            try:
                await self.bot.close()
            except Exception:
                pass
        finally:
            self._recovering = False

    @tasks.loop(minutes=3)
    async def check_loop(self):
        token = getattr(self.bot.http, "token", None)
        if not token:
            return
        ok = await self.validate(token)
        if not ok:
            await self.recover("periodic_check_failed")

    @check_loop.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_disconnect(self):
        await asyncio.sleep(2)
        token = getattr(self.bot.http, "token", None)
        if token and not await self.validate(token):
            await self.recover("disconnect")

    @commands.Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        err = str(kwargs) + str(args)
        if "401" in err or "Unauthorized" in err or "Invalid" in err:
            await self.recover("on_error_auth")

    @commands.command(name="setlogin")
    async def setlogin(self, ctx, email: str, password: str):
        await ctx.message.delete()
        self.email = email
        self.password = password
        env = Path(".env")
        text = env.read_text() if env.exists() else ""
        lines = [l for l in text.splitlines() if not l.startswith("EMAIL=") and not l.startswith("PASSWORD=")]
        lines.append(f"EMAIL={email}")
        lines.append(f"PASSWORD={password}")
        env.write_text("\n".join(lines) + "\n")
        await ctx.send("login saved", delete_after=4)

    @commands.command(name="refresh")
    async def refresh(self, ctx):
        await ctx.message.delete()
        if not self.email or not self.password:
            await ctx.send("set EMAIL/PASSWORD first (.setlogin)", delete_after=5)
            return
        new = await self.login_email(self.email, self.password)
        if not new:
            await ctx.send("refresh failed", delete_after=4)
            return
        self.save_token(new)
        await ctx.send("new token saved — restart bot", delete_after=6)

    @commands.command(name="checktokenlive")
    async def checktokenlive(self, ctx):
        await ctx.message.delete()
        ok = await self.validate(getattr(self.bot.http, "token", ""))
        await ctx.send("alive" if ok else "dead", delete_after=4)

async def setup(bot):
    await bot.add_cog(Relogin(bot))
