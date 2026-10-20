import asyncio
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v9"

class Quest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False

    def _h(self):
        return {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    async def _api(self, method, route, body=None):
        async with aiohttp.ClientSession() as s:
            kwargs = {"headers": self._h()}
            if body is not None:
                kwargs["json"] = body
            async with getattr(s, method.lower())(API + route, **kwargs) as r:
                if r.status == 204:
                    return None
                try:
                    return await r.json(content_type=None)
                except Exception:
                    return None

    @commands.command(name="quests")
    async def quests(self, ctx):
        await ctx.message.delete()
        data = await self._api("GET", "/quests/@me")
        quests = []
        if isinstance(data, dict):
            quests = data.get("quests") or []
        elif isinstance(data, list):
            quests = data
        if not quests:
            await ctx.send("no quests", delete_after=5)
            return
        lines = []
        for q in quests[:15]:
            name = (q.get("config") or {}).get("messages", {}).get("quest_name") or q.get("id")
            status = q.get("user_status") or q.get("userStatus") or {}
            state = "done" if status.get("completed_at") or status.get("completedAt") else "open"
            if status.get("enrolled_at") or status.get("enrolledAt"):
                state = "enrolled" if state == "open" else state
            lines.append(f"{name} · {state}")
        await ctx.send("\n".join(lines), delete_after=20)

    @commands.command(name="qstart")
    async def qstart(self, ctx):
        await ctx.message.delete()
        if self.running:
            await ctx.send("already running", delete_after=3)
            return
        self.running = True
        await ctx.send("quest eng started (heartbeat/video loops)", delete_after=5)
        try:
            data = await self._api("GET", "/quests/@me")
            quests = (data or {}).get("quests") if isinstance(data, dict) else (data or [])
            for q in quests or []:
                qid = q.get("id")
                status = q.get("user_status") or {}
                if status.get("completed_at") or status.get("completedAt"):
                    continue
                if not (status.get("enrolled_at") or status.get("enrolledAt")):
                    try:
                        await self._api("POST", f"/quests/{qid}/enroll", {"location": 11, "is_targeted": False})
                        await asyncio.sleep(1)
                    except Exception:
                        pass
                # light heartbeat pass
                for _ in range(3):
                    try:
                        await self._api("POST", f"/quests/{qid}/heartbeat", {"terminal": False})
                    except Exception:
                        pass
                    await asyncio.sleep(2)
        finally:
            self.running = False
            try:
                await ctx.send("quest pass done", delete_after=5)
            except Exception:
                pass

    @commands.command(name="qstop")
    async def qstop(self, ctx):
        await ctx.message.delete()
        self.running = False
        await ctx.send("stopped", delete_after=3)

    @commands.command(name="qclaim")
    async def qclaim(self, ctx):
        await ctx.message.delete()
        data = await self._api("GET", "/quests/@me")
        quests = (data or {}).get("quests") if isinstance(data, dict) else (data or [])
        claimed = 0
        for q in quests or []:
            status = q.get("user_status") or {}
            if not (status.get("completed_at") or status.get("completedAt")):
                continue
            try:
                await self._api("POST", f"/quests/{q.get('id')}/claim-reward", {})
                claimed += 1
            except Exception:
                pass
            await asyncio.sleep(0.8)
        await ctx.send(f"claimed {claimed}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Quest(bot))
