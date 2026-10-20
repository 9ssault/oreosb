import random
import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hug")
    async def hug(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        await ctx.send(f"*hugs {u.mention}*")

    @commands.command(name="kiss")
    async def kiss(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        await ctx.send(f"*kisses {u.mention}*")

    @commands.command(name="slap")
    async def slap(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        await ctx.send(f"*slaps {u.mention}*")

    @commands.command(name="8ball")
    async def eightball(self, ctx, *, q: str = ""):
        await ctx.message.delete()
        answers = ["yes", "no", "maybe", "definitely", "ask later", "looks good", "nah"]
        await ctx.send(f"🎱 {random.choice(answers)}")

    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
        await ctx.message.delete()
        await ctx.send(random.choice(["heads", "tails"]))

    @commands.command(name="roll")
    async def roll(self, ctx, sides: int = 6):
        await ctx.message.delete()
        await ctx.send(f"🎲 `{random.randint(1, max(2, sides))}`")

async def setup(bot):
    await bot.add_cog(Fun(bot))
