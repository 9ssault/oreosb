import asyncio
import discord
from discord.ext import commands

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto = {}

    @commands.command(name="autoreact")
    async def autoreact(self, ctx, emoji: str = None):
        await ctx.message.delete()
        if not emoji:
            self.auto.pop(ctx.channel.id, None)
            await ctx.send("autoreact off", delete_after=3)
            return
        self.auto[ctx.channel.id] = emoji
        await ctx.send(f"autoreact {emoji}", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        emoji = self.auto.get(message.channel.id)
        if emoji:
            try:
                await message.add_reaction(emoji)
            except Exception:
                pass

    @commands.command(name="massreact")
    async def massreact(self, ctx, emoji: str, limit: int = 20):
        await ctx.message.delete()
        count = 0
        async for m in ctx.channel.history(limit=limit):
            try:
                await m.add_reaction(emoji)
                count += 1
            except Exception:
                pass
            await asyncio.sleep(0.4)
        await ctx.send(f"reacted {count}", delete_after=4)

async def setup(bot):
    await bot.add_cog(React(bot))
