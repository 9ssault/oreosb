import random
import string
import discord
from discord.ext import commands

class NitroGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nitros")
    async def nitros(self, ctx, amount: int = 5):
        await ctx.message.delete()
        codes = []
        for _ in range(min(amount, 20)):
            code = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            codes.append(f"discord.gift/{code}")
        await ctx.send("\n".join(codes), delete_after=20)

async def setup(bot):
    await bot.add_cog(NitroGen(bot))
