import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, init
import discord
from discord.ext import commands

init(autoreset=True)
load_dotenv()

with open("config.json") as f:
    BASE_CFG = json.load(f)

MASTER_TOKEN = (os.getenv("TOKEN") or BASE_CFG.get("token") or "").strip()
PREFIX = os.getenv("PREFIX") or BASE_CFG.get("prefix") or "."
WORKER_COGS = ["sniper", "status", "farmer", "presence", "rpc"]

class TokenWorker:
    def __init__(self, token: str):
        self.token = token.strip()
        self.key = self.token[:16]
        self.bot = None
        self.task = None

    async def start(self):
        bot = commands.Bot(
            command_prefix=PREFIX,
            self_bot=True,
            chunk_guilds_at_startup=False,
            help_command=None,
        )
        bot.cfg = dict(BASE_CFG)
        self.bot = bot

        @bot.event
        async def on_ready():
            print(f"{Fore.GREEN}[WORKER] {bot.user} online")

        for cog in WORKER_COGS:
            try:
                await bot.load_extension(f"cogs.{cog}")
            except Exception as e:
                print(f"{Fore.YELLOW}[WORKER] {cog}: {e}")

        try:
            await bot.start(self.token, log_handler=None)
        except Exception as e:
            print(f"{Fore.RED}[WORKER] {self.key} died: {e}")

async def run_master():
    bot = commands.Bot(
        command_prefix=PREFIX,
        self_bot=True,
        chunk_guilds_at_startup=False,
        help_command=None,
    )
    bot.cfg = BASE_CFG
    bot.workers = {}

    @bot.event
    async def on_ready():
        print(f"{Fore.MAGENTA}[MASTER] {bot.user} multi-token control online")

    for fname in sorted(os.listdir("cogs")):
        if fname.endswith(".py") and not fname.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{fname[:-3]}")
                print(f"{Fore.CYAN}[MASTER] {fname}")
            except Exception as e:
                print(f"{Fore.RED}[MASTER] {fname}: {e}")

    @bot.command(name="workers")
    async def workers_cmd(ctx):
        await ctx.message.delete()
        lines = []
        for k, w in bot.workers.items():
            u = w.bot.user if w.bot and w.bot.user else "starting"
            lines.append(f"`{k}` → {u}")
        await ctx.send("workers:\n" + ("\n".join(lines) or "none"), delete_after=12)

    @bot.command(name="startworkers")
    async def startworkers(ctx):
        await ctx.message.delete()
        path = Path("tokens.txt")
        if not path.exists():
            await ctx.send("tokens.txt missing", delete_after=4)
            return
        toks = [l.strip() for l in path.read_text().splitlines() if l.strip() and l.strip() != MASTER_TOKEN]
        launched = 0
        for t in toks:
            key = t[:16]
            if key in bot.workers:
                continue
            w = TokenWorker(t)
            bot.workers[key] = w
            w.task = asyncio.create_task(w.start())
            launched += 1
        await ctx.send(f"launched {launched} (total {len(bot.workers)})", delete_after=5)

    @bot.command(name="stopworkers")
    async def stopworkers(ctx):
        await ctx.message.delete()
        for w in list(bot.workers.values()):
            try:
                if w.bot:
                    await w.bot.close()
            except Exception:
                pass
            if w.task:
                w.task.cancel()
        bot.workers.clear()
        await ctx.send("all workers stopped", delete_after=4)

    await bot.start(MASTER_TOKEN, log_handler=None)

if __name__ == "__main__":
    if not MASTER_TOKEN:
        print(f"{Fore.RED}TOKEN missing")
        raise SystemExit(1)
    asyncio.run(run_master())
