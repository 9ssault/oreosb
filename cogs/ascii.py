import discord
from discord.ext import commands

FONT = {
    "a": "𝗮", "b": "𝗯", "c": "𝗰", "d": "𝗱", "e": "𝗲", "f": "𝗳", "g": "𝗴", "h": "𝗵",
    "i": "𝗶", "j": "𝗷", "k": "𝗸", "l": "𝗹", "m": "𝗺", "n": "𝗻", "o": "𝗼", "p": "𝗽",
    "q": "𝗾", "r": "𝗿", "s": "𝘀", "t": "𝘁", "u": "𝘂", "v": "𝘃", "w": "𝘄", "x": "𝘅",
    "y": "𝘆", "z": "𝘇", " ": " ",
}
BUBBLE = {
    "a": "ⓐ", "b": "ⓑ", "c": "ⓒ", "d": "ⓓ", "e": "ⓔ", "f": "ⓕ", "g": "ⓖ", "h": "ⓗ",
    "i": "ⓘ", "j": "ⓙ", "k": "ⓚ", "l": "ⓛ", "m": "ⓜ", "n": "ⓝ", "o": "ⓞ", "p": "ⓟ",
    "q": "ⓠ", "r": "ⓡ", "s": "ⓢ", "t": "ⓣ", "u": "ⓤ", "v": "ⓥ", "w": "ⓦ", "x": "ⓧ",
    "y": "ⓨ", "z": "ⓩ", " ": " ",
}

class Ascii(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fancy")
    async def fancy(self, ctx, *, text: str):
        await ctx.message.delete()
        out = "".join(FONT.get(c.lower(), c) for c in text)
        await ctx.send(out[:2000])

    @commands.command(name="bubble")
    async def bubble(self, ctx, *, text: str):
        await ctx.message.delete()
        out = "".join(BUBBLE.get(c.lower(), c) for c in text)
        await ctx.send(out[:2000])

    @commands.command(name="mock")
    async def mock(self, ctx, *, text: str):
        await ctx.message.delete()
        out = "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
        await ctx.send(out[:2000])

    @commands.command(name="clap")
    async def clap(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(" 👏 ".join(text.split())[:2000])

    @commands.command(name="space")
    async def space(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(" ".join(list(text.replace(" ", "")))[:2000])

async def setup(bot):
    await bot.add_cog(Ascii(bot))
