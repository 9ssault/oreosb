import aiohttp
import discord
from discord.ext import commands
from datetime import datetime, timezone

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        created = discord.utils.snowflake_time(u.id).strftime("%Y-%m-%d")
        await ctx.send(
            f"**{u}**\nid `{u.id}`\ncreated {created}\nbot {u.bot}\navatar {u.display_avatar.url}",
            delete_after=14,
        )

    @commands.command(name="avatar")
    async def avatar(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        u = user or ctx.author
        await ctx.send(str(u.display_avatar.with_size(1024).url), delete_after=12)

    @commands.command(name="servericon")
    async def servericon(self, ctx):
        await ctx.message.delete()
        if ctx.guild and ctx.guild.icon:
            await ctx.send(str(ctx.guild.icon.with_size(1024).url), delete_after=10)
        else:
            await ctx.send("no icon", delete_after=3)

    @commands.command(name="firstmessage")
    async def firstmessage(self, ctx):
        await ctx.message.delete()
        async for m in ctx.channel.history(limit=1, oldest_first=True):
            await ctx.send(f"first: {m.jump_url}\n{m.author}: {(m.content or '')[:200]}", delete_after=12)
            return

    @commands.command(name="id")
    async def id_(self, ctx, target: discord.User = None):
        await ctx.message.delete()
        t = target or ctx.author
        await ctx.send(f"`{t.id}`", delete_after=6)

    @commands.command(name="pingweb")
    async def pingweb(self, ctx, url: str):
        await ctx.message.delete()
        if not url.startswith("http"):
            url = "https://" + url
        try:
            t0 = datetime.now(timezone.utc)
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=10) as r:
                    ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
                    await ctx.send(f"`{r.status}` `{ms:.0f}ms`", delete_after=6)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="snowflake")
    async def snowflake(self, ctx, sid: int):
        await ctx.message.delete()
        t = discord.utils.snowflake_time(sid)
        await ctx.send(f"`{sid}` → {t.strftime('%Y-%m-%d %H:%M:%S UTC')}", delete_after=10)

    @commands.command(name="guilds")
    async def guilds(self, ctx):
        await ctx.message.delete()
        lines = [f"`{g.id}` {g.name} ({g.member_count})" for g in sorted(self.bot.guilds, key=lambda x: x.member_count or 0, reverse=True)[:40]]
        await ctx.send(f"**guilds ({len(self.bot.guilds)})**\n" + "\n".join(lines), delete_after=20)

async def setup(bot):
    await bot.add_cog(Util(bot))
