import discord
from discord.ext import commands
from datetime import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        await ctx.message.delete()
        g = ctx.guild
        if not g:
            return
        await ctx.send(
            f"**{g.name}**\n"
            f"id `{g.id}`\n"
            f"owner `{g.owner_id}`\n"
            f"members {g.member_count}\n"
            f"channels {len(g.channels)}\n"
            f"roles {len(g.roles)}\n"
            f"boosts {g.premium_subscription_count}",
            delete_after=15
        )

    @commands.command(name="channelinfo")
    async def channelinfo(self, ctx):
        await ctx.message.delete()
        c = ctx.channel
        await ctx.send(f"**{c.name}**\nid `{c.id}`\ntype {c.type}", delete_after=8)

    @commands.command(name="roleinfo")
    async def roleinfo(self, ctx, role: discord.Role):
        await ctx.message.delete()
        await ctx.send(
            f"**{role.name}**\nid `{role.id}`\ncolor {role.color}\nmembers {len(role.members)}\nhoist {role.hoist}",
            delete_after=10
        )

    @commands.command(name="roles")
    async def roles(self, ctx):
        await ctx.message.delete()
        names = [r.name for r in ctx.guild.roles if not r.is_default()]
        await ctx.send("roles:\n" + ", ".join(names[:40]), delete_after=12)

async def setup(bot):
    await bot.add_cog(Info(bot))
