import aiohttp
import discord
from discord.ext import commands

class Copy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="copyuser")
    async def copyuser(self, ctx, user: discord.User):
        await ctx.message.delete()
        # pfp
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(str(user.display_avatar.url)) as r:
                    data = await r.read()
                    mime = r.content_type
            import base64
            b64 = base64.b64encode(data).decode()
            await self.bot.user.edit(avatar=base64.b64decode(b64) if False else data)
        except Exception as e:
            await ctx.send(f"pfp fail {e}", delete_after=5)
            return
        await ctx.send(f"copied pfp from {user}", delete_after=5)

    @commands.command(name="copystatus")
    async def copystatus(self, ctx, member: discord.Member):
        await ctx.message.delete()
        if not member.activities:
            await ctx.send("no activity", delete_after=3)
            return
        act = member.activities[0]
        await self.bot.change_presence(activity=act)
        await ctx.send(f"copied activity from {member}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Copy(bot))
