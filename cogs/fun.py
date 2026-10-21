import random
import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def eightball(self, ctx, *, q: str = "?"):
        await ctx.message.delete()
        answers = [
            "yes", "no", "maybe", "absolutely", "never", "ask later",
            "without a doubt", "doubt", "sure", "nah", "try again",
        ]
        await ctx.send(f"**{q}**\n`{random.choice(answers)}`", delete_after=12)

    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
        await ctx.message.delete()
        await ctx.send(random.choice(["heads", "tails"]), delete_after=6)

    @commands.command(name="roll")
    async def roll(self, ctx, sides: int = 6):
        await ctx.message.delete()
        sides = max(2, min(sides, 1000))
        await ctx.send(f"`{random.randint(1, sides)}` / {sides}", delete_after=6)

    @commands.command(name="choose")
    async def choose(self, ctx, *, options: str):
        await ctx.message.delete()
        parts = [p.strip() for p in options.split("|") if p.strip()]
        if len(parts) < 2:
            await ctx.send("usage: `.choose a | b | c`", delete_after=5)
            return
        await ctx.send(random.choice(parts), delete_after=8)

    @commands.command(name="rate")
    async def rate(self, ctx, *, thing: str):
        await ctx.message.delete()
        await ctx.send(f"**{thing}** → `{random.randint(0, 10)}/10`", delete_after=8)

    @commands.command(name="ship")
    async def ship(self, ctx, a: str, b: str):
        await ctx.message.delete()
        pct = random.randint(0, 100)
        await ctx.send(f"**{a}** x **{b}** → `{pct}%`", delete_after=10)

    @commands.command(name="kiss")
    async def kiss(self, ctx, user: discord.Member = None):
        await ctx.message.delete()
        t = user.mention if user else "the air"
        await ctx.send(f"*{ctx.author.display_name} kisses {t}*", delete_after=8)

    @commands.command(name="slap")
    async def slap(self, ctx, user: discord.Member = None):
        await ctx.message.delete()
        t = user.mention if user else "themself"
        await ctx.send(f"*{ctx.author.display_name} slaps {t}*", delete_after=8)

async def setup(bot):
    await bot.add_cog(Fun(bot))
