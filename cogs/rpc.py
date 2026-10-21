import os
from discord.ext import commands

# presence/RPC disabled by default — discord.py-self build crashes on change_presence
# (MessageToDict including_default_value_fields). Enable only with RPC_ON=1 after upgrade.


class RPC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = os.getenv("RPC_ON", "0").lower() in ("1", "true", "yes")
        self.name = os.getenv("RPC_NAME", " ")
        self.stream_url = os.getenv("RPC_STREAM_URL", "https://twitch.tv/ikcold")

    async def _apply(self):
        if not self.enabled:
            return
        try:
            import discord
            # minimal — still may fail on broken protobuf builds
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.playing, name=self.name or "\u200b"),
                status=discord.Status.online,
            )
        except TypeError as e:
            print(f"[RPC] skipped (lib bug): {e}")
            self.enabled = False
        except Exception as e:
            print(f"[RPC] skipped: {e}")
            self.enabled = False

    @commands.command(name="rpc")
    async def rpc(self, ctx, mode: str = None, *, value: str = None):
        await ctx.message.delete()
        if mode is None:
            await ctx.send(
                f"rpc {'on' if self.enabled else 'off'} (off avoids crash on this discord.py-self)",
                delete_after=8,
            )
            return
        m = mode.lower()
        if m == "on":
            self.enabled = True
            await self._apply()
            await ctx.send("rpc on" if self.enabled else "rpc failed — left off", delete_after=4)
        elif m == "off":
            self.enabled = False
            await ctx.send("rpc off", delete_after=3)
        elif m == "name" and value is not None:
            self.name = value
            if self.enabled:
                await self._apply()
            await ctx.send("name set", delete_after=3)
        elif m == "url" and value:
            self.stream_url = value
            await ctx.send("url stored", delete_after=3)
        elif m == "refresh":
            await self._apply()
            await ctx.send("refreshed" if self.enabled else "rpc off", delete_after=3)
        else:
            await ctx.send("rpc on|off|name|url|refresh", delete_after=4)

    @commands.Cog.listener()
    async def on_ready(self):
        # do not auto-apply — prevents boot spam / crash on broken builds
        return


async def setup(bot):
    await bot.add_cog(RPC(bot))
