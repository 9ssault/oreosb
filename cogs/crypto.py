import aiohttp
import discord
from discord.ext import commands

COINS = {
    "btc": "BTC",
    "eth": "ETH",
    "sol": "SOL",
    "ltc": "LTC",
    "xrp": "XRP",
    "doge": "DOGE",
}

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _price(self, symbol: str):
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot",
                timeout=10,
            ) as r:
                if r.status != 200:
                    return None
                d = await r.json()
                return d.get("data", {}).get("amount")

    @commands.command(name="btc")
    async def btc(self, ctx):
        await ctx.message.delete()
        p = await self._price("BTC")
        await ctx.send(f"BTC `${p}`" if p else "fail", delete_after=8)

    @commands.command(name="eth")
    async def eth(self, ctx):
        await ctx.message.delete()
        p = await self._price("ETH")
        await ctx.send(f"ETH `${p}`" if p else "fail", delete_after=8)

    @commands.command(name="sol")
    async def sol(self, ctx):
        await ctx.message.delete()
        p = await self._price("SOL")
        await ctx.send(f"SOL `${p}`" if p else "fail", delete_after=8)

    @commands.command(name="price")
    async def price(self, ctx, symbol: str = "BTC"):
        await ctx.message.delete()
        sym = COINS.get(symbol.lower(), symbol.upper())
        p = await self._price(sym)
        await ctx.send(f"{sym} `${p}`" if p else f"fail {sym}", delete_after=8)

async def setup(bot):
    await bot.add_cog(Crypto(bot))
