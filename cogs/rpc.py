import asyncio
import os
import time

import aiohttp
import discord
from discord.ext import commands

RPC_APP = os.getenv("RPC_APP_ID", "1554236986515132416")
RPC_IMG = os.getenv(
    "RPC_IMG",
    "https://cdn.discordapp.com/app-assets/1554236986515132416/1554565446403883028.png",
)
RPC_STREAM = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")


class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # workers always start with RPC on; master respects env (default on)
        role = getattr(bot, "role", "master")
        if role == "worker":
            self.enabled = True
        else:
            self.enabled = os.getenv("RPC_ON", "1").lower() in ("1", "true", "yes")
        self.name = os.getenv("RPC_NAME", " ")
        self.stream_url = RPC_STREAM
        self.app_id = RPC_APP
        self.img_url = RPC_IMG
        self.asset = None
        self._task = None

    async def _resolve_asset(self):
        if self.asset and self.asset != "fatdog":
            return self.asset
        token = getattr(self.bot.http, "token", "")
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    f"https://discord.com/api/v9/applications/{self.app_id}/external-assets",
                    headers=headers,
                    json={"urls": [self.img_url]},
                    timeout=aiohttp.ClientTimeout(total=12),
                ) as r:
                    if r.status == 200:
                        data = await r.json(content_type=None)
                        if isinstance(data, list) and data:
                            path = data[0].get("external_asset_path")
                            if path:
                                self.asset = path if str(path).startswith("mp:") else f"mp:{path}"
                                return self.asset
        except Exception:
            pass
        self.asset = None
        return None

    async def push(self, refresh: bool = False):
        if refresh:
            self.asset = None
        if self.enabled:
            await self._resolve_asset()

        # 1) try library Streaming
        if self.enabled:
            try:
                activity = discord.Streaming(name=self.name or " ", url=self.stream_url)
                await self.bot.change_presence(activity=activity, status=discord.Status.online)
            except Exception:
                try:
                    activity = discord.Activity(
                        type=discord.ActivityType.playing,
                        name=self.name or "\u200b",
                    )
                    await self.bot.change_presence(activity=activity, status=discord.Status.online)
                except Exception:
                    pass
        else:
            try:
                await self.bot.change_presence(activity=None, status=discord.Status.online)
            except Exception:
                pass

        # 2) raw OP 3
        ws = getattr(self.bot, "ws", None)
        if not ws:
            return False
        if self.enabled:
            act = {
                "name": self.name or " ",
                "type": 1,
                "url": self.stream_url,
                "application_id": str(self.app_id),
            }
            if self.asset:
                act["assets"] = {"large_image": self.asset, "large_text": " "}
            data = {
                "since": int(time.time() * 1000),
                "activities": [act],
                "status": "online",
                "afk": True,
            }
        else:
            data = {"since": 0, "activities": [], "status": "online", "afk": False}
        try:
            await ws.send_as_json({"op": 3, "d": data})
            return True
        except Exception as e:
            print(f"[RPC] {e}")
            return False

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(f"rpc · {'on' if self.enabled else 'off'}", delete_after=5)
            return
        m = mode.lower()
        if m == "on":
            self.enabled = True
            ok = await self.push(True)
            await ctx.send("rpc · on" if ok else "rpc · partial", delete_after=4)
        elif m == "off":
            self.enabled = False
            await self.push(False)
            await ctx.send("rpc · off", delete_after=3)
        elif m == "name" and value is not None:
            self.name = value
            await self.push(False)
            await ctx.send("ok", delete_after=3)
        elif m == "url" and value:
            self.stream_url = value
            await self.push(False)
            await ctx.send("ok", delete_after=3)
        elif m == "refresh":
            ok = await self.push(True)
            await ctx.send("ok" if ok else "fail", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        # workers always force on at ready
        if getattr(self.bot, "role", "master") == "worker":
            self.enabled = True
        if self.enabled:
            await self.push(True)
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def _loop(self):
        while not self.bot.is_closed():
            await asyncio.sleep(180)
            if getattr(self.bot, "role", "master") == "worker":
                self.enabled = True
            if self.enabled:
                await self.push(False)


async def setup(bot):
    await bot.add_cog(RPC(bot))
