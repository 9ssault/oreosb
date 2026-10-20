import urllib.parse
import aiohttp
import discord
from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        await ctx.message.delete()
        q = urllib.parse.quote(city.strip())
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://wttr.in/{q}?format=%l:+%c+%t+%h+%w",
                    headers={"User-Agent": "curl/8.0"},
                    timeout=12,
                ) as r:
                    txt = (await r.text()).strip()
            if not txt or "Unknown location" in txt:
                await ctx.send("unknown city", delete_after=5)
                return
            await ctx.send(txt, delete_after=15)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Weather(bot))
