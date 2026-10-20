# cogs/vanity.py — vanity url sniper
import asyncio
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class VanitySniper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watching = set()
        self._task = None

    @commands.command(name="vanitywatch")
    async def vanitywatch(self, ctx, code: str):
        await ctx.message.delete()
        self.watching.add(code.lower())
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._loop())
        await ctx.send(f"watching vanity `{code}`", delete_after=4)

    @commands.command(name="vanityunwatch")
    async def vanityunwatch(self, ctx, code: str):
        await ctx.message.delete()
        self.watching.discard(code.lower())
        await ctx.send(f"stopped `{code}`", delete_after=3)

    async def _loop(self):
        headers = {"Authorization": self.bot.http.token, "Content-Type": "application/json"}
        while self.watching:
            for code in list(self.watching):
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.get(f"{API}/invites/{code}", headers=headers) as r:
                            if r.status == 404:
                                # try claim on a guild the bot owns / has admin
                                print(f"[VANITY] {code} free — attempt claim")
                                # claim requires guild_id with MANAGE_GUILD
                                # left as hook for user to set target guild
                except Exception:
                    pass
            await asyncio.sleep(2.5)

async def setup(bot):
    await bot.add_cog(VanitySniper(bot))
