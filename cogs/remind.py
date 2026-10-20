import asyncio
import discord
from discord.ext import commands

class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remind")
    async def remind(self, ctx, seconds: int, *, message: str):
        await ctx.message.delete()
        seconds = max(1, min(seconds, 86400))
        await ctx.send(f"remind in {seconds}s", delete_after=3)

        async def job():
            await asyncio.sleep(seconds)
            try:
                await ctx.author.send(f"reminder: {message[:1500]}")
            except Exception:
                try:
                    await ctx.send(f"{ctx.author.mention} reminder: {message[:1500]}", delete_after=30)
                except Exception:
                    pass

        asyncio.create_task(job())

    @commands.command(name="timer")
    async def timer(self, ctx, seconds: int):
        await ctx.message.delete()
        seconds = max(1, min(seconds, 3600))
        await ctx.send(f"timer {seconds}s", delete_after=3)
        await asyncio.sleep(seconds)
        try:
            await ctx.send(f"{ctx.author.mention} time", delete_after=10)
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Remind(bot))
