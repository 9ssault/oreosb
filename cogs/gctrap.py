import asyncio
import discord
from discord.ext import commands
from pathlib import Path
import json

WL = Path("gc_whitelist.json")

def load_wl():
    if WL.exists():
        return set(json.loads(WL.read_text()))
    return set()

def save_wl(s):
    WL.write_text(json.dumps(list(s)))

class GCTrap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wl = load_wl()
        self.msg = "nice try"
        self.icon = None
        self.busy = set()

    @commands.command(name="gcwl")
    async def gcwl(self, ctx, user_id: int):
        await ctx.message.delete()
        self.wl.add(str(user_id))
        save_wl(self.wl)
        await ctx.send(f"+ wl {user_id}", delete_after=4)

    @commands.command(name="gcunwl")
    async def gcunwl(self, ctx, user_id: int):
        await ctx.message.delete()
        self.wl.discard(str(user_id))
        save_wl(self.wl)
        await ctx.send(f"- wl {user_id}", delete_after=4)

    @commands.Cog.listener()
    async def on_private_channel_create(self, channel):
        if not isinstance(channel, discord.GroupChannel):
            return
        if channel.id in self.busy:
            return
        self.busy.add(channel.id)
        try:
            owner = getattr(channel, "owner_id", None)
            if owner and str(owner) in self.wl:
                return
            try:
                await channel.edit(name="trapped")
            except Exception:
                pass
            try:
                await channel.send(self.msg)
            except Exception:
                pass
            await asyncio.sleep(0.4)
            try:
                await channel.delete()
            except Exception:
                pass
        finally:
            await asyncio.sleep(3)
            self.busy.discard(channel.id)

async def setup(bot):
    await bot.add_cog(GCTrap(bot))
