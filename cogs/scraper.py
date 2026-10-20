import json
import csv
import asyncio
from pathlib import Path
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
            await ctx.send("need guild", delete_after=3)
            return
        guild = self.bot.get_guild(gid)
        if not guild:
            try:
                guild = await self.bot.fetch_guild(gid)
            except Exception:
                await ctx.send("guild not found", delete_after=4)
                return
        members = []
        try:
            async for m in guild.fetch_members(limit=None):
                members.append({
                    "id": str(m.id),
                    "username": str(m),
                    "display_name": m.display_name,
                    "bot": m.bot,
                    "joined_at": m.joined_at.isoformat() if m.joined_at else None,
                    "roles": [str(r.id) for r in getattr(m, "roles", [])],
                })
        except Exception:
            for m in guild.members:
                members.append({
                    "id": str(m.id),
                    "username": str(m),
                    "display_name": m.display_name,
                    "bot": m.bot,
                    "joined_at": m.joined_at.isoformat() if m.joined_at else None,
                    "roles": [str(r.id) for r in m.roles],
                })
        fname = f"scrape_{guild.id}"
        if fmt.lower() == "csv" and members:
            with open(f"{fname}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(members[0].keys()))
                w.writeheader()
                w.writerows(members)
            out = f"{fname}.csv"
        else:
            Path(f"{fname}.json").write_text(json.dumps(members, indent=2), encoding="utf-8")
            out = f"{fname}.json"
        await ctx.send(f"scraped {len(members)} → `{out}`", delete_after=6)

    @commands.command(name="msgscrape")
    async def msgscrape(self, ctx, channel_id: int = None, limit: int = 500):
        await ctx.message.delete()
        limit = max(1, min(limit, 5000))
        ch = self.bot.get_channel(channel_id) if channel_id else ctx.channel
        if not ch:
            await ctx.send("channel not found", delete_after=3)
            return
        msgs = []
        async for m in ch.history(limit=limit):
            msgs.append({
                "id": str(m.id),
                "author": str(m.author),
                "author_id": str(m.author.id),
                "content": m.content,
                "timestamp": m.created_at.isoformat(),
                "attachments": [a.url for a in m.attachments],
                "embeds": len(m.embeds),
            })
        path = f"messages_{ch.id}.json"
        Path(path).write_text(json.dumps(msgs, indent=2), encoding="utf-8")
        await ctx.send(f"scraped {len(msgs)} msgs → `{path}`", delete_after=5)

    @commands.command(name="scrapechannels")
    async def scrapechannels(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        g = self.bot.get_guild(guild_id or (ctx.guild.id if ctx.guild else 0))
        if not g:
            return
        data = []
        for c in g.channels:
            data.append({
                "id": str(c.id),
                "name": c.name,
                "type": str(c.type),
                "category": str(c.category_id) if getattr(c, "category_id", None) else None,
                "position": getattr(c, "position", None),
            })
        path = f"channels_{g.id}.json"
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        await ctx.send(f"{len(data)} channels → `{path}`", delete_after=5)

    @commands.command(name="scraperoles")
    async def scraperoles(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        g = self.bot.get_guild(guild_id or (ctx.guild.id if ctx.guild else 0))
        if not g:
            return
        data = [{
            "id": str(r.id),
            "name": r.name,
            "color": r.color.value,
            "perms": r.permissions.value,
            "position": r.position,
            "hoist": r.hoist,
            "mentionable": r.mentionable,
        } for r in g.roles]
        path = f"roles_{g.id}.json"
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        await ctx.send(f"{len(data)} roles → `{path}`", delete_after=5)

    @commands.command(name="scrapeemojis")
    async def scrapeemojis(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        g = self.bot.get_guild(guild_id or (ctx.guild.id if ctx.guild else 0))
        if not g:
            return
        data = [{
            "id": str(e.id),
            "name": e.name,
            "animated": e.animated,
            "url": str(e.url),
        } for e in g.emojis]
        path = f"emojis_{g.id}.json"
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        await ctx.send(f"{len(data)} emojis → `{path}`", delete_after=5)

async def setup(bot):
    await bot.add_cog(Scraper(bot))
