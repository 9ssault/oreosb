import json
from pathlib import Path
import discord
from discord.ext import commands

MACROS = Path("macros.json")

def load():
    if MACROS.exists():
        return json.loads(MACROS.read_text())
    return {}

def save(d):
    MACROS.write_text(json.dumps(d, indent=2))

class Macro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="macro")
    async def macro(self, ctx, name: str = None, *, content: str = None):
        await ctx.message.delete()
        data = load()
        if name is None:
            await ctx.send("macros: " + ", ".join(data.keys()) or "none", delete_after=10)
            return
        if content is None:
            await ctx.send(data.get(name, "not found"), delete_after=15)
            return
        data[name] = content
        save(data)
        await ctx.send(f"macro `{name}` saved", delete_after=3)

    @commands.command(name="delmacro")
    async def delmacro(self, ctx, name: str):
        await ctx.message.delete()
        data = load()
        data.pop(name, None)
        save(data)
        await ctx.send("deleted", delete_after=3)

    @commands.command(name="runmacro")
    async def runmacro(self, ctx, name: str):
        await ctx.message.delete()
        data = load()
        text = data.get(name)
        if not text:
            await ctx.send("missing", delete_after=3)
            return
        await ctx.send(text)

async def setup(bot):
    await bot.add_cog(Macro(bot))
