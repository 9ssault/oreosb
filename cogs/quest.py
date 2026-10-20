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
            fn = getattr(s, method.lower())
            async with fn(API + route, **kwargs) as r:
                if r.status == 204:
                    return {"_status": 204}
                try:
                    data = await r.json(content_type=None)
                    if isinstance(data, dict):
                        data["_status"] = r.status
                    return data
                except Exception:
                    return {"_status": r.status}

    def _list_quests(self, data):
        if isinstance(data, dict):
            return data.get("quests") or []
        if isinstance(data, list):
            return data
        return []

    @commands.command(name="quests")
    async def quests(self, ctx):
        await ctx.message.delete()
        data = await self._api("GET", "/quests/@me")
        quests = self._list_quests(data)
        if not quests:
            await ctx.send("no quests", delete_after=5)
            return
        lines = []
        for q in quests[:20]:
            cfg = q.get("config") or {}
            msgs = cfg.get("messages") or {}
            name = msgs.get("quest_name") or q.get("id")
            status = q.get("user_status") or q.get("userStatus") or {}
            if status.get("completed_at") or status.get("completedAt"):
                state = "done"
            elif status.get("enrolled_at") or status.get("enrolledAt"):
                state = "enrolled"
            else:
                state = "open"
            lines.append(f"`{q.get('id')}` {name} · {state}")
        await ctx.send("\n".join(lines), delete_after=25)

    @commands.command(name="qstart")
    async def qstart(self, ctx):
        await ctx.message.delete()
        if self.running:
            await ctx.send("already running", delete_after=3)
            return
        self.running = True
        await ctx.send("quest engine on", delete_after=4)
        try:
            data = await self._api("GET", "/quests/@me")
            quests = self._list_quests(data)
            for q in quests:
                if not self.running:
                    break
                qid = q.get("id")
                if not qid:
                    continue
                status = q.get("user_status") or {}
                if status.get("completed_at") or status.get("completedAt"):
                    continue
                if not (status.get("enrolled_at") or status.get("enrolledAt")):
                    await self._api("POST", f"/quests/{qid}/enroll", {"location": 11, "is_targeted": False})
                    await asyncio.sleep(1.2)
                for _ in range(5):
                    if not self.running:
                        break
                    await self._api("POST", f"/quests/{qid}/heartbeat", {"terminal": False})
                    await asyncio.sleep(2.5)
            try:
                await ctx.send("quest pass done", delete_after=5)
            except Exception:
                pass
        finally:
            self.running = False

    @commands.command(name="qstop")
    async def qstop(self, ctx):
        await ctx.message.delete()
        self.running = False
        await ctx.send("quest stopped", delete_after=3)

    @commands.command(name="qclaim")
    async def qclaim(self, ctx):
        await ctx.message.delete()
        data = await self._api("GET", "/quests/@me")
        quests = self._list_quests(data)
        claimed = 0
        for q in quests:
            status = q.get("user_status") or {}
            if not (status.get("completed_at") or status.get("completedAt")):
                continue
            qid = q.get("id")
            if not qid:
                continue
            res = await self._api("POST", f"/quests/{qid}/claim-reward", {})
            if res and res.get("_status") in (200, 204):
                claimed += 1
            await asyncio.sleep(0.9)
        await ctx.send(f"claimed {claimed}", delete_after=5)

    @commands.command(name="qenroll")
    async def qenroll(self, ctx, quest_id: str):
        await ctx.message.delete()
        res = await self._api("POST", f"/quests/{quest_id}/enroll", {"location": 11, "is_targeted": False})
        await ctx.send(f"enroll `{res.get('_status') if res else '?'}`", delete_after=5)

async def setup(bot):
    await bot.add_cog(Quest(bot))
