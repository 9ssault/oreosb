import asyncio
import discord
from discord.ext import commands

class Pin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pin")
    async def pin(self, ctx, message_id: int = None):
        await ctx.message.delete()
        if message_id:
            try:
                m = await ctx.channel.fetch_message(message_id)
            except Exception:
                await ctx.send("not found", delete_after=3)
                return
        else:
            m = None
            async for msg in ctx.channel.history(limit=2):
                if msg.id != ctx.message.id:
                    m = msg
                    break
            if not m:
                return
        try:
            await m.pin()
            await ctx.send("pinned", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="unpin")
    async def unpin(self, ctx, message_id: int = None):
        await ctx.message.delete()
        if message_id:
            m = await ctx.channel.fetch_message(message_id)
            await m.unpin()
        else:
            pins = await ctx.channel.pins()
            if pins:
                await pins[0].unpin()
        await ctx.send("unpinned", delete_after=3)

    @commands.command(name="unpinall")
    async def unpinall(self, ctx):
        await ctx.message.delete()
        pins = await ctx.channel.pins()
        for p in pins:
            try:
                await p.unpin()
            except Exception:
                pass
            await asyncio.sleep(0.4)
        await ctx.send(f"unpinned {len(pins)}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Pin(bot))
