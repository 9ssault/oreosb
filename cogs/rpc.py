import asyncio
import os

import discord
from discord.ext import commands

# matches the style you asked for (stream presence, no random title spam)
DEFAULT_NAME = " "
DEFAULT_URL = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")
DEFAULT_APP = os.getenv("RPC_APP_ID", "1554236986515132416")


class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = os.getenv("RPC_ON", "1").lower() in ("1", "true", "yes")
        self.app_id = DEFAULT_APP
        self.stream_url = DEFAULT_URL
        self.name = os.getenv("RPC_NAME", DEFAULT_NAME)
        self.large_text = os.getenv("RPC_LARGE_TEXT", " ")

    async def _apply(self):
        if not self.enabled:
            try:
                await self.bot.change_presence(activity=None, status=discord.Status.online)
            except Exception:
                pass
            return
        # streaming type — name can be a single space (clean bar like your other client)
        activity = discord.Streaming(name=self.name or " ", url=self.stream_url)
        try:
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            print(f"[RPC] apply fail: {e}")

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            state = "on" if self.enabled else "off"
            await ctx.send(f"rpc {state} | name=`{self.name}` | url={self.stream_url}", delete_after=6)
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
        elif m == "name" and value is not None:
            self.name = value
            await self._apply()
            await ctx.send("name set", delete_after=3)
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
        # only apply if enabled — default stream url/name from env, not "OreoSB"
        await asyncio.sleep(1.5)
        if self.enabled:
            try:
                await self._apply()
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(RPC(bot))
