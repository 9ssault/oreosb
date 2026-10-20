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
        msgs = []
        async for m in ctx.channel.history(limit=min(limit, 1000)):
            msgs.append({
                "id": str(m.id),
                "author": str(m.author),
                "content": m.content,
                "ts": m.created_at.isoformat(),
            })
        path = Path(f"export_{ctx.channel.id}.json")
        path.write_text(json.dumps(msgs, indent=2))
        await ctx.send(f"exported {len(msgs)} → {path.name}", delete_after=8)

    @commands.command(name="exportdm")
    async def exportdm(self, ctx, user: discord.User, limit: int = 100):
        await ctx.message.delete()
        dm = await user.create_dm()
        msgs = []
        async for m in dm.history(limit=min(limit, 500)):
            msgs.append({"id": str(m.id), "author": str(m.author), "content": m.content})
        path = Path(f"export_dm_{user.id}.json")
        path.write_text(json.dumps(msgs, indent=2))
        await ctx.send(f"dm export {len(msgs)}", delete_after=6)

async def setup(bot):
    await bot.add_cog(Export(bot))
