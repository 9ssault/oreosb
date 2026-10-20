import asyncio
import re
import aiohttp
import discord
from discord.ext import commands

EMOJI_RE = re.compile(r"<(a?):(\w+):(\d+)>")

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="steal")
    async def steal(self, ctx, emoji: str = None, *, name: str = None):
        await ctx.message.delete()
        url = None
        if emoji:
            m = EMOJI_RE.match(emoji.strip())
            if m:
                animated, ename, eid = m.groups()
                ext = "gif" if animated else "png"
                url = f"https://cdn.discordapp.com/emojis/{eid}.{ext}"
                name = name or ename
            elif emoji.startswith("http"):
                url = emoji
                name = name or "stolen"
        if not url and ctx.message.attachments:
            url = ctx.message.attachments[0].url
            name = name or "stolen"
        if not url:
            await ctx.send("need emoji, url, or attachment", delete_after=4)
            return
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status != 200:
                    await ctx.send(f"fetch {r.status}", delete_after=4)
                    return
                data = await r.read()
        try:
            e = await ctx.guild.create_custom_emoji(name=(name or "stolen")[:32], image=data)
            await ctx.send(f"added {e}", delete_after=5)
        except Exception as ex:
            await ctx.send(f"fail {ex}", delete_after=5)

    @commands.command(name="emojistealall")
    async def emojistealall(self, ctx, source_id: int):
        await ctx.message.delete()
        src = self.bot.get_guild(source_id)
        if not src:
            await ctx.send("guild not found / not mutual", delete_after=4)
            return
        ok = fail = 0
        for e in list(src.emojis):
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(str(e.url)) as r:
                        data = await r.read()
                await ctx.guild.create_custom_emoji(name=e.name[:32], image=data)
                ok += 1
            except Exception:
                fail += 1
            await asyncio.sleep(1.1)
        await ctx.send(f"stole {ok} · fail {fail}", delete_after=6)

    @commands.command(name="emojilist")
    async def emojilist(self, ctx):
        await ctx.message.delete()
        if not ctx.guild:
            return
        em = list(ctx.guild.emojis)[:40]
        body = " ".join(str(e) for e in em) or "none"
        await ctx.send(f"emojis ({len(ctx.guild.emojis)})\n{body}", delete_after=15)

async def setup(bot):
    await bot.add_cog(Emoji(bot))
