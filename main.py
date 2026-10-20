# main.py — OreoSB entry point
import os
import json
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)
load_dotenv()

with open("config.json") as f:
    cfg = json.load(f)

TOKEN = os.getenv("TOKEN") or cfg.get("token")
PREFIX = os.getenv("PREFIX") or cfg.get("prefix", ".")

class OreoSB(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            self_bot=True,
            chunk_guilds_at_startup=False,
            help_command=None,
        )
        self.cfg = cfg
        self.start_time = None

    async def setup_hook(self):
        # load all cogs
        for fname in os.listdir("./cogs"):
            if fname.endswith(".py") and not fname.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{fname[:-3]}")
                    print(f"{Fore.GREEN}[+] loaded cog: {fname}")
                except Exception as e:
                    print(f"{Fore.RED}[!] failed {fname}: {e}")
        print(f"{Fore.CYAN}[+] {len(self.cogs)} cogs ready")

    async def on_ready(self):
        import time
        self.start_time = time.time()
        print(f"{Fore.MAGENTA}╔══════════════════════════════════════╗")
        print(f"{Fore.MAGENTA}║         OreoSB  —  online            ║")
        print(f"{Fore.MAGENTA}╚══════════════════════════════════════╝")
        print(f"{Fore.WHITE}user  : {self.user} ({self.user.id})")
        print(f"{Fore.WHITE}prefix: {PREFIX}")
        print(f"{Fore.WHITE}guilds: {len(self.guilds)}")
        if self.cfg.get("status_rotate"):
            from cogs.status import start_rotator
            asyncio.create_task(start_rotator(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            return
        print(f"{Fore.RED}[!] {error}")

bot = OreoSB()

@bot.command(name="ping")
async def ping(ctx):
    await ctx.message.delete()
    lat = round(bot.latency * 1000)
    await ctx.send(f"`{lat}ms`", delete_after=3)

@bot.command(name="uptime")
async def uptime(ctx):
    await ctx.message.delete()
    import time
    secs = int(time.time() - bot.start_time)
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    await ctx.send(f"`{h}h {m}m {s}s`", delete_after=5)

@bot.command(name="reload")
async def reload(ctx, cog: str = None):
    await ctx.message.delete()
    if cog:
        try:
            await bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"reloaded `{cog}`", delete_after=3)
        except Exception as e:
            await ctx.send(f"fail: {e}", delete_after=5)
    else:
        for name in list(bot.extensions):
            await bot.reload_extension(name)
        await ctx.send(f"reloaded all ({len(bot.extensions)})", delete_after=3)

if __name__ == "__main__":
    if not TOKEN:
        print(f"{Fore.RED}[!] TOKEN missing — set in .env or config.json")
        raise SystemExit(1)
    bot.run(TOKEN, log_handler=None)
