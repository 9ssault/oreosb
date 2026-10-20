# multi_token.py — master multi-token runner
# each token can have its own config in configs/<token_id>.json
# master token (from .env / config.json) can control all via commands
import asyncio
import json
import os
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore, init

init(autoreset=True)
load_dotenv()

MASTER_TOKEN = os.getenv("TOKEN") or json.load(open("config.json")).get("token")
PREFIX = os.getenv("PREFIX", ".")

class TokenWorker:
    def __init__(self, token: str, name: str = None):
        self.token = token
        self.name = name or token[:12]
        self.bot = None
        self.task = None
        self.cfg = self._load_cfg()

    def _load_cfg(self):
        # per-token config if exists
        uid = None
        path = Path("configs")
        path.mkdir(exist_ok=True)
        # fallback to global
        with open("config.json") as f:
            base = json.load(f)
        return base

    async def start(self):
        bot = commands.Bot(command_prefix=PREFIX, self_bot=True, chunk_guilds_at_startup=False, help_command=None)
        self.bot = bot

        @bot.event
        async def on_ready():
            print(f"{Fore.GREEN}[WORKER] {bot.user} online")

        # load core cogs only for workers (lighter)
        for cog in ["sniper", "status", "farmer"]:
            try:
                await bot.load_extension(f"cogs.{cog}")
            except Exception as e:
                print(f"{Fore.YELLOW}[WORKER] cog {cog} skip: {e}")

        try:
            await bot.start(self.token, log_handler=None)
        except Exception as e:
            print(f"{Fore.RED}[WORKER] {self.name} died: {e}")

async def run_master():
    with open("config.json") as f:
        cfg = json.load(f)
    bot = commands.Bot(command_prefix=PREFIX, self_bot=True, chunk_guilds_at_startup=False, help_command=None)
    bot.cfg = cfg
    bot.workers = {}

    @bot.event
    async def on_ready():
        print(f"{Fore.MAGENTA}[MASTER] {bot.user} ready — multi-token control online")

    # load ALL cogs on master
    for f in os.listdir("cogs"):
        if f.endswith(".py") and not f.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{f[:-3]}")
                print(f"{Fore.CYAN}[MASTER] loaded {f}")
            except Exception as e:
                print(f"{Fore.RED}[MASTER] fail {f}: {e}")

    @bot.command(name="workers")
    async def workers_cmd(ctx):
        await ctx.message.delete()
        lines = [f"`{n}` → {w.bot.user if w.bot and w.bot.user else 'starting'}" for n, w in bot.workers.items()]
        await ctx.send("workers:\n" + ("\n".join(lines) or "none"), delete_after=10)

    @bot.command(name="startworkers")
    async def startworkers(ctx):
        await ctx.message.delete()
        try:
            with open("tokens.txt") as f:
                toks = [l.strip() for l in f if l.strip() and l.strip() != MASTER_TOKEN]
        except FileNotFoundError:
            await ctx.send("tokens.txt empty", delete_after=3)
            return
        for t in toks:
            if t in bot.workers:
                continue
            w = TokenWorker(t)
            bot.workers[t[:16]] = w
            w.task = asyncio.create_task(w.start())
        await ctx.send(f"launched {len(toks)} workers", delete_after=5)

    @bot.command(name="stopworkers")
    async def stopworkers(ctx):
        await ctx.message.delete()
        for w in bot.workers.values():
            if w.bot:
                await w.bot.close()
            if w.task:
                w.task.cancel()
        bot.workers.clear()
        await ctx.send("all workers stopped", delete_after=4)

    await bot.start(MASTER_TOKEN, log_handler=None)

if __name__ == "__main__":
    if not MASTER_TOKEN:
        print("TOKEN missing")
        raise SystemExit(1)
    asyncio.run(run_master())
