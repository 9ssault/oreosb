"""Shared helpers: owner gate, token store, persistence."""
from __future__ import annotations

import json
import os
from pathlib import Path
from functools import wraps
from typing import Callable, List, Optional

import discord
from discord.ext import commands

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TOKENS_FILE = Path("tokens.txt")
STATE_FILE = DATA_DIR / "state.json"
PERSIST_FILE = DATA_DIR / "persist.json"


def load_tokens() -> List[str]:
    if not TOKENS_FILE.exists():
        return []
    out = []
    for line in TOKENS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        t = line.strip()
        if t and not t.startswith("#"):
            out.append(t)
    return out


def save_tokens(tokens: List[str]) -> None:
    TOKENS_FILE.write_text("\n".join(tokens) + ("\n" if tokens else ""), encoding="utf-8")


def add_token(token: str) -> None:
    toks = load_tokens()
    if token not in toks:
        toks.append(token)
        save_tokens(toks)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(data: dict) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_persist() -> dict:
    if PERSIST_FILE.exists():
        try:
            return json.loads(PERSIST_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_persist(data: dict) -> None:
    PERSIST_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def master_id() -> Optional[int]:
    """Discord user id of the main TOKEN account (set after ready)."""
    try:
        return int(os.getenv("MASTER_ID") or "0") or None
    except Exception:
        return None


def is_master_ctx(ctx: commands.Context) -> bool:
    mid = master_id()
    if mid:
        return ctx.author.id == mid
    # fallback: only the bot user itself (selfbot)
    return ctx.author.id == ctx.bot.user.id


def owner_only():
    """Critical commands: only master account may run them."""

    def deco(func: Callable):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if not is_master_ctx(ctx):
                return
            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return deco


def owner_check():
    async def pred(ctx: commands.Context) -> bool:
        return is_master_ctx(ctx)

    return commands.check(pred)
