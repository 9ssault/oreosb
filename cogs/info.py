import discord
from discord.ext import commands
from datetime import datetime, timezone

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        await ctx.message.delete()
        g = ctx.guild
        if not g:
            return
        created = discord.utils.snowflake_time(g.id).strftime("%Y-%m-%d")
        await ctx.send(
            f"**{g.name}**\n"
            f"id `{g.id}`\n"
            f"owner `{g.owner_id}`\n"
            f"members {g.member_count}\n"
            f"channels {len(g.channels)} · roles {len(g.roles)}\n"
            f"boosts {g.premium_subscription_count} · level {g.premium_tier}\n"
            f"created {created}",
            delete_after=18,
        )

    @commands.command(name="channelinfo")
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        await ctx.message.delete()
        c = channel or ctx.channel
        await ctx.send(
            f"**{getattr(c, 'name', c)}**\nid `{c.id}`\ntype {c.type}\n"
            f"topic {(getattr(c, 'topic', None) or '-')[:80]}",
            delete_after=10,
        )

    @commands.command(name="roleinfo")
    async def roleinfo(self, ctx, role: discord.Role):
        await ctx.message.delete()
        await ctx.send(
            f"**{role.name}**\nid `{role.id}`\ncolor `{role.color}`\n"
            f"members {len(role.members)} · hoist {role.hoist} · mentionable {role.mentionable}\n"
            f"pos {role.position}",
            delete_after=12,
        )

    @commands.command(name="roles")
    async def roles(self, ctx):
        await ctx.message.delete()
        names = [f"{r.name}" for r in ctx.guild.roles if not r.is_default()]
        await ctx.send("roles: " + ", ".join(names[:50]), delete_after=14)

    @commands.command(name="whois")
    async def whois(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        created = discord.utils.snowflake_time(u.id).strftime("%Y-%m-%d %H:%M UTC")
        member = ctx.guild.get_member(u.id) if ctx.guild else None
        extra = ""
        if member:
            joined = member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "?"
            roles = ", ".join(r.name for r in member.roles if not r.is_default())[:120]
            extra = f"\njoined {joined}\nroles {roles or '-'}"
        await ctx.send(
            f"**{u}**\nid `{u.id}`\ncreated {created}\nbot {u.bot}{extra}",
            delete_after=16,
        )

async def setup(bot):
    await bot.add_cog(Info(bot))
