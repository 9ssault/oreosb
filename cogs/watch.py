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
            body = ", ".join(f"<@{u}>" for u in self.targets) or "none"
            await ctx.send(f"watching: {body}", delete_after=10)
            return
        self.targets.add(user.id)
        self.alert_channel = ctx.channel
        await ctx.send(f"watching `{user}`", delete_after=4)

    @commands.command(name="unwatch")
    async def unwatch(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        if user is None:
            self.targets.clear()
            await ctx.send("cleared all", delete_after=3)
            return
        self.targets.discard(user.id)
        await ctx.send(f"unwatch `{user}`", delete_after=3)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.id not in self.targets:
            return
        if before.status == after.status and before.activity == after.activity:
            return
        ch = self.alert_channel
        if not ch:
            return
        try:
            act = after.activity.name if after.activity else "-"
            await ch.send(f"watch: **{after}** status=`{after.status}` activity=`{act}`")
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Watch(bot))
