import re
import time
import asyncio
import aiohttp
import discord
from discord.ext import commands

try:
    from evasion.rate_limiter import acquire, update_from_response
except Exception:
    async def acquire(scope="global"):
        pass
    def update_from_response(scope, headers):
        pass

NITRO_RE = re.compile(
    r"(discord(?:app)?\.com/gifts/|discord\.gift/)([a-zA-Z0-9]{16,24})",
    re.I,
)
GIVEAWAY_KW = ("giveaway", "🎉", "react to enter", "react with", "winner", "prize", "hosted by")

class Sniper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped = set()
        self.cfg = bot.cfg

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author and message.author.id == self.bot.user.id:
            return
        text = message.content or ""
        if self.cfg.get("nitro_sniper", True) and text:
            for _, code in NITRO_RE.findall(text):
                if code in self.sniped:
                    continue
                self.sniped.add(code)
                asyncio.create_task(self._redeem(code, message))
        if self.cfg.get("giveaway_sniper", True):
            low = text.lower()
            is_gw = any(k in low for k in GIVEAWAY_KW)
            if message.embeds:
                for e in message.embeds:
                    t = ((e.title or "") + " " + (e.description or "")).lower()
                    if any(k in t for k in GIVEAWAY_KW):
                        is_gw = True
            if is_gw:
                await asyncio.sleep(0.25)
                try:
                    await message.add_reaction("🎉")
                    print(f"[GWSNIPE] {message.jump_url}")
                except Exception:
                    pass

    async def _redeem(self, code: str, src: discord.Message):
        t0 = time.perf_counter()
        url = f"https://discord.com/api/v10/entitlements/gift-codes/{code}/redeem"
        headers = {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        await acquire("nitro")
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, headers=headers, json={}) as r:
                    update_from_response("nitro", r.headers)
                    ms = (time.perf_counter() - t0) * 1000
                    data = await r.json(content_type=None)
                    if r.status == 200:
                        print(f"[NITRO] ok {code} {ms:.0f}ms from {src.guild}")
                    elif r.status == 429:
                        print(f"[NITRO] 429 {code}")
                    else:
                        msg = data.get("message") if isinstance(data, dict) else str(data)[:80]
                        print(f"[NITRO] {r.status} {code} {msg}")
        except Exception as e:
            print(f"[NITRO] err {code}: {e}")

async def setup(bot):
    await bot.add_cog(Sniper(bot))
