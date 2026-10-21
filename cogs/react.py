import asyncio
import os

import discord
from discord.ext import commands


class React(commands.Cog):
    """JS-style fleet reacts: .r .sr .rt .rlist .rend + channel autoreact."""

    def __init__(self, bot):
        self.bot = bot
        self.targets = {}  # user_id -> emoji
        self.self_emoji = None
        self.channel_auto = {}  # channel_id -> emoji
        self.master_id = None

    def _master(self):
        if self.master_id:
            return self.master_id
        try:
            mid = int(os.getenv("MASTER_ID") or "0")
            if mid:
                self.master_id = mid
                return mid
        except Exception:
            pass
        if self.bot.user:
            return self.bot.user.id
        return None

    def _is_master_process(self):
        return getattr(self.bot, "role", "master") == "master"

    def _apply_target(self, uid: int, emoji: str = None):
        if emoji is None:
            self.targets.pop(uid, None)
        else:
            self.targets[uid] = emoji

    def _broadcast_to_workers(self, uid: int, emoji: str = None):
        """Push target onto all worker bots' React cogs."""
        workers = getattr(self.bot, "workers", None) or {}
        for w in workers.values():
            wbot = w.get("bot")
            if not wbot:
                continue
            cog = wbot.get_cog("React")
            if cog:
                cog._apply_target(uid, emoji)

    @commands.Cog.listener()
    async def on_ready(self):
        self._master()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author:
            return
        uid = message.author.id

        emoji = self.targets.get(uid)
        if emoji:
            try:
                await message.add_reaction(emoji)
            except Exception:
                pass

        if self.self_emoji and self.bot.user and uid == self.bot.user.id:
            await asyncio.sleep(0.28)
            try:
                await message.add_reaction(self.self_emoji)
            except Exception:
                pass

        if self.bot.user and uid != self.bot.user.id:
            ce = self.channel_auto.get(message.channel.id)
            if ce:
                try:
                    await message.add_reaction(ce)
                except Exception:
                    pass

    @commands.command(name="r", aliases=["reactall"])
    async def r(self, ctx, emoji: str = None):
        """
        Master: set emoji so ALL workers + master react to master's messages.
        Worker: only this account reacts to its own messages.
        Clear: .r with no emoji.
        """
        await ctx.message.delete()
        me = self.bot.user.id if self.bot.user else None
        mid = self._master()
        is_master = self._is_master_process() and me and mid and me == mid

        if not emoji:
            if is_master:
                if mid:
                    self._apply_target(mid, None)
                    self._broadcast_to_workers(mid, None)
                await ctx.send("fleet master reaction cleared", delete_after=4)
            else:
                if me:
                    self._apply_target(me, None)
                await ctx.send("self reaction cleared", delete_after=3)
            return

        if is_master:
            # fleet: everyone reacts when master speaks
            self._apply_target(mid, emoji)
            self._broadcast_to_workers(mid, emoji)
            n = len(getattr(self.bot, "workers", {}) or {})
            await ctx.send(f"fleet → master {emoji} ({n} workers)", delete_after=5)
        else:
            # worker: only react to own messages
            if not me:
                return
            self._apply_target(me, emoji)
            await ctx.send(f"self → {emoji}", delete_after=4)

    @commands.command(name="sr", aliases=["superselfreact"])
    async def sr(self, ctx, emoji: str = None):
        await ctx.message.delete()
        if not emoji:
            self.self_emoji = None
            if self._is_master_process():
                for w in (getattr(self.bot, "workers", {}) or {}).values():
                    cog = (w.get("bot") or None) and w["bot"].get_cog("React")
                    if cog:
                        cog.self_emoji = None
            await ctx.send("super self cleared", delete_after=3)
            return
        self.self_emoji = emoji
        if self._is_master_process():
            for w in (getattr(self.bot, "workers", {}) or {}).values():
                cog = (w.get("bot") or None) and w["bot"].get_cog("React")
                if cog:
                    cog.self_emoji = emoji
        await ctx.send(f"super self → {emoji}", delete_after=4)

    @commands.command(name="rt", aliases=["sreact"])
    async def rt(self, ctx, target_id: str = None, emoji: str = None):
        await ctx.message.delete()
        if not target_id or not emoji:
            await ctx.send("rt <id> <emoji>", delete_after=4)
            return
        uid = int("".join(c for c in target_id if c.isdigit()) or 0)
        if not uid:
            await ctx.send("bad id", delete_after=3)
            return
        self._apply_target(uid, emoji)
        if self._is_master_process():
            self._broadcast_to_workers(uid, emoji)
        await ctx.send(f"{uid} → {emoji}", delete_after=4)

    @commands.command(name="rtclear")
    async def rtclear(self, ctx, target_id: str = None):
        await ctx.message.delete()
        if not target_id:
            await ctx.send("rtclear <id>", delete_after=3)
            return
        uid = int("".join(c for c in target_id if c.isdigit()) or 0)
        self._apply_target(uid, None)
        if self._is_master_process():
            self._broadcast_to_workers(uid, None)
        await ctx.send(f"cleared {uid}", delete_after=3)

    @commands.command(name="rlist")
    async def rlist(self, ctx):
        await ctx.message.delete()
        lines = []
        if self.self_emoji:
            lines.append(f"super self {self.self_emoji}")
        mid = self._master()
        for uid, emoji in self.targets.items():
            label = "master " if uid == mid else ""
            lines.append(f"{label}{uid} {emoji}")
        await ctx.send("\n".join(lines) if lines else "empty", delete_after=12)

    @commands.command(name="rend")
    async def rend(self, ctx):
        await ctx.message.delete()
        self.targets.clear()
        self.self_emoji = None
        if self._is_master_process():
            for w in (getattr(self.bot, "workers", {}) or {}).values():
                cog = (w.get("bot") or None) and w["bot"].get_cog("React")
                if cog:
                    cog.targets.clear()
                    cog.self_emoji = None
        await ctx.send("all reactions stopped", delete_after=3)

    @commands.command(name="autoreact")
    async def autoreact(self, ctx, emoji: str = None):
        await ctx.message.delete()
        if not emoji:
            self.channel_auto.pop(ctx.channel.id, None)
            await ctx.send("autoreact off", delete_after=3)
            return
        self.channel_auto[ctx.channel.id] = emoji
        await ctx.send(f"autoreact {emoji}", delete_after=3)

    @commands.command(name="massreact")
    async def massreact(self, ctx, emoji: str, limit: int = 20):
        await ctx.message.delete()
        limit = max(1, min(limit, 50))
        n = 0
        async for m in ctx.channel.history(limit=limit):
            try:
                await m.add_reaction(emoji)
                n += 1
            except Exception:
                pass
            await asyncio.sleep(0.4)
        await ctx.send(f"reacted {n}", delete_after=4)


async def setup(bot):
    await bot.add_cog(React(bot))
