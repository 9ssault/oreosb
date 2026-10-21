import asyncio

import discord
from discord.ext import commands


class VoiceTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._vc = None

    async def _connect(self, channel: discord.VoiceChannel):
        if self.bot.voice_clients:
            for vc in list(self.bot.voice_clients):
                try:
                    await vc.disconnect(force=True)
                except Exception:
                    pass
        try:
            self._vc = await channel.connect()
            return self._vc
        except Exception as e:
            # discord.py-self voice can be flaky — retry once
            await asyncio.sleep(1)
            self._vc = await channel.connect()
            return self._vc

    @commands.command(name="vcjoin")
    async def vcjoin(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        ch = None
        if channel_id:
            ch = self.bot.get_channel(channel_id)
        elif getattr(ctx.author, "voice", None) and ctx.author.voice:
            ch = ctx.author.voice.channel
        if not ch or not isinstance(ch, (discord.VoiceChannel, discord.StageChannel)):
            await ctx.send("need voice channel id or be in vc", delete_after=4)
            return
        try:
            await self._connect(ch)
            await ctx.send(f"joined {ch.name}", delete_after=4)
        except Exception as e:
            await ctx.send(f"vcjoin fail: {e}", delete_after=6)

    @commands.command(name="vcleave")
    async def vcleave(self, ctx):
        await ctx.message.delete()
        ok = 0
        for vc in list(self.bot.voice_clients):
            try:
                await vc.disconnect(force=True)
                ok += 1
            except Exception:
                pass
        self._vc = None
        await ctx.send(f"left {ok}", delete_after=3)

    @commands.command(name="vcmove")
    async def vcmove(self, ctx, channel_id: int):
        await ctx.message.delete()
        ch = self.bot.get_channel(channel_id)
        if not ch:
            await ctx.send("channel not found", delete_after=3)
            return
        try:
            if self.bot.voice_clients:
                await self.bot.voice_clients[0].move_to(ch)
            else:
                await self._connect(ch)
            await ctx.send(f"moved → {ch.name}", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="vcmute")
    async def vcmute(self, ctx):
        await ctx.message.delete()
        if not self.bot.voice_clients:
            return
        vc = self.bot.voice_clients[0]
        try:
            await self.bot.guilds[0].me.edit(mute=True) if False else None
        except Exception:
            pass
        # self mute via voice state
        try:
            await vc.guild.change_voice_state(channel=vc.channel, self_mute=True)
            await ctx.send("self mute", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="vcunmute")
    async def vcunmute(self, ctx):
        await ctx.message.delete()
        if not self.bot.voice_clients:
            return
        vc = self.bot.voice_clients[0]
        try:
            await vc.guild.change_voice_state(channel=vc.channel, self_mute=False)
            await ctx.send("unmuted", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="vcdeaf")
    async def vcdeaf(self, ctx):
        await ctx.message.delete()
        if not self.bot.voice_clients:
            return
        vc = self.bot.voice_clients[0]
        try:
            await vc.guild.change_voice_state(channel=vc.channel, self_deaf=True)
            await ctx.send("deaf", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="vcundeaf")
    async def vcundeaf(self, ctx):
        await ctx.message.delete()
        if not self.bot.voice_clients:
            return
        vc = self.bot.voice_clients[0]
        try:
            await vc.guild.change_voice_state(channel=vc.channel, self_deaf=False)
            await ctx.send("undeaf", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=4)

    @commands.command(name="vclist")
    async def vclist(self, ctx):
        await ctx.message.delete()
        if not ctx.guild:
            return
        lines = []
        for ch in ctx.guild.voice_channels:
            n = len(ch.members)
            lines.append(f"`{ch.id}` {ch.name} ({n})")
        await ctx.send("\n".join(lines[:30]) or "none", delete_after=15)

    @commands.command(name="muteall")
    async def muteall(self, ctx):
        await ctx.message.delete()
        ok = 0
        for m in ctx.guild.members:
            if m.voice and m != ctx.guild.me:
                try:
                    await m.edit(mute=True)
                    ok += 1
                except Exception:
                    pass
                await asyncio.sleep(0.25)
        await ctx.send(f"muted {ok}", delete_after=4)

    @commands.command(name="unmuteall")
    async def unmuteall(self, ctx):
        await ctx.message.delete()
        ok = 0
        for m in ctx.guild.members:
            if m.voice:
                try:
                    await m.edit(mute=False)
                    ok += 1
                except Exception:
                    pass
                await asyncio.sleep(0.25)
        await ctx.send(f"unmuted {ok}", delete_after=4)


async def setup(bot):
    await bot.add_cog(VoiceTools(bot))
