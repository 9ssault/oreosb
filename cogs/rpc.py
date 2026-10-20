import asyncio
import discord
from discord.ext import commands

class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.stream_url = "https://twitch.tv/discord"
        self.name = "OreoSB"
        self.details = None

    async def _apply(self):
        if not self.enabled:
            await self.bot.change_presence(activity=None)
            return
        activity = discord.Streaming(name=self.name[:128], url=self.stream_url)
        await self.bot.change_presence(activity=activity, status=discord.Status.online)

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            state = "on" if self.enabled else "off"
            await ctx.send(f"rpc `{state}` · `{self.name}` · {self.stream_url}", delete_after=6)
            return
        m = mode.lower()
        if m == "on":
            self.enabled = True
            await self._apply()
            await ctx.send("rpc on", delete_after=3)
        elif m == "off":
            self.enabled = False
            await self._apply()
            await ctx.send("rpc off", delete_after=3)
        elif m == "name" and value:
            self.name = value
            if self.enabled:
                await self._apply()
            await ctx.send(f"name → `{value}`", delete_after=3)
        elif m == "url" and value:
            if not value.startswith("http"):
                value = "https://twitch.tv/" + value
            self.stream_url = value
            if self.enabled:
                await self._apply()
            await ctx.send("url set", delete_after=3)
        elif m == "refresh":
            await self._apply()
            await ctx.send("refreshed", delete_after=3)
        else:
            await ctx.send("`rpc on|off|name|url|refresh`", delete_after=4)

async def setup(bot):
    await bot.add_cog(RPC(bot))
