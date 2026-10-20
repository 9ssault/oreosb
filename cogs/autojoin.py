import asyncio
import random
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class AutoJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._joins = 0
        self._window = 0.0

    def _rate_ok(self) -> bool:
        import time
        now = time.monotonic()
        max_j = int(self.bot.cfg.get("max_joins_per_hour", 5))
        if now - self._window > 3600:
            self._window = now
            self._joins = 0
        return self._joins < max_j

    @commands.command(name="join")
    async def join(self, ctx, invite: str):
        await ctx.message.delete()
        code = invite.rstrip("/").split("/")[-1].split("?")[0]
        if not self._rate_ok():
            await ctx.send("join rate limit (config max_joins_per_hour)", delete_after=5)
            return
        headers = {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(f"{API}/invites/{code}", headers=headers, json={}) as r:
                    data = await r.json(content_type=None)
                    if r.status in (200, 204):
                        self._joins += 1
                        g = (data.get("guild") or {}).get("name", "?")
                        await ctx.send(f"joined {g}", delete_after=5)
                    else:
                        await ctx.send(f"fail {r.status} {str(data)[:100]}", delete_after=6)
        except Exception as e:
            await ctx.send(f"err {e}", delete_after=5)

    @commands.command(name="leave")
    async def leave(self, ctx, guild_id: int = None):
        await ctx.message.delete()
        gid = guild_id or (ctx.guild.id if ctx.guild else None)
        if not gid:
            return
        g = self.bot.get_guild(gid)
        if not g:
            await ctx.send("not in guild", delete_after=3)
            return
        try:
            await g.leave()
            await ctx.send(f"left {gid}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="leaveall")
    async def leaveall(self, ctx, keep: int = 0):
        await ctx.message.delete()
        left = 0
        for g in list(self.bot.guilds):
            if keep and g.id == keep:
                continue
            if ctx.guild and g.id == ctx.guild.id:
                continue
            try:
                await g.leave()
                left += 1
            except Exception:
                pass
            await asyncio.sleep(random.uniform(0.8, 1.6))
        await ctx.send(f"left {left}", delete_after=5)

    @commands.command(name="invitejoin")
    async def invitejoin(self, ctx, *invites: str):
        await ctx.message.delete()
        ok = 0
        for inv in invites:
            if not self._rate_ok():
                break
            code = inv.rstrip("/").split("/")[-1].split("?")[0]
            headers = {
                "Authorization": self.bot.http.token,
                "Content-Type": "application/json",
            }
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.post(f"{API}/invites/{code}", headers=headers, json={}) as r:
                        if r.status in (200, 204):
                            self._joins += 1
                            ok += 1
            except Exception:
                pass
            await asyncio.sleep(random.uniform(2.0, 4.5))
        await ctx.send(f"joined {ok}/{len(invites)}", delete_after=5)

async def setup(bot):
    await bot.add_cog(AutoJoin(bot))
