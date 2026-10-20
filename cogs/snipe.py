from datetime import datetime, timezone
import discord
from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deleted = {}
        self.edited = {}
        self.cache = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.id == self.bot.user.id:
            return
        ch = self.cache.setdefault(message.channel.id, {})
        if len(ch) > 80:
            ch.pop(next(iter(ch)), None)
        ch[message.id] = {
            "content": message.content or "",
            "author": str(message.author),
            "author_id": str(message.author.id),
            "attachments": [a.url for a in message.attachments],
            "ts": datetime.now(timezone.utc).isoformat(),
        }

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message or message.author.id == self.bot.user.id:
            return
        data = None
        ch_cache = self.cache.get(message.channel.id, {})
        data = ch_cache.pop(message.id, None)
        if not data:
            data = {
                "content": message.content or "[no content]",
                "author": str(message.author),
                "author_id": str(message.author.id),
                "attachments": [a.url for a in message.attachments],
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        self.deleted[message.channel.id] = data

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.id == self.bot.user.id or before.content == after.content:
            return
        self.edited[before.channel.id] = {
            "author": str(before.author),
            "author_id": str(before.author.id),
            "old": before.content or "",
            "new": after.content or "",
            "ts": datetime.now(timezone.utc).isoformat(),
        }

    @commands.command(name="snipe")
    async def snipe(self, ctx, channel_id: int = None):
        await ctx.message.delete()
        cid = channel_id or ctx.channel.id
        d = self.deleted.get(cid)
        if not d:
            await ctx.send("no snipe", delete_after=4)
            return
        att = ("\n" + ", ".join(d["attachments"])) if d.get("attachments") else ""
        await ctx.send(
            f"**{d['author']}** (`{d['author_id']}`)\n{d['content'][:1500]}{att}",
            delete_after=20,
        )

    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx):
        await ctx.message.delete()
        d = self.edited.get(ctx.channel.id)
        if not d:
            await ctx.send("no edit snipe", delete_after=4)
            return
        await ctx.send(
            f"**{d['author']}**\nold: {d['old'][:700]}\nnew: {d['new'][:700]}",
            delete_after=20,
        )

    @commands.command(name="clearsnipes")
    async def clearsnipes(self, ctx):
        await ctx.message.delete()
        self.deleted.clear()
        self.edited.clear()
        await ctx.send("snipes cleared", delete_after=3)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
