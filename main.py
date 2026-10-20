import os
import json
import time
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)
load_dotenv()

CFG_PATH = "config.json"
if not os.path.isfile(CFG_PATH):
    with open(CFG_PATH, "w") as f:
        json.dump({
            "token": "",
            "prefix": ".",
            "nitro_sniper": True,
            "giveaway_sniper": True,
            "status_rotate": False,
            "status_interval": 30,
            "statuses": ["Gaming", "Chilling", "Coding", "Watching"],
            "afk_message": "AFK",
            "private_mode": True,
            "delay": [0.4, 2.5],
        }, f, indent=2)

with open(CFG_PATH) as f:
    cfg = json.load(f)

TOKEN = (os.getenv("TOKEN") or cfg.get("token") or "").strip()
PREFIX = os.getenv("PREFIX") or cfg.get("prefix") or "."

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
        loaded = 0
        for fname in sorted(os.listdir("./cogs")):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            name = fname[:-3]
            try:
                await self.load_extension(f"cogs.{name}")
                print(f"{Fore.GREEN}[+] {name}")
                loaded += 1
            except Exception as e:
                print(f"{Fore.RED}[!] {name}: {e}")
        print(f"{Fore.CYAN}[+] {loaded} cogs")

    async def on_ready(self):
        self.start_time = time.time()
        print(f"{Fore.MAGENTA}╔══════════════════════════════════════╗")
        print(f"{Fore.MAGENTA}║         OreoSB  —  online            ║")
        print(f"{Fore.MAGENTA}╚══════════════════════════════════════╝")
        print(f"{Fore.WHITE}user  : {self.user} ({self.user.id})")
        print(f"{Fore.WHITE}prefix: {PREFIX}")
        print(f"{Fore.WHITE}guilds: {len(self.guilds)}")
        if self.cfg.get("status_rotate"):
            try:
                from cogs.status import start_rotator
                asyncio.create_task(start_rotator(self))
            except Exception as e:
                print(f"{Fore.YELLOW}[status] rotator skip: {e}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, commands.MissingRequiredArgument)):
            return
        print(f"{Fore.RED}[!] {type(error).__name__}: {error}")

bot = OreoSB()

@bot.command(name="ping")
async def ping(ctx):
    await ctx.message.delete()
    lat = round(bot.latency * 1000)
    await ctx.send(f"`{lat}ms`", delete_after=3)

@bot.command(name="uptime")
async def uptime(ctx):
    await ctx.message.delete()
    if not bot.start_time:
        await ctx.send("`starting`", delete_after=3)
        return
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
        return
    n = 0
    for name in list(bot.extensions):
        try:
            await bot.reload_extension(name)
            n += 1
        except Exception as e:
            print(f"{Fore.RED}[reload] {name}: {e}")
    await ctx.send(f"reloaded {n}", delete_after=3)

@bot.command(name="load")
async def load(ctx, cog: str):
    await ctx.message.delete()
    try:
        await bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"loaded `{cog}`", delete_after=3)
    except Exception as e:
        await ctx.send(f"fail: {e}", delete_after=5)

@bot.command(name="unload")
async def unload(ctx, cog: str):
    await ctx.message.delete()
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await ctx.send(f"unloaded `{cog}`", delete_after=3)
    except Exception as e:
        await ctx.send(f"fail: {e}", delete_after=5)

if __name__ == "__main__":
    if not TOKEN:
        print(f"{Fore.RED}[!] TOKEN missing — set TOKEN= in .env (see .env.example) or config.json")
        raise SystemExit(1)
    bot.run(TOKEN, log_handler=None)
