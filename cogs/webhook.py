import asyncio
import random
import aiohttp
import discord
from discord.ext import commands

try:
    from evasion.delay import human_delay
except Exception:
    async def human_delay(lo=0.4, hi=1.2):
        await asyncio.sleep(random.uniform(lo, hi))

class WebhookTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._stop = False

    @commands.command(name="wspam")
    async def wspam(self, ctx, url: str, count: int = 10, *, message: str):
        await ctx.message.delete()
        self._stop = False
        count = max(1, min(count, 200))
        sent = 0
        async with aiohttp.ClientSession() as s:
            for _ in range(count):
                if self._stop:
                    break
                try:
                    async with s.post(url, json={"content": message[:2000]}) as r:
                        if r.status in (200, 204):
                            sent += 1
                except Exception:
                    pass
                await human_delay(0.6, 1.8)
        await ctx.send(f"webhook spam {sent}/{count}", delete_after=5)

    @commands.command(name="wdel")
    async def wdel(self, ctx, url: str):
        await ctx.message.delete()
        try:
            async with aiohttp.ClientSession() as s:
                async with s.delete(url) as r:
                    await ctx.send(f"delete {r.status}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="wdelall")
    async def wdelall(self, ctx):
        await ctx.message.delete()
        if not ctx.guild:
            return
        n = 0
        for ch in ctx.guild.text_channels:
            try:
                hooks = await ch.webhooks()
                for h in hooks:
                    try:
                        await h.delete()
                        n += 1
                    except Exception:
                        pass
                    await human_delay(0.3, 0.8)
            except Exception:
                pass
        await ctx.send(f"deleted {n} webhooks", delete_after=5)

    @commands.command(name="stopwspam")
    async def stopwspam(self, ctx):
        self._stop = True
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(WebhookTools(bot))
