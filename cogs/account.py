import asyncio
import base64
import random
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

try:
    from evasion.delay import human_delay
except Exception:
    async def human_delay(lo=0.5, hi=1.5):
        await asyncio.sleep(random.uniform(lo, hi))

class AccountTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _headers(self):
        return {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    @commands.command(name="setbio")
    async def setbio(self, ctx, *, bio: str):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{API}/users/@me/profile",
                headers=await self._headers(),
                json={"bio": bio[:190]},
            ) as r:
                await ctx.send(f"bio `{r.status}`", delete_after=3)

    @commands.command(name="setpfp")
    async def setpfp(self, ctx, url: str = None):
        await ctx.message.delete()
        if not url and ctx.message.attachments:
            url = ctx.message.attachments[0].url
        if not url:
            await ctx.send("need url or attach image", delete_after=4)
            return
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status != 200:
                    await ctx.send(f"fetch {r.status}", delete_after=4)
                    return
                data = base64.b64encode(await r.read()).decode()
                mime = r.content_type or "image/png"
            async with s.patch(
                f"{API}/users/@me",
                headers=await self._headers(),
                json={"avatar": f"data:{mime};base64,{data}"},
            ) as r2:
                await ctx.send(f"avatar `{r2.status}`", delete_after=3)

    @commands.command(name="setbanner")
    async def setbanner(self, ctx, url: str = None):
        await ctx.message.delete()
        if not url and ctx.message.attachments:
            url = ctx.message.attachments[0].url
        if not url:
            await ctx.send("need url or attach image", delete_after=4)
            return
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = base64.b64encode(await r.read()).decode()
                mime = r.content_type or "image/png"
            async with s.patch(
                f"{API}/users/@me",
                headers=await self._headers(),
                json={"banner": f"data:{mime};base64,{data}"},
            ) as r2:
                await ctx.send(f"banner `{r2.status}`", delete_after=3)

    @commands.command(name="setpronouns")
    async def setpronouns(self, ctx, *, pronouns: str):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{API}/users/@me/profile",
                headers=await self._headers(),
                json={"pronouns": pronouns[:40]},
            ) as r:
                await ctx.send(f"pronouns `{r.status}`", delete_after=3)

    @commands.command(name="leaveall")
    async def leaveall(self, ctx, delay: float = 0.8):
        await ctx.message.delete()
        guilds = [g for g in self.bot.guilds if not ctx.guild or g.id != ctx.guild.id]
        n = 0
        for g in guilds:
            try:
                await g.leave()
                n += 1
            except Exception:
                pass
            await human_delay(delay * 0.7, delay * 1.4)
        await ctx.send(f"left {n}", delete_after=5)

    @commands.command(name="hypesquad")
    async def hypesquad(self, ctx, house: str = "1"):
        await ctx.message.delete()
        map_ = {"bravery": 1, "brilliance": 2, "balance": 3, "1": 1, "2": 2, "3": 3}
        hid = map_.get(house.lower(), 1)
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{API}/hypesquad/online",
                headers=await self._headers(),
                json={"house_id": hid},
            ) as r:
                await ctx.send(f"hype house={hid} `{r.status}`", delete_after=3)

    @commands.command(name="friendspam")
    async def friendspam(self, ctx, username: str, count: int = 5):
        await ctx.message.delete()
        count = max(1, min(count, 20))
        async with aiohttp.ClientSession() as s:
            for _ in range(count):
                async with s.post(
                    f"{API}/users/@me/relationships",
                    headers=await self._headers(),
                    json={"username": username},
                ) as r:
                    print(f"[FRIEND] {r.status}")
                await human_delay(1.2, 2.8)

    @commands.command(name="me")
    async def me(self, ctx):
        await ctx.message.delete()
        u = self.bot.user
        await ctx.send(
            f"**{u}**\nid `{u.id}`\navatar {u.display_avatar.url}",
            delete_after=12,
        )

async def setup(bot):
    await bot.add_cog(AccountTools(bot))
