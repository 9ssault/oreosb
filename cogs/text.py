import discord
from discord.ext import commands

class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="embed")
    async def embed(self, ctx, title: str, *, desc: str = ""):
        await ctx.message.delete()
        e = discord.Embed(title=title, description=desc, color=0x2b2d31)
        await ctx.send(embed=e)

    @commands.command(name="reverse")
    async def reverse(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text[::-1])

    @commands.command(name="len")
    async def length(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(f"`{len(text)}` chars", delete_after=5)

    @commands.command(name="spoiler")
    async def spoiler(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(f"||{text}||")

async def setup(bot):
    await bot.add_cog(Text(bot))
