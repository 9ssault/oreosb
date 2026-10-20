import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = set()
        Path("logs").mkdir(exist_ok=True)

    @commands.command(name="log")
    async def log(self, ctx, mode: str = "on"):
        await ctx.message.delete()
        cid = ctx.channel.id
        if mode.lower() in ("on", "start", "1"):
            self.enabled.add(cid)
            await ctx.send(f"logging on in this channel", delete_after=3)
        else:
            self.enabled.discard(cid)
            await ctx.send(f"logging off", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id not in self.enabled:
            return
        if message.author == self.bot.user:
            return
        entry = {
            "t": datetime.utcnow().isoformat(),
            "a": str(message.author),
            "c": message.content[:2000],
            "id": str(message.id),
        }
        path = Path("logs") / f"{message.channel.id}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

async def setup(bot):
    await bot.add_cog(Logger(bot))
