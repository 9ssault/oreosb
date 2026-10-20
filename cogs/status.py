# cogs/status.py
import asyncio
import random
import discord
from discord.ext import commands

async def start_rotator(bot):
    interval = bot.cfg.get("status_interval", 30)
    statuses = bot.cfg.get("statuses", ["Gaming", "Chilling"])
    while True:
        try:
            await bot.change_presence(activity=discord.CustomActivity(name=random.choice(statuses)))
        except Exception:
            pass
        await asyncio.sleep(interval)

class StatusTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._task = None

    @commands.command(name="setstatus")
    async def setstatus(self, ctx, status_type: str = "online"):
        await ctx.message.delete()
        map_ = {
            "online": discord.Status.online,
            "dnd": discord.Status.dnd,
            "idle": discord.Status.idle,
            "invisible": discord.Status.invisible,
        }
        await self.bot.change_presence(status=map_.get(status_type.lower(), discord.Status.online))

    @commands.command(name="setgame")
    async def setgame(self, ctx, *, game: str):
        await ctx.message.delete()
        await self.bot.change_presence(activity=discord.Game(name=game))

    @commands.command(name="setstream")
    async def setstream(self, ctx, url: str, *, name: str = "Streaming"):
        await ctx.message.delete()
        await self.bot.change_presence(activity=discord.Streaming(name=name, url=url))

    @commands.command(name="setcustom")
    async def setcustom(self, ctx, *, text: str):
        await ctx.message.delete()
        await self.bot.change_presence(activity=discord.CustomActivity(name=text))

    @commands.command(name="rotatestatus")
    async def rotatestatus(self, ctx, interval: int = 30):
        await ctx.message.delete()
        if self._task:
            self._task.cancel()
        async def loop():
            while True:
                name = random.choice(self.bot.cfg.get("statuses", ["..."]))
                await self.bot.change_presence(activity=discord.CustomActivity(name=name))
                await asyncio.sleep(interval)
        self._task = asyncio.create_task(loop())
        await ctx.send(f"rotating every {interval}s", delete_after=3)

    @commands.command(name="stopstatus")
    async def stopstatus(self, ctx):
        await ctx.message.delete()
        if self._task:
            self._task.cancel()
            self._task = None

async def setup(bot):
    await bot.add_cog(StatusTools(bot))
