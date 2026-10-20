import json
from datetime import datetime, timezone
from pathlib import Path
import discord
from discord.ext import commands

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = set()
        self.global_on = False
        Path("logs").mkdir(exist_ok=True)

    def _write(self, channel_id: int, entry: dict):
        path = Path("logs") / f"{channel_id}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @commands.command(name="log")
    async def log(self, ctx, mode: str = "on"):
        await ctx.message.delete()
        m = mode.lower()
        if m in ("on", "start", "1", "true"):
            self.enabled.add(ctx.channel.id)
            await ctx.send("logging on (this channel)", delete_after=3)
        elif m in ("off", "stop", "0", "false"):
            self.enabled.discard(ctx.channel.id)
            await ctx.send("logging off", delete_after=3)
        elif m == "global":
            self.global_on = not self.global_on
            await ctx.send(f"global log `{'on' if self.global_on else 'off'}`", delete_after=4)
        elif m == "status":
            await ctx.send(
                f"channels={len(self.enabled)} global={self.global_on}",
                delete_after=5,
            )
        else:
            await ctx.send("`log on|off|global|status`", delete_after=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if not self.global_on and message.channel.id not in self.enabled:
            return
        entry = {
            "t": datetime.now(timezone.utc).isoformat(),
            "type": "message",
            "a": str(message.author),
            "aid": str(message.author.id),
            "c": (message.content or "")[:2000],
            "id": str(message.id),
            "gid": str(message.guild.id) if message.guild else None,
            "attachments": [a.url for a in message.attachments],
        }
        self._write(message.channel.id, entry)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not self.global_on and message.channel.id not in self.enabled:
            return
        if not message or message.author.id == self.bot.user.id:
            return
        entry = {
            "t": datetime.now(timezone.utc).isoformat(),
            "type": "delete",
            "a": str(message.author),
            "aid": str(message.author.id),
            "c": (message.content or "")[:2000],
            "id": str(message.id),
        }
        self._write(message.channel.id, entry)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not self.global_on and before.channel.id not in self.enabled:
            return
        if before.author.id == self.bot.user.id or before.content == after.content:
            return
        entry = {
            "t": datetime.now(timezone.utc).isoformat(),
            "type": "edit",
            "a": str(before.author),
            "aid": str(before.author.id),
            "before": (before.content or "")[:1000],
            "after": (after.content or "")[:1000],
            "id": str(before.id),
        }
        self._write(before.channel.id, entry)

    @commands.command(name="logtail")
    async def logtail(self, ctx, lines: int = 10):
        await ctx.message.delete()
        path = Path("logs") / f"{ctx.channel.id}.jsonl"
        if not path.exists():
            await ctx.send("no log file", delete_after=3)
            return
        rows = path.read_text(encoding="utf-8").splitlines()[-max(1, min(lines, 30)):]
        body = "\n".join(rows)[:1900]
        await ctx.send(f"```\n{body}\n```", delete_after=20)

async def setup(bot):
    await bot.add_cog(Logger(bot))
