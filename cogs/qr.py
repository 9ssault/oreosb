import aiohttp
import discord
from discord.ext import commands
from io import BytesIO

class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="qr")
    async def qr(self, ctx, *, data: str):
        await ctx.message.delete()
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={data}"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                img = await r.read()
        await ctx.send(file=discord.File(BytesIO(img), "qr.png"))

async def setup(bot):
    await bot.add_cog(QR(bot))
