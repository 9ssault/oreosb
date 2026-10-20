import urllib.parse
import aiohttp
import discord
from discord.ext import commands

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="urban")
    async def urban(self, ctx, *, term: str):
        await ctx.message.delete()
        q = urllib.parse.quote(term)
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://api.urbandictionary.com/v0/define?term={q}",
                    timeout=10,
                ) as r:
                    data = await r.json()
            defs = data.get("list") or []
            if not defs:
                await ctx.send("no results", delete_after=4)
                return
            d = defs[0]
            text = (d.get("definition") or "")[:800].replace("[", "").replace("]", "")
            await ctx.send(f"**{d.get('word')}**\n{text}", delete_after=20)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="define")
    async def define(self, ctx, *, word: str):
        await ctx.message.delete()
        q = urllib.parse.quote(word.strip())
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://api.dictionaryapi.dev/api/v2/entries/en/{q}",
                    timeout=10,
                ) as r:
                    if r.status != 200:
                        await ctx.send("no definition", delete_after=4)
                        return
                    data = await r.json()
            meanings = data[0].get("meanings") or []
            if not meanings:
                await ctx.send("none", delete_after=3)
                return
            defs = meanings[0].get("definitions") or []
            text = (defs[0].get("definition") if defs else "?")[:500]
            pos = meanings[0].get("partOfSpeech", "")
            await ctx.send(f"**{word}** ({pos})\n{text}", delete_after=15)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Search(bot))
