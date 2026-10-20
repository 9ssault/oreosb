import asyncio
import discord
from discord.ext import commands

class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remind")
    async def remind(self, ctx, seconds: int, *, text: str):
        await ctx.message.delete()
        await ctx.send(f"remind in {seconds}s", delete_after=3)
        await asyncio.sleep(seconds)
        try:
            await ctx.channel.send(f"remind: {text}")
        except Exception:
            pass

    @commands.command(name="timer")
    async def timer(self, ctx, seconds: int):
        await ctx.message.delete()
        m = await ctx.send(f"timer `{seconds}`")
        await asyncio.sleep(seconds)
        try:
            await m.edit(content="timer done")
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Remind(bot))
