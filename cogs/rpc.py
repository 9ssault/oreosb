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
        # mode: stream | play | listen | watch | compete | custom | off
        self.mode = "stream" if self.enabled else "off"
        self.bland = False  # when True: title only, no assets, no app id decoration

    async def _resolve_asset(self):
        if self.bland:
            self.asset = None
            return None
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

    def _build_activity(self):
        """Single bland activity — title only when bland=True."""
        title = (self.name or " ").strip() or " "
        if self.mode == "off" or not self.enabled:
            return None

        if self.bland:
            # pure title card, no assets / no extra fields
            type_map = {
                "stream": 1,
                "play": 0,
                "listen": 2,
                "watch": 3,
                "compete": 5,
                "custom": 4,
            }
            t = type_map.get(self.mode, 0)
            act = {"name": title, "type": t}
            if t == 1:
                act["url"] = self.stream_url
            if t == 4:
                # custom status style
                act = {"name": "Custom Status", "type": 4, "state": title}
            return act

        # rich (default stream with optional asset)
        act = {
            "name": title,
            "type": 1,
            "url": self.stream_url,
            "application_id": str(self.app_id),
        }
        if self.asset:
            act["assets"] = {"large_image": self.asset, "large_text": " "}
        return act

    async def push(self, refresh: bool = False):
        if refresh and not self.bland:
            self.asset = None
        if self.enabled and not self.bland:
            await self._resolve_asset()

        act = self._build_activity()

        # library presence — single activity only
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

        # raw OP 3 — always one activity max, never duplicates
        ws = getattr(self.bot, "ws", None)
        if not ws:
            return False
        if act is None:
            data = {"since": 0, "activities": [], "status": "online", "afk": False}
        else:
            data = {
                "since": int(time.time() * 1000),
                "activities": [act],  # single card only
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
        self.asset = None
        return await self.push(False)

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(
                f"rpc · {'on' if self.enabled else 'off'} · {self.mode} · {self.name!r}",
                delete_after=6,
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
            ok = await self.push(True)
            await ctx.send("ok" if ok else "fail", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.command(name="setstream")
    async def setstream(self, ctx, *, title: str):
        """.setstream hyper → single bland streaming card titled 'hyper'"""
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
        """.setrpc stream|play|listen|watch|compete|custom <title>"""
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
            act = None
            if self.enabled:
                # keep current single activity
                pass
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
