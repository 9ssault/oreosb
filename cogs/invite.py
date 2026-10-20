import asyncio
import discord
from discord.ext import commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invites")
    async def invites(self, ctx):
        await ctx.message.delete()
        try:
            invs = await ctx.guild.invites()
            lines = [f"`{i.code}` uses={i.uses} max={i.max_uses} by {i.inviter}" for i in invs[:25]]
            await ctx.send("invites:\n" + ("\n".join(lines) or "none"), delete_after=15)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="createinvite")
    async def createinvite(self, ctx, max_age: int = 0, max_uses: int = 0):
        await ctx.message.delete()
        try:
            inv = await ctx.channel.create_invite(max_age=max_age, max_uses=max_uses, unique=True)
            await ctx.send(str(inv.url), delete_after=20)
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
            await asyncio.sleep(0.35)
        await ctx.send(f"deleted {ok}", delete_after=4)

    @commands.command(name="invinfo")
    async def invinfo(self, ctx, code: str):
        await ctx.message.delete()
        code = code.rstrip("/").split("/")[-1]
        try:
            inv = await self.bot.fetch_invite(code)
            g = inv.guild
            await ctx.send(
                f"**{getattr(g, 'name', '?')}**\n"
                f"code `{inv.code}` uses {inv.uses}/{inv.max_uses}\n"
                f"members {getattr(g, 'member_count', '?')}",
                delete_after=12,
            )
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Invite(bot))
