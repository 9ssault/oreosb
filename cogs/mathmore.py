import discord
from discord.ext import commands
import random

class MathMore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="choose")
    async def choose(self, ctx, *, options: str):
        await ctx.message.delete()
        parts = [p.strip() for p in options.split(",") if p.strip()]
        if len(parts) < 2:
            await ctx.send("need options a, b, c", delete_after=3)
            return
        await ctx.send(random.choice(parts))

    @commands.command(name="rate")
    async def rate(self, ctx, *, thing: str):
        await ctx.message.delete()
        await ctx.send(f"{thing} → `{random.randint(0, 100)}/100`")

    @commands.command(name="ship")
    async def ship(self, ctx, a: str, b: str):
        await ctx.message.delete()
        await ctx.send(f"{a} + {b} = `{random.randint(0, 100)}%`")

async def setup(bot):
    await bot.add_cog(MathMore(bot))
