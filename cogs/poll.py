import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll")
    async def poll(self, ctx, *, question: str):
        await ctx.message.delete()
        m = await ctx.send(f"**poll**\n{question}")
        await m.add_reaction("👍")
        await m.add_reaction("👎")

    @commands.command(name="ypoll")
    async def ypoll(self, ctx, *, question: str):
        await ctx.message.delete()
        m = await ctx.send(f"**yes/no**\n{question}")
        await m.add_reaction("✅")
        await m.add_reaction("❌")

async def setup(bot):
    await bot.add_cog(Poll(bot))
