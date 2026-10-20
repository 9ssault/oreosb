# cogs/voice.py
import asyncio
import discord
from discord.ext import commands

class VoiceTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vcjoin")
    async def vcjoin(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        ch = None
        if channel_id:
            ch = self.bot.get_channel(channel_id)
        elif ctx.author.voice:
            ch = ctx.author.voice.channel
        if ch:
            await ch.connect()

    @commands.command(name="vcleave")
    async def vcleave(self, ctx):
        await ctx.message.delete()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command(name="muteall")
    async def muteall(self, ctx):
        await ctx.message.delete()
        for m in ctx.guild.members:
            if m.voice:
                try:
                    await m.edit(mute=True)
                except Exception:
                    pass
                await asyncio.sleep(0.2)

async def setup(bot):
    await bot.add_cog(VoiceTools(bot))
