import discord
from discord.ext import commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keywords = set()
        self.alert = None

    @commands.command(name="kwadd")
    async def kwadd(self, ctx, *, word: str):
        await ctx.message.delete()
        self.keywords.add(word.lower())
        await ctx.send(f"+ keyword `{word}`", delete_after=3)

    @commands.command(name="kwdel")
    async def kwdel(self, ctx, *, word: str):
        await ctx.message.delete()
        self.keywords.discard(word.lower())
        await ctx.send(f"- keyword `{word}`", delete_after=3)

    @commands.command(name="kwlist")
    async def kwlist(self, ctx):
        await ctx.message.delete()
        await ctx.send("keywords: " + ", ".join(self.keywords) or "none", delete_after=10)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or not self.keywords:
            return
        content = (message.content or "").lower()
        for kw in self.keywords:
            if kw in content:
                try:
                    await message.add_reaction("👀")
                except Exception:
                    pass
                break

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
