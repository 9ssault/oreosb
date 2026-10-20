import aiohttp
import discord
from discord.ext import commands

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="urban")
    async def urban(self, ctx, *, term: str):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://api.urbandictionary.com/v0/define?term={term}") as r:
                d = await r.json()
        if not d.get("list"):
            await ctx.send("no results", delete_after=4)
            return
        defn = d["list"][0]
        await ctx.send(f"**{defn['word']}**\n{defn['definition'][:400]}", delete_after=20)

    @commands.command(name="define")
    async def define(self, ctx, *, word: str):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as r:
                if r.status != 200:
                    await ctx.send("not found", delete_after=3)
                    return
                d = await r.json()
        meaning = d[0]["meanings"][0]["definitions"][0]["definition"]
        await ctx.send(f"**{word}** — {meaning}", delete_after=15)

async def setup(bot):
    await bot.add_cog(Search(bot))
