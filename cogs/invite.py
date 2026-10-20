import asyncio
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invites")
    async def invites(self, ctx):
        await ctx.message.delete()
        try:
            invs = await ctx.guild.invites()
            lines = [f"{i.code} → {i.uses} uses" for i in invs[:20]]
            await ctx.send("invites:\n" + "\n".join(lines) or "none", delete_after=12)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="createinvite")
    async def createinvite(self, ctx, max_age: int = 0, max_uses: int = 0):
        await ctx.message.delete()
        try:
            inv = await ctx.channel.create_invite(max_age=max_age, max_uses=max_uses, unique=True)
            await ctx.send(f"{inv.url}", delete_after=15)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="delinvites")
    async def delinvites(self, ctx):
        await ctx.message.delete()
        invs = await ctx.guild.invites()
        ok = 0
        for i in invs:
            try:
                await i.delete()
                ok += 1
            except Exception:
                pass
            await asyncio.sleep(0.4)
        await ctx.send(f"deleted {ok}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Invite(bot))
