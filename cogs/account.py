# cogs/account.py
import asyncio
import base64
import random
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class AccountTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _headers(self):
        return {"Authorization": self.bot.http.token, "Content-Type": "application/json"}

    @commands.command(name="setbio")
    async def setbio(self, ctx, *, bio: str):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.patch(f"{API}/users/@me/profile", headers=await self._headers(), json={"bio": bio}) as r:
                await ctx.send(f"bio {r.status}", delete_after=3)

    @commands.command(name="setpfp")
    async def setpfp(self, ctx, url: str = None):
        await ctx.message.delete()
        if not url and ctx.message.attachments:
            url = ctx.message.attachments[0].url
        if not url:
            return
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = base64.b64encode(await r.read()).decode()
                mime = r.content_type
            async with s.patch(f"{API}/users/@me", headers=await self._headers(),
                               json={"avatar": f"data:{mime};base64,{data}"}) as r2:
                await ctx.send(f"avatar {r2.status}", delete_after=3)

    @commands.command(name="leaveall")
    async def leaveall(self, ctx, delay: float = 0.6):
        await ctx.message.delete()
        guilds = list(self.bot.guilds)
        for g in guilds:
            try:
                await g.leave()
            except Exception:
                pass
            await asyncio.sleep(delay)
        await ctx.send(f"left {len(guilds)}", delete_after=5)

    @commands.command(name="hypesquad")
    async def hypesquad(self, ctx, house: int = 1):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/hypesquad/online", headers=await self._headers(),
                              json={"house_id": house}) as r:
                await ctx.send(f"hype {r.status}", delete_after=3)

    @commands.command(name="friendspam")
    async def friendspam(self, ctx, username: str, count: int = 5):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            for _ in range(count):
                async with s.post(f"{API}/users/@me/relationships",
                                  headers=await self._headers(),
                                  json={"username": username}) as r:
                    print(f"[FRIEND] {r.status}")
                await asyncio.sleep(random.uniform(1.2, 2.8))

async def setup(bot):
    await bot.add_cog(AccountTools(bot))
