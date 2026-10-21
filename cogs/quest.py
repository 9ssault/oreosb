import asyncio
import base64
import json
import os
import random
import time
from datetime import datetime, timezone

import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v9"
TASK_PRIORITY = [
    "WATCH_VIDEO",
    "WATCH_VIDEO_ON_MOBILE",
    "PLAY_ON_DESKTOP",
    "PLAY_ON_DESKTOP_V2",
    "STREAM_ON_DESKTOP",
    "PLAY_ACTIVITY",
]
HEARTBEAT_TASKS = {
    "PLAY_ON_DESKTOP",
    "PLAY_ON_DESKTOP_V2",
    "STREAM_ON_DESKTOP",
    "PLAY_ACTIVITY",
}
VIDEO_TASKS = {"WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE"}
SKIP_TASKS = {
    "ACHIEVEMENT_IN_ACTIVITY",
    "ACHIEVEMENT_IN_GAME",
    "PLAY_ON_XBOX",
    "PLAY_ON_PLAYSTATION",
    "progress",
}

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Discord/1.0.9173 Chrome/132.0.6834.196 "
    "Electron/34.3.2 Safari/537.36"
)


def _super_props(locale: str = "en-US") -> str:
    payload = {
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": "stable",
        "client_build_number": 561532,
        "os_version": "10.0.22631",
        "os_arch": "x64",
        "app_arch": "x64",
        "system_locale": locale,
        "browser_user_agent": DESKTOP_UA,
        "browser_version": "34.3.2",
        "client_event_source": None,
    }
    return base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()


def _parse_ts(s: str) -> float:
    if not s:
        return 0.0
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000+00:00")


def _get_task(quest):
    cfg_q = quest.get("config") or {}
    tc = cfg_q.get("task_config_v2") or cfg_q.get("task_config")
    if not tc:
        return None, None
    if tc.get("type") == 2:
        return None, None
    tasks = tc.get("tasks") or {}
    for name in TASK_PRIORITY:
        if tasks.get(name) is not None:
            return name, tasks[name]
    available = [k for k in tasks if k not in SKIP_TASKS]
    if available:
        return available[0], tasks[available[0]]
    return None, None


def _user_status(quest):
    return quest.get("user_status") or quest.get("userStatus") or {}


def _progress(us, task):
    bt = (us.get("progress") or {}).get(task) or {}
    if "value" in bt:
        return float(bt["value"])
    return 0.0


def _quest_name(quest):
    msgs = (quest.get("config") or {}).get("messages") or {}
    return msgs.get("quest_name") or msgs.get("questName") or str(quest.get("id"))


class Quest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = False
        self._stop = False
        self.locale = os.getenv("LOCALE", "en-US")
        self.timezone = os.getenv("TIMEZONE", "America/New_York")

    def _token(self):
        return getattr(self.bot.http, "token", None) or ""

    def _headers(self):
        return {
            "Authorization": self._token(),
            "User-Agent": DESKTOP_UA,
            "Content-Type": "application/json",
            "X-Super-Properties": _super_props(self.locale),
            "X-Discord-Locale": self.locale,
            "X-Discord-Timezone": self.timezone,
        }

    async def _get(self, sess, path):
        async with sess.get(f"{API}{path}", headers=self._headers()) as r:
            if r.status == 403:
                text = await r.text()
                raise Exception(f"403 forbidden — {text[:120]}")
            if r.status == 401:
                raise Exception("401 unauthorized — token dead")
            data = await r.json(content_type=None) if r.status != 204 else {}
            if r.status not in (200, 204):
                raise Exception(f"{r.status}:{str(data)[:120]}")
            return data

    async def _post(self, sess, path, body):
        async with sess.post(f"{API}{path}", headers=self._headers(), json=body) as r:
            if r.status == 403:
                text = await r.text()
                raise Exception(f"403 forbidden — {text[:120]}")
            if r.status == 429:
                try:
                    d = await r.json(content_type=None)
                    wait = float(d.get("retry_after", 5))
                except Exception:
                    wait = 5.0
                await asyncio.sleep(wait + random.uniform(0.2, 0.8))
                return await self._post(sess, path, body)
            if r.status == 204:
                return {}
            data = await r.json(content_type=None)
            if r.status not in (200, 204):
                raise Exception(f"{r.status}:{str(data)[:120]}")
            return data

    def _split(self, quest_list):
        now = time.time()
        enrolled, unenrolled = [], []
        for q in quest_list:
            us = _user_status(q)
            exp = (q.get("config") or {}).get("expires_at", "")
            tt, _ = _get_task(q)
            if exp and _parse_ts(exp) <= now:
                continue
            if us.get("claimed_at") or us.get("claimedAt"):
                continue
            if us.get("completed_at") or us.get("completedAt"):
                continue
            if not tt:
                continue
            if us.get("enrolled_at") or us.get("enrolledAt"):
                enrolled.append(q)
            else:
                unenrolled.append(q)
        return enrolled, unenrolled

    async def _run_video(self, sess, quest, task, task_data):
        qid = quest["id"]
        name = _quest_name(quest)
        us = _user_status(quest)
        target = float(task_data.get("target", 0) or 0)
        progress = _progress(us, task)
        enrolled_ts = _parse_ts(us.get("enrolled_at") or us.get("enrolledAt") or "")
        if enrolled_ts == 0.0:
            enrolled_ts = time.time()
        try:
            await self._post(sess, f"/quests/{qid}/video-progress", {"timestamp": 0})
            await asyncio.sleep(1)
        except Exception:
            pass
        print(f"[QUEST] video {name} {progress}/{target}")
        done = False
        while not self._stop and not done and progress < target:
            if (time.time() - enrolled_ts) + 10 - progress >= 7:
                nxt = min(target, progress + 7 + random.random())
                try:
                    resp = await self._post(
                        sess, f"/quests/{qid}/video-progress", {"timestamp": int(nxt)}
                    )
                    progress = nxt
                    print(f"[QUEST] video {name} {int(progress)}/{int(target)}")
                    tp = (resp.get("progress") or {}).get(task) or {}
                    if tp.get("completed_at") is not None or progress >= target:
                        done = True
                except Exception as e:
                    print(f"[QUEST] video err {name}: {e}")
            if not done:
                await asyncio.sleep(1)
        if not done and not self._stop:
            try:
                await self._post(
                    sess, f"/quests/{qid}/video-progress", {"timestamp": int(target)}
                )
            except Exception as e:
                print(f"[QUEST] video final {name}: {e}")
        print(f"[QUEST] video done {name}")

    async def _run_heartbeat(self, sess, quest, task, task_data):
        qid = quest["id"]
        name = _quest_name(quest)
        us = _user_status(quest)
        target = float(task_data.get("target", 0) or 0)
        progress = _progress(us, task)
        skey = f"call:{qid}:1"
        print(f"[QUEST] beat {name} {progress}/{target}")
        while not self._stop:
            try:
                resp = await self._post(
                    sess,
                    f"/quests/{qid}/heartbeat",
                    {"stream_key": skey, "terminal": False},
                )
                prog_map = resp.get("progress") or {}
                task_prog = prog_map.get(task) or {}
                progress = float(task_prog.get("value", progress))
                print(f"[QUEST] beat {name} {int(progress)}/{int(target)}")
                if progress >= target:
                    await self._post(
                        sess,
                        f"/quests/{qid}/heartbeat",
                        {"stream_key": skey, "terminal": True},
                    )
                    break
            except Exception as e:
                print(f"[QUEST] beat err {name}: {e}")
            await asyncio.sleep(30)
        print(f"[QUEST] beat done {name}")

    async def _engine(self, report=None):
        self._stop = False
        self.running = True
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as sess:
            try:
                resp = await self._get(sess, "/quests/@me")
            except Exception as e:
                if report:
                    await report(f"fetch fail: {e}")
                print(f"[QUEST] fetch fail {e}")
                self.running = False
                return
            quests = resp.get("quests") or []
            blocked = resp.get("quest_enrollment_blocked_until")
            if blocked and report:
                await report(f"enrollment blocked until {blocked}")
            enrolled, unenrolled = self._split(quests)
            if unenrolled and not blocked:
                for q in unenrolled:
                    qname = _quest_name(q)
                    try:
                        us = await self._post(
                            sess, f"/quests/{q['id']}/enroll", {"location": 11}
                        )
                        q["user_status"] = us or {
                            "enrolled_at": _now_iso(),
                            "completed_at": None,
                            "claimed_at": None,
                            "progress": {},
                        }
                        enrolled.append(q)
                        print(f"[QUEST] enrolled {qname}")
                    except Exception as e:
                        print(f"[QUEST] enroll fail {qname}: {e}")
                await asyncio.sleep(1)
            if not enrolled:
                if report:
                    await report("no eligible quests")
                self.running = False
                return
            if report:
                await report(f"running {len(enrolled)} quest(s)")

            async def handle(quest):
                task, task_data = _get_task(quest)
                name = _quest_name(quest)
                if not task or not task_data:
                    return
                try:
                    if task in VIDEO_TASKS:
                        await self._run_video(sess, quest, task, task_data)
                    elif task in HEARTBEAT_TASKS:
                        await self._run_heartbeat(sess, quest, task, task_data)
                    else:
                        print(f"[QUEST] skip {task} {name}")
                except Exception as e:
                    print(f"[QUEST] handle {name}: {e}")

            await asyncio.gather(*[handle(q) for q in enrolled])
            if report:
                await report("quests finished")
        self.running = False

    @commands.command(name="quests")
    async def quests(self, ctx):
        await ctx.message.delete()
        timeout = aiohttp.ClientTimeout(total=20)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as sess:
                resp = await self._get(sess, "/quests/@me")
        except Exception as e:
            await ctx.send(f"fail: {e}", delete_after=8)
            return
        quests = resp.get("quests") or []
        if not quests:
            await ctx.send("no quests", delete_after=5)
            return
        lines = []
        for q in quests[:20]:
            name = _quest_name(q)
            us = _user_status(q)
            task, td = _get_task(q)
            tgt = int((td or {}).get("target", 0) or 0)
            prog = int(_progress(us, task)) if task else 0
            if us.get("claimed_at") or us.get("claimedAt"):
                state = "claimed"
            elif us.get("completed_at") or us.get("completedAt"):
                state = "done"
            elif us.get("enrolled_at") or us.get("enrolledAt"):
                state = f"enrolled {prog}/{tgt}"
            else:
                state = "open"
            lines.append(f"{name} · {task or '?'} · {state}")
        await ctx.send("\n".join(lines)[:1900], delete_after=25)

    @commands.command(name="qstart")
    async def qstart(self, ctx):
        await ctx.message.delete()
        if self.running:
            await ctx.send("already running", delete_after=3)
            return
        await ctx.send("quest engine started", delete_after=5)

        async def report(msg):
            try:
                await ctx.send(msg, delete_after=12)
            except Exception:
                pass

        asyncio.create_task(self._engine(report))

    @commands.command(name="qstop")
    async def qstop(self, ctx):
        await ctx.message.delete()
        self._stop = True
        self.running = False
        await ctx.send("stop flagged", delete_after=3)

    @commands.command(name="qclaim")
    async def qclaim(self, ctx):
        await ctx.message.delete()
        timeout = aiohttp.ClientTimeout(total=30)
        claimed = 0
        try:
            async with aiohttp.ClientSession(timeout=timeout) as sess:
                resp = await self._get(sess, "/quests/@me")
                for q in resp.get("quests") or []:
                    us = _user_status(q)
                    if not (us.get("completed_at") or us.get("completedAt")):
                        continue
                    if us.get("claimed_at") or us.get("claimedAt"):
                        continue
                    try:
                        await self._post(sess, f"/quests/{q['id']}/claim-reward", {})
                        claimed += 1
                    except Exception as e:
                        print(f"[QUEST] claim {e}")
                    await asyncio.sleep(0.8)
        except Exception as e:
            await ctx.send(f"claim fail: {e}", delete_after=6)
            return
        await ctx.send(f"claimed {claimed}", delete_after=5)


async def setup(bot):
    await bot.add_cog(Quest(bot))
