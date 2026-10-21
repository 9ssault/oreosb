import json
from pathlib import Path

import discord
from discord.ext import commands

from core_utils import load_persist, save_persist, owner_check

class Persist(commands.Cog):
    """Persistent key/value + restore AFK/keywords/macros across restarts."""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_persist()

    def _save(self):
        save_persist(self.data)

    @commands.Cog.listener()
    async def on_ready(self):
        # restore automod keywords if present
        am = self.bot.get_cog("AutoMod")
        if am and "keywords" in self.data:
            am.keywords = set(self.data["keywords"])
        afk = self.bot.get_cog("AFK")
        if afk and "afk_msg" in self.data:
            afk.msg = self.data["afk_msg"]

    @commands.command(name="psave")
    @owner_check()
    async def psave(self, ctx, key: str, *, value: str):
        await ctx.message.delete()
        self.data[key] = value
        self._save()
        await ctx.send(f"saved `{key}`", delete_after=3)

    @commands.command(name="pget")
    @owner_check()
    async def pget(self, ctx, key: str):
        await ctx.message.delete()
        await ctx.send(str(self.data.get(key, "none")), delete_after=10)

    @commands.command(name="plist")
    @owner_check()
    async def plist(self, ctx):
        await ctx.message.delete()
        keys = list(self.data.keys())[:40]
        await ctx.send("persist: " + ", ".join(keys) if keys else "empty", delete_after=10)

    @commands.command(name="snapshot")
    @owner_check()
    async def snapshot(self, ctx):
        await ctx.message.delete()
        am = self.bot.get_cog("AutoMod")
        if am:
            self.data["keywords"] = list(getattr(am, "keywords", set()))
        afk = self.bot.get_cog("AFK")
        if afk:
            self.data["afk_msg"] = getattr(afk, "msg", None)
        self.data["prefix"] = str(self.bot.command_prefix)
        self._save()
        await ctx.send("snapshot ok", delete_after=3)


async def setup(bot):
    await bot.add_cog(Persist(bot))
