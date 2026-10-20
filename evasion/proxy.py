import os
from typing import Optional

def proxy_url() -> Optional[str]:
    return (os.getenv("PROXY") or "").strip() or None

def aiohttp_proxy() -> Optional[str]:
    return proxy_url()

def httpx_proxy() -> Optional[dict]:
    p = proxy_url()
    if not p:
        return None
    return {"http://": p, "https://": p}
