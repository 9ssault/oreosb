import urllib.parse
from io import BytesIO
import aiohttp
import discord
from discord.ext import commands

class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="qr")
    async def qr(self, ctx, *, data: str):
        await ctx.message.delete()
        q = urllib.parse.quote(data[:1800], safe="")
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={q}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=15) as r:
                    if r.status != 200:
                        await ctx.send(f"qr api {r.status}", delete_after=4)
                        return
                    img = await r.read()
            await ctx.send(file=discord.File(BytesIO(img), "qr.png"))
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(QR(bot))
