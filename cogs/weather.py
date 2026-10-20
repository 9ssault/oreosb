import aiohttp
import discord
from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        await ctx.message.delete()
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"https://wttr.in/{city}?format=3") as r:
                    txt = await r.text()
            await ctx.send(txt.strip(), delete_after=12)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Weather(bot))
