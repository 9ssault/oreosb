import asyncio
import random
import string
import aiohttp
import discord
from discord.ext import commands

class NitroGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _code(self, length=16):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @commands.command(name="nitros")
    async def nitros(self, ctx, amount: int = 5):
        await ctx.message.delete()
        amount = max(1, min(amount, 25))
        codes = [f"discord.gift/{self._code()}" for _ in range(amount)]
        await ctx.send("\n".join(codes), delete_after=25)

    @commands.command(name="nitrocheck")
    async def nitrocheck(self, ctx, code: str):
        await ctx.message.delete()
        code = code.strip().replace("https://discord.gift/", "").replace("discord.gift/", "")
        code = code.replace("https://discord.com/gifts/", "").split("?")[0]
        url = f"https://discord.com/api/v10/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"
        headers = {
            "Authorization": self.bot.http.token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=headers) as r:
                    data = await r.json(content_type=None)
                    if r.status == 200:
                        uses = data.get("uses")
                        max_uses = data.get("max_uses")
                        redeemed = data.get("redeemed")
                        plan = (data.get("subscription_plan") or {}).get("name") or "?"
                        await ctx.send(
                            f"`{code}` valid | uses {uses}/{max_uses} | redeemed={redeemed} | {plan}",
                            delete_after=15,
                        )
                    else:
                        msg = data.get("message") if isinstance(data, dict) else str(data)[:100]
                        await ctx.send(f"`{code}` {r.status} {msg}", delete_after=10)
        except Exception as e:
            await ctx.send(f"err {e}", delete_after=6)

async def setup(bot):
    await bot.add_cog(NitroGen(bot))
