import discord
from discord.ext import commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg = None
        self.replied = set()

    @commands.command(name="afk")
    async def afk(self, ctx, *, text: str = None):
        await ctx.message.delete()
        if text is None:
            self.msg = None
            self.replied.clear()
            await ctx.send("afk off", delete_after=3)
        else:
            self.msg = text[:500]
            self.replied.clear()
            await ctx.send(f"afk: {text[:100]}", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.msg or message.author.id == self.bot.user.id:
            return
        hit = self.bot.user in message.mentions or isinstance(message.channel, discord.DMChannel)
        if not hit:
            return
        key = (message.channel.id, message.author.id)
        if key in self.replied:
            return
        self.replied.add(key)
        try:
            await message.channel.send(f"AFK: {self.msg}")
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(AFK(bot))
