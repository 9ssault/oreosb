import asyncio
import discord
from discord.ext import commands

class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = True
        self.app_id = "1554236986515132416"
        self.stream_url = "https://twitch.tv/oreosb"
        self.large_text = "OreoSB"
        self.name = "OreoSB"
        self._task = None

    async def _apply(self):
        if not self.enabled:
            await self.bot.change_presence(activity=None, status=discord.Status.online)
            return
        activity = discord.Streaming(name=self.name, url=self.stream_url)
        await self.bot.change_presence(activity=activity, status=discord.Status.online)

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(f"rpc {'on' if self.enabled else 'off'} | {self.name}", delete_after=5)
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
            await self._apply()
            await ctx.send(f"name → {value}", delete_after=3)
        elif m == "url" and value:
            self.stream_url = value
            await self._apply()
            await ctx.send("url set", delete_after=3)
        elif m == "refresh":
            await self._apply()
            await ctx.send("refreshed", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        try:
            await self._apply()
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(RPC(bot))
