import aiohttp
import discord
from discord.ext import commands

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tr")
    async def tr(self, ctx, lang: str, *, text: str):
        await ctx.message.delete()
        # libretranslate public instance
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post("https://libretranslate.com/translate", json={
                    "q": text, "source": "auto", "target": lang, "format": "text"
                }) as r:
                    if r.status == 200:
                        d = await r.json()
                        await ctx.send(d.get("translatedText", "?"), delete_after=15)
                    else:
                        await ctx.send(f"fail {r.status}", delete_after=4)
        except Exception as e:
            await ctx.send(f"err {e}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Translate(bot))
