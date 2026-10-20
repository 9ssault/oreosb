import json
from pathlib import Path
import discord
from discord.ext import commands

class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="export")
    async def export(self, ctx, limit: int = 200):
        await ctx.message.delete()
        limit = max(1, min(limit, 2000))
        msgs = []
        async for m in ctx.channel.history(limit=limit):
            msgs.append({
                "id": str(m.id),
                "author": str(m.author),
                "author_id": str(m.author.id),
                "content": m.content,
                "ts": m.created_at.isoformat(),
                "attachments": [a.url for a in m.attachments],
            })
        path = Path(f"export_{ctx.channel.id}.json")
        path.write_text(json.dumps(msgs, indent=2), encoding="utf-8")
        await ctx.send(f"exported {len(msgs)} → `{path.name}`", delete_after=8)

    @commands.command(name="exportdm")
    async def exportdm(self, ctx, user: discord.User, limit: int = 100):
        await ctx.message.delete()
        limit = max(1, min(limit, 1000))
        dm = user.dm_channel or await user.create_dm()
        msgs = []
        async for m in dm.history(limit=limit):
            msgs.append({
                "id": str(m.id),
                "author": str(m.author),
                "content": m.content,
                "ts": m.created_at.isoformat(),
            })
        path = Path(f"export_dm_{user.id}.json")
        path.write_text(json.dumps(msgs, indent=2), encoding="utf-8")
        await ctx.send(f"dm export {len(msgs)} → `{path.name}`", delete_after=6)

async def setup(bot):
    await bot.add_cog(Export(bot))
