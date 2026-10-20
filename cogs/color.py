import discord
from discord.ext import commands
from io import BytesIO
from PIL import Image

class Color(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="color")
    async def color(self, ctx, hexcode: str):
        await ctx.message.delete()
        hexcode = hexcode.lstrip("#")
        try:
            rgb = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            await ctx.send("bad hex", delete_after=3)
            return
        img = Image.new("RGB", (120, 120), rgb)
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "color.png"))

async def setup(bot):
    await bot.add_cog(Color(bot))
