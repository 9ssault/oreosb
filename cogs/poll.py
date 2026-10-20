import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll")
    async def poll(self, ctx, *, question: str):
        await ctx.message.delete()
        m = await ctx.send(f"**poll**\n{question}")
        for e in ("👍", "👎"):
            try:
                await m.add_reaction(e)
            except Exception:
                pass

    @commands.command(name="ypoll")
    async def ypoll(self, ctx, *, question: str):
        await ctx.message.delete()
        m = await ctx.send(f"**yes/no**\n{question}")
        for e in ("✅", "❌"):
            try:
                await m.add_reaction(e)
            except Exception:
                pass

    @commands.command(name="mpoll")
    async def mpoll(self, ctx, *, body: str):
        """mpoll Question | opt1 | opt2 | opt3"""
        await ctx.message.delete()
        parts = [p.strip() for p in body.split("|") if p.strip()]
        if len(parts) < 3:
            await ctx.send("usage: `.mpoll Question | a | b | c`", delete_after=6)
            return
        q, opts = parts[0], parts[1:10]
        nums = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        lines = [f"**{q}**"] + [f"{nums[i]} {o}" for i, o in enumerate(opts)]
        m = await ctx.send("\n".join(lines))
        for i in range(len(opts)):
            try:
                await m.add_reaction(nums[i])
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Poll(bot))
