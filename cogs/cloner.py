import asyncio
import json
from pathlib import Path
import discord
from discord.ext import commands

class Cloner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clone")
    async def clone(self, ctx, source_id: int, target_id: int = None):
        await ctx.message.delete()
        src = self.bot.get_guild(source_id)
        if not src:
            try:
                src = await self.bot.fetch_guild(source_id)
            except Exception:
                await ctx.send("source not found", delete_after=4)
                return
        tgt = self.bot.get_guild(target_id) if target_id else ctx.guild
        if not tgt:
            await ctx.send("target not found", delete_after=4)
            return
        role_ok = ch_ok = 0
        for role in reversed(list(src.roles)):
            if role.is_default():
                continue
            try:
                await tgt.create_role(
                    name=role.name[:100],
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                )
                role_ok += 1
            except Exception as e:
                print(f"[CLONE] role {role.name}: {e}")
            await asyncio.sleep(0.45)
        for ch in src.channels:
            try:
                if isinstance(ch, discord.CategoryChannel):
                    await tgt.create_category(ch.name)
                elif isinstance(ch, discord.TextChannel):
                    await tgt.create_text_channel(ch.name, topic=(ch.topic or "")[:1024])
                elif isinstance(ch, discord.VoiceChannel):
                    await tgt.create_voice_channel(ch.name)
                ch_ok += 1
            except Exception as e:
                print(f"[CLONE] channel {ch.name}: {e}")
            await asyncio.sleep(0.4)
        await ctx.send(f"clone → roles {role_ok} channels {ch_ok}", delete_after=8)

    @commands.command(name="backup")
    async def backup(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        g = self.bot.get_guild(guild_id or (ctx.guild.id if ctx.guild else 0))
        if not g:
            await ctx.send("guild not found", delete_after=3)
            return
        data = {
            "name": g.name,
            "id": str(g.id),
            "roles": [{
                "name": r.name,
                "perms": r.permissions.value,
                "color": r.color.value,
                "hoist": r.hoist,
                "mentionable": r.mentionable,
                "position": r.position,
            } for r in g.roles],
            "channels": [{
                "name": c.name,
                "type": str(c.type),
                "position": getattr(c, "position", 0),
                "topic": getattr(c, "topic", None),
                "category_id": str(c.category_id) if getattr(c, "category_id", None) else None,
            } for c in g.channels],
            "emojis": [{"name": e.name, "id": str(e.id), "url": str(e.url)} for e in g.emojis],
        }
        path = f"backup_{g.id}.json"
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        await ctx.send(f"`{path}` written", delete_after=5)

async def setup(bot):
    await bot.add_cog(Cloner(bot))
