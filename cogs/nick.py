import asyncio
import random
import discord
from discord.ext import commands

try:
    from evasion.delay import human_delay
except Exception:
    async def human_delay(lo=0.4, hi=0.9):
        await asyncio.sleep(random.uniform(lo, hi))

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nick")
    async def nick(self, ctx, *, name: str = None):
        await ctx.message.delete()
        if not ctx.guild:
            return
        try:
            await ctx.guild.me.edit(nick=name)
            await ctx.send(f"nick → `{name or 'reset'}`", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="massnick")
    async def massnick(self, ctx, *, name: str):
        await ctx.message.delete()
        if not ctx.guild:
            return
        ok = 0
        for m in list(ctx.guild.members)[:100]:
            if ctx.guild.me and m.top_role >= ctx.guild.me.top_role:
                continue
            try:
                await m.edit(nick=name[:32])
                ok += 1
            except Exception:
                pass
            await human_delay(0.4, 0.9)
        await ctx.send(f"massnick {ok}", delete_after=4)

    @commands.command(name="clearnicks")
    async def clearnicks(self, ctx, confirm: str = None):
        await ctx.message.delete()
        if confirm != "confirm":
            await ctx.send("`clearnicks confirm`", delete_after=4)
            return
        ok = 0
        for m in list(ctx.guild.members)[:100]:
            if not m.nick:
                continue
            if ctx.guild.me and m.top_role >= ctx.guild.me.top_role:
                continue
            try:
                await m.edit(nick=None)
                ok += 1
            except Exception:
                pass
            await human_delay(0.35, 0.8)
        await ctx.send(f"cleared {ok} nicks", delete_after=4)

async def setup(bot):
    await bot.add_cog(Nick(bot))
