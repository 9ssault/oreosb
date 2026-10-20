import base64
import json

UA_FIREFOX = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) "
    "Gecko/20100101 Firefox/136.0"
)
UA_ELECTRON = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) discord/1.0.9181 Chrome/138.0.7204.92 "
    "Electron/36.2.1 Safari/537.36"
)

def browser_headers(token: str = None, extra: dict = None) -> dict:
    h = {
        "Content-Type": "application/json",
        "User-Agent": UA_FIREFOX,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
    }
    if token:
        h["Authorization"] = token
    if extra:
        h.update(extra)
    return h

def electron_headers(token: str = None, super_props: str = None, extra: dict = None) -> dict:
    h = {
        "Content-Type": "application/json",
        "User-Agent": UA_ELECTRON,
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
    }
    if super_props:
        h["X-Super-Properties"] = super_props
    if token:
        h["Authorization"] = token
    if extra:
        h.update(extra)
    return h

def encode_locale_props(build: int = 373069) -> str:
    props = {
        "os": "Windows",
        "browser": "Discord Client",
        "release_channel": "stable",
        "client_version": "1.0.9181",
        "os_version": "10.0.22631",
        "os_arch": "x64",
        "app_arch": "x64",
        "system_locale": "en-US",
        "browser_user_agent": UA_ELECTRON,
        "browser_version": "138.0.7204.92",
        "client_build_number": build,
        "native_build_number": 50430,
        "client_event_source": None,
        "design_id": 0,
    }
    return base64.b64encode(json.dumps(props, separators=(",", ":")).encode()).decode()
