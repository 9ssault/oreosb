import asyncio
import random
import discord
from discord.ext import commands

try:
    from evasion.delay import human_delay, jitter
except Exception:
    async def human_delay(lo=0.4, hi=1.2):
        await asyncio.sleep(random.uniform(lo, hi))
    def jitter(base, spread=0.3):
        return max(0.05, base + random.uniform(-spread, spread))

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @commands.command(name="spam")
    async def spam(self, ctx, count: int, delay: float, *, message: str):
        await ctx.message.delete()
        self.running = True
        count = max(1, min(count, 500))
        for _ in range(count):
            if not self.running:
                break
            try:
                await ctx.channel.send(message[:2000])
            except Exception:
                break
            await asyncio.sleep(jitter(delay, 0.35))
        self.running = False

    @commands.command(name="ghostping")
    async def ghostping(self, ctx, target: discord.Member):
        await ctx.message.delete()
        m = await ctx.channel.send(f"{target.mention}")
        await asyncio.sleep(0.12)
        try:
            await m.delete()
        except Exception:
            pass

    @commands.command(name="editloop")
    async def editloop(self, ctx, count: int, *, messages: str):
        await ctx.message.delete()
        msgs = [m.strip() for m in messages.split("|") if m.strip()]
        if not msgs:
            return
        sent = await ctx.channel.send(msgs[0])
        for i in range(1, max(1, min(count, 100))):
            await asyncio.sleep(jitter(0.9, 0.2))
            try:
                await sent.edit(content=msgs[i % len(msgs)][:2000])
            except Exception:
                break

    @commands.command(name="stopspam")
    async def stopspam(self, ctx):
        self.running = False
        await ctx.message.delete()

    @commands.command(name="purge")
    async def purge(self, ctx, limit: int = 100):
        await ctx.message.delete()
        limit = max(1, min(limit, 500))
        count = 0
        async for m in ctx.channel.history(limit=800):
            if m.author == self.bot.user and count < limit:
                try:
                    await m.delete()
                    count += 1
                except Exception:
                    pass
                await human_delay(0.25, 0.55)
        await ctx.send(f"purged {count}", delete_after=3)

async def setup(bot):
    await bot.add_cog(Spam(bot))
