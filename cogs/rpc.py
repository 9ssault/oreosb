import asyncio
import os
import time

import aiohttp
from discord.ext import commands

RPC_APP = os.getenv("RPC_APP_ID", "1554236986515132416")
RPC_IMG = os.getenv(
    "RPC_IMG",
    "https://cdn.discordapp.com/app-assets/1554236986515132416/1554565446403883028.png",
)
RPC_STREAM = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")
API = "https://discord.com/api/v9"


class RPC(commands.Cog):
    """Rich stream presence matching the JS selfbot pushPresence payload."""

    def __init__(self, bot):
        self.bot = bot
        self.enabled = os.getenv("RPC_ON", "1").lower() in ("1", "true", "yes")
        self.name = os.getenv("RPC_NAME", " ")
        self.stream_url = RPC_STREAM
        self.app_id = RPC_APP
        self.img_url = RPC_IMG
        self.asset = None  # mp:external path
        self._timer = None

    def _token(self):
        return getattr(self.bot.http, "token", None) or ""

    async def _resolve_asset(self):
        """POST /applications/{id}/external-assets like RichPresence.getExternal."""
        if self.asset:
            return self.asset
        headers = {
            "Authorization": self._token(),
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        body = {"urls": [self.img_url]}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    f"{API}/applications/{self.app_id}/external-assets",
                    headers=headers,
                    json=body,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as r:
                    if r.status == 200:
                        data = await r.json(content_type=None)
                        if isinstance(data, list) and data:
                            path = data[0].get("external_asset_path") or data[0].get("url")
                            if path:
                                self.asset = path if str(path).startswith("mp:") else f"mp:{path}"
                                return self.asset
        except Exception as e:
            print(f"[RPC] external asset: {e}")
        self.asset = "fatdog"
        return self.asset

    def _activities(self):
        act = {
            "name": self.name if self.name is not None else " ",
            "type": 1,  # streaming
            "url": self.stream_url,
            "application_id": str(self.app_id),
        }
        if self.asset:
            act["assets"] = {
                "large_image": self.asset,
                "large_text": " ",
            }
        return [act]

    async def push_presence(self, refresh_asset: bool = False):
        ws = getattr(self.bot, "ws", None)
        if ws is None:
            return False

        if not self.enabled:
            payload = {
                "op": 3,
                "d": {
                    "since": 0,
                    "activities": [],
                    "status": "online",
                    "afk": False,
                },
            }
        else:
            if refresh_asset or not self.asset:
                await self._resolve_asset()
            payload = {
                "op": 3,
                "d": {
                    "since": int(time.time() * 1000),
                    "activities": self._activities(),
                    "status": "online",
                    "afk": True,
                },
            }

        try:
            await ws.send_as_json(payload)
            return True
        except Exception as e:
            print(f"[RPC] op3 fail: {e}")
            return False

    async def _loop(self):
        while not self.bot.is_closed():
            await asyncio.sleep(180)
            if self.enabled:
                await self.push_presence(False)

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(
                f"rpc · {'on' if self.enabled else 'off'} | `{self.name}` | {self.stream_url}",
                delete_after=8,
            )
            return
        m = mode.lower()
        if m == "on":
            self.enabled = True
            ok = await self.push_presence(True)
            await ctx.send("rpc · on" if ok else "rpc · send fail", delete_after=4)
        elif m == "off":
            self.enabled = False
            ok = await self.push_presence(False)
            await ctx.send("rpc · off" if ok else "rpc · send fail", delete_after=4)
        elif m == "name" and value is not None:
            self.name = value
            await self.push_presence(False)
            await ctx.send("rpc · name set", delete_after=3)
        elif m == "url" and value:
            self.stream_url = value
            await self.push_presence(False)
            await ctx.send("rpc · url set", delete_after=3)
        elif m == "img" and value:
            self.img_url = value
            self.asset = None
            await self.push_presence(True)
            await ctx.send("rpc · img set", delete_after=3)
        elif m == "app" and value:
            self.app_id = value
            self.asset = None
            await self.push_presence(True)
            await ctx.send("rpc · app set", delete_after=3)
        elif m == "refresh":
            self.asset = None
            ok = await self.push_presence(True)
            await ctx.send("rpc · refreshed" if ok else "rpc · fail", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|img|app|refresh", delete_after=5)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        if self.enabled:
            await self.push_presence(True)
        if self._timer is None or self._timer.done():
            self._timer = asyncio.create_task(self._loop())


async def setup(bot):
    await bot.add_cog(RPC(bot))
