import asyncio
import json
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

import discord
from discord.ext import commands

from core_utils import owner_check

EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


class Export(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _collect(self, channel, limit: int):
        msgs = []
        # no hard 1000 cap — paginate with before
        fetched = 0
        before = None
        while fetched < limit:
            batch = min(100, limit - fetched)
            kwargs = {"limit": batch}
            if before:
                kwargs["before"] = before
            chunk = []
            async for m in channel.history(**kwargs):
                chunk.append(m)
            if not chunk:
                break
            for m in chunk:
                msgs.append({
                    "id": str(m.id),
                    "author": str(m.author),
                    "author_id": str(m.author.id),
                    "content": m.content or "",
                    "ts": m.created_at.isoformat() if m.created_at else "",
                    "attachments": [a.url for a in m.attachments],
                    "embeds": len(m.embeds),
                })
            fetched += len(chunk)
            before = chunk[-1]
            if len(chunk) < batch:
                break
            await asyncio.sleep(0.15)
        return msgs

    def _write_split(self, base: str, msgs: list, max_chars: int = 1_800_000):
        """Write JSON; if huge, split into parts and zip. Returns path list / zip path."""
        raw = json.dumps(msgs, ensure_ascii=False, indent=2)
        if len(raw) <= max_chars:
            path = EXPORT_DIR / f"{base}.json"
            path.write_text(raw, encoding="utf-8")
            return [path], None
        # split by message batches
        parts = []
        part_i = 0
        buf = []
        size = 2
        for item in msgs:
            piece = json.dumps(item, ensure_ascii=False)
            if size + len(piece) > max_chars and buf:
                p = EXPORT_DIR / f"{base}_part{part_i}.json"
                p.write_text(json.dumps(buf, ensure_ascii=False, indent=2), encoding="utf-8")
                parts.append(p)
                part_i += 1
                buf = []
                size = 2
            buf.append(item)
            size += len(piece) + 2
        if buf:
            p = EXPORT_DIR / f"{base}_part{part_i}.json"
            p.write_text(json.dumps(buf, ensure_ascii=False, indent=2), encoding="utf-8")
            parts.append(p)
        zpath = EXPORT_DIR / f"{base}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in parts:
                zf.write(p, p.name)
        return parts, zpath

    @commands.command(name="export")
    @owner_check()
    async def export(self, ctx, limit: int = 500):
        status = await ctx.send(f"exporting up to {limit}…")
        try:
            msgs = await self._collect(ctx.channel, max(1, limit))
            base = f"ch_{ctx.channel.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            parts, zpath = self._write_split(base, msgs)
            count = len(msgs)
            if zpath:
                # try send zip if under 25MB else local only
                size = zpath.stat().st_size
                if size < 24 * 1024 * 1024:
                    await ctx.send(
                        f"exported **{count}** msgs → `{zpath.name}` ({size // 1024} KB)",
                        file=discord.File(zpath),
                    )
                else:
                    await ctx.send(
                        f"exported **{count}** msgs → `{zpath}` on disk ({size // 1024} KB) — too large to upload"
                    )
            else:
                p = parts[0]
                size = p.stat().st_size
                if size < 24 * 1024 * 1024:
                    await ctx.send(
                        f"exported **{count}** msgs → `{p.name}`",
                        file=discord.File(p),
                    )
                else:
                    await ctx.send(f"exported **{count}** → `{p}` ({size // 1024} KB)")
        except Exception as e:
            await ctx.send(f"export fail: {e}")
        try:
            await status.delete()
        except Exception:
            pass

    @commands.command(name="exportdm")
    @owner_check()
    async def exportdm(self, ctx, user: discord.User, limit: int = 300):
        status = await ctx.send(f"exporting dm {user}…")
        try:
            dm = user.dm_channel or await user.create_dm()
            msgs = await self._collect(dm, max(1, limit))
            base = f"dm_{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            parts, zpath = self._write_split(base, msgs)
            count = len(msgs)
            target = zpath or parts[0]
            size = target.stat().st_size
            if size < 24 * 1024 * 1024:
                await ctx.send(f"dm **{count}** → `{target.name}`", file=discord.File(target))
            else:
                await ctx.send(f"dm **{count}** → `{target}` ({size // 1024} KB)")
        except Exception as e:
            await ctx.send(f"exportdm fail: {e}")
        try:
            await status.delete()
        except Exception:
            pass

    @commands.command(name="exportguild")
    @owner_check()
    async def exportguild(self, ctx, limit_per_channel: int = 200):
        if not ctx.guild:
            await ctx.send("guild only")
            return
        status = await ctx.send("exporting guild…")
        all_data = {"guild": str(ctx.guild.id), "name": ctx.guild.name, "channels": {}}
        total = 0
        for ch in ctx.guild.text_channels:
            try:
                msgs = await self._collect(ch, limit_per_channel)
                all_data["channels"][str(ch.id)] = {"name": ch.name, "messages": msgs}
                total += len(msgs)
            except Exception:
                continue
            await asyncio.sleep(0.2)
        base = f"guild_{ctx.guild.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        parts, zpath = self._write_split(base, [all_data])
        # always write full structure as single json too
        path = EXPORT_DIR / f"{base}_full.json"
        path.write_text(json.dumps(all_data, ensure_ascii=False), encoding="utf-8")
        await ctx.send(f"guild export **{total}** msgs → `{path.name}`")
        try:
            await status.delete()
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Export(bot))


# ── full account export (from exportz) ─────────────────────────
import os
import re
import html as html_mod
import aiohttp
from datetime import timezone

def _safe_name(s, maxlen=60):
    if not s:
        return "unnamed"
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", s).strip(". ")
    return s[:maxlen] or "unnamed"


class FullExportMixin:
    pass


# attach fullexport onto Export class via monkey after class def — instead rewrite command into Export
