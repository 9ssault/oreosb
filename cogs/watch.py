import discord
from discord.ext import commands

class Watch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.targets = set()
        self.alert_channel = None

    @commands.command(name="watch")
    async def watch(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        if user is None:
            await ctx.send("watching: " + ", ".join(str(u) for u in self.targets) or "none", delete_after=8)
            return
        self.targets.add(user.id)
        self.alert_channel = ctx.channel
        await ctx.send(f"watching {user}", delete_after=4)

    @commands.command(name="unwatch")
    async def unwatch(self, ctx, user: discord.User):
        await ctx.message.delete()
        self.targets.discard(user.id)
        await ctx.send(f"unwatch {user}", delete_after=3)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.id not in self.targets:
            return
        if before.status == after.status:
            return
        if not self.alert_channel:
            return
        try:
            await self.alert_channel.send(f"watch: {after} → {after.status}")
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Watch(bot))
