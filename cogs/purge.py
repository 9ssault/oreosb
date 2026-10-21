import asyncio
import discord
from discord.ext import commands


class Purge(commands.Cog):
    """Self-bot message purge — available to master and workers."""

    def __init__(self, bot):
        self.bot = bot

    async def _purge_own(self, channel, limit: int, *, silent: bool = False, ctx=None):
        limit = max(1, min(int(limit), 500))
        me = self.bot.user.id if self.bot.user else None
        if not me:
            return 0
        n = 0
        async for m in channel.history(limit=limit * 3):
            if n >= limit:
                break
            if m.author and m.author.id == me:
                try:
                    await m.delete()
                    n += 1
                except Exception:
                    pass
                await asyncio.sleep(0.35)
        if not silent and ctx is not None:
            try:
                await ctx.send(f"purged {n}", delete_after=3)
            except Exception:
                pass
        return n

    @commands.command(name="purge")
    async def purge(self, ctx, amount: int = 10):
        """.purge 30 — delete last N of your own messages in this channel."""
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await self._purge_own(ctx.channel, amount, silent=False, ctx=ctx)

    @commands.command(name="spurge", aliases=["silentpurge", "spur"])
    async def spurge(self, ctx, amount: int = 10):
        """.spurge 30 — same as purge but no status reply."""
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await self._purge_own(ctx.channel, amount, silent=True, ctx=None)

    @commands.command(name="selfpurge")
    async def selfpurge(self, ctx, amount: int = 20):
        """alias of purge"""
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await self._purge_own(ctx.channel, amount, silent=False, ctx=ctx)


async def setup(bot):
    await bot.add_cog(Purge(bot))
