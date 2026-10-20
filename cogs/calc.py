import discord
from discord.ext import commands
import ast
import operator as op

ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg}

def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        return ops[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return ops[type(node.op)](_eval(node.operand))
    raise ValueError("bad")

class Calc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="calc")
    async def calc(self, ctx, *, expr: str):
        await ctx.message.delete()
        try:
            result = _eval(ast.parse(expr, mode="eval").body)
            await ctx.send(f"`{expr}` = `{result}`", delete_after=10)
        except Exception:
            await ctx.send("invalid", delete_after=3)

async def setup(bot):
    await bot.add_cog(Calc(bot))
