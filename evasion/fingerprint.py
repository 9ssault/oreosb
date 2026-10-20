# evasion/fingerprint.py
import base64
import json
import re
import aiohttp

SUPER_PROPS_ELECTRON = {
    "os": "Windows",
    "browser": "Discord Client",
    "release_channel": "stable",
    "client_version": "1.0.9181",
    "os_version": "10.0.22631",
    "os_arch": "x64",
    "app_arch": "x64",
    "system_locale": "en-US",
    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/138.0.7204.92 Electron/36.2.1 Safari/537.36",
    "browser_version": "138.0.7204.92",
    "client_build_number": 373069,
    "native_build_number": 50430,
    "client_event_source": None,
    "design_id": 0,
}

_build_cache = None

async def fetch_build_number() -> int:
    global _build_cache
    if _build_cache:
        return _build_cache
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("https://discord.com/login") as r:
                html = await r.text()
            scripts = re.findall(r'src="/assets/([a-f0-9]+\.js)"', html)
            for slug in scripts[-6:]:
                async with s.get(f"https://discord.com/assets/{slug}") as r:
                    text = await r.text()
                    m = re.search(r'buildNumber:"(\d+)"', text)
                    if m:
                        _build_cache = int(m.group(1))
                        return _build_cache
    except Exception:
        pass
    return 373069

def encode_props(props: dict) -> str:
    return base64.b64encode(json.dumps(props).encode()).decode()

async def get_super_properties(mode: str = "electron") -> str:
    props = SUPER_PROPS_ELECTRON.copy()
    props["client_build_number"] = await fetch_build_number()
    return encode_props(props)
