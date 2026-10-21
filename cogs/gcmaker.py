import asyncio
import discord
from discord.ext import commands

class GCMaker(commands.Cog):
    """Group DM mass-create (ported from JS gcm)."""

    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.targets = set()
        self.msg = "no you dont :p"
        self.name = "gc"
        self.delay = 2.0
        self._task = None
        self.count = 0

    async def _loop(self):
        while self.enabled:
            if not self.targets:
                await asyncio.sleep(1)
                continue
            try:
                recipients = [int(x) for x in list(self.targets)[:9]]
                if not recipients:
                    await asyncio.sleep(self.delay)
                    continue
                ch = await self.bot.create_group(*[discord.Object(id=uid) for uid in recipients])
                self.count += 1
                try:
                    await ch.edit(name=self.name)
                except Exception:
                    pass
                safe = self.msg.replace("@everyone", "@\u200beveryone")
                try:
                    await ch.send(safe)
                except Exception:
                    pass
                await asyncio.sleep(2.5)
                try:
                    await ch.delete()
                except Exception:
                    pass
            except Exception as e:
                print(f"[GCM] {e}")
            await asyncio.sleep(max(0.5, self.delay))

    def _ensure_task(self):
        if self.enabled and (self._task is None or self._task.done()):
            self._task = asyncio.create_task(self._loop())

    @commands.command(name="gcm")
    async def gcm(self, ctx, action: str = None, *, value: str = None):
        await ctx.message.delete()
        a = (action or "").lower()

        if a in ("", "status"):
            await ctx.send(
                f"gcm `{'on' if self.enabled else 'off'}` targets={len(self.targets)} "
                f"delay={self.delay}s made={self.count}",
                delete_after=8,
            )
            return

        if a == "on":
            if not self.targets:
                await ctx.send("add targets first: `gcm target <id>`", delete_after=5)
                return
            self.enabled = True
            self._ensure_task()
            await ctx.send("gcm on", delete_after=3)
            return

        if a == "off":
            self.enabled = False
            if self._task and not self._task.done():
                self._task.cancel()
            await ctx.send(f"gcm off (made {self.count})", delete_after=4)
            return

        if a == "target" and value:
            uid = "".join(c for c in value if c.isdigit())
            if len(uid) >= 17:
                self.targets.add(uid)
                await ctx.send(f"+ target `{uid}`", delete_after=3)
            return

        if a == "removetarget" and value:
            uid = "".join(c for c in value if c.isdigit())
            self.targets.discard(uid)
            await ctx.send(f"- target `{uid}`", delete_after=3)
            return

        if a == "targets":
            body = ", ".join(list(self.targets)[:20]) or "none"
            await ctx.send(f"targets: {body}", delete_after=10)
            return

        if a == "msg" and value:
            self.msg = value
            await ctx.send("msg set", delete_after=3)
            return

        if a == "name" and value:
            self.name = value[:100]
            await ctx.send(f"name → `{self.name}`", delete_after=3)
            return

        if a == "delay" and value:
            try:
                self.delay = max(0.5, float(value))
                await ctx.send(f"delay {self.delay}s", delete_after=3)
            except ValueError:
                await ctx.send("bad delay", delete_after=3)
            return

        await ctx.send(
            "`gcm on|off|target|removetarget|targets|msg|name|delay|status`",
            delete_after=6,
        )

async def setup(bot):
    await bot.add_cog(GCMaker(bot))
