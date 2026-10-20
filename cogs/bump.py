import asyncio
import discord
from discord.ext import commands

class Bump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = None

    @commands.command(name="autobump")
    async def autobump(self, ctx, delay: int = 7200):
        await ctx.message.delete()
        if self.task:
            self.task.cancel()
        async def loop():
            while True:
                try:
                    await ctx.channel.send("!d bump")
                except Exception:
                    pass
                await asyncio.sleep(delay)
        self.task = asyncio.create_task(loop())
        await ctx.send(f"autobump every {delay}s", delete_after=4)

    @commands.command(name="stopbump")
    async def stopbump(self, ctx):
        await ctx.message.delete()
        if self.task:
            self.task.cancel()
            self.task = None
        await ctx.send("bump stopped", delete_after=3)

async def setup(bot):
    await bot.add_cog(Bump(bot))
