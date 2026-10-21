import asyncio
import json
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands

from core_utils import owner_check, load_persist, save_persist

API = "https://discord.com/api/v10"
DATA = Path("data")
DATA.mkdir(exist_ok=True)


class AutoJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        p = load_persist()
        self.codes = list(p.get("autojoin_codes") or [])
        self.guild_ids = set(str(x) for x in (p.get("autoleave_guilds") or []))
        self._task = None

    def _save(self):
        p = load_persist()
        p["autojoin_codes"] = self.codes
        p["autoleave_guilds"] = list(self.guild_ids)
        save_persist(p)

    def _headers(self):
        return {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    @commands.command(name="autojoin")
    @owner_check()
    async def autojoin(self, ctx, code: str = None):
        await ctx.message.delete()
        if not code:
            await ctx.send("codes: " + ", ".join(self.codes) or "none", delete_after=8)
            return
        code = code.replace("https://discord.gg/", "").replace("discord.gg/", "").strip()
        if code not in self.codes:
            self.codes.append(code)
            self._save()
        # join now
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/invites/{code}", headers=self._headers(), json={}) as r:
                await ctx.send(f"join {code} → {r.status}", delete_after=5)

    @commands.command(name="autojoinrm")
    @owner_check()
    async def autojoinrm(self, ctx, code: str):
        await ctx.message.delete()
        code = code.replace("https://discord.gg/", "").replace("discord.gg/", "").strip()
        self.codes = [c for c in self.codes if c != code]
        self._save()
        await ctx.send("removed", delete_after=3)

    @commands.command(name="joinall")
    @owner_check()
    async def joinall(self, ctx):
        await ctx.message.delete()
        ok = 0
        async with aiohttp.ClientSession() as s:
            for code in list(self.codes):
                try:
                    async with s.post(
                        f"{API}/invites/{code}", headers=self._headers(), json={}
                    ) as r:
                        if r.status in (200, 204):
                            ok += 1
                except Exception:
                    pass
                await asyncio.sleep(1.5)
        await ctx.send(f"joined {ok}/{len(self.codes)}", delete_after=6)

    @commands.command(name="autoleave")
    @owner_check()
    async def autoleave(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        gid = str(guild_id or (ctx.guild.id if ctx.guild else ""))
        if not gid:
            await ctx.send("need guild id", delete_after=3)
            return
        self.guild_ids.add(gid)
        self._save()
        await ctx.send(f"autoleave +{gid}", delete_after=4)

    @commands.command(name="autoleaverm")
    @owner_check()
    async def autoleaverm(self, ctx, guild_id: int):
        await ctx.message.delete()
        self.guild_ids.discard(str(guild_id))
        self._save()
        await ctx.send("removed", delete_after=3)

    @commands.command(name="leaveguild")
    @owner_check()
    async def leaveguild(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        gid = guild_id or (ctx.guild.id if ctx.guild else None)
        if not gid:
            return
        async with aiohttp.ClientSession() as s:
            async with s.delete(f"{API}/users/@me/guilds/{gid}", headers=self._headers()) as r:
                await ctx.send(f"leave {gid} → {r.status}", delete_after=5)

    @commands.command(name="leaveall")
    @owner_check()
    async def leaveall(self, ctx, delay: float = 1.0):
        await ctx.message.delete()
        ok = 0
        async with aiohttp.ClientSession() as s:
            for g in list(self.bot.guilds):
                try:
                    async with s.delete(
                        f"{API}/users/@me/guilds/{g.id}", headers=self._headers()
                    ) as r:
                        if r.status in (200, 204):
                            ok += 1
                except Exception:
                    pass
                await asyncio.sleep(max(0.3, delay))
        await ctx.send(f"left {ok}", delete_after=5)

    @commands.Cog.listener()
    async def on_ready(self):
        # process autoleave list
        for gid in list(self.guild_ids):
            g = self.bot.get_guild(int(gid)) if gid.isdigit() else None
            if g:
                try:
                    await g.leave()
                    print(f"[AUTOLEAVE] left {gid}")
                except Exception:
                    pass


async def setup(bot):
    await bot.add_cog(AutoJoin(bot))
