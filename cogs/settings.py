import json
from pathlib import Path
import discord
from discord.ext import commands

CFG = Path("config.json")

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _save(self):
        CFG.write_text(json.dumps(self.bot.cfg, indent=2))

    @commands.command(name="cfg")
    async def cfg(self, ctx, key: str = None, *, value: str = None):
        await ctx.message.delete()
        if not key:
            pretty = json.dumps(self.bot.cfg, indent=2)[:1800]
            await ctx.send(f"```json\n{pretty}\n```", delete_after=20)
            return
        if value is None:
            await ctx.send(f"`{key}` = `{self.bot.cfg.get(key)}`", delete_after=8)
            return
        low = value.lower()
        if low in ("true", "false"):
            parsed = low == "true"
        else:
            try:
                parsed = int(value)
            except ValueError:
                try:
                    parsed = float(value)
                except ValueError:
                    parsed = value
        self.bot.cfg[key] = parsed
        self._save()
        await ctx.send(f"set `{key}` = `{parsed}`", delete_after=5)

    @commands.command(name="prefix")
    async def prefix(self, ctx, new: str):
        await ctx.message.delete()
        self.bot.command_prefix = new
        self.bot.cfg["prefix"] = new
        self._save()
        await ctx.send(f"prefix → `{new}`", delete_after=4)

async def setup(bot):
    await bot.add_cog(Settings(bot))
