import discord
from discord.ext import commands
from collections import defaultdict, deque
from datetime import datetime, timezone

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deleted = defaultdict(lambda: deque(maxlen=10))
        self.edited = defaultdict(lambda: deque(maxlen=10))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message or message.author.bot:
            return
        if not message.content and not message.attachments:
            return
        self.deleted[message.channel.id].appendleft({
            "author": str(message.author),
            "author_id": message.author.id,
            "content": (message.content or "")[:1500],
            "time": datetime.now(timezone.utc).isoformat(),
            "attachments": [a.url for a in message.attachments],
        })

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        self.edited[before.channel.id].appendleft({
            "author": str(before.author),
            "before": (before.content or "")[:800],
            "after": (after.content or "")[:800],
            "time": datetime.now(timezone.utc).isoformat(),
        })

    @commands.command(name="snipe")
    async def snipe(self, ctx, index: int = 1):
        await ctx.message.delete()
        q = self.deleted.get(ctx.channel.id)
        if not q:
            await ctx.send("nothing to snipe", delete_after=3)
            return
        index = max(1, min(index, len(q)))
        data = q[index - 1]
        att = "\n".join(data["attachments"]) if data["attachments"] else ""
        await ctx.send(
            f"**{data['author']}** deleted ({index}/{len(q)}):\n{data['content']}\n{att}",
            delete_after=18,
        )

    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx, index: int = 1):
        await ctx.message.delete()
        q = self.edited.get(ctx.channel.id)
        if not q:
            await ctx.send("nothing edited", delete_after=3)
            return
        index = max(1, min(index, len(q)))
        data = q[index - 1]
        await ctx.send(
            f"**{data['author']}** edited ({index}/{len(q)}):\n- {data['before']}\n+ {data['after']}",
            delete_after=18,
        )

    @commands.command(name="snipeall")
    async def snipeall(self, ctx):
        await ctx.message.delete()
        q = self.deleted.get(ctx.channel.id)
        if not q:
            await ctx.send("empty", delete_after=3)
            return
        lines = [f"`{i+1}` **{d['author']}**: {(d['content'] or '')[:80]}" for i, d in enumerate(q)]
        await ctx.send("\n".join(lines)[:1900], delete_after=20)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
