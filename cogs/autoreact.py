import discord
from discord.ext import commands

class AutoReact(commands.Cog):
    """Per-user multi-emoji auto react (from JS react system)."""

    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self.targets = {}  # user_id -> [emoji, ...]
        self.bot_emoji = None

    @commands.command(name="react")
    async def react(self, ctx, action: str = None, user: str = None, *emojis):
        await ctx.message.delete()
        a = (action or "").lower()

        if a == "on":
            if not self.targets:
                await ctx.send("no targets — `react add <id> <emojis>`", delete_after=5)
                return
            self.enabled = True
            await ctx.send(f"react on ({len(self.targets)} targets)", delete_after=3)
            return

        if a == "off":
            self.enabled = False
            await ctx.send("react off", delete_after=3)
            return

        if a == "list":
            if not self.targets:
                await ctx.send("none", delete_after=3)
                return
            lines = [f"<@{uid}> {' '.join(ems)}" for uid, ems in list(self.targets.items())[:20]]
            await ctx.send("\n".join(lines), delete_after=15)
            return

        if a == "add" and user:
            uid = "".join(c for c in user if c.isdigit())
            if not uid or not emojis:
                await ctx.send("`react add <id> emoji1 emoji2...`", delete_after=5)
                return
            self.targets[int(uid)] = list(emojis)
            await ctx.send(f"react add <@{uid}> {' '.join(emojis)}", delete_after=4)
            return

        if a == "remove" and user:
            uid = int("".join(c for c in user if c.isdigit()) or 0)
            self.targets.pop(uid, None)
            if not self.targets:
                self.enabled = False
            await ctx.send("removed", delete_after=3)
            return

        await ctx.send("`react on|off|list|add|remove`", delete_after=5)

    @commands.command(name="reactmsg")
    async def reactmsg(self, ctx, message_id: int, *emojis):
        await ctx.message.delete()
        if not emojis:
            await ctx.send("need emojis", delete_after=3)
            return
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except Exception:
            await ctx.send("msg not found", delete_after=3)
            return
        ok = 0
        for e in emojis:
            try:
                await msg.add_reaction(e)
                ok += 1
            except Exception:
                pass
        await ctx.send(f"reacted {ok}/{len(emojis)}", delete_after=4)

    @commands.command(name="r")
    async def r(self, ctx, emoji: str = None):
        await ctx.message.delete()
        self.bot_emoji = emoji
        await ctx.send(f"bot react → {emoji or 'off'}", delete_after=3)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            if self.bot_emoji:
                try:
                    await message.add_reaction(self.bot_emoji)
                except Exception:
                    pass
            return
        if not self.enabled:
            return
        ems = self.targets.get(message.author.id)
        if not ems:
            return
        for e in ems:
            try:
                await message.add_reaction(e)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(AutoReact(bot))
