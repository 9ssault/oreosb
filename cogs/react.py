import asyncio
import discord
from discord.ext import commands

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        emoji = self.auto.get(message.channel.id)
        if not emoji:
            return
        try:
            await message.add_reaction(emoji)
        except Exception:
            pass

    @commands.command(name="autoreact")
    async def autoreact(self, ctx, emoji: str = None):
        await ctx.message.delete()
        if not emoji:
            self.auto.pop(ctx.channel.id, None)
            await ctx.send("autoreact off", delete_after=3)
            return
        self.auto[ctx.channel.id] = emoji
        await ctx.send(f"autoreact {emoji}", delete_after=3)

    @commands.command(name="massreact")
    async def massreact(self, ctx, emoji: str, limit: int = 20):
        await ctx.message.delete()
        limit = max(1, min(limit, 50))
        n = 0
        async for m in ctx.channel.history(limit=limit):
            try:
                await m.add_reaction(emoji)
                n += 1
            except Exception:
                pass
            await asyncio.sleep(0.4)
        await ctx.send(f"reacted {n}", delete_after=4)

async def setup(bot):
    await bot.add_cog(React(bot))
