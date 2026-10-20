import ast
import operator
import discord
from discord.ext import commands

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("bad expr")

class Calc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="calc")
    async def calc(self, ctx, *, expr: str):
        await ctx.message.delete()
        try:
            tree = ast.parse(expr, mode="eval")
            result = _eval(tree)
            await ctx.send(f"`{expr}` = `{result}`", delete_after=12)
        except Exception:
            await ctx.send("invalid expr", delete_after=4)

async def setup(bot):
    await bot.add_cog(Calc(bot))
