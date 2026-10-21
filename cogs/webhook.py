# cogs/webhook.py
import asyncio
import random
import aiohttp
import discord
from discord.ext import commands
from core_utils import owner_check

class WebhookTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @commands.command(name="wspam")
    @owner_check()
    async def wspam(self, ctx, url: str, count: int, delay: float, *, message: str):
        await ctx.message.delete()
        self.running = True
        sent = 0
        async with aiohttp.ClientSession() as s:
            for _ in range(count):
                if not self.running:
                    break
                payload = {"content": message, "username": "OreoSB"}
                async with s.post(url, json=payload) as r:
                    if r.status in (200, 204):
                        sent += 1
                    elif r.status == 429:
                        data = await r.json(content_type=None)
                        await asyncio.sleep(float(data.get("retry_after", 1)))
                await asyncio.sleep(delay + random.uniform(0, 0.25))
        await ctx.send(f"webhook {sent}/{count}", delete_after=4)

    @commands.command(name="wdel")
    @owner_check()
    async def wdel(self, ctx, url: str):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.delete(url) as r:
                await ctx.send("deleted" if r.status == 204 else f"fail {r.status}", delete_after=3)

    @commands.command(name="wdelall")
    @owner_check()
    async def wdelall(self, ctx):
        await ctx.message.delete()
        count = 0
        for ch in ctx.guild.channels:
            try:
                for h in await ch.webhooks():
                    await h.delete()
                    count += 1
                    await asyncio.sleep(0.3)
            except Exception:
                pass
        await ctx.send(f"deleted {count} hooks", delete_after=4)

async def setup(bot):
    await bot.add_cog(WebhookTools(bot))
