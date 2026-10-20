import json
from pathlib import Path
import discord
from discord.ext import commands

TAGS = Path("tags.json")

class Tag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tags = {}
        if TAGS.exists():
            try:
                self.tags = json.loads(TAGS.read_text())
            except Exception:
                self.tags = {}

    def _save(self):
        TAGS.write_text(json.dumps(self.tags, indent=2))

    @commands.command(name="tag")
    async def tag(self, ctx, name: str = None, *, content: str = None):
        await ctx.message.delete()
        if name is None:
            await ctx.send("tags: " + (", ".join(list(self.tags)[:40]) or "none"), delete_after=10)
            return
        if content is None:
            val = self.tags.get(name)
            if not val:
                await ctx.send("unknown tag", delete_after=3)
                return
            await ctx.send(val[:2000])
            return
        self.tags[name] = content
        self._save()
        await ctx.send(f"tag `{name}` saved", delete_after=3)

    @commands.command(name="deltag")
    async def deltag(self, ctx, name: str):
        await ctx.message.delete()
        if name in self.tags:
            del self.tags[name]
            self._save()
            await ctx.send(f"deleted `{name}`", delete_after=3)
        else:
            await ctx.send("missing", delete_after=3)

async def setup(bot):
    await bot.add_cog(Tag(bot))
