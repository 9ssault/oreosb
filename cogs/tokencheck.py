import asyncio
import aiohttp
import discord
from discord.ext import commands
from pathlib import Path

API = "https://discord.com/api/v10"

class TokenCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _info(self, token: str):
        headers = {"Authorization": token, "Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{API}/users/@me", headers=headers, timeout=10) as r:
                    if r.status != 200:
                        return None
                    return await r.json()
        except Exception:
            return None

    @commands.command(name="checktoken")
    async def checktoken(self, ctx, token: str = None):
        await ctx.message.delete()
        t = (token or self.bot.http.token or "").strip()
        info = await self._info(t)
        if not info:
            await ctx.send("dead", delete_after=4)
            return
        nitro = info.get("premium_type", 0)
        flags = info.get("flags", 0)
        await ctx.send(
            f"**{info.get('username')}** `{info.get('id')}`\n"
            f"nitro={nitro} verified={info.get('verified')} mfa={info.get('mfa_enabled')} flags={flags}",
            delete_after=15,
        )

    @commands.command(name="bulkcheck")
    async def bulkcheck(self, ctx):
        await ctx.message.delete()
        path = Path("tokens.txt")
        if not path.exists():
            await ctx.send("no tokens.txt", delete_after=3)
            return
        toks = [l.strip() for l in path.read_text().splitlines() if l.strip()]
        valid, dead = [], []
        for t in toks:
            info = await self._info(t)
            if info:
                valid.append(f"{info.get('username')} `{t[:14]}...`")
            else:
                dead.append(t[:14])
            await asyncio.sleep(0.4)
        Path("valid_tokens.txt").write_text(
            "\n".join(t for t in toks if any(t[:14] in v for v in valid)) + "\n"
            if valid else ""
        )
        body = f"valid {len(valid)} / dead {len(dead)}\n" + "\n".join(valid[:25])
        await ctx.send(body[:1900], delete_after=25)

async def setup(bot):
    await bot.add_cog(TokenCheck(bot))
