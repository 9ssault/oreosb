import asyncio
import os
import time

import aiohttp
import discord
from discord.ext import commands

# fixed application for all RPC assets
RPC_APP = "1554236986515132416"
RPC_IMG = os.getenv(
    "RPC_IMG",
    f"https://cdn.discordapp.com/app-assets/{RPC_APP}/1554565446403883028.png",
)
RPC_STREAM = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")


class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        self.asset_key = None
        self._asset_cache = {}  # name/id -> resolved large_image value
        self._task = None
        self.mode = "stream" if self.enabled else "off"
        self.bland = False

    def _headers(self):
        token = getattr(self.bot.http, "token", "")
        return {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    async def _fetch_app_assets(self):
        """List rich presence assets on app 1554236986515132416."""
        url = f"https://discord.com/api/v9/oauth2/applications/{self.app_id}/assets"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=self._headers(), timeout=aiohttp.ClientTimeout(total=12)) as r:
                    if r.status == 200:
                        data = await r.json(content_type=None)
                        if isinstance(data, list):
                            return data
        except Exception:
            pass
        return []

    async def _convert_key(self, key: str) -> str:
        """
        Turn any user input into the format Discord expects for large_image:
        - already mp:... → keep
        - numeric snowflake / asset id → use as-is (Discord accepts id under application_id)
        - asset name → look up id from app assets list, use id
        - http(s) url → external-assets → mp: path
        """
        key = (key or "").strip()
        if not key:
            return None
        if key in self._asset_cache:
            return self._asset_cache[key]

        # already correct media proxy path
        if key.startswith("mp:"):
            self._asset_cache[key] = key
            return key

        # external image url → resolve via external-assets
        if key.startswith("http://") or key.startswith("https://"):
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.post(
                        f"https://discord.com/api/v9/applications/{self.app_id}/external-assets",
                        headers=self._headers(),
                        json={"urls": [key]},
                        timeout=aiohttp.ClientTimeout(total=12),
                    ) as r:
                        if r.status == 200:
                            data = await r.json(content_type=None)
                            if isinstance(data, list) and data:
                                path = data[0].get("external_asset_path")
                                if path:
                                    resolved = path if str(path).startswith("mp:") else f"mp:{path}"
                                    self._asset_cache[key] = resolved
                                    return resolved
            except Exception:
                pass
            return None

        # pure digits → treat as asset id under this application
        if key.isdigit():
            self._asset_cache[key] = key
            return key

        # name → fetch app assets and match by name (case-insensitive)
        assets = await self._fetch_app_assets()
        lower = key.lower()
        for a in assets:
            name = (a.get("name") or "").lower()
            aid = str(a.get("id") or "")
            if name == lower or aid == key:
                resolved = aid
                self._asset_cache[key] = resolved
                self._asset_cache[aid] = resolved
                return resolved

        # fallback: use the name string itself (Discord sometimes accepts it with application_id)
        self._asset_cache[key] = key
        return key

    async def _resolve_asset(self):
        if self.asset_key:
            resolved = await self._convert_key(self.asset_key)
            self.asset = resolved
            return self.asset

        if self.bland:
            self.asset = None
            return None

        if self.asset and self.asset != "fatdog":
            return self.asset

        # default image url from this app
        resolved = await self._convert_key(self.img_url)
        self.asset = resolved
        return self.asset

    def _build_activity(self):
        title = (self.name or " ").strip() or " "
        if self.mode == "off" or not self.enabled:
            return None

        type_map = {
            "stream": 1,
            "play": 0,
            "listen": 2,
            "watch": 3,
            "compete": 5,
            "custom": 4,
        }
        t = type_map.get(self.mode, 0)

        if self.bland and not self.asset_key:
            act = {"name": title, "type": t}
            if t == 1:
                act["url"] = self.stream_url
            if t == 4:
                act = {"name": "Custom Status", "type": 4, "state": title}
            return act

        if t == 4:
            act = {"name": "Custom Status", "type": 4, "state": title}
        else:
            act = {"name": title, "type": t}
            if t == 1:
                act["url"] = self.stream_url
            act["application_id"] = str(self.app_id)
            if self.asset:
                act["assets"] = {"large_image": self.asset, "large_text": " "}
        return act

    async def push(self, refresh: bool = False):
        if refresh and not self.asset_key:
            self.asset = None
        if self.enabled:
            await self._resolve_asset()

        act = self._build_activity()

        try:
            if act is None:
                await self.bot.change_presence(activity=None, status=discord.Status.online)
            else:
                t = act.get("type", 0)
                name = act.get("name") or act.get("state") or " "
                if t == 1:
                    lib = discord.Streaming(name=name, url=act.get("url") or self.stream_url)
                elif t == 2:
                    lib = discord.Activity(type=discord.ActivityType.listening, name=name)
                elif t == 3:
                    lib = discord.Activity(type=discord.ActivityType.watching, name=name)
                elif t == 5:
                    lib = discord.Activity(type=discord.ActivityType.competing, name=name)
                elif t == 4:
                    lib = discord.CustomActivity(name=act.get("state") or name)
                else:
                    lib = discord.Game(name=name)
                await self.bot.change_presence(activity=lib, status=discord.Status.online)
        except Exception:
            pass

        ws = getattr(self.bot, "ws", None)
        if not ws:
            return False
        if act is None:
            data = {"since": 0, "activities": [], "status": "online", "afk": False}
        else:
            data = {
                "since": int(time.time() * 1000),
                "activities": [act],
                "status": "online",
                "afk": True,
            }
        try:
            await ws.send_as_json({"op": 3, "d": data})
            return True
        except Exception as e:
            print(f"[RPC] {e}")
            return False

    async def _set_bland(self, mode: str, title: str):
        self.enabled = True
        self.bland = True
        self.mode = mode
        self.name = title
        if not self.asset_key:
            self.asset = None
        return await self.push(False)

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            key = self.asset_key or "-"
            await ctx.send(
                f"rpc · {'on' if self.enabled else 'off'} · {self.mode} · {self.name!r} · key {key} · app {self.app_id}",
                delete_after=8,
            )
            return
        m = mode.lower()
        if m == "on":
            self.enabled = True
            self.bland = False
            self.mode = "stream"
            ok = await self.push(True)
            await ctx.send("rpc · on" if ok else "rpc · partial", delete_after=4)
        elif m == "off":
            self.enabled = False
            self.mode = "off"
            self.bland = False
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
            self._asset_cache.clear()
            ok = await self.push(True)
            await ctx.send("ok" if ok else "fail", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.command(name="setkey", aliases=["setasset", "rpcasset"])
    async def setkey(self, ctx, *, key: str = None):
        """
        .setkey <name|id|url|mp:...>
        Pulls from app 1554236986515132416 and auto-converts to the format Discord wants.
        .setkey clear → remove
        """
        await ctx.message.delete()
        if not key or key.lower() in ("clear", "off", "none", "null"):
            self.asset_key = None
            self.asset = None
            await self.push(True)
            await ctx.send("key cleared", delete_after=3)
            return
        key = key.strip()
        self.asset_key = key
        self.bland = False
        self.enabled = True
        if self.mode == "off":
            self.mode = "stream"
        resolved = await self._convert_key(key)
        self.asset = resolved
        ok = await self.push(True)
        shown = resolved or key
        await ctx.send(f"key · {shown}" if ok else f"key · {shown} · push fail", delete_after=5)

    @commands.command(name="listassets", aliases=["assets"])
    async def listassets(self, ctx):
        """List rich presence assets on app 1554236986515132416."""
        await ctx.message.delete()
        assets = await self._fetch_app_assets()
        if not assets:
            await ctx.send("no assets / failed to fetch", delete_after=5)
            return
        lines = []
        for a in assets[:30]:
            lines.append(f"`{a.get('id')}` {a.get('name')}")
        await ctx.send("**app assets**\n" + "\n".join(lines), delete_after=20)

    @commands.command(name="setstream")
    async def setstream(self, ctx, *, title: str):
        await ctx.message.delete()
        ok = await self._set_bland("stream", title)
        await ctx.send(f"stream · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setgame", aliases=["setplaying"])
    async def setgame(self, ctx, *, title: str):
        await ctx.message.delete()
        ok = await self._set_bland("play", title)
        await ctx.send(f"playing · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setlisten", aliases=["setlistening"])
    async def setlisten(self, ctx, *, title: str):
        await ctx.message.delete()
        ok = await self._set_bland("listen", title)
        await ctx.send(f"listening · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setwatch", aliases=["setwatching"])
    async def setwatch(self, ctx, *, title: str):
        await ctx.message.delete()
        ok = await self._set_bland("watch", title)
        await ctx.send(f"watching · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setcompete", aliases=["setcompeting"])
    async def setcompete(self, ctx, *, title: str):
        await ctx.message.delete()
        ok = await self._set_bland("compete", title)
        await ctx.send(f"competing · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setcustom")
    async def setcustom(self, ctx, *, title: str):
        await ctx.message.delete()
        ok = await self._set_bland("custom", title)
        await ctx.send(f"custom · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setrpc")
    async def setrpc(self, ctx, kind: str = None, *, title: str = None):
        await ctx.message.delete()
        if not kind or not title:
            await ctx.send("setrpc stream|play|listen|watch|compete|custom <title>", delete_after=6)
            return
        k = kind.lower()
        map_ = {
            "stream": "stream",
            "play": "play",
            "playing": "play",
            "game": "play",
            "listen": "listen",
            "listening": "listen",
            "watch": "watch",
            "watching": "watch",
            "compete": "compete",
            "competing": "compete",
            "custom": "custom",
        }
        mode = map_.get(k)
        if not mode:
            await ctx.send("stream|play|listen|watch|compete|custom", delete_after=5)
            return
        ok = await self._set_bland(mode, title)
        await ctx.send(f"{mode} · {title}" if ok else "fail", delete_after=4)

    @commands.command(name="setstatus")
    async def setstatus(self, ctx, status: str = "online"):
        await ctx.message.delete()
        map_ = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible,
            "offline": discord.Status.invisible,
        }
        st = map_.get(status.lower())
        if not st:
            await ctx.send("online|idle|dnd|invisible", delete_after=4)
            return
        try:
            await self.bot.change_presence(status=st, activity=self.bot.activity)
            await ctx.send(f"status · {status.lower()}", delete_after=3)
        except Exception:
            await ctx.send("fail", delete_after=3)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        if getattr(self.bot, "role", "master") == "worker":
            self.enabled = True
            if self.mode == "off":
                self.mode = "stream"
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
