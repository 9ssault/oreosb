import asyncio
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Friends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _h(self):
        return {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
        }

    @commands.command(name="friends")
    async def friends(self, ctx):
        await ctx.message.delete()
        rels = list(getattr(self.bot, "friends", []) or [])
        lines = []
        for r in rels[:50]:
            u = getattr(r, "user", r)
            lines.append(f"`{u.id}` {u}")
        await ctx.send(f"**friends ({len(rels)})**\n" + ("\n".join(lines) or "none"), delete_after=25)

    @commands.command(name="addfriend")
    async def addfriend(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.put(
                f"{API}/users/@me/relationships/{user.id}",
                headers=await self._h(),
                json={},
            ) as r:
                await ctx.send(f"addfriend `{r.status}`", delete_after=4)

    @commands.command(name="removefriend")
    async def removefriend(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.delete(
                f"{API}/users/@me/relationships/{user.id}",
                headers=await self._h(),
            ) as r:
                await ctx.send(f"removefriend `{r.status}`", delete_after=4)

    @commands.command(name="block")
    async def block(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.put(
                f"{API}/users/@me/relationships/{user.id}",
                headers=await self._h(),
                json={"type": 2},
            ) as r:
                await ctx.send(f"block `{r.status}`", delete_after=4)

    @commands.command(name="unblock")
    async def unblock(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.delete(
                f"{API}/users/@me/relationships/{user.id}",
                headers=await self._h(),
            ) as r:
                await ctx.send(f"unblock `{r.status}`", delete_after=4)

    @commands.command(name="incoming")
    async def incoming(self, ctx):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/users/@me/relationships", headers=await self._h()) as r:
                if r.status != 200:
                    await ctx.send(f"fail {r.status}", delete_after=4)
                    return
                data = await r.json()
        pending = [d for d in data if d.get("type") == 3]
        lines = [f"`{d.get('id')}` {d.get('user', {}).get('username', '?')}" for d in pending[:30]]
        await ctx.send(f"incoming ({len(pending)})\n" + ("\n".join(lines) or "none"), delete_after=15)

    @commands.command(name="acceptall")
    async def acceptall(self, ctx):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/users/@me/relationships", headers=await self._h()) as r:
                data = await r.json() if r.status == 200 else []
        n = 0
        for d in data:
            if d.get("type") != 3:
                continue
            uid = d.get("id") or (d.get("user") or {}).get("id")
            if not uid:
                continue
            async with aiohttp.ClientSession() as s:
                async with s.put(
                    f"{API}/users/@me/relationships/{uid}",
                    headers=await self._h(),
                    json={},
                ) as r:
                    if r.status in (200, 204):
                        n += 1
            await asyncio.sleep(0.8)
        await ctx.send(f"accepted {n}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Friends(bot))
