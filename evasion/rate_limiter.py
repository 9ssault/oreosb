# evasion/rate_limiter.py
import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Bucket:
    limit: int
    remaining: int
    reset_at: float = 0.0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            if now >= self.reset_at:
                self.remaining = self.limit
            if self.remaining <= 0:
                wait = self.reset_at - now
                if wait > 0:
                    await asyncio.sleep(wait + 0.05)
                self.remaining = self.limit
            self.remaining -= 1

    def update(self, headers: dict):
        self.limit = int(headers.get("X-RateLimit-Limit", self.limit))
        self.remaining = int(headers.get("X-RateLimit-Remaining", self.remaining))
        reset_after = float(headers.get("X-RateLimit-Reset-After", 0))
        self.reset_at = time.monotonic() + reset_after

class RateLimitManager:
    def __init__(self):
        self._buckets: Dict[str, Bucket] = {}
        self._global = Bucket(limit=50, remaining=50)

    async def acquire(self, scope: str = "global"):
        await self._global.acquire()
        if scope != "global":
            if scope not in self._buckets:
                self._buckets[scope] = Bucket(limit=5, remaining=5)
            await self._buckets[scope].acquire()

    def update(self, scope: str, headers):
        h = dict(headers)
        if "X-RateLimit-Bucket" in h:
            bid = h["X-RateLimit-Bucket"]
            if bid not in self._buckets:
                self._buckets[bid] = Bucket(limit=5, remaining=5)
            self._buckets[bid].update(h)
            self._buckets[scope] = self._buckets[bid]

_manager = RateLimitManager()

async def acquire(scope: str = "global"):
    await _manager.acquire(scope)

def update_from_response(scope: str, headers):
    _manager.update(scope, headers)
