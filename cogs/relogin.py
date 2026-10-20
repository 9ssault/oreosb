import asyncio
import aiohttp
import json
import os
from pathlib import Path
import discord
from discord.ext import commands, tasks

API = "https://discord.com/api/v10"

class Relogin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()

    async def _headers(self, token=None):
        t = token or self.bot.http.token
        return {
            "Authorization": t,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }

    async def validate(self, token: str) -> bool:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{API}/users/@me", headers=await self._headers(token), timeout=8) as r:
                    return r.status == 200
        except Exception:
            return False

    async def login_email(self, email: str, password: str) -> str | None:
        payload = {
            "login": email,
            "password": password,
            "undelete": False,
            "login_source": None,
            "gift_code_sku_id": None,
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                    data = await r.json(content_type=None)
                    if r.status == 200 and "token" in data:
                        return data["token"]
                    if data.get("mfa") or data.get("ticket"):
                        print("[RELOGIN] 2FA required — cannot auto")
                        return None
                    print("[RELOGIN] login fail", data)
                    return None
        except Exception as e:
            print("[RELOGIN] err", e)
            return None

    def save_token(self, token: str):
        # update .env
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
        # update config.json
        cfg_path = Path("config.json")
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            cfg["token"] = token
            cfg_path.write_text(json.dumps(cfg, indent=2))
        print("[RELOGIN] token saved")

    @tasks.loop(minutes=5)
    async def check_loop(self):
        token = self.bot.http.token
        ok = await self.validate(token)
        if ok:
            return
        print("[RELOGIN] token dead — attempting refresh")
        if self.email and self.password:
            new = await self.login_email(self.email, self.password)
            if new:
                self.save_token(new)
                print("[RELOGIN] new token acquired — restart process to apply")
                # soft close so external process manager can restart
                await self.bot.close()
        else:
            print("[RELOGIN] no EMAIL/PASSWORD in env — cannot auto-login")

    @check_loop.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.command(name="setlogin")
    async def setlogin(self, ctx, email: str, password: str):
        await ctx.message.delete()
        self.email = email
        self.password = password
        # persist
        env = Path(".env")
        text = env.read_text() if env.exists() else ""
        lines = [l for l in text.splitlines() if not l.startswith("EMAIL=") and not l.startswith("PASSWORD=")]
        lines.append(f"EMAIL={email}")
        lines.append(f"PASSWORD={password}")
        env.write_text("\n".join(lines) + "\n")
        await ctx.send("login creds saved", delete_after=4)

    @commands.command(name="refresh")
    async def refresh(self, ctx):
        await ctx.message.delete()
        if not self.email or not self.password:
            await ctx.send("set login first: .setlogin email pass", delete_after=5)
            return
        new = await self.login_email(self.email, self.password)
        if not new:
            await ctx.send("refresh failed", delete_after=4)
            return
        self.save_token(new)
        await ctx.send("new token saved — restart bot", delete_after=5)

    @commands.command(name="checktokenlive")
    async def checktokenlive(self, ctx):
        await ctx.message.delete()
        ok = await self.validate(self.bot.http.token)
        await ctx.send("token alive" if ok else "token dead", delete_after=4)

async def setup(bot):
    await bot.add_cog(Relogin(bot))
