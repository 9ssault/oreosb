import asyncio
import os

import discord
from discord.ext import commands

DEFAULT_NAME = " "
DEFAULT_URL = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")


class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = os.getenv("RPC_ON", "1").lower() in ("1", "true", "yes")
        self.stream_url = DEFAULT_URL
        self.name = os.getenv("RPC_NAME", DEFAULT_NAME)

    async def _apply(self):
        """Avoid Streaming()/protobuf Activity path that breaks on some discord.py-self builds."""
        try:
            if not self.enabled:
                await self.bot.change_presence(activity=None, status=discord.Status.online)
                return
            # Game activity is stable; no MessageToDict including_default_value_fields
            activity = discord.Game(name=self.name if self.name.strip() else "\u200b")
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            print(f"[RPC] apply fail: {e}")

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            state = "on" if self.enabled else "off"
            await ctx.send(f"rpc {state} | name=`{self.name}`", delete_after=6)
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
            await ctx.send("url stored (presence uses game name on this build)", delete_after=5)
        elif m == "refresh":
            await self._apply()
            await ctx.send("refreshed", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(1.5)
        if self.enabled:
            await self._apply()


async def setup(bot):
    await bot.add_cog(RPC(bot))
