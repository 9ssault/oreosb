import asyncio
import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jobs = []

    @commands.command(name="schedule")
    async def schedule(self, ctx, seconds: int, *, message: str):
        await ctx.message.delete()
        async def job():
            await asyncio.sleep(seconds)
            try:
                await ctx.channel.send(message)
            except Exception:
                pass
        self.jobs.append(asyncio.create_task(job()))
        await ctx.send(f"scheduled in {seconds}s", delete_after=4)

    @commands.command(name="loopmsg")
    async def loopmsg(self, ctx, count: int, delay: float, *, message: str):
        await ctx.message.delete()
        for _ in range(count):
            await ctx.channel.send(message)
            await asyncio.sleep(delay)

async def setup(bot):
    await bot.add_cog(Scheduler(bot))
