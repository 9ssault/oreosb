import json
import asyncio
from pathlib import Path
import discord
from discord.ext import commands

MACROS = Path("macros.json")

class Macro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.macros = {}
        if MACROS.exists():
            try:
                self.macros = json.loads(MACROS.read_text())
            except Exception:
                self.macros = {}

    def _save(self):
        MACROS.write_text(json.dumps(self.macros, indent=2))

    @commands.command(name="macro")
    async def macro(self, ctx, name: str = None, *, steps: str = None):
        """macro name | step1 | step2  OR macro name to list"""
        await ctx.message.delete()
        if name is None:
            await ctx.send("macros: " + (", ".join(list(self.macros)[:30]) or "none"), delete_after=10)
            return
        if steps is None:
            m = self.macros.get(name)
            if not m:
                await ctx.send("unknown", delete_after=3)
                return
            await ctx.send(f"`{name}`: " + " | ".join(m)[:500], delete_after=12)
            return
        parts = [p.strip() for p in steps.split("|") if p.strip()]
        self.macros[name] = parts
        self._save()
        await ctx.send(f"macro `{name}` ({len(parts)} steps)", delete_after=4)

    @commands.command(name="delmacro")
    async def delmacro(self, ctx, name: str):
        await ctx.message.delete()
        if name in self.macros:
            del self.macros[name]
            self._save()
            await ctx.send(f"deleted `{name}`", delete_after=3)

    @commands.command(name="runmacro")
    async def runmacro(self, ctx, name: str, delay: float = 1.0):
        await ctx.message.delete()
        steps = self.macros.get(name)
        if not steps:
            await ctx.send("unknown macro", delete_after=3)
            return
        for s in steps:
            try:
                await ctx.send(s[:2000])
            except Exception:
                break
            await asyncio.sleep(max(0.3, delay))

async def setup(bot):
    await bot.add_cog(Macro(bot))
