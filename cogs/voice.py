import discord
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vcjoin")
    async def vcjoin(self, ctx, channel: discord.VoiceChannel = None):
        await ctx.message.delete()
        ch = channel
        if not ch and ctx.author.voice:
            ch = ctx.author.voice.channel
        if not ch:
            await ctx.send("need voice channel", delete_after=4)
            return
        try:
            await ch.connect(reconnect=False, self_deaf=True)
            await ctx.send(f"joined `{ch.name}`", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="vcleave")
    async def vcleave(self, ctx):
        await ctx.message.delete()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("left vc", delete_after=3)
        else:
            await ctx.send("not in vc", delete_after=3)

    @commands.command(name="muteall")
    async def muteall(self, ctx):
        await ctx.message.delete()
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("join a vc first", delete_after=4)
            return
        n = 0
        for m in ctx.author.voice.channel.members:
            if m.id == self.bot.user.id:
                continue
            try:
                await m.edit(mute=True)
                n += 1
            except Exception:
                pass
        await ctx.send(f"server-muted {n}", delete_after=4)

async def setup(bot):
    await bot.add_cog(Voice(bot))
