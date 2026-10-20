import asyncio
import discord
from discord.ext import commands

class Group(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gcreate")
    async def gcreate(self, ctx, *users: discord.User):
        await ctx.message.delete()
        if not users:
            return
        try:
            dm = await users[0].create_dm()
            # discord.py-self group create via recipients
            ch = await self.bot.http.start_group([u.id for u in users])
            await ctx.send(f"group created", delete_after=4)
        except Exception as e:
            await ctx.send(f"fail {e}", delete_after=5)

    @commands.command(name="gleave")
    async def gleave(self, ctx):
        await ctx.message.delete()
        if isinstance(ctx.channel, discord.GroupChannel):
            await ctx.channel.leave()
            await ctx.send("left group", delete_after=3)

async def setup(bot):
    await bot.add_cog(Group(bot))
