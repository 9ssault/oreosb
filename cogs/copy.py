import base64
import aiohttp
import discord
from discord.ext import commands

API = "https://discord.com/api/v10"

class Copy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="copyuser")
    async def copyuser(self, ctx, user: discord.User):
        await ctx.message.delete()
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(str(user.display_avatar.with_size(1024).url)) as r:
                    data = await r.read()
                    mime = r.content_type or "image/png"
                b64 = base64.b64encode(data).decode()
                headers = {
                    "Authorization": self.bot.http.token,
                    "Content-Type": "application/json",
                }
                async with s.patch(
                    f"{API}/users/@me",
                    headers=headers,
                    json={"avatar": f"data:{mime};base64,{b64}"},
                ) as r2:
                    if r2.status == 200:
                        await ctx.send(f"copied pfp from `{user}`", delete_after=5)
                    else:
                        await ctx.send(f"pfp fail `{r2.status}`", delete_after=5)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="copystatus")
    async def copystatus(self, ctx, member: discord.Member):
        await ctx.message.delete()
        acts = [a for a in (member.activities or []) if a]
        if not acts:
            await ctx.send("no activity", delete_after=3)
            return
        act = acts[0]
        try:
            await self.bot.change_presence(activity=act)
            await ctx.send(f"copied activity from `{member}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Copy(bot))
