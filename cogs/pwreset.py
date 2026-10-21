import aiohttp
import json
import os
import secrets
import string
from pathlib import Path
import discord
from discord.ext import commands
from core_utils import owner_check

API = "https://discord.com/api/v10"

class PasswordReset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _h(self, token=None):
        t = token or getattr(self.bot.http, "token", "")
        return {
            "Authorization": t,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    def _gen_password(self, n=16):
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return "".join(secrets.choice(alphabet) for _ in range(n))

    def _save_password(self, password: str):
        env = Path(".env")
        lines = []
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("PASSWORD="):
                    lines.append(f"PASSWORD={password}")
                else:
                    lines.append(line)
        else:
            lines = [f"PASSWORD={password}"]
        if not any(l.startswith("PASSWORD=") for l in lines):
            lines.append(f"PASSWORD={password}")
        env.write_text("\n".join(lines) + "\n")

    @commands.command(name="changepass")
    @owner_check()
    async def changepass(self, ctx, current_password: str, new_password: str = None):
        """Change password while logged in (requires current password). Updates .env PASSWORD."""
        await ctx.message.delete()
        if not new_password:
            new_password = self._gen_password()
        payload = {
            "password": current_password,
            "new_password": new_password,
        }
        async with aiohttp.ClientSession() as s:
            async with s.patch(f"{API}/users/@me", headers=self._h(), json=payload) as r:
                data = await r.json(content_type=None) if r.content_type else {}
                if r.status in (200, 204):
                    self._save_password(new_password)
                    # new token may be issued
                    if isinstance(data, dict) and data.get("token"):
                        from pathlib import Path as P
                        env = P(".env")
                        lines = []
                        for line in (env.read_text().splitlines() if env.exists() else []):
                            if line.startswith("TOKEN="):
                                lines.append(f"TOKEN={data['token']}")
                            else:
                                lines.append(line)
                        if not any(l.startswith("TOKEN=") for l in lines):
                            lines.insert(0, f"TOKEN={data['token']}")
                        env.write_text("\n".join(lines) + "\n")
                    await ctx.send(f"password changed → saved to .env\n`{new_password}`\nrestart recommended", delete_after=20)
                else:
                    await ctx.send(f"fail {r.status} {str(data)[:150]}", delete_after=10)

    @commands.command(name="forgotpass")
    @owner_check()
    async def forgotpass(self, ctx, email: str = None):
        """Trigger Discord forgot-password email (you must open the link + set new pass, then .setlogin)."""
        await ctx.message.delete()
        email = email or os.getenv("EMAIL", "")
        if not email:
            await ctx.send("need email", delete_after=4)
            return
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{API}/auth/forgot",
                json={"login": email},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
            ) as r:
                if r.status in (200, 204):
                    await ctx.send("reset email sent — open link, set new password, then .setlogin email newpass", delete_after=15)
                else:
                    txt = await r.text()
                    await ctx.send(f"fail {r.status} {txt[:120]}", delete_after=8)

    @commands.command(name="autoreset")
    @owner_check()
    async def autoreset(self, ctx):
        """If still logged in: rotate password to a new random one and save it. Helps after session wipes when password still works."""
        await ctx.message.delete()
        current = os.getenv("PASSWORD", "")
        if not current:
            await ctx.send("PASSWORD not in .env — use .changepass old new", delete_after=6)
            return
        new_password = self._gen_password()
        payload = {"password": current, "new_password": new_password}
        async with aiohttp.ClientSession() as s:
            async with s.patch(f"{API}/users/@me", headers=self._h(), json=payload) as r:
                data = await r.json(content_type=None) if r.status != 204 else {}
                if r.status in (200, 204):
                    self._save_password(new_password)
                    if isinstance(data, dict) and data.get("token"):
                        env = Path(".env")
                        lines = []
                        for line in (env.read_text().splitlines() if env.exists() else []):
                            if line.startswith("TOKEN="):
                                lines.append(f"TOKEN={data['token']}")
                            else:
                                lines.append(line)
                        env.write_text("\n".join(lines) + "\n")
                    await ctx.send(f"rotated password → `.env` updated\n`{new_password}`", delete_after=20)
                else:
                    await ctx.send(f"fail {r.status} — password may already be wrong; use .forgotpass", delete_after=10)

async def setup(bot):
    await bot.add_cog(PasswordReset(bot))
