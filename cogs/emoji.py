import asyncio
import aiohttp
import discord
from discord.ext import commands

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="steal")
    async def steal(self, ctx, emoji: discord.PartialEmoji = None, *, name: str = None):
        await ctx.message.delete()
        if not emoji and ctx.message.attachments:
            url = ctx.message.attachments[0].url
            name = name or "stolen"
        elif emoji:
            url = str(emoji.url)
            name = name or emoji.name
        else:
            return
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.read()
        try:
            e = await ctx.guild.create_custom_emoji(name=name, image=data)
            await ctx.send(f"added {e}", delete_after=5)
        except Exception as ex:
            await ctx.send(f"fail {ex}", delete_after=5)

    @commands.command(name="emojistealall")
    async def emojistealall(self, ctx, source_id: int):
        await ctx.message.delete()
        src = self.bot.get_guild(source_id)
        if not src:
            await ctx.send("guild not found", delete_after=3)
            return
        ok = 0
        for e in src.emojis:
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(str(e.url)) as r:
                        data = await r.read()
                await ctx.guild.create_custom_emoji(name=e.name, image=data)
                ok += 1
            except Exception:
                pass
            await asyncio.sleep(1.1)
        await ctx.send(f"stole {ok} emojis", delete_after=5)

async def setup(bot):
    await bot.add_cog(Emoji(bot))
