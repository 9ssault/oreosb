# cogs/farmer.py
import asyncio
import random
import discord
from discord.ext import commands

class Farmer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    def _loop(self, channel_id: int, cmds: list, delay_range: tuple):
        async def task():
            ch = self.bot.get_channel(channel_id)
            if not ch:
                return
            while True:
                for c in cmds:
                    try:
                        await ch.send(c)
                    except Exception:
                        pass
                    await asyncio.sleep(random.uniform(*delay_range))
        return asyncio.create_task(task())

    @commands.command(name="owofarm")
    async def owofarm(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        cid = channel_id or ctx.channel.id
        self.tasks["owo"] = self._loop(cid, ["owo hunt", "owo battle", "owo pray"], (16, 23))
        await ctx.send(f"owo farm <#{cid}>", delete_after=3)

    @commands.command(name="dankfarm")
    async def dankfarm(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        cid = channel_id or ctx.channel.id
        self.tasks["dank"] = self._loop(cid, ["pls work", "pls fish", "pls hunt", "pls crime", "pls beg"], (22, 32))
        await ctx.send(f"dank farm <#{cid}>", delete_after=3)

    @commands.command(name="mee6farm")
    async def mee6farm(self, ctx, delay: float = 65.0):
        await ctx.message.delete()
        msgs = [".", "nice", "ok", "lol", "yes", "based", "true"]
        self.tasks["mee6"] = self._loop(ctx.channel.id, msgs, (delay, delay + 8))
        await ctx.send("mee6 xp farm on", delete_after=3)

    @commands.command(name="stopfarm")
    async def stopfarm(self, ctx, which: str = "all"):
        await ctx.message.delete()
        if which == "all":
            for t in self.tasks.values():
                t.cancel()
            self.tasks.clear()
        elif which in self.tasks:
            self.tasks[which].cancel()
            del self.tasks[which]
        await ctx.send(f"stopped {which}", delete_after=3)

async def setup(bot):
    await bot.add_cog(Farmer(bot))
