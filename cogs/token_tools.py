# cogs/token_tools.py
import asyncio
import aiohttp
import discord
from discord.ext import commands
from core_utils import owner_check

API = "https://discord.com/api/v10"

async def check_token(token: str) -> dict:
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    }
    async with aiohttp.ClientSession(headers=headers) as s:
        async with s.get(f"{API}/users/@me") as r:
            if r.status == 200:
                return {"status": "valid", "data": await r.json()}
            if r.status == 401:
                return {"status": "invalid"}
            if r.status == 403:
                return {"status": "locked"}
            return {"status": f"unknown_{r.status}"}

class TokenTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="checktoken")
    @owner_check()
    async def checktoken(self, ctx, token: str):
        await ctx.message.delete()
        res = await check_token(token)
        if res["status"] == "valid":
            d = res["data"]
            nitro = "yes" if d.get("premium_type", 0) > 0 else "no"
            phone = "yes" if d.get("phone") else "no"
            out = f"**valid**\n{d['username']} | id:{d['id']}\nnitro:{nitro} phone:{phone}\nemail:{d.get('email','?')}"
        else:
            out = f"status: `{res['status']}`"
        await ctx.send(out, delete_after=12)

    @commands.command(name="bulkcheck")
    @owner_check()
    async def bulkcheck(self, ctx):
        await ctx.message.delete()
        try:
            with open("tokens.txt") as f:
                tokens = [l.strip() for l in f if l.strip()]
        except FileNotFoundError:
            await ctx.send("tokens.txt missing", delete_after=3)
            return
        valid, locked, dead = [], [], []
        for t in tokens:
            r = await check_token(t)
            if r["status"] == "valid":
                valid.append(t)
            elif r["status"] == "locked":
                locked.append(t)
            else:
                dead.append(t)
            await asyncio.sleep(0.6)
        with open("valid_tokens.txt", "w") as f:
            f.write("\n".join(valid))
        await ctx.send(f"valid:{len(valid)} locked:{len(locked)} dead:{len(dead)}", delete_after=10)

async def setup(bot):
    await bot.add_cog(TokenTools(bot))
