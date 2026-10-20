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
            while True:
                ch = self.bot.get_channel(channel_id)
                if not ch:
                    await asyncio.sleep(5)
                    continue
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
        if "owo" in self.tasks:
            self.tasks["owo"].cancel()
        self.tasks["owo"] = self._loop(cid, ["owo hunt", "owo battle", "owo pray"], (16, 24))
        await ctx.send(f"owo farm <#{cid}>", delete_after=3)

    @commands.command(name="dankfarm")
    async def dankfarm(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        cid = channel_id or ctx.channel.id
        if "dank" in self.tasks:
            self.tasks["dank"].cancel()
        self.tasks["dank"] = self._loop(
            cid, ["pls work", "pls fish", "pls hunt", "pls crime", "pls beg"], (22, 34)
        )
        await ctx.send(f"dank farm <#{cid}>", delete_after=3)

    @commands.command(name="mee6farm")
    async def mee6farm(self, ctx, delay: float = 65.0):
        await ctx.message.delete()
        msgs = [".", "nice", "ok", "lol", "yes", "based", "true", "real", "facts"]
        if "mee6" in self.tasks:
            self.tasks["mee6"].cancel()
        self.tasks["mee6"] = self._loop(ctx.channel.id, msgs, (max(45.0, delay), delay + 12))
        await ctx.send("mee6 xp farm on", delete_after=3)

    @commands.command(name="customfarm")
    async def customfarm(self, ctx, delay: float, *, commands_pipe: str):
        await ctx.message.delete()
        cmds = [c.strip() for c in commands_pipe.split("|") if c.strip()]
        if not cmds:
            await ctx.send("usage: `.customfarm 20 cmd1 | cmd2`", delete_after=5)
            return
        if "custom" in self.tasks:
            self.tasks["custom"].cancel()
        self.tasks["custom"] = self._loop(ctx.channel.id, cmds, (max(5.0, delay), delay + 5))
        await ctx.send(f"custom farm {len(cmds)} cmds", delete_after=3)

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
        await ctx.send(f"stopped `{which}`", delete_after=3)

    @commands.command(name="farmstatus")
    async def farmstatus(self, ctx):
        await ctx.message.delete()
        keys = list(self.tasks.keys()) or ["none"]
        await ctx.send("running: " + ", ".join(keys), delete_after=6)

async def setup(bot):
    await bot.add_cog(Farmer(bot))
