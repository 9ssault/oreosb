import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks

API = "https://discord.com/api/v10"

class Vanity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watching = {}
        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=8)
    async def loop(self):
        if not self.watching:
            return
        token = getattr(self.bot.http, "token", None)
        if not token:
            return
        headers = {"Authorization": token, "Content-Type": "application/json"}
        for code, guild_id in list(self.watching.items()):
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.patch(
                        f"{API}/guilds/{guild_id}/vanity-url",
                        headers=headers,
                        json={"code": code},
                    ) as r:
                        if r.status == 200:
                            print(f"[VANITY] claimed {code} on {guild_id}")
                            del self.watching[code]
                        elif r.status == 429:
                            await asyncio.sleep(5)
            except Exception as e:
                print(f"[VANITY] {code}: {e}")

    @loop.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @commands.command(name="vanitywatch")
    async def vanitywatch(self, ctx, code: str, guild_id: int = None):
        await ctx.message.delete()
        gid = guild_id or (ctx.guild.id if ctx.guild else None)
        if not gid:
            await ctx.send("need guild id", delete_after=4)
            return
        self.watching[code.lower()] = gid
        await ctx.send(f"watching `{code}` → {gid}", delete_after=5)

    @commands.command(name="vanitystop")
    async def vanitystop(self, ctx, code: str = None):
        await ctx.message.delete()
        if code:
            self.watching.pop(code.lower(), None)
        else:
            self.watching.clear()
        await ctx.send("stopped", delete_after=3)

    @commands.command(name="vanitylist")
    async def vanitylist(self, ctx):
        await ctx.message.delete()
        body = "\n".join(f"`{c}` → {g}" for c, g in self.watching.items()) or "none"
        await ctx.send(body, delete_after=10)

async def setup(bot):
    await bot.add_cog(Vanity(bot))
