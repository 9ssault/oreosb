import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# kill library noise before anything else
logging.disable(logging.INFO)
for _name in ("discord", "discord.http", "discord.gateway", "discord.client", "asyncio"):
    logging.getLogger(_name).disabled = True
    logging.getLogger(_name).setLevel(logging.CRITICAL)

import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)
load_dotenv()

# discord may re-add handlers on import
logging.disable(logging.INFO)
for _name in ("discord", "discord.http", "discord.gateway", "discord.client"):
    log = logging.getLogger(_name)
    log.handlers.clear()
    log.propagate = False
    log.disabled = True

from core_utils import load_tokens, save_state, load_state, DATA_DIR

DATA_DIR.mkdir(exist_ok=True)

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

TOKEN = os.getenv("TOKEN") or cfg.get("token") or ""
PREFIX = os.getenv("PREFIX") or cfg.get("prefix", ".")
# workers off unless explicitly enabled — keeps logs clean like your target format
AUTO_WORKERS = os.getenv("AUTO_WORKERS", "0").lower() in ("1", "true", "yes")

WORKER_COGS = {
    "sniper", "status", "farmer", "presence", "rpc", "afk", "react",
    "snipe", "logger", "quest", "bump", "watch", "anti", "automod",
    "help", "util", "text", "info", "remind", "scheduler", "last",
    "macro", "tag", "note", "voice", "autojoin",
}

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
        self.role = role
        self.auth_token = token
        self.workers = {}
        self.failed_workers = set()
        self._token_file_mtime = 0.0

    async def setup_hook(self):
        loaded = 0
        for fname in sorted(os.listdir("./cogs")):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            name = fname[:-3]
            if self.role == "worker" and (name in MASTER_ONLY_COGS or name not in WORKER_COGS):
                continue
            try:
                await self.load_extension(f"cogs.{name}")
                if self.role == "master":
                    print(f"{Fore.GREEN}[+] {name}")
                loaded += 1
            except Exception as e:
                if self.role == "master":
                    print(f"{Fore.YELLOW}[-] skip {name}")
        if self.role == "master":
            print(f"{Fore.CYAN}[+] {loaded} cogs")

    async def on_ready(self):
        self.start_time = time.time()
        if self.role == "master":
            os.environ["MASTER_ID"] = str(self.user.id)
            print(f"{Fore.MAGENTA}╔══════════════════════════════════════╗")
            print(f"{Fore.MAGENTA}║         OreoSB  —  online            ║")
            print(f"{Fore.MAGENTA}╚══════════════════════════════════════╝")
            print(f"{Fore.WHITE}user  : {self.user} ({self.user.id})")
            print(f"{Fore.WHITE}prefix: {PREFIX}")
            print(f"{Fore.WHITE}guilds: {len(self.guilds)}")
            st = load_state()
            st["last_user"] = str(self.user)
            st["last_id"] = str(self.user.id)
            st["last_ready"] = time.time()
            save_state(st)
            if AUTO_WORKERS:
                asyncio.create_task(self._boot_workers())
                asyncio.create_task(self._watch_tokens_file())

    async def _boot_workers(self):
        await asyncio.sleep(1.5)
        n = 0
        for t in load_tokens():
            if t == self.auth_token or t[:20] in self.workers:
                continue
            await self._start_worker(t)
            n += 1
            await asyncio.sleep(1.2)
        if n:
            print(f"{Fore.CYAN}[workers] {n} started")

    async def _start_worker(self, token: str):
        key = token[:20]
        if key in self.workers:
            return
        wbot = OreoSB(token, role="worker")

        async def runner():
            try:
                await wbot.start(token, log_handler=None)
            except Exception as e:
                print(f"{Fore.RED}[worker] dead {key[:8]}: {e}")
                self.failed_workers.add(key)
            finally:
                self.workers.pop(key, None)

        self.workers[key] = {"bot": wbot, "task": asyncio.create_task(runner()), "token": token}

    async def _watch_tokens_file(self):
        path = Path("tokens.txt")
        while not self.is_closed():
            try:
                if path.exists():
                    mtime = path.stat().st_mtime
                    if mtime != self._token_file_mtime:
                        self._token_file_mtime = mtime
                        for t in load_tokens():
                            if t != self.auth_token and t[:20] not in self.workers:
                                await self._start_worker(t)
                                await asyncio.sleep(1.0)
            except Exception:
                pass
            await asyncio.sleep(5)

    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure, commands.MissingRequiredArgument)):
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
    lines = [f"`{k[:12]}` → {getattr(w.get('bot'), 'user', None) or 'starting'}" for k, w in bot.workers.items()]
    await ctx.send("workers:\n" + ("\n".join(lines) or "none — set AUTO_WORKERS=1"), delete_after=12)


@bot.command(name="startworkers")
async def startworkers(ctx):
    await ctx.message.delete()
    if str(ctx.author.id) != os.getenv("MASTER_ID", ""):
        return
    n = 0
    for t in load_tokens():
        if t != bot.auth_token and t[:20] not in bot.workers:
            await bot._start_worker(t)
            n += 1
            await asyncio.sleep(0.8)
    await ctx.send(f"started {n}", delete_after=5)


if __name__ == "__main__":
    if not TOKEN:
        print(f"{Fore.RED}[!] TOKEN missing — set in .env")
        raise SystemExit(1)
    bot.run(TOKEN, log_handler=None)
