import asyncio
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Group(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _h(self):
        return {
            "Authorization": self.bot.http.token,
            "Content-Type": "application/json",
        }

    @commands.command(name="gcreate")
    async def gcreate(self, ctx, *user_ids: int):
        await ctx.message.delete()
        recipients = list(user_ids)[:9]
        if not recipients:
            await ctx.send("need user ids", delete_after=4)
            return
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{API}/users/@me/channels",
                headers=await self._h(),
                json={"recipients": recipients},
            ) as r:
                data = await r.json(content_type=None)
                if r.status == 200:
                    await ctx.send(f"gc created `{data.get('id')}`", delete_after=6)
                else:
                    await ctx.send(f"fail {r.status}", delete_after=5)

    @commands.command(name="gleave")
    async def gleave(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        cid = channel_id or ctx.channel.id
        async with aiohttp.ClientSession() as s:
            async with s.delete(
                f"{API}/channels/{cid}",
                headers=await self._h(),
            ) as r:
                await ctx.send(f"leave `{r.status}`", delete_after=4)

async def setup(bot):
    await bot.add_cog(Group(bot))
