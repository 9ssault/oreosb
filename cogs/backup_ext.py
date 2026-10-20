import json
from pathlib import Path
import discord
from discord.ext import commands

class BackupExt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="exportfriends")
    async def exportfriends(self, ctx):
        await ctx.message.delete()
        data = [{"id": str(r.user.id), "name": str(r.user)} for r in self.bot.friends]
        Path("friends_export.json").write_text(json.dumps(data, indent=2))
        await ctx.send(f"exported {len(data)} friends", delete_after=5)

    @commands.command(name="exportguilds")
    async def exportguilds(self, ctx):
        await ctx.message.delete()
        data = [{"id": str(g.id), "name": g.name, "members": g.member_count} for g in self.bot.guilds]
        Path("guilds_export.json").write_text(json.dumps(data, indent=2))
        await ctx.send(f"exported {len(data)} guilds", delete_after=5)

async def setup(bot):
    await bot.add_cog(BackupExt(bot))
