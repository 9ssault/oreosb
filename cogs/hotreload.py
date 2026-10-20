import discord
from discord.ext import commands

class HotReload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload")
    async def reload(self, ctx, name: str = None):
        await ctx.message.delete()
        if not name:
            loaded = []
            for ext in list(self.bot.extensions):
                try:
                    await self.bot.reload_extension(ext)
                    loaded.append(ext.split(".")[-1])
                except Exception as e:
                    loaded.append(f"{ext}:fail")
            await ctx.send("reloaded: " + ", ".join(loaded[:30]), delete_after=10)
            return
        try:
            await self.bot.reload_extension(f"cogs.{name}")
            await ctx.send(f"reloaded {name}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=6)

    @commands.command(name="load")
    async def load(self, ctx, name: str):
        await ctx.message.delete()
        try:
            await self.bot.load_extension(f"cogs.{name}")
            await ctx.send(f"loaded {name}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=6)

    @commands.command(name="unload")
    async def unload(self, ctx, name: str):
        await ctx.message.delete()
        try:
            await self.bot.unload_extension(f"cogs.{name}")
            await ctx.send(f"unloaded {name}", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=6)

async def setup(bot):
    await bot.add_cog(HotReload(bot))
