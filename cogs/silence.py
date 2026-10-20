import asyncio
import discord
from discord.ext import commands

class Silence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.silenced = set()

    @commands.command(name="silence")
    async def silence(self, ctx, user: discord.User, seconds: int = 0):
        await ctx.message.delete()
        self.silenced.add(user.id)
        await ctx.send(
            f"silenced `{user}`" + (f" {seconds}s" if seconds > 0 else ""),
            delete_after=4,
        )
        if seconds > 0:
            await asyncio.sleep(seconds)
            self.silenced.discard(user.id)

    @commands.command(name="unsilence")
    async def unsilence(self, ctx, user: discord.User):
        await ctx.message.delete()
        self.silenced.discard(user.id)
        await ctx.send(f"unsilenced `{user}`", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.silenced and message.author.id != self.bot.user.id:
            try:
                await message.delete()
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Silence(bot))
