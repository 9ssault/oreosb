import asyncio
import aiohttp
import json
import os
from pathlib import Path
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class TokenReset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _h(self, token=None):
        t = token or self.bot.http.token
        return {
            "Authorization": t,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

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
            data = json.loads(cfg.read_text())
            data["token"] = token
            cfg.write_text(json.dumps(data, indent=2))
        print("[TOKEN] saved new token")

    @commands.command(name="resettoken")
    async def resettoken(self, ctx):
        """POST /auth/reset to invalidate session and get flow - requires password re-login after"""
        await ctx.message.delete()
        await ctx.send("use .fullreset email password  (resets sessions then logs in fresh)", delete_after=8)

    @commands.command(name="fullreset")
    async def fullreset(self, ctx, email: str, password: str):
        """logout all sessions + login again for brand new token"""
        await ctx.message.delete()
        status = await ctx.send("resetting…")
        # 1) try disable all sessions (requires password)
        async with aiohttp.ClientSession() as s:
            # logout other sessions
            try:
                async with s.post(
                    f"{API}/auth/logout",
                    headers=self._h(),
                    json={"provider": None, "token": None, "account_token": None},
                ) as r:
                    pass
            except Exception:
                pass
            # login for fresh token
            payload = {
                "login": email,
                "password": password,
                "undelete": False,
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            }
            async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                data = await r.json(content_type=None)
                if r.status == 200 and "token" in data:
                    new = data["token"]
                    self.save_token(new)
                    await status.edit(content=f"new token saved — restart bot\n`{new[:20]}...`")
                    return
                if data.get("mfa") or data.get("ticket"):
                    await status.edit(content="2FA required — complete login manually then .settoken")
                    return
                await status.edit(content=f"fail {r.status} {str(data)[:120]}")

    @commands.command(name="settoken")
    async def settoken(self, ctx, token: str):
        await ctx.message.delete()
        self.save_token(token)
        await ctx.send("token written to .env — restart", delete_after=5)

    @commands.command(name="sessions")
    async def sessions(self, ctx):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/auth/sessions", headers=self._h()) as r:
                if r.status != 200:
                    await ctx.send(f"fail {r.status}", delete_after=5)
                    return
                data = await r.json()
        user_sessions = data.get("user_sessions") or data.get("sessions") or []
        lines = []
        for i, sess in enumerate(user_sessions[:15]):
            ca = sess.get("client_info") or {}
            lines.append(f"`{i}` {ca.get('os','?')} {ca.get('platform','?')} {sess.get('id','')[:8]}")
        await ctx.send("sessions:\n" + ("\n".join(lines) or "none"), delete_after=20)

async def setup(bot):
    await bot.add_cog(TokenReset(bot))
