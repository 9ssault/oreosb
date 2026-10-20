import asyncio
import json
from pathlib import Path
import discord
from discord.ext import commands

WL_FILE = Path("gc_whitelist.json")

def _load_wl():
    if WL_FILE.exists():
        try:
            data = json.loads(WL_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return set(str(x) for x in data.get("agctWhitelist", data.get("wl", [])))
            if isinstance(data, list):
                return set(str(x) for x in data)
        except Exception:
            pass
    return set()

def _save_wl(s):
    WL_FILE.write_text(
        json.dumps({"agctWhitelist": list(s)}, indent=2),
        encoding="utf-8",
    )

class GCTrap(commands.Cog):
    """Anti group-DM trap (ported from AGCT)."""

    def __init__(self, bot):
        self.bot = bot
        self.wl = _load_wl()
        self.trap_msg = "no you dont :p"
        self.trap_name = "trapped"
        self.enabled = True
        self.busy = set()

    @commands.command(name="agct")
    async def agct(self, ctx, action: str = None, sub: str = None, *, value: str = None):
        await ctx.message.delete()
        a = (action or "status").lower()

        if a in ("status", "s"):
            await ctx.send(
                f"agct `{'on' if self.enabled else 'off'}` · wl={len(self.wl)} · "
                f"msg=`{self.trap_msg[:40]}`",
                delete_after=8,
            )
            return

        if a in ("on", "off"):
            self.enabled = a == "on"
            await ctx.send(f"agct `{a}`", delete_after=3)
            return

        if a == "msg":
            text = sub if value is None else f"{sub} {value}".strip()
            if not text:
                await ctx.send(f"current: {self.trap_msg}", delete_after=6)
                return
            self.trap_msg = text
            await ctx.send("trap msg set", delete_after=3)
            return

        if a == "name" and sub:
            self.trap_name = sub[:100]
            await ctx.send(f"trap name → `{self.trap_name}`", delete_after=3)
            return

        if a == "wl":
            s = (sub or "list").lower()
            if s == "add" and value:
                uid = "".join(c for c in value if c.isdigit())
                if uid:
                    self.wl.add(uid)
                    _save_wl(self.wl)
                    await ctx.send(f"+ wl `{uid}`", delete_after=3)
                return
            if s == "remove" and value:
                uid = "".join(c for c in value if c.isdigit())
                self.wl.discard(uid)
                _save_wl(self.wl)
                await ctx.send(f"- wl `{uid}`", delete_after=3)
                return
            if s == "list":
                body = ", ".join(list(self.wl)[:30]) or "empty"
                await ctx.send(f"wl ({len(self.wl)}): {body}", delete_after=12)
                return

        await ctx.send(
            "`agct status|on|off|msg <text>|name <n>|wl add|remove|list`",
            delete_after=6,
        )

    @commands.command(name="gcwl")
    async def gcwl(self, ctx, user_id: int):
        await ctx.message.delete()
        self.wl.add(str(user_id))
        _save_wl(self.wl)
        await ctx.send(f"+ wl `{user_id}`", delete_after=3)

    @commands.command(name="gcunwl")
    async def gcunwl(self, ctx, user_id: int):
        await ctx.message.delete()
        self.wl.discard(str(user_id))
        _save_wl(self.wl)
        await ctx.send(f"- wl `{user_id}`", delete_after=3)

    @commands.command(name="leavegcs")
    async def leavegcs(self, ctx):
        await ctx.message.delete()
        left = 0
        for ch in list(self.bot.private_channels):
            if isinstance(ch, discord.GroupChannel):
                try:
                    await ch.delete()
                    left += 1
                except Exception:
                    pass
                await asyncio.sleep(0.35)
        await ctx.send(f"left {left} GCs", delete_after=5)

    @commands.Cog.listener()
    async def on_private_channel_create(self, channel):
        if not self.enabled:
            return
        if not isinstance(channel, discord.GroupChannel):
            return
        if channel.id in self.busy:
            return
        self.busy.add(channel.id)
        try:
            owner_id = getattr(channel, "owner_id", None)
            if owner_id and str(owner_id) in self.wl:
                return
            if owner_id and self.bot.user and owner_id == self.bot.user.id:
                return
            try:
                await channel.edit(name=self.trap_name)
            except Exception:
                pass
            safe = self.trap_msg.replace("@everyone", "@\u200beveryone")
            try:
                await channel.send(safe)
            except Exception:
                pass
            await asyncio.sleep(0.5)
            try:
                await channel.delete()
            except Exception:
                pass
        finally:
            await asyncio.sleep(2)
            self.busy.discard(channel.id)

async def setup(bot):
    await bot.add_cog(GCTrap(bot))
