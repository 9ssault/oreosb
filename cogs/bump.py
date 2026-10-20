import asyncio
import discord
from discord.ext import commands

class Bump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = None

    @commands.command(name="autobump")
    async def autobump(self, ctx, interval: int = 7200):
        await ctx.message.delete()
        interval = max(3600, interval)
        if self.task:
            self.task.cancel()
        ch = ctx.channel

        async def loop():
            while True:
                try:
                    await ch.send("!d bump")
                except Exception:
                    pass
                await asyncio.sleep(interval)

        self.task = asyncio.create_task(loop())
        await ctx.send(f"autobump every {interval}s", delete_after=4)

    @commands.command(name="stopbump")
    async def stopbump(self, ctx):
        await ctx.message.delete()
        if self.task:
            self.task.cancel()
            self.task = None
        await ctx.send("bump stopped", delete_after=3)

async def setup(bot):
    await bot.add_cog(Bump(bot))
