"""Restored utility commands that were dropped from history."""
import asyncio
from datetime import datetime, timezone

import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"


class ExtrasRestore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="incoming")
    async def incoming(self, ctx):
        await ctx.message.delete()
        headers = {"Authorization": self.bot.http.token}
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/users/@me/relationships", headers=headers) as r:
                data = await r.json(content_type=None) if r.status == 200 else []
        pending = [x for x in data if x.get("type") == 3]
        if not pending:
            await ctx.send("no incoming", delete_after=4)
            return
        lines = [f"<@{p['id']}>" for p in pending[:30]]
        await ctx.send("incoming:\n" + "\n".join(lines), delete_after=20)

    @commands.command(name="acceptall")
    async def acceptall(self, ctx):
        await ctx.message.delete()
        headers = {"Authorization": self.bot.http.token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/users/@me/relationships", headers=headers) as r:
                data = await r.json(content_type=None) if r.status == 200 else []
            ok = 0
            for p in data:
                if p.get("type") != 3:
                    continue
                async with s.put(
                    f"{API}/users/@me/relationships/{p['id']}",
                    headers=headers,
                    json={"type": 1},
                ) as r2:
                    if r2.status in (200, 204):
                        ok += 1
                await asyncio.sleep(0.8)
        await ctx.send(f"accepted {ok}", delete_after=5)

    @commands.command(name="untimeout")
    async def untimeout(self, ctx, member: discord.Member):
        await ctx.message.delete()
        try:
            await member.timeout(None)
            await ctx.send(f"untimeout {member}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="snipeall")
    async def snipeall(self, ctx):
        await ctx.message.delete()
        sn = self.bot.get_cog("Snipe")
        if not sn or not getattr(sn, "deleted", None):
            await ctx.send("no snipe cache", delete_after=4)
            return
        items = list(getattr(sn, "deleted", {}).get(ctx.channel.id, []))[-10:]
        if not items:
            await ctx.send("empty", delete_after=3)
            return
        lines = [f"**{a}**: {c[:80]}" for a, c, *_ in items]
        await ctx.send("\n".join(lines)[:1900], delete_after=20)

    @commands.command(name="stopwspam")
    async def stopwspam(self, ctx):
        await ctx.message.delete()
        wh = self.bot.get_cog("Webhook")
        if wh and hasattr(wh, "stop"):
            wh.stop = True
        await ctx.send("wspam stop flagged", delete_after=3)

    @commands.command(name="setbanner")
    async def setbanner(self, ctx, url: str):
        await ctx.message.delete()
        import base64
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                raw = await r.read()
                mime = r.content_type or "image/png"
        b64 = base64.b64encode(raw).decode()
        headers = {"Authorization": self.bot.http.token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{API}/users/@me",
                headers=headers,
                json={"banner": f"data:{mime};base64,{b64}"},
            ) as r:
                await ctx.send(f"banner {r.status}", delete_after=4)

    @commands.command(name="setpronouns")
    async def setpronouns(self, ctx, *, pronouns: str):
        await ctx.message.delete()
        headers = {"Authorization": self.bot.http.token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{API}/users/@me/profile",
                headers=headers,
                json={"pronouns": pronouns},
            ) as r:
                await ctx.send(f"pronouns {r.status}", delete_after=4)

    @commands.command(name="me")
    async def me(self, ctx):
        await ctx.message.delete()
        u = self.bot.user
        await ctx.send(f"{u} `{u.id}`", delete_after=8)

    @commands.command(name="snowflake")
    async def snowflake(self, ctx, sid: int):
        await ctx.message.delete()
        ts = ((sid >> 22) + 1420070400000) / 1000
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        await ctx.send(f"{sid} → {dt.isoformat()}", delete_after=10)

    @commands.command(name="guilds")
    async def guilds(self, ctx):
        await ctx.message.delete()
        lines = [f"`{g.id}` {g.name}" for g in list(self.bot.guilds)[:40]]
        await ctx.send("\n".join(lines) or "none", delete_after=20)

    @commands.command(name="join")
    async def join(self, ctx, code: str):
        await ctx.message.delete()
        code = code.replace("https://discord.gg/", "").replace("discord.gg/", "").strip()
        headers = {"Authorization": self.bot.http.token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/invites/{code}", headers=headers, json={}) as r:
                await ctx.send(f"join {r.status}", delete_after=4)

    @commands.command(name="leave")
    async def leave(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        gid = guild_id or (ctx.guild.id if ctx.guild else None)
        if not gid:
            return
        headers = {"Authorization": self.bot.http.token}
        async with aiohttp.ClientSession() as s:
            async with s.delete(f"{API}/users/@me/guilds/{gid}", headers=headers) as r:
                await ctx.send(f"leave {r.status}", delete_after=4)

    @commands.command(name="mpoll")
    async def mpoll(self, ctx, *, text: str):
        await ctx.message.delete()
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 2:
            await ctx.send("q | a | b | c", delete_after=4)
            return
        q, opts = parts[0], parts[1:10]
        msg = await ctx.send(f"**{q}**\n" + "\n".join(f"{i+1}. {o}" for i, o in enumerate(opts)))
        for i in range(len(opts)):
            try:
                await msg.add_reaction(f"{i+1}\u20e3")
            except Exception:
                pass

    @commands.command(name="nitrocheck")
    async def nitrocheck(self, ctx, code: str):
        await ctx.message.delete()
        code = code.replace("https://discord.gift/", "").strip()
        headers = {"Authorization": self.bot.http.token}
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API}/entitlements/gift-codes/{code}", headers=headers) as r:
                data = await r.json(content_type=None) if r.content_type else {}
                await ctx.send(f"{r.status} {str(data)[:150]}", delete_after=10)

    @commands.command(name="customfarm")
    async def customfarm(self, ctx, channel_id: int, *, message: str):
        await ctx.message.delete()
        if not hasattr(self, "_farms"):
            self._farms = {}
        self._farms[channel_id] = message
        await ctx.send("customfarm set — use farm loop in farmer cog", delete_after=5)

    @commands.command(name="farmstatus")
    async def farmstatus(self, ctx):
        await ctx.message.delete()
        f = self.bot.get_cog("Farmer")
        await ctx.send(f"farmer={bool(f)}", delete_after=4)

    @commands.command(name="stopworkers")
    async def stopworkers(self, ctx):
        await ctx.message.delete()
        n = 0
        for k, w in list(getattr(self.bot, "workers", {}).items()):
            try:
                w["task"].cancel()
                n += 1
            except Exception:
                pass
            self.bot.workers.pop(k, None)
        await ctx.send(f"stopped {n}", delete_after=4)


async def setup(bot):
    await bot.add_cog(ExtrasRestore(bot))
