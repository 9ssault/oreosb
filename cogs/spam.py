# cogs/spam.py
import asyncio
import random
import discord
from discord.ext import commands

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @commands.command(name="spam")
    async def spam(self, ctx, count: int, delay: float, *, message: str):
        await ctx.message.delete()
        self.running = True
        for _ in range(count):
            if not self.running:
                break
            await ctx.channel.send(message)
            await asyncio.sleep(delay + random.uniform(0, 0.4))

    @commands.command(name="ghostping")
    async def ghostping(self, ctx, target: discord.Member):
        await ctx.message.delete()
        m = await ctx.channel.send(f"{target.mention}")
        await asyncio.sleep(0.12)
        await m.delete()

    @commands.command(name="editloop")
    async def editloop(self, ctx, count: int, *, messages: str):
        await ctx.message.delete()
        msgs = [m.strip() for m in messages.split("|")]
        sent = await ctx.channel.send(msgs[0])
        for i in range(1, count):
            await asyncio.sleep(0.9)
            await sent.edit(content=msgs[i % len(msgs)])

    @commands.command(name="stopspam")
    async def stopspam(self, ctx):
        self.running = False
        await ctx.message.delete()

    @commands.command(name="purge")
    async def purge(self, ctx, limit: int = 100):
        await ctx.message.delete()
        count = 0
        async for m in ctx.channel.history(limit=500):
            if m.author == self.bot.user and count < limit:
                try:
                    await m.delete()
                    count += 1
                except Exception:
                    pass
                await asyncio.sleep(0.35)
        await ctx.send(f"purged {count}", delete_after=3)

async def setup(bot):
    await bot.add_cog(Spam(bot))
