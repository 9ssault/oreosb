import asyncio
import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cleardm")
    async def cleardm(self, ctx, user: discord.User = None, limit: int = 100):
        await ctx.message.delete()
        limit = max(1, min(limit, 500))
        if user:
            ch = user.dm_channel or await user.create_dm()
        else:
            ch = ctx.channel
            if not isinstance(ch, discord.DMChannel):
                await ctx.send("use in DM or pass a user", delete_after=4)
                return
        n = 0
        async for m in ch.history(limit=800):
            if m.author.id == self.bot.user.id and n < limit:
                try:
                    await m.delete()
                    n += 1
                except Exception:
                    pass
                await asyncio.sleep(0.4)
        await ctx.send(f"cleared {n}", delete_after=4)

    @commands.command(name="clearalldms")
    async def clearalldms(self, ctx, limit_per: int = 50):
        await ctx.message.delete()
        total = 0
        for ch in list(self.bot.private_channels):
            if not isinstance(ch, discord.DMChannel):
                continue
            n = 0
            async for m in ch.history(limit=200):
                if m.author.id == self.bot.user.id and n < limit_per:
                    try:
                        await m.delete()
                        n += 1
                        total += 1
                    except Exception:
                        pass
                    await asyncio.sleep(0.35)
        await ctx.send(f"cleared {total} across DMs", delete_after=6)

async def setup(bot):
    await bot.add_cog(Clear(bot))
