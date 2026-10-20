import discord
from discord.ext import commands

class Anti(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False

    @commands.command(name="antiban")
    async def antiban(self, ctx, mode: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(f"antiban `{'on' if self.enabled else 'off'}`", delete_after=4)
            return
        self.enabled = mode.lower() in ("on", "1", "true", "yes")
        await ctx.send(f"antiban → {'on' if self.enabled else 'off'}", delete_after=3)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not self.enabled:
            return
        if user.id != self.bot.user.id:
            return
        print(f"[ANTI] banned in {guild.id} — leaving if still present")
        g = self.bot.get_guild(guild.id)
        if g:
            try:
                await g.leave()
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Anti(bot))
