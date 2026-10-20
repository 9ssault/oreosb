import asyncio
import base64
import aiohttp
from pathlib import Path
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _load_tokens(self):
        p = Path("tokens.txt")
        if not p.exists():
            return []
        return [l.strip() for l in p.read_text().splitlines() if l.strip()]

    def _save_tokens(self, toks):
        Path("tokens.txt").write_text("\n".join(toks) + ("\n" if toks else ""))

    async def _headers(self, token):
        return {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }

    async def _patch_me(self, token, payload):
        async with aiohttp.ClientSession() as s:
            async with s.patch(f"{API}/users/@me", headers=await self._headers(token), json=payload) as r:
                return r.status

    async def _patch_profile(self, token, payload):
        async with aiohttp.ClientSession() as s:
            async with s.patch(f"{API}/users/@me/profile", headers=await self._headers(token), json=payload) as r:
                return r.status

    @commands.command(name="tlist")
    async def tlist(self, ctx):
        await ctx.message.delete()
        toks = self._load_tokens()
        if not toks:
            await ctx.send("tokens.txt empty — use `.addtoken`", delete_after=4)
            return
        lines = []
        for i, t in enumerate(toks[:40]):
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{API}/users/@me", headers=await self._headers(t)) as r:
                    if r.status == 200:
                        d = await r.json()
                        nitro = "N" if d.get("premium_type") else "-"
                        lines.append(f"`{i}` {d.get('username')} [{nitro}] `{t[:12]}...`")
                    else:
                        lines.append(f"`{i}` dead `{t[:12]}...`")
            await asyncio.sleep(0.35)
        await ctx.send("**tokens**\n" + "\n".join(lines), delete_after=25)

    @commands.command(name="addtoken")
    async def addtoken(self, ctx, token: str):
        await ctx.message.delete()
        token = token.strip()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/users/@me", headers=await self._headers(token)) as r:
                if r.status != 200:
                    await ctx.send("invalid token", delete_after=4)
                    return
                d = await r.json()
        toks = self._load_tokens()
        if token not in toks:
            toks.append(token)
            self._save_tokens(toks)
        await ctx.send(f"added **{d.get('username')}** — total {len(toks)}", delete_after=6)

    @commands.command(name="rmtoken")
    async def rmtoken(self, ctx, partial: str):
        await ctx.message.delete()
        toks = self._load_tokens()
        new = [t for t in toks if partial not in t]
        self._save_tokens(new)
        await ctx.send(f"removed — left {len(new)}", delete_after=4)

    @commands.command(name="setallpfp")
    async def setallpfp(self, ctx, url: str):
        await ctx.message.delete()
        toks = self._load_tokens()
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                raw = await r.read()
                mime = r.content_type or "image/png"
        data = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
        ok = 0
        for t in toks:
            if await self._patch_me(t, {"avatar": data}) == 200:
                ok += 1
            await asyncio.sleep(1.2)
        await ctx.send(f"setallpfp {ok}/{len(toks)}", delete_after=6)

    @commands.command(name="setallbio")
    async def setallbio(self, ctx, *, bio: str):
        await ctx.message.delete()
        toks = self._load_tokens()
        ok = 0
        for t in toks:
            if await self._patch_profile(t, {"bio": bio[:190]}) in (200, 204):
                ok += 1
            await asyncio.sleep(1.0)
        await ctx.send(f"setallbio {ok}/{len(toks)}", delete_after=6)

    @commands.command(name="setallstatus")
    async def setallstatus(self, ctx, status: str = "online"):
        await ctx.message.delete()
        map_ = {"online": "online", "dnd": "dnd", "idle": "idle", "invisible": "invisible"}
        st = map_.get(status.lower(), "online")
        toks = self._load_tokens()
        ok = 0
        for t in toks:
            async with aiohttp.ClientSession() as s:
                async with s.patch(
                    f"{API}/users/@me/settings",
                    headers=await self._headers(t),
                    json={"status": st},
                ) as r:
                    if r.status in (200, 204):
                        ok += 1
            await asyncio.sleep(0.8)
        await ctx.send(f"setallstatus {ok}/{len(toks)}", delete_after=5)

    @commands.command(name="setallgame")
    async def setallgame(self, ctx, *, game: str):
        await ctx.message.delete()
        toks = self._load_tokens()
        ok = 0
        for t in toks:
            async with aiohttp.ClientSession() as s:
                payload = {"activities": [{"type": 0, "name": game[:128]}]}
                async with s.patch(
                    f"{API}/users/@me/settings",
                    headers=await self._headers(t),
                    json=payload,
                ) as r:
                    if r.status in (200, 204):
                        ok += 1
            await asyncio.sleep(0.9)
        await ctx.send(f"setallgame {ok}/{len(toks)}", delete_after=5)

    @commands.command(name="leavealltokens")
    async def leavealltokens(self, ctx, guild_id: int):
        await ctx.message.delete()
        toks = self._load_tokens()
        ok = 0
        for t in toks:
            async with aiohttp.ClientSession() as s:
                async with s.delete(
                    f"{API}/users/@me/guilds/{guild_id}",
                    headers=await self._headers(t),
                ) as r:
                    if r.status in (204, 200):
                        ok += 1
            await asyncio.sleep(0.7)
        await ctx.send(f"leavealltokens {ok}/{len(toks)}", delete_after=5)

    @commands.command(name="joinaltokens")
    async def joinaltokens(self, ctx, code: str):
        await ctx.message.delete()
        code = code.replace("https://discord.gg/", "").replace("discord.gg/", "").strip()
        toks = self._load_tokens()
        ok = 0
        for t in toks:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    f"{API}/invites/{code}",
                    headers=await self._headers(t),
                    json={},
                ) as r:
                    if r.status in (200, 204):
                        ok += 1
            await asyncio.sleep(1.5)
        await ctx.send(f"joinaltokens {ok}/{len(toks)}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Manager(bot))
