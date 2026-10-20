import asyncio
import discord
from discord.ext import commands

class Pin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pin")
    async def pin(self, ctx):
        await ctx.message.delete()
        if ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await msg.pin()
            await ctx.send("pinned", delete_after=3)

    @commands.command(name="unpin")
    async def unpin(self, ctx):
        await ctx.message.delete()
        if ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await msg.unpin()
            await ctx.send("unpinned", delete_after=3)

    @commands.command(name="unpinall")
    async def unpinall(self, ctx):
        await ctx.message.delete()
        pins = await ctx.channel.pins()
        ok = 0
        for p in pins:
            try:
                await p.unpin()
                ok += 1
            except Exception:
                pass
            await asyncio.sleep(0.4)
        await ctx.send(f"unpinned {ok}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Pin(bot))
