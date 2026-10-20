import json
from pathlib import Path
import discord
from discord.ext import commands

NOTES = Path("notes.json")

class Note(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        if NOTES.exists():
            try:
                self.data = json.loads(NOTES.read_text())
            except Exception:
                self.data = {}

    def _save(self):
        NOTES.write_text(json.dumps(self.data, indent=2))

    @commands.command(name="note")
    async def note(self, ctx, key: str = None, *, value: str = None):
        await ctx.message.delete()
        if key is None:
            keys = list(self.data.keys())[:40]
            await ctx.send("notes: " + (", ".join(keys) or "none"), delete_after=10)
            return
        if value is None:
            await ctx.send(self.data.get(key, "not found")[:1900], delete_after=12)
            return
        self.data[key] = value
        self._save()
        await ctx.send(f"saved `{key}`", delete_after=3)

    @commands.command(name="clearnote")
    async def clearnote(self, ctx, key: str):
        await ctx.message.delete()
        if key in self.data:
            del self.data[key]
            self._save()
            await ctx.send(f"cleared `{key}`", delete_after=3)
        else:
            await ctx.send("missing", delete_after=3)

async def setup(bot):
    await bot.add_cog(Note(bot))
