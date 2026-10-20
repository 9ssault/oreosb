import asyncio
import discord
from discord.ext import commands

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nick")
    async def nick(self, ctx, *, name: str = None):
        await ctx.message.delete()
        try:
            await ctx.guild.me.edit(nick=name)
            await ctx.send(f"nick → {name or 'reset'}", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="massnick")
    async def massnick(self, ctx, *, name: str):
        await ctx.message.delete()
        ok = 0
        for m in list(ctx.guild.members)[:80]:
            if m.top_role >= ctx.guild.me.top_role:
                continue
            try:
                await m.edit(nick=name)
                ok += 1
            except Exception:
                pass
            await asyncio.sleep(0.5)
        await ctx.send(f"massnick {ok}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Nick(bot))
