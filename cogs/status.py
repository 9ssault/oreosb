import asyncio
import random
import discord
from discord.ext import commands

async def start_rotator(bot):
    interval = max(10, int(bot.cfg.get("status_interval", 30)))
    statuses = bot.cfg.get("statuses") or ["Gaming", "Chilling"]
    while True:
        try:
            name = random.choice(statuses)
            await bot.change_presence(activity=discord.CustomActivity(name=name))
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
            "offline": discord.Status.invisible,
        }
        await self.bot.change_presence(status=map_.get(status_type.lower(), discord.Status.online))

    @commands.command(name="setgame")
    async def setgame(self, ctx, *, game: str):
        await ctx.message.delete()
        await self.bot.change_presence(activity=discord.Game(name=game[:128]))

    @commands.command(name="setstream")
    async def setstream(self, ctx, url: str, *, name: str = "Streaming"):
        await ctx.message.delete()
        if not url.startswith("http"):
            url = "https://twitch.tv/" + url
        await self.bot.change_presence(activity=discord.Streaming(name=name[:128], url=url))

    @commands.command(name="setcustom")
    async def setcustom(self, ctx, *, text: str):
        await ctx.message.delete()
        await self.bot.change_presence(activity=discord.CustomActivity(name=text[:128]))

    @commands.command(name="rotatestatus")
    async def rotatestatus(self, ctx, interval: int = 30):
        await ctx.message.delete()
        if self._task:
            self._task.cancel()
        interval = max(10, interval)

        async def loop():
            while True:
                name = random.choice(self.bot.cfg.get("statuses") or ["..."])
                try:
                    await self.bot.change_presence(activity=discord.CustomActivity(name=name))
                except Exception:
                    pass
                await asyncio.sleep(interval)

        self._task = asyncio.create_task(loop())
        await ctx.send(f"rotating every {interval}s", delete_after=3)

    @commands.command(name="stopstatus")
    async def stopstatus(self, ctx):
        await ctx.message.delete()
        if self._task:
            self._task.cancel()
            self._task = None
        try:
            await self.bot.change_presence(activity=None)
        except Exception:
            pass
        await ctx.send("stopped", delete_after=3)

async def setup(bot):
    await bot.add_cog(StatusTools(bot))
