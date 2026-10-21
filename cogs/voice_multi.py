import asyncio
import discord
from discord.ext import commands

class VoiceMulti(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mj")
    async def mj(self, ctx, channel_id: int):
        await ctx.message.delete()
        ch = self.bot.get_channel(channel_id)
        if not isinstance(ch, discord.VoiceChannel):
            try:
                ch = await self.bot.fetch_channel(channel_id)
            except Exception:
                await ctx.send("invalid channel", delete_after=4)
                return
        if not isinstance(ch, discord.VoiceChannel):
            await ctx.send("not a voice channel", delete_after=4)
            return
        try:
            await ch.connect(reconnect=True, self_deaf=False, self_mute=True)
            await ctx.send(f"joined `{ch.name}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="ml")
    async def ml(self, ctx):
        await ctx.message.delete()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("left vc", delete_after=3)
        else:
            await ctx.send("not in vc", delete_after=3)

    @commands.command(name="mstatus")
    async def mstatus(self, ctx):
        await ctx.message.delete()
        vc = ctx.voice_client
        if vc and vc.channel:
            await ctx.send(f"connected → `{vc.channel.name}`", delete_after=5)
        else:
            await ctx.send("not connected", delete_after=3)

async def setup(bot):
    await bot.add_cog(VoiceMulti(bot))
