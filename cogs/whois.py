import discord
from discord.ext import commands
from datetime import datetime

class Whois(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="whois")
    async def whois(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        created = u.created_at.strftime("%Y-%m-%d %H:%M")
        flags = []
        if u.bot:
            flags.append("bot")
        if u.system:
            flags.append("system")
        member = ctx.guild.get_member(u.id) if ctx.guild else None
        joined = ""
        if member and member.joined_at:
            joined = f"\njoined {member.joined_at.strftime('%Y-%m-%d')}"
        await ctx.send(
            f"**{u}**\n"
            f"id `{u.id}`\n"
            f"created {created}{joined}\n"
            f"{' '.join(flags) if flags else 'user'}",
            delete_after=15
        )

async def setup(bot):
    await bot.add_cog(Whois(bot))
