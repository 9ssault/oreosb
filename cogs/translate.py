import urllib.parse
import aiohttp
import discord
from discord.ext import commands

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tr")
    async def tr(self, ctx, lang: str, *, text: str):
        await ctx.message.delete()
        q = urllib.parse.quote(text[:500])
        url = f"https://api.mymemory.translated.net/get?q={q}&langpair=en|{lang}"
        if "|" in lang:
            url = f"https://api.mymemory.translated.net/get?q={q}&langpair={lang}"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=12) as r:
                    data = await r.json()
            out = (data.get("responseData") or {}).get("translatedText") or "?"
            await ctx.send(out[:1900], delete_after=20)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Translate(bot))
