import json
from pathlib import Path
import discord
from discord.ext import commands

NOTES = Path("notes.json")

def load():
    if NOTES.exists():
        return json.loads(NOTES.read_text())
    return {}

def save(data):
    NOTES.write_text(json.dumps(data, indent=2))

class Note(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="note")
    async def note(self, ctx, *, text: str = None):
        await ctx.message.delete()
        data = load()
        uid = str(ctx.author.id)
        if text is None:
            await ctx.send(data.get(uid, "no note"), delete_after=10)
            return
        data[uid] = text
        save(data)
        await ctx.send("note saved", delete_after=3)

    @commands.command(name="clearnote")
    async def clearnote(self, ctx):
        await ctx.message.delete()
        data = load()
        data.pop(str(ctx.author.id), None)
        save(data)
        await ctx.send("note cleared", delete_after=3)

async def setup(bot):
    await bot.add_cog(Note(bot))
