import asyncio
import aiohttp
import discord
from discord.ext import commands
from datetime import datetime

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        created = u.created_at.strftime("%Y-%m-%d")
        await ctx.send(f"**{u}**\nid `{u.id}`\ncreated {created}\nbot {u.bot}", delete_after=12)

    @commands.command(name="avatar")
    async def avatar(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        await ctx.send(str(u.display_avatar.url), delete_after=10)

    @commands.command(name="servericon")
    async def servericon(self, ctx):
        await ctx.message.delete()
        if ctx.guild and ctx.guild.icon:
            await ctx.send(str(ctx.guild.icon.url), delete_after=10)

    @commands.command(name="firstmessage")
    async def firstmessage(self, ctx):
        await ctx.message.delete()
        async for m in ctx.channel.history(limit=1, oldest_first=True):
            await ctx.send(f"first: {m.jump_url}", delete_after=8)
            return

    @commands.command(name="id")
    async def id_(self, ctx, target: discord.User = None):
        await ctx.message.delete()
        t = target or ctx.author
        await ctx.send(f"`{t.id}`", delete_after=6)

    @commands.command(name="pingweb")
    async def pingweb(self, ctx, url: str):
        await ctx.message.delete()
        try:
            t0 = datetime.utcnow()
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=8) as r:
                    ms = (datetime.utcnow() - t0).total_seconds() * 1000
                    await ctx.send(f"{r.status} `{ms:.0f}ms`", delete_after=6)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Util(bot))
