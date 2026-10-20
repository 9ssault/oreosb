# cogs/massdm.py
import asyncio
import random
import discord
from discord.ext import commands

class MassDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @commands.command(name="massdm")
    async def massdm(self, ctx, guild_id: int, *, message: str):
        await ctx.message.delete()
        guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
        if not guild:
            return
        self.running = True
        sent = failed = 0
        members = [m async for m in guild.fetch_members(limit=None) if not m.bot and m.id != self.bot.user.id]
        for m in members:
            if not self.running:
                break
            try:
                dm = await m.create_dm()
                await dm.send(message)
                sent += 1
                print(f"[MASSDM] {m} ({sent}/{len(members)})")
            except Exception as e:
                failed += 1
                print(f"[MASSDM] fail {m}: {e}")
            await asyncio.sleep(random.uniform(1.4, 3.8))
        await ctx.send(f"done: {sent} ok / {failed} fail", delete_after=6)
        self.running = False

    @commands.command(name="stopdm")
    async def stopdm(self, ctx):
        self.running = False
        await ctx.message.delete()

    @commands.command(name="dmfriends")
    async def dmfriends(self, ctx, *, message: str):
        await ctx.message.delete()
        self.running = True
        sent = 0
        for rel in self.bot.friends:
            if not self.running:
                break
            try:
                await rel.user.send(message)
                sent += 1
            except Exception:
                pass
            await asyncio.sleep(random.uniform(1.5, 4.0))
        await ctx.send(f"friends dm: {sent}", delete_after=5)
        self.running = False

async def setup(bot):
    await bot.add_cog(MassDM(bot))
