# cogs/sniper.py
import re
import time
import asyncio
import aiohttp
import discord
from discord.ext import commands

NITRO_RE = re.compile(r"(discord(?:app)?\.com/gifts/|discord\.gift/)([a-zA-Z0-9]{16,24})")
GIVEAWAY_KW = ("giveaway", "🎉", "react to enter", "react with", "winner", "prize")

class Sniper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped = set()
        self.cfg = bot.cfg

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.content and not message.embeds:
            return
        # nitro
        if self.cfg.get("nitro_sniper", True):
            for _, code in NITRO_RE.findall(message.content or ""):
                if code in self.sniped:
                    continue
                self.sniped.add(code)
                asyncio.create_task(self._redeem(code, message))
        # giveaway
        if self.cfg.get("giveaway_sniper", True):
            text = (message.content or "").lower()
            is_gw = any(k in text for k in GIVEAWAY_KW)
            if message.embeds:
                for e in message.embeds:
                    t = (e.title or "") + (e.description or "")
                    if any(k in t.lower() for k in GIVEAWAY_KW):
                        is_gw = True
            if is_gw:
                await asyncio.sleep(0.35)
                try:
                    await message.add_reaction("🎉")
                    print(f"[GWSNIPE] reacted → {message.jump_url}")
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
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, headers=headers, json={}) as r:
                    ms = (time.perf_counter() - t0) * 1000
                    data = await r.json(content_type=None)
                    if r.status == 200:
                        print(f"[NITRO] ✓ {code} in {ms:.0f}ms")
                    elif r.status == 429:
                        print(f"[NITRO] rate-limited {code}")
                    else:
                        print(f"[NITRO] fail {code} {r.status} {data}")
        except Exception as e:
            print(f"[NITRO] err {code}: {e}")

async def setup(bot):
    await bot.add_cog(Sniper(bot))
