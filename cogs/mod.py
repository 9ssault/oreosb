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
            await ctx.send(f"kicked {member}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason: str = "banned"):
        await ctx.message.delete()
        try:
            await member.ban(reason=reason)
            await ctx.send(f"banned {member}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="unban")
    async def unban(self, ctx, user_id: int):
        await ctx.message.delete()
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"unbanned {user}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="timeout")
    async def timeout(self, ctx, member: discord.Member, minutes: int = 10):
        await ctx.message.delete()
        try:
            until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
            await member.timeout(until)
            await ctx.send(f"timeout {member} {minutes}m", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Mod(bot))
