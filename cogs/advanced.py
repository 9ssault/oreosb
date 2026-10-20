# cogs/advanced.py — extra power tools
import asyncio
import random
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Advanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        """last deleted message in channel (simple cache)"""
        await ctx.message.delete()
        # lightweight: just acknowledge — full snipe needs on_message_delete listener
        await ctx.send("snipe cache not persistent yet — enable on_message_delete for full", delete_after=4)

    @commands.command(name="copycat")
    async def copycat(self, ctx, target: discord.Member = None):
        await ctx.message.delete()
        if not hasattr(self, "_copy"):
            self._copy = None
        if target:
            self._copy = target.id
            await ctx.send(f"copying {target}", delete_after=3)
        else:
            self._copy = None
            await ctx.send("copycat off", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if getattr(self, "_copy", None) and message.author.id == self._copy:
            if message.content and message.author != self.bot.user:
                try:
                    await message.channel.send(message.content)
                except Exception:
                    pass

    @commands.command(name="autoreply")
    async def autoreply(self, ctx, *, text: str = None):
        await ctx.message.delete()
        if not hasattr(self, "_ar"):
            self._ar = None
        if text:
            self._ar = text
            await ctx.send("auto-reply set", delete_after=3)
        else:
            self._ar = None
            await ctx.send("auto-reply off", delete_after=3)

    @commands.Cog.listener()
    async def on_message_mention(self, message):
        pass  # placeholder

    @commands.command(name="serverclone")
    async def serverclone(self, ctx, target_id: int = None):
        """basic structure dump of current or target guild"""
        await ctx.message.delete()
        g = self.bot.get_guild(target_id) if target_id else ctx.guild
        if not g:
            return
        data = {
            "name": g.name,
            "id": str(g.id),
            "channels": [{"name": c.name, "type": str(c.type), "id": str(c.id)} for c in g.channels],
            "roles": [{"name": r.name, "id": str(r.id), "perms": r.permissions.value} for r in g.roles],
        }
        import json
        with open(f"clone_{g.id}.json", "w") as f:
            json.dump(data, f, indent=2)
        await ctx.send(f"dumped → clone_{g.id}.json", delete_after=5)

    @commands.command(name="invitejoin")
    async def invitejoin(self, ctx, code: str):
        await ctx.message.delete()
        code = code.replace("https://discord.gg/", "").replace("discord.gg/", "").strip()
        headers = {"Authorization": self.bot.http.token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/invites/{code}", headers=headers, json={}) as r:
                data = await r.json(content_type=None)
                if r.status in (200, 204):
                    await ctx.send(f"joined {data.get('guild', {}).get('name', code)}", delete_after=5)
                else:
                    await ctx.send(f"fail {r.status}: {str(data)[:80]}", delete_after=6)

    @commands.command(name="massleave")
    async def massleave(self, ctx, delay: float = 0.8):
        await ctx.message.delete()
        left = 0
        for g in list(self.bot.guilds):
            try:
                await g.leave()
                left += 1
            except Exception:
                pass
            await asyncio.sleep(delay)
        await ctx.send(f"left {left}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Advanced(bot))
