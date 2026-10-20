# cogs/snipe.py — deleted + edited message snipe
import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deleted = defaultdict(lambda: None)   # channel_id -> last deleted
        self.edited = defaultdict(lambda: None)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.content:
            return
        self.deleted[message.channel.id] = {
            "author": str(message.author),
            "content": message.content[:1500],
            "time": datetime.utcnow().isoformat(),
            "attachments": [a.url for a in message.attachments],
        }

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        self.edited[before.channel.id] = {
            "author": str(before.author),
            "before": before.content[:800],
            "after": after.content[:800],
            "time": datetime.utcnow().isoformat(),
        }

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        await ctx.message.delete()
        data = self.deleted.get(ctx.channel.id)
        if not data:
            await ctx.send("nothing to snipe", delete_after=3)
            return
        att = "\n".join(data["attachments"]) if data["attachments"] else ""
        await ctx.send(f"**{data['author']}** deleted:\n{data['content']}\n{att}", delete_after=15)

    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx):
        await ctx.message.delete()
        data = self.edited.get(ctx.channel.id)
        if not data:
            await ctx.send("nothing edited", delete_after=3)
            return
        await ctx.send(f"**{data['author']}** edited:\n- {data['before']}\n+ {data['after']}", delete_after=15)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
