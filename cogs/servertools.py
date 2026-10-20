import asyncio
import discord
from discord.ext import commands

class ServerTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lock")
    async def lock(self, ctx):
        await ctx.message.delete()
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("locked", delete_after=3)

    @commands.command(name="unlock")
    async def unlock(self, ctx):
        await ctx.message.delete()
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("unlocked", delete_after=3)

    @commands.command(name="slowmode")
    async def slowmode(self, ctx, seconds: int = 0):
        await ctx.message.delete()
        await ctx.channel.edit(slowmode_delay=max(0, min(seconds, 21600)))
        await ctx.send(f"slowmode {seconds}s", delete_after=3)

    @commands.command(name="topic")
    async def topic(self, ctx, *, text: str = ""):
        await ctx.message.delete()
        await ctx.channel.edit(topic=text)
        await ctx.send("topic set", delete_after=3)

async def setup(bot):
    await bot.add_cog(ServerTools(bot))
