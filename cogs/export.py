import asyncio
import os
import re
import json
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

import aiohttp
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



    @commands.command(name="fullexport")
    @owner_check()
    async def fullexport(self, ctx, mode: str = "quick"):
        """Full account dump to zip (account + guilds + dms). mode=quick|full"""
        await ctx.message.delete()
        token = self.bot.http.token
        if not token:
            await ctx.send("no token", delete_after=4)
            return
        status = await ctx.send("fullexport starting…")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = EXPORT_DIR / f"full_{stamp}"
        out.mkdir(parents=True, exist_ok=True)
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        API = "https://discord.com/api/v10"
        stats = {"guilds": 0, "dms": 0, "channels": 0, "messages": 0}

        def safe(s, maxlen=60):
            if not s:
                return "unnamed"
            s = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1f]', "_", str(s)).strip(". ")
            return s[:maxlen] or "unnamed"

        async def api_get(session, path):
            for _ in range(5):
                try:
                    async with session.get(f"{API}{path}", headers=headers) as r:
                        if r.status == 429:
                            try:
                                body = await r.json()
                                await asyncio.sleep(float(body.get("retry_after", 1.5)) + 0.2)
                            except Exception:
                                await asyncio.sleep(1.5)
                            continue
                        if r.status in (401, 403, 404):
                            return None
                        if r.status == 200:
                            return await r.json(content_type=None)
                        return None
                except Exception:
                    await asyncio.sleep(0.5)
            return None

        async def fetch_msgs(session, cid, max_pages=None):
            if max_pages is None:
                max_pages = 40 if mode != "full" else 400
            all_m = []
            before = None
            for _ in range(max_pages):
                q = f"/channels/{cid}/messages?limit=100"
                if before:
                    q += f"&before={before}"
                data = await api_get(session, q)
                if not data or not isinstance(data, list):
                    break
                all_m.extend(data)
                if len(data) < 100:
                    break
                before = data[-1]["id"]
                await asyncio.sleep(0.35)
            return all_m

        try:
            async with aiohttp.ClientSession() as session:
                me = await api_get(session, "/users/@me")
                if not me:
                    await status.edit(content="token invalid")
                    return
                (out / "account").mkdir(exist_ok=True)
                (out / "account" / "me.json").write_text(json.dumps(me, indent=2), encoding="utf-8")
                for ep, fn in [
                    ("/users/@me/relationships", "relationships.json"),
                    ("/users/@me/connections", "connections.json"),
                    ("/users/@me/settings", "settings.json"),
                    ("/users/@me/guilds", "guilds_list.json"),
                    ("/users/@me/channels", "dm_channels_list.json"),
                ]:
                    data = await api_get(session, ep)
                    if data is not None:
                        (out / "account" / fn).write_text(
                            json.dumps(data, indent=2, default=str), encoding="utf-8"
                        )

                guilds = await api_get(session, "/users/@me/guilds") or []
                if isinstance(guilds, list):
                    for g in guilds:
                        gid = g.get("id")
                        if not gid:
                            continue
                        gdir = out / "guilds" / f"{safe(g.get('name',''))}_{gid}"
                        gdir.mkdir(parents=True, exist_ok=True)
                        (gdir / "guild.json").write_text(json.dumps(g, indent=2), encoding="utf-8")
                        chans = await api_get(session, f"/guilds/{gid}/channels") or []
                        if isinstance(chans, list):
                            (gdir / "channels.json").write_text(
                                json.dumps(chans, indent=2), encoding="utf-8"
                            )
                            for ch in chans:
                                if ch.get("type") not in (0, 5):
                                    continue
                                cid = ch["id"]
                                msgs = await fetch_msgs(session, cid)
                                stats["messages"] += len(msgs)
                                stats["channels"] += 1
                                cdir = gdir / "channels" / f"{safe(ch.get('name',''))}_{cid}"
                                cdir.mkdir(parents=True, exist_ok=True)
                                (cdir / "messages.json").write_text(
                                    json.dumps(msgs, indent=2, default=str), encoding="utf-8"
                                )
                        stats["guilds"] += 1
                        await status.edit(
                            content=f"fullexport guilds {stats['guilds']}/{len(guilds)} msgs={stats['messages']}"
                        )

                dms = await api_get(session, "/users/@me/channels") or []
                if isinstance(dms, list):
                    for ch in dms:
                        cid = ch.get("id")
                        if not cid:
                            continue
                        label = f"dm_{cid}"
                        if ch.get("type") == 1:
                            rec = (ch.get("recipients") or [{}])[0]
                            label = f"dm_{safe(rec.get('username','u'))}_{cid}"
                        elif ch.get("type") == 3:
                            label = f"group_{cid}"
                        ddir = out / "dms" / label
                        ddir.mkdir(parents=True, exist_ok=True)
                        (ddir / "info.json").write_text(
                            json.dumps(ch, indent=2, default=str), encoding="utf-8"
                        )
                        msgs = await fetch_msgs(session, cid)
                        stats["messages"] += len(msgs)
                        stats["dms"] += 1
                        (ddir / "messages.json").write_text(
                            json.dumps(msgs, indent=2, default=str), encoding="utf-8"
                        )
                    await status.edit(
                        content=f"fullexport dms {stats['dms']} msgs={stats['messages']}"
                    )

            zpath = EXPORT_DIR / f"full_{stamp}.zip"
            with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(out):
                    for fn in files:
                        fp = Path(root) / fn
                        z.write(fp, fp.relative_to(out))
            summary = (
                f"fullexport done — guilds={stats['guilds']} dms={stats['dms']} "
                f"channels={stats['channels']} msgs={stats['messages']}"
            )
            try:
                await status.delete()
            except Exception:
                pass
            size = zpath.stat().st_size
            if size < 24 * 1024 * 1024:
                await ctx.send(summary, file=discord.File(str(zpath)))
            else:
                await ctx.send(f"{summary}\nzip too large ({size // 1024 // 1024} MB) saved `{zpath}`")
        except Exception as e:
            try:
                await status.edit(content=f"fullexport fail: {e}")
            except Exception:
                await ctx.send(f"fullexport fail: {e}", delete_after=10)




async def setup(bot):
    await bot.add_cog(Export(bot))
