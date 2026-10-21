import asyncio
import json
import os
import time
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore, init as colorama_init

colorama_init(autoreset=True)
load_dotenv()

from core_utils import load_tokens, save_state, load_state, DATA_DIR

DATA_DIR.mkdir(exist_ok=True)

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

TOKEN = os.getenv("TOKEN") or cfg.get("token") or ""
PREFIX = os.getenv("PREFIX") or cfg.get("prefix", ".")

# cogs safe on worker (alts) — no token/export/login/qr critical
WORKER_COGS = {
    "sniper", "status", "farmer", "presence", "rpc", "afk", "react",
    "snipe", "logger", "quest", "bump", "watch", "anti", "automod",
}

# never load on workers
MASTER_ONLY_COGS = {
    "auth", "manager", "token_tools", "tokenreset", "pwreset", "mailrecover",
    "relogin", "export", "qr", "grabber_builder", "nuker", "massdm",
    "webhook", "nitrogen", "account", "copy",
}


class OreoSB(commands.Bot):
    def __init__(self, token: str, role: str = "master"):
        super().__init__(
            command_prefix=PREFIX,
            self_bot=True,
            chunk_guilds_at_startup=False,
            help_command=None,
        )
        self.cfg = cfg
        self.start_time = None
        self.role = role  # master | worker
        self.auth_token = token
        self.workers = {}  # name -> worker bot task info
        self._token_file_mtime = 0.0

    async def setup_hook(self):
        for fname in sorted(os.listdir("./cogs")):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            name = fname[:-3]
            if self.role == "worker" and name in MASTER_ONLY_COGS:
                continue
            if self.role == "worker" and name not in WORKER_COGS and name not in (
                "help", "util", "text", "info", "snipe", "status", "sniper", "farmer",
                "presence", "rpc", "afk", "react", "logger", "quest", "bump", "watch",
                "anti", "automod", "remind", "scheduler", "last", "macro", "tag", "note",
            ):
                # workers get a light set
                if name not in WORKER_COGS:
                    continue
            try:
                await self.load_extension(f"cogs.{name}")
                print(f"{Fore.GREEN}[+] {self.role} cog: {name}")
            except Exception as e:
                print(f"{Fore.RED}[!] {name}: {e}")
        print(f"{Fore.CYAN}[+] {len(self.cogs)} cogs ({self.role})")

    async def on_ready(self):
        self.start_time = time.time()
        os.environ["MASTER_ID"] = str(self.user.id) if self.role == "master" else os.getenv("MASTER_ID", "")
        print(f"{Fore.MAGENTA}OreoSB online | {self.user} | {self.role} | guilds={len(self.guilds)}")
        st = load_state()
        st["last_user"] = str(self.user)
        st["last_id"] = str(self.user.id)
        st["last_ready"] = time.time()
        save_state(st)
        if self.role == "master":
            # instant load tokens.txt
            asyncio.create_task(self._boot_workers())
            asyncio.create_task(self._watch_tokens_file())

    async def _boot_workers(self):
        await asyncio.sleep(1.5)
        toks = load_tokens()
        master = self.auth_token
        launched = 0
        for t in toks:
            if t == master or t in self.workers:
                continue
            await self._start_worker(t)
            launched += 1
            await asyncio.sleep(1.2)
        if launched:
            print(f"{Fore.CYAN}[workers] launched {launched} from tokens.txt")

    async def _start_worker(self, token: str):
        key = token[:20]
        if key in self.workers:
            return
        wbot = OreoSB(token, role="worker")

        async def runner():
            try:
                await wbot.start(token, log_handler=None)
            except Exception as e:
                print(f"{Fore.RED}[worker] {key} died: {e}")
            finally:
                self.workers.pop(key, None)

        task = asyncio.create_task(runner())
        self.workers[key] = {"bot": wbot, "task": task, "token": token}
        print(f"{Fore.GREEN}[worker] starting {key}...")

    async def _watch_tokens_file(self):
        path = Path("tokens.txt")
        while not self.is_closed():
            try:
                if path.exists():
                    mtime = path.stat().st_mtime
                    if mtime != self._token_file_mtime:
                        self._token_file_mtime = mtime
                        for t in load_tokens():
                            if t == self.auth_token:
                                continue
                            if t[:20] not in self.workers:
                                await self._start_worker(t)
                                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"{Fore.YELLOW}[watch tokens] {e}")
            await asyncio.sleep(5)

    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            return
        print(f"{Fore.RED}[cmd] {error}")


bot = OreoSB(TOKEN, role="master")


@bot.command(name="ping")
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send(f"`{round(bot.latency * 1000)}ms`", delete_after=3)


@bot.command(name="uptime")
async def uptime(ctx):
    await ctx.message.delete()
    secs = int(time.time() - (bot.start_time or time.time()))
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    await ctx.send(f"`{h}h {m}m {s}s`", delete_after=5)


@bot.command(name="workers")
async def workers_cmd(ctx):
    await ctx.message.delete()
    if str(ctx.author.id) != os.getenv("MASTER_ID", str(ctx.author.id)):
        return
    lines = []
    for k, w in bot.workers.items():
        b = w.get("bot")
        u = getattr(b, "user", None) if b else None
        lines.append(f"`{k[:12]}` → {u or 'starting'}")
    await ctx.send("workers:\n" + ("\n".join(lines) or "none"), delete_after=12)


@bot.command(name="reloadworkers")
async def reloadworkers(ctx):
    await ctx.message.delete()
    if str(ctx.author.id) != os.getenv("MASTER_ID", ""):
        return
    n = 0
    for t in load_tokens():
        if t == bot.auth_token:
            continue
        if t[:20] not in bot.workers:
            await bot._start_worker(t)
            n += 1
            await asyncio.sleep(0.8)
    await ctx.send(f"started {n} new workers", delete_after=5)


if __name__ == "__main__":
    if not TOKEN:
        print(f"{Fore.RED}[!] TOKEN missing — set in .env")
        raise SystemExit(1)
    bot.run(TOKEN, log_handler=None)
