from io import BytesIO
import discord
from discord.ext import commands

try:
    from PIL import Image
except ImportError:
    Image = None

class Color(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="color")
    async def color(self, ctx, hexcode: str):
        await ctx.message.delete()
        h = hexcode.strip().lstrip("#")
        if len(h) not in (3, 6):
            await ctx.send("use #rrggbb", delete_after=4)
            return
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except ValueError:
            await ctx.send("bad hex", delete_after=3)
            return
        if Image is None:
            await ctx.send(f"#{h} rgb({r},{g},{b})", delete_after=8)
            return
        img = Image.new("RGB", (120, 120), (r, g, b))
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        await ctx.send(f"`#{h}` rgb({r},{g},{b})", file=discord.File(buf, "color.png"))

async def setup(bot):
    await bot.add_cog(Color(bot))
