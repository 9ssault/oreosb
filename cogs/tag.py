import json
from pathlib import Path
import discord
from discord.ext import commands

TAGS = Path("tags.json")

def load():
    if TAGS.exists():
        return json.loads(TAGS.read_text())
    return {}

def save(data):
    TAGS.write_text(json.dumps(data, indent=2))

class Tag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tag")
    async def tag(self, ctx, name: str = None, *, content: str = None):
        await ctx.message.delete()
        data = load()
        if name is None:
            await ctx.send("tags: " + ", ".join(list(data.keys())[:30]), delete_after=10)
            return
        if content is None:
            await ctx.send(data.get(name, "not found"), delete_after=12)
            return
        data[name] = content
        save(data)
        await ctx.send(f"tag `{name}` saved", delete_after=3)

    @commands.command(name="deltag")
    async def deltag(self, ctx, name: str):
        await ctx.message.delete()
        data = load()
        data.pop(name, None)
        save(data)
        await ctx.send("deleted", delete_after=3)

async def setup(bot):
    await bot.add_cog(Tag(bot))
