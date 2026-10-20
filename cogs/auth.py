# cogs/auth.py — login system + token management
import asyncio
import aiohttp
import json
import os
import discord
from discord.ext import commands
from colorama import Fore

API = "https://discord.com/api/v10"

class Auth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def _session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    @commands.command(name="login")
    async def login(self, ctx, method: str = None, *, credentials: str = None):
        """login email:pass  OR  login token <token>"""
        await ctx.message.delete()
        if not method:
            await ctx.send("usage: `.login email:pass` or `.login token <token>`", delete_after=6)
            return
        if method.lower() == "token" and credentials:
            token = credentials.strip()
            ok = await self._validate(token)
            if ok:
                await ctx.send(f"token valid → `{ok['username']}`", delete_after=8)
                # optionally switch (requires restart for full switch)
                with open("config.json") as f:
                    cfg = json.load(f)
                cfg["token"] = token
                with open("config.json", "w") as f:
                    json.dump(cfg, f, indent=2)
                await ctx.send("saved to config — restart to apply", delete_after=5)
            else:
                await ctx.send("invalid token", delete_after=4)
            return
        # email:pass path
        if ":" in method and not credentials:
            credentials = method
        if not credentials or ":" not in credentials:
            await ctx.send("format: email:password", delete_after=4)
            return
        email, password = credentials.split(":", 1)
        result = await self._login_email(email.strip(), password.strip())
        if result.get("token"):
            tok = result["token"]
            await ctx.send(f"logged in → token starts `{tok[:20]}...`", delete_after=10)
            with open("config.json") as f:
                cfg = json.load(f)
            cfg["token"] = tok
            with open("config.json", "w") as f:
                json.dump(cfg, f, indent=2)
            # also append to tokens.txt
            with open("tokens.txt", "a") as f:
                f.write(tok + "\n")
            await ctx.send("saved + appended tokens.txt — restart to use", delete_after=5)
        else:
            await ctx.send(f"login failed: {result.get('error', 'unknown')}", delete_after=8)

    async def _login_email(self, email: str, password: str) -> dict:
        s = await self._session()
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
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEzNi4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEzNi4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTM2LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MzczMDY5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
        }
        try:
            async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                data = await r.json(content_type=None)
                if r.status == 200 and "token" in data:
                    return {"token": data["token"]}
                if "mfa" in data or data.get("mfa"):
                    return {"error": "2FA required — use token login or provide ticket"}
                return {"error": data.get("message") or str(data)[:120]}
        except Exception as e:
            return {"error": str(e)}

    async def _validate(self, token: str):
        s = await self._session()
        headers = {"Authorization": token, "Content-Type": "application/json"}
        try:
            async with s.get(f"{API}/users/@me", headers=headers) as r:
                if r.status == 200:
                    return await r.json()
        except Exception:
            pass
        return None

    @commands.command(name="tokens")
    async def tokens(self, ctx):
        """list managed tokens status"""
        await ctx.message.delete()
        try:
            with open("tokens.txt") as f:
                toks = [l.strip() for l in f if l.strip()]
        except FileNotFoundError:
            await ctx.send("no tokens.txt", delete_after=3)
            return
        valid = locked = dead = 0
        lines = []
        for t in toks[:30]:  # cap
            info = await self._validate(t)
            if info:
                valid += 1
                nitro = "N" if info.get("premium_type", 0) else "-"
                lines.append(f"`{t[:12]}...` {info['username']} [{nitro}]")
            else:
                dead += 1
            await asyncio.sleep(0.4)
        summary = f"valid:{valid} dead:{dead} (showing up to 30)"
        body = "\n".join(lines) or "none"
        await ctx.send(f"{summary}\n{body}", delete_after=20)

    @commands.command(name="addtoken")
    async def addtoken(self, ctx, token: str):
        await ctx.message.delete()
        info = await self._validate(token)
        if not info:
            await ctx.send("invalid", delete_after=3)
            return
        with open("tokens.txt", "a") as f:
            f.write(token.strip() + "\n")
        await ctx.send(f"added {info['username']}", delete_after=4)

    @commands.command(name="rmtoken")
    async def rmtoken(self, ctx, partial: str):
        await ctx.message.delete()
        try:
            with open("tokens.txt") as f:
                toks = [l.strip() for l in f if l.strip()]
        except FileNotFoundError:
            return
        new = [t for t in toks if partial not in t]
        with open("tokens.txt", "w") as f:
            f.write("\n".join(new) + ("\n" if new else ""))
        await ctx.send(f"removed matches — left {len(new)}", delete_after=4)

    @commands.command(name="gentoken")
    async def gentoken(self, ctx):
        """generate realistic-looking fake token (for testing patterns)"""
        await ctx.message.delete()
        import random, string, base64
        def b64(n):
            return base64.b64encode(os.urandom(n)).decode().rstrip("=").replace("+", "").replace("/", "")[:n]
        # user id part (snowflake-ish)
        uid = str(random.randint(10**17, 10**18 - 1))
        part1 = base64.b64encode(uid.encode()).decode().rstrip("=")
        part2 = "".join(random.choices(string.ascii_letters + string.digits + "-_", k=6))
        part3 = "".join(random.choices(string.ascii_letters + string.digits + "-_", k=27))
        fake = f"{part1}.{part2}.{part3}"
        await ctx.send(f"fake pattern:\n`{fake}`", delete_after=12)

async def setup(bot):
    await bot.add_cog(Auth(bot))
