import asyncio
import discord
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member, *, reason: str = "kicked"):
        await ctx.message.delete()
        try:
            await member.kick(reason=reason)
            await ctx.send(f"kicked `{member}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason: str = "banned"):
        await ctx.message.delete()
        try:
            await member.ban(reason=reason, delete_message_days=0)
            await ctx.send(f"banned `{member}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="unban")
    async def unban(self, ctx, user_id: int):
        await ctx.message.delete()
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"unbanned `{user}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="timeout")
    async def timeout(self, ctx, member: discord.Member, minutes: int = 10):
        await ctx.message.delete()
        try:
            until = discord.utils.utcnow() + discord.timedelta(minutes=max(1, minutes))
            await member.timeout(until, reason="timeout")
            await ctx.send(f"timeout `{member}` {minutes}m", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="untimeout")
    async def untimeout(self, ctx, member: discord.Member):
        await ctx.message.delete()
        try:
            await member.timeout(None)
            await ctx.send(f"cleared timeout `{member}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="lock")
    async def lock(self, ctx, channel: discord.TextChannel = None):
        await ctx.message.delete()
        ch = channel or ctx.channel
        try:
            overwrite = ch.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(f"locked `{ch.name}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="unlock")
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        await ctx.message.delete()
        ch = channel or ctx.channel
        try:
            overwrite = ch.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = None
            await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(f"unlocked `{ch.name}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="slowmode")
    async def slowmode(self, ctx, seconds: int = 0, channel: discord.TextChannel = None):
        await ctx.message.delete()
        ch = channel or ctx.channel
        try:
            await ch.edit(slowmode_delay=max(0, min(seconds, 21600)))
            await ctx.send(f"slowmode `{ch.name}` = {seconds}s", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="topic")
    async def topic(self, ctx, *, text: str):
        await ctx.message.delete()
        try:
            await ctx.channel.edit(topic=text[:1024])
            await ctx.send("topic set", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Mod(bot))
