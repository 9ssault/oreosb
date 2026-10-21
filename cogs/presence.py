import discord
from discord.ext import commands


class Presence(commands.Cog):
    """Thin wrappers — all go through RPC cog for one bland card, no duplicates."""

    def __init__(self, bot):
        self.bot = bot

    def _rpc(self):
        return self.bot.get_cog("RPC")

    @commands.command(name="spotify")
    async def spotify(self, ctx, *, title: str = "Unknown"):
        await ctx.message.delete()
        cog = self._rpc()
        if cog:
            ok = await cog._set_bland("listen", title)
            await ctx.send(f"listening · {title}" if ok else "fail", delete_after=3)
        else:
            act = discord.Activity(type=discord.ActivityType.listening, name=title)
            await self.bot.change_presence(activity=act)
            await ctx.send(f"listening {title}", delete_after=3)

    @commands.command(name="watching")
    async def watching(self, ctx, *, title: str):
        await ctx.message.delete()
        cog = self._rpc()
        if cog:
            ok = await cog._set_bland("watch", title)
            await ctx.send(f"watching · {title}" if ok else "fail", delete_after=3)
        else:
            act = discord.Activity(type=discord.ActivityType.watching, name=title)
            await self.bot.change_presence(activity=act)
            await ctx.send(f"watching {title}", delete_after=3)

    @commands.command(name="competing")
    async def competing(self, ctx, *, title: str):
        await ctx.message.delete()
        cog = self._rpc()
        if cog:
            ok = await cog._set_bland("compete", title)
            await ctx.send(f"competing · {title}" if ok else "fail", delete_after=3)
        else:
            act = discord.Activity(type=discord.ActivityType.competing, name=title)
            await self.bot.change_presence(activity=act)
            await ctx.send(f"competing {title}", delete_after=3)

    @commands.command(name="clearpresence")
    async def clearpresence(self, ctx):
        await ctx.message.delete()
        cog = self._rpc()
        if cog:
            cog.enabled = False
            cog.mode = "off"
            cog.bland = False
            await cog.push(False)
        else:
            await self.bot.change_presence(activity=None)
        await ctx.send("cleared", delete_after=3)


async def setup(bot):
    await bot.add_cog(Presence(bot))
