import asyncio
import random

async def human_delay(lo: float = 0.4, hi: float = 2.5):
    await asyncio.sleep(random.uniform(lo, hi))

def jitter(base: float, spread: float = 0.35) -> float:
    return max(0.05, base + random.uniform(-spread, spread))

async def paced(n: int, base: float = 1.2, spread: float = 0.5):
    for i in range(n):
        yield i
        await asyncio.sleep(jitter(base, spread))
