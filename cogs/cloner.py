# cogs/cloner.py — server structure cloner
import asyncio
import json
import discord
from discord.ext import commands

class Cloner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clone")
    async def clone(self, ctx, source_id: int, target_id: int = None):
        """clone channels + roles from source guild into target (or current)"""
        await ctx.message.delete()
        src = self.bot.get_guild(source_id) or await self.bot.fetch_guild(source_id)
        tgt = self.bot.get_guild(target_id) if target_id else ctx.guild
        if not src or not tgt:
            await ctx.send("guild not found", delete_after=4)
            return
        # roles
        role_map = {}
        for role in reversed(src.roles):
            if role.is_default():
                continue
            try:
                new = await tgt.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                )
                role_map[role.id] = new
                await asyncio.sleep(0.4)
            except Exception as e:
                print(f"[CLONE] role fail {role.name}: {e}")
        # channels (simple text/voice)
        for ch in src.channels:
            try:
                if isinstance(ch, discord.TextChannel):
                    await tgt.create_text_channel(ch.name, topic=ch.topic or "")
                elif isinstance(ch, discord.VoiceChannel):
                    await tgt.create_voice_channel(ch.name)
                await asyncio.sleep(0.35)
            except Exception as e:
                print(f"[CLONE] channel fail {ch.name}: {e}")
        await ctx.send(f"clone done → {tgt.name}", delete_after=6)

    @commands.command(name="backup")
    async def backup(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        g = self.bot.get_guild(guild_id or ctx.guild.id)
        if not g:
            return
        data = {
            "name": g.name,
            "id": str(g.id),
            "roles": [{"name": r.name, "perms": r.permissions.value, "color": r.color.value} for r in g.roles],
            "channels": [{"name": c.name, "type": str(c.type)} for c in g.channels],
        }
        with open(f"backup_{g.id}.json", "w") as f:
            json.dump(data, f, indent=2)
        await ctx.send(f"backup_{g.id}.json written", delete_after=4)

async def setup(bot):
    await bot.add_cog(Cloner(bot))
