import asyncio
import random
import discord
from discord.ext import commands

try:
    from evasion.delay import human_delay
except Exception:
    async def human_delay(lo=1.0, hi=2.5):
        await asyncio.sleep(random.uniform(lo, hi))

class MassDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    @commands.command(name="massdm")
    async def massdm(self, ctx, guild_id: int, *, message: str):
        await ctx.message.delete()
        guild = self.bot.get_guild(guild_id)
        if not guild:
            try:
                guild = await self.bot.fetch_guild(guild_id)
            except Exception:
                await ctx.send("guild not found", delete_after=4)
                return
        self.running = True
        sent = failed = 0
        members = []
        try:
            async for m in guild.fetch_members(limit=None):
                if not m.bot and m.id != self.bot.user.id:
                    members.append(m)
        except Exception:
            members = [m for m in guild.members if not m.bot and m.id != self.bot.user.id]
        for m in members:
            if not self.running:
                break
            try:
                dm = await m.create_dm()
                await dm.send(message[:2000])
                sent += 1
                print(f"[MASSDM] {m} ({sent}/{len(members)})")
            except Exception as e:
                failed += 1
                print(f"[MASSDM] fail {m}: {e}")
            await human_delay(1.4, 3.8)
        self.running = False
        await ctx.send(f"done: {sent} ok / {failed} fail", delete_after=6)

    @commands.command(name="stopdm")
    async def stopdm(self, ctx):
        self.running = False
        await ctx.message.delete()

    @commands.command(name="dmfriends")
    async def dmfriends(self, ctx, *, message: str):
        await ctx.message.delete()
        self.running = True
        sent = 0
        friends = list(getattr(self.bot, "friends", []) or [])
        for rel in friends:
            if not self.running:
                break
            user = getattr(rel, "user", rel)
            try:
                await user.send(message[:2000])
                sent += 1
            except Exception:
                pass
            await human_delay(1.5, 4.0)
        self.running = False
        await ctx.send(f"friends dm: {sent}", delete_after=5)

async def setup(bot):
    await bot.add_cog(MassDM(bot))
