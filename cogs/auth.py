import asyncio
import aiohttp
import json
import os
import base64
import random
import string
import discord
from discord.ext import commands
from colorama import Fore

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
            "client_version": "1.0.9181",
            "os_version": "10.0.22631",
            "os_arch": "x64",
            "system_locale": "en-US",
            "client_build_number": 373069,
            "client_event_source": None,
        }
        return base64.b64encode(json.dumps(props).encode()).decode()

class Auth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def _session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _headers(self, token=None):
        h = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/138.0.7204.92 Electron/36.2.1 Safari/537.36",
            "X-Super-Properties": await _super_props(),
        }
        if token:
            h["Authorization"] = token
        return h

    @commands.command(name="login")
    async def login(self, ctx, method: str = None, *, credentials: str = None):
        await ctx.message.delete()
        if not method:
            await ctx.send("usage: `.login email:pass` or `.login token <token>`", delete_after=6)
            return
        if method.lower() == "token" and credentials:
            token = credentials.strip()
            ok = await self._validate(token)
            if ok:
                await ctx.send(f"token valid → `{ok['username']}`", delete_after=8)
                with open("config.json") as f:
                    cfg = json.load(f)
                cfg["token"] = token
                with open("config.json", "w") as f:
                    json.dump(cfg, f, indent=2)
                await ctx.send("saved to config — restart to apply", delete_after=5)
            else:
                await ctx.send("invalid token", delete_after=4)
            return
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
        headers = await self._headers()
        try:
            async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                data = await r.json(content_type=None)
                if r.status == 200 and isinstance(data, dict) and "token" in data:
                    return {"token": data["token"]}
                if isinstance(data, dict) and (data.get("mfa") or data.get("ticket")):
                    return {"error": "2FA required — use token login or provide ticket"}
                return {"error": (data.get("message") if isinstance(data, dict) else str(data))[:120]}
        except Exception as e:
            return {"error": str(e)}

    async def _validate(self, token: str):
        s = await self._session()
        headers = await self._headers(token)
        try:
            async with s.get(f"{API}/users/@me", headers=headers) as r:
                if r.status == 200:
                    return await r.json()
        except Exception:
            pass
        return None

    @commands.command(name="tokens")
    async def tokens(self, ctx):
        await ctx.message.delete()
        try:
            with open("tokens.txt") as f:
                toks = [l.strip() for l in f if l.strip()]
        except FileNotFoundError:
            await ctx.send("no tokens.txt", delete_after=3)
            return
        valid = dead = 0
        lines = []
        for t in toks[:30]:
            info = await self._validate(t)
            if info:
                valid += 1
                nitro = "N" if info.get("premium_type", 0) else "-"
                lines.append(f"`{t[:12]}...` {info['username']} [{nitro}]")
            else:
                dead += 1
            await asyncio.sleep(0.35)
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
        await ctx.message.delete()
        uid = str(random.randint(10**17, 10**18 - 1))
        part1 = base64.b64encode(uid.encode()).decode().rstrip("=")
        part2 = "".join(random.choices(string.ascii_letters + string.digits + "-_", k=6))
        part3 = "".join(random.choices(string.ascii_letters + string.digits + "-_", k=27))
        fake = f"{part1}.{part2}.{part3}"
        await ctx.send(f"fake pattern:\n`{fake}`", delete_after=12)

async def setup(bot):
    await bot.add_cog(Auth(bot))
