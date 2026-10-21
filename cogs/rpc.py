import asyncio
import os
import time

from discord.ext import commands

DEFAULT_NAME = os.getenv("RPC_NAME", " ")
DEFAULT_URL = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")


class RPC(commands.Cog):
    """Stream-style presence via raw gateway OP 3 — avoids change_presence protobuf crash."""

    def __init__(self, bot):
        self.bot = bot
        self.enabled = os.getenv("RPC_ON", "1").lower() in ("1", "true", "yes")
        self.name = DEFAULT_NAME
        self.stream_url = DEFAULT_URL
        self.status = "online"

    def _activity(self):
        # type 1 = streaming
        return {
            "name": self.name if self.name is not None else " ",
            "type": 1,
            "url": self.stream_url,
        }

    async def _apply(self):
        ws = getattr(self.bot, "ws", None)
        if ws is None:
            return False
        payload = {
            "op": 3,
            "d": {
                "since": int(time.time() * 1000) if False else 0,
                "activities": [self._activity()] if self.enabled else [],
                "status": self.status if self.enabled else "online",
                "afk": False,
            },
        }
        try:
            await ws.send_as_json(payload)
            return True
        except Exception as e:
            print(f"[RPC] gateway status fail: {e}")
            return False

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(
                f"rpc {'on' if self.enabled else 'off'} | `{self.name}` | {self.stream_url}",
                delete_after=8,
            )
            return
        m = mode.lower()
        if m == "on":
            self.enabled = True
            ok = await self._apply()
            await ctx.send("rpc on" if ok else "rpc send failed", delete_after=4)
        elif m == "off":
            self.enabled = False
            ok = await self._apply()
            await ctx.send("rpc off" if ok else "rpc send failed", delete_after=4)
        elif m == "name" and value is not None:
            self.name = value
            await self._apply()
            await ctx.send("name set", delete_after=3)
        elif m == "url" and value:
            self.stream_url = value
            await self._apply()
            await ctx.send("url set", delete_after=3)
        elif m == "refresh":
            ok = await self._apply()
            await ctx.send("ok" if ok else "fail", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        if self.enabled:
            await self._apply()


async def setup(bot):
    await bot.add_cog(RPC(bot))
