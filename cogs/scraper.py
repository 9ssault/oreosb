# cogs/scraper.py
import json
import csv
import asyncio
import discord
from discord.ext import commands

class Scraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="scrape")
    async def scrape(self, ctx, guild_id: int = None, fmt: str = "json"):
        await ctx.message.delete()
        gid = guild_id or (ctx.guild.id if ctx.guild else None)
        if not gid:
            return
        guild = self.bot.get_guild(gid) or await self.bot.fetch_guild(gid)
        members = []
        async for m in guild.fetch_members(limit=None):
            members.append({
                "id": str(m.id),
                "username": str(m),
                "display_name": m.display_name,
                "bot": m.bot,
                "joined_at": str(m.joined_at) if m.joined_at else None,
                "roles": [str(r.id) for r in m.roles],
            })
            await asyncio.sleep(0.01)
        fname = f"scrape_{guild.id}"
        if fmt == "csv":
            with open(f"{fname}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=members[0].keys())
                w.writeheader()
                w.writerows(members)
        else:
            with open(f"{fname}.json", "w", encoding="utf-8") as f:
                json.dump(members, f, indent=2)
        await ctx.send(f"scraped {len(members)} → {fname}.{fmt}", delete_after=5)

    @commands.command(name="msgscrape")
    async def msgscrape(self, ctx, channel_id: int = None, limit: int = 1000):
        await ctx.message.delete()
        ch = ctx.channel if not channel_id else self.bot.get_channel(channel_id)
        if not ch:
            return
        msgs = []
        async for m in ch.history(limit=limit):
            msgs.append({
                "id": str(m.id),
                "author": str(m.author),
                "content": m.content,
                "timestamp": str(m.created_at),
                "attachments": [a.url for a in m.attachments],
            })
        with open(f"messages_{ch.id}.json", "w", encoding="utf-8") as f:
            json.dump(msgs, f, indent=2)
        await ctx.send(f"scraped {len(msgs)} msgs", delete_after=3)

    @commands.command(name="ginfo")
    async def ginfo(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        g = self.bot.get_guild(guild_id or ctx.guild.id) if (guild_id or ctx.guild) else None
        if not g:
            return
        data = {
            "id": str(g.id),
            "name": g.name,
            "owner_id": str(g.owner_id),
            "member_count": g.member_count,
            "channels": len(g.channels),
            "roles": len(g.roles),
            "emojis": len(g.emojis),
            "boosts": g.premium_subscription_count,
        }
        await ctx.send(f"```json\n{json.dumps(data, indent=2)}\n```", delete_after=15)

async def setup(bot):
    await bot.add_cog(Scraper(bot))
