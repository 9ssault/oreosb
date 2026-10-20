import asyncio
import discord
from discord.ext import commands

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spotify")
    async def spotify(self, ctx, *, title: str = "Unknown"):
        await ctx.message.delete()
        act = discord.Activity(type=discord.ActivityType.listening, name=title)
        await self.bot.change_presence(activity=act)
        await ctx.send(f"listening {title}", delete_after=3)

    @commands.command(name="watching")
    async def watching(self, ctx, *, title: str):
        await ctx.message.delete()
        act = discord.Activity(type=discord.ActivityType.watching, name=title)
        await self.bot.change_presence(activity=act)
        await ctx.send(f"watching {title}", delete_after=3)

    @commands.command(name="competing")
    async def competing(self, ctx, *, title: str):
        await ctx.message.delete()
        act = discord.Activity(type=discord.ActivityType.competing, name=title)
        await self.bot.change_presence(activity=act)
        await ctx.send(f"competing {title}", delete_after=3)

    @commands.command(name="clearpresence")
    async def clearpresence(self, ctx):
        await ctx.message.delete()
        await self.bot.change_presence(activity=None)
        await ctx.send("cleared", delete_after=3)

async def setup(bot):
    await bot.add_cog(Presence(bot))
