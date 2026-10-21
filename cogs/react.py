import asyncio
import os
import re

import discord
from discord.ext import commands


class React(commands.Cog):
    """
    .r [user] emoji  — normal reaction to that user (or self if no user)
    .sr [user] emoji — nitro super reaction to that user (or self if no user)
    .rt .rlist .rend + channel autoreact
    """

    def __init__(self, bot):
        self.bot = bot
        self.targets = {}       # user_id -> (emoji, super:bool)
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

    def _parse_uid(self, raw: str):
        if not raw:
            return None
        digits = re.sub(r"\D", "", raw)
        if not digits:
            return None
        try:
            return int(digits)
        except Exception:
            return None

    def _looks_like_emoji(self, s: str) -> bool:
        if not s:
            return False
        if s.startswith("<") and s.endswith(">") and ":" in s:
            return True
        # unicode emoji-ish (no pure digits / plain words)
        if re.fullmatch(r"\d+", s):
            return False
        return True

    def _apply_target(self, uid: int, emoji: str = None, super_react: bool = False):
        if emoji is None:
            self.targets.pop(uid, None)
        else:
            self.targets[uid] = (emoji, super_react)

    def _broadcast_to_workers(self, uid: int, emoji: str = None, super_react: bool = False):
        workers = getattr(self.bot, "workers", None) or {}
        for w in workers.values():
            wbot = w.get("bot")
            if not wbot:
                continue
            cog = wbot.get_cog("React")
            if cog:
                cog._apply_target(uid, emoji, super_react)

    async def _super_react(self, message: discord.Message, emoji: str):
        """Nitro super reaction (burst) via Discord API type=1."""
        if emoji.startswith("<") and emoji.endswith(">"):
            parts = emoji.strip("<>").split(":")
            if len(parts) >= 3:
                emoji_path = f"{parts[1]}:{parts[2]}"
            else:
                emoji_path = emoji
        else:
            emoji_path = discord.utils._uriquote(emoji)

        route = discord.http.Route(
            "PUT",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=message.channel.id,
            message_id=message.id,
            emoji=emoji_path,
        )
        await self.bot.http.request(route, params={"type": 1})

    @commands.Cog.listener()
    async def on_ready(self):
        self._master()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author:
            return
        uid = message.author.id

        entry = self.targets.get(uid)
        if entry:
            emoji, is_super = entry
            await asyncio.sleep(0.15)
            try:
                if is_super:
                    await self._super_react(message, emoji)
                else:
                    await message.add_reaction(emoji)
            except Exception:
                pass

        if self.bot.user and uid != self.bot.user.id:
            ce = self.channel_auto.get(message.channel.id)
            if ce:
                try:
                    await message.add_reaction(ce)
                except Exception:
                    pass

    async def _set_react(self, ctx, args, *, super_react: bool):
        """Shared handler: .r / .sr [user] emoji | clear with no args."""
        await ctx.message.delete()
        me = self.bot.user.id if self.bot.user else None
        mid = self._master()
        is_master = self._is_master_process() and me and mid and me == mid
        kind = "super" if super_react else "normal"

        # no args → clear self (or master fleet if master)
        if not args:
            target = mid if is_master else me
            if target:
                self._apply_target(target, None)
                if is_master:
                    self._broadcast_to_workers(target, None)
            await ctx.send(f"{kind} reaction cleared", delete_after=3)
            return

        # parse: [user] emoji
        user_arg = None
        emoji = None
        if len(args) == 1:
            # only emoji → self
            emoji = args[0]
            user_arg = None
        else:
            # first could be user or emoji
            maybe_user = args[0]
            rest = " ".join(args[1:])
            uid = self._parse_uid(maybe_user)
            if uid and not self._looks_like_emoji(maybe_user):
                user_arg = uid
                emoji = rest
            else:
                # treat whole as emoji (rare multi-token emoji)
                emoji = " ".join(args)
                user_arg = None

        if not emoji:
            await ctx.send(f".{'sr' if super_react else 'r'} [user] emoji", delete_after=4)
            return

        if user_arg is None:
            # self
            target = me
            if not target:
                return
            self._apply_target(target, emoji, super_react)
            if is_master:
                self._broadcast_to_workers(target, emoji, super_react)
            await ctx.send(f"self {kind} → {emoji}", delete_after=4)
        else:
            self._apply_target(user_arg, emoji, super_react)
            if is_master:
                self._broadcast_to_workers(user_arg, emoji, super_react)
            await ctx.send(f"{user_arg} {kind} → {emoji}", delete_after=4)

    @commands.command(name="r", aliases=["reactall"])
    async def r(self, ctx, *args):
        """.r [user] emoji — normal react. no user = self. no args = clear."""
        await self._set_react(ctx, args, super_react=False)

    @commands.command(name="sr", aliases=["superselfreact", "superreact"])
    async def sr(self, ctx, *args):
        """.sr [user] emoji — nitro super react. no user = self. no args = clear."""
        await self._set_react(ctx, args, super_react=True)

    @commands.command(name="rt", aliases=["sreact"])
    async def rt(self, ctx, target_id: str = None, emoji: str = None):
        await ctx.message.delete()
        if not target_id or not emoji:
            await ctx.send("rt <id> <emoji>", delete_after=4)
            return
        uid = self._parse_uid(target_id)
        if not uid:
            await ctx.send("bad id", delete_after=3)
            return
        self._apply_target(uid, emoji, False)
        if self._is_master_process():
            self._broadcast_to_workers(uid, emoji, False)
        await ctx.send(f"{uid} → {emoji}", delete_after=4)

    @commands.command(name="rtclear")
    async def rtclear(self, ctx, target_id: str = None):
        await ctx.message.delete()
        if not target_id:
            await ctx.send("rtclear <id>", delete_after=3)
            return
        uid = self._parse_uid(target_id)
        self._apply_target(uid, None)
        if self._is_master_process():
            self._broadcast_to_workers(uid, None)
        await ctx.send(f"cleared {uid}", delete_after=3)

    @commands.command(name="rlist")
    async def rlist(self, ctx):
        await ctx.message.delete()
        lines = []
        mid = self._master()
        for uid, (emoji, is_super) in self.targets.items():
            kind = "super" if is_super else "normal"
            label = "master " if uid == mid else ""
            lines.append(f"{label}{uid} {kind} {emoji}")
        await ctx.send("\n".join(lines) if lines else "empty", delete_after=12)

    @commands.command(name="rend")
    async def rend(self, ctx):
        await ctx.message.delete()
        self.targets.clear()
        if self._is_master_process():
            for w in (getattr(self.bot, "workers", {}) or {}).values():
                cog = (w.get("bot") or None) and w["bot"].get_cog("React")
                if cog:
                    cog.targets.clear()
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
