import asyncio
import discord
from discord.ext import commands

class Stealth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.silent = bool(bot.cfg.get("private_mode", True))

    @commands.command(name="silent")
    async def silent(self, ctx, mode: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(f"silent={`on` if self.silent else `off`}", delete_after=4)
            return
        self.silent = mode.lower() in ("on", "1", "true", "yes")
        self.bot.cfg["private_mode"] = self.silent
        await ctx.send(f"silent → {'on' if self.silent else 'off'}", delete_after=3)

    @commands.command(name="selfpurge")
    async def selfpurge(self, ctx, limit: int = 50):
        await ctx.message.delete()
        limit = max(1, min(limit, 300))
        n = 0
        async for m in ctx.channel.history(limit=500):
            if m.author.id == self.bot.user.id and n < limit:
                try:
                    await m.delete()
                    n += 1
                except Exception:
                    pass
                await asyncio.sleep(0.35)
        if not self.silent:
            await ctx.send(f"purged {n}", delete_after=3)

    @commands.command(name="ghost")
    async def ghost(self, ctx, *, text: str):
        await ctx.message.delete()
        m = await ctx.send(text)
        await asyncio.sleep(0.15)
        try:
            await m.delete()
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Stealth(bot))
