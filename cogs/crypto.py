import aiohttp
import discord
from discord.ext import commands

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="btc")
    async def btc(self, ctx):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get("https://api.coinbase.com/v2/prices/BTC-USD/spot") as r:
                d = await r.json()
                price = d["data"]["amount"]
        await ctx.send(f"BTC `${price}`", delete_after=8)

    @commands.command(name="eth")
    async def eth(self, ctx):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get("https://api.coinbase.com/v2/prices/ETH-USD/spot") as r:
                d = await r.json()
                price = d["data"]["amount"]
        await ctx.send(f"ETH `${price}`", delete_after=8)

async def setup(bot):
    await bot.add_cog(Crypto(bot))
