import asyncio
import json
import os
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands, tasks

from core_utils import owner_check, save_state, load_state

API = "https://discord.com/api/v10"


class Relogin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")
        self._recovering = False
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()

    def _headers(self, token=None):
        t = token or getattr(self.bot.http, "token", None) or ""
        return {
            "Authorization": t,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    async def validate(self, token: str) -> bool:
        if not token:
            return False
        try:
            timeout = aiohttp.ClientTimeout(total=12)
            async with aiohttp.ClientSession(timeout=timeout) as s:
                async with s.get(f"{API}/users/@me", headers=self._headers(token)) as r:
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
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as s:
                async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                    data = await r.json(content_type=None)
                    if r.status == 200 and isinstance(data, dict) and data.get("token"):
                        return data["token"]
                    if isinstance(data, dict) and (data.get("mfa") or data.get("ticket")):
                        print("[RELOGIN] 2FA required")
                        return None
                    print("[RELOGIN] login fail", r.status, str(data)[:180])
                    return None
        except Exception as e:
            print("[RELOGIN] err", e)
            return None

    def save_token(self, token: str):
        env = Path(".env")
        lines = []
        if env.exists():
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("TOKEN="):
                    lines.append(f"TOKEN={token}")
                else:
                    lines.append(line)
        else:
            lines = [f"TOKEN={token}", "PREFIX=."]
        if not any(l.startswith("TOKEN=") for l in lines):
            lines.insert(0, f"TOKEN={token}")
        env.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cfg_path = Path("config.json")
        if cfg_path.exists():
            try:
                data = json.loads(cfg_path.read_text(encoding="utf-8"))
                data["token"] = token
                cfg_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass
        st = load_state()
        st["last_token_refresh"] = __import__("time").time()
        save_state(st)
        print("[RELOGIN] token saved")

    async def recover(self, reason: str = "unknown"):
        if self._recovering:
            return
        if getattr(self.bot, "role", "master") != "master":
            return
        self._recovering = True
        print(f"[RELOGIN] recover: {reason}")
        try:
            # try mailrecover cog first if available
            mail = self.bot.get_cog("MailRecover")
            if mail and os.getenv("AUTO_RECOVER", "0").lower() in ("1", "true", "yes"):
                try:
                    await mail.full_recover()
                    return
                except Exception as e:
                    print("[RELOGIN] mailrecover failed", e)
            if not self.email or not self.password:
                print("[RELOGIN] no EMAIL/PASSWORD")
                return
            new = await self.login_email(self.email, self.password)
            if not new:
                return
            self.save_token(new)
            print("[RELOGIN] closing for restart")
            await self.bot.close()
        finally:
            self._recovering = False

    @tasks.loop(minutes=2)
    async def check_loop(self):
        if getattr(self.bot, "role", "master") != "master":
            return
        token = getattr(self.bot.http, "token", None)
        if not token:
            return
        if not await self.validate(token):
            await self.recover("periodic")

    @check_loop.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_disconnect(self):
        if getattr(self.bot, "role", "master") != "master":
            return
        await asyncio.sleep(5)
        token = getattr(self.bot.http, "token", None)
        if token and not await self.validate(token):
            await self.recover("disconnect")

    @commands.command(name="setlogin")
    @owner_check()
    async def setlogin(self, ctx, email: str, password: str):
        await ctx.message.delete()
        self.email = email
        self.password = password
        env = Path(".env")
        text = env.read_text(encoding="utf-8") if env.exists() else ""
        lines = [
            l
            for l in text.splitlines()
            if not l.startswith("EMAIL=") and not l.startswith("PASSWORD=")
        ]
        lines.append(f"EMAIL={email}")
        lines.append(f"PASSWORD={password}")
        env.write_text("\n".join(lines) + "\n", encoding="utf-8")
        await ctx.send("login saved", delete_after=4)

    @commands.command(name="refresh")
    @owner_check()
    async def refresh(self, ctx):
        await ctx.message.delete()
        if not self.email or not self.password:
            await ctx.send("set EMAIL/PASSWORD first", delete_after=5)
            return
        new = await self.login_email(self.email, self.password)
        if not new:
            await ctx.send("refresh failed", delete_after=4)
            return
        self.save_token(new)
        await ctx.send("token saved — restart", delete_after=5)

    @commands.command(name="checktokenlive")
    @owner_check()
    async def checktokenlive(self, ctx):
        await ctx.message.delete()
        ok = await self.validate(getattr(self.bot.http, "token", ""))
        await ctx.send("alive" if ok else "dead", delete_after=4)


async def setup(bot):
    await bot.add_cog(Relogin(bot))
