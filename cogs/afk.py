import discord
from discord.ext import commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg = None

    @commands.command(name="afk")
    async def afk(self, ctx, *, text: str = None):
        await ctx.message.delete()
        if text is None:
            self.msg = None
            await ctx.send("afk off", delete_after=3)
        else:
            self.msg = text
            await ctx.send(f"afk: {text}", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.msg:
            return
        if message.author == self.bot.user:
            return
        if self.bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            try:
                await message.channel.send(self.msg)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(AFK(bot))
