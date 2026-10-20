import discord
from discord.ext import commands

class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message[:2000])

    @commands.command(name="embed")
    async def embed(self, ctx, title: str, *, desc: str = ""):
        await ctx.message.delete()
        e = discord.Embed(title=title[:256], description=desc[:4000], color=0x2b2d31)
        await ctx.send(embed=e)

    @commands.command(name="reverse")
    async def reverse(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text[::-1][:2000])

    @commands.command(name="len")
    async def length(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(f"`{len(text)}` chars · `{len(text.split())}` words", delete_after=6)

    @commands.command(name="spoiler")
    async def spoiler(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(f"||{text[:1990]}||")

    @commands.command(name="upper")
    async def upper(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text.upper()[:2000])

    @commands.command(name="lower")
    async def lower(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text.lower()[:2000])

    @commands.command(name="code")
    async def code(self, ctx, lang: str = "", *, body: str = None):
        await ctx.message.delete()
        if body is None:
            body, lang = lang, ""
        await ctx.send(f"```{lang}\n{body[:1900]}\n```")

    @commands.command(name="bold")
    async def bold(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(f"**{text[:1990]}**")

async def setup(bot):
    await bot.add_cog(Text(bot))
