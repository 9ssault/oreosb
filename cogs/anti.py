import asyncio
import discord
from discord.ext import commands

class Anti(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shield = False

    @commands.command(name="antiban")
    async def antiban(self, ctx, mode: str = "on"):
        await ctx.message.delete()
        self.shield = mode.lower() in ("on", "1", "true")
        await ctx.send(f"antiban {'on' if self.shield else 'off'}", delete_after=3)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not self.shield:
            return
        if user.id == self.bot.user.id:
            try:
                await guild.leave()
                print(f"[ANTIBAN] left {guild.id} after ban detect")
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"[LEAVE] removed from {guild.name} ({guild.id})")

async def setup(bot):
    await bot.add_cog(Anti(bot))
