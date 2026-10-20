import asyncio
import discord
from discord.ext import commands

class PurgeExt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cleardm")
    async def cleardm(self, ctx, user: discord.User = None, limit: int = 50):
        await ctx.message.delete()
        if not user:
            return
        dm = await user.create_dm()
        count = 0
        async for m in dm.history(limit=200):
            if m.author == self.bot.user and count < limit:
                try:
                    await m.delete()
                    count += 1
                except Exception:
                    pass
                await asyncio.sleep(0.4)
        await ctx.send(f"cleardm {count}", delete_after=4)

    @commands.command(name="clearalldms")
    async def clearalldms(self, ctx, limit: int = 30):
        await ctx.message.delete()
        total = 0
        for ch in self.bot.private_channels:
            if not isinstance(ch, discord.DMChannel):
                continue
            async for m in ch.history(limit=limit):
                if m.author == self.bot.user:
                    try:
                        await m.delete()
                        total += 1
                    except Exception:
                        pass
                    await asyncio.sleep(0.35)
        await ctx.send(f"clearalldms {total}", delete_after=5)

async def setup(bot):
    await bot.add_cog(PurgeExt(bot))
