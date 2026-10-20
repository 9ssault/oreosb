import asyncio
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Friends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _h(self):
        return {"Authorization": self.bot.http.token, "Content-Type": "application/json"}

    @commands.command(name="friends")
    async def friends(self, ctx):
        await ctx.message.delete()
        rels = [r for r in self.bot.friends]
        lines = [f"{r.user}" for r in rels[:40]]
        await ctx.send(f"**friends ({len(rels)})**\n" + "\n".join(lines), delete_after=20)

    @commands.command(name="addfriend")
    async def addfriend(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.put(f"{API}/users/@me/relationships/{user.id}", headers=await self._h(), json={}) as r:
                await ctx.send(f"addfriend {r.status}", delete_after=4)

    @commands.command(name="removefriend")
    async def removefriend(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.delete(f"{API}/users/@me/relationships/{user.id}", headers=await self._h()) as r:
                await ctx.send(f"removefriend {r.status}", delete_after=4)

    @commands.command(name="block")
    async def block(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.put(f"{API}/users/@me/relationships/{user.id}", headers=await self._h(), json={"type": 2}) as r:
                await ctx.send(f"block {r.status}", delete_after=4)

    @commands.command(name="unblock")
    async def unblock(self, ctx, user: discord.User):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.delete(f"{API}/users/@me/relationships/{user.id}", headers=await self._h()) as r:
                await ctx.send(f"unblock {r.status}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Friends(bot))
