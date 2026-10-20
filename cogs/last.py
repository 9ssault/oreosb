import discord
from discord.ext import commands

class Last(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        self.last[message.channel.id] = message

    @commands.command(name="last")
    async def last_msg(self, ctx):
        await ctx.message.delete()
        m = self.last.get(ctx.channel.id)
        if not m:
            await ctx.send("none", delete_after=3)
            return
        await ctx.send(f"{m.author}: {m.content[:300]}", delete_after=12)

async def setup(bot):
    await bot.add_cog(Last(bot))
