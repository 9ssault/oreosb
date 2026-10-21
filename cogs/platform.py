import os
from discord.ext import commands

# gateway platform presets (IDENTIFY properties)
PRESETS = {
    "desktop": {"$os": "Windows", "$browser": "Discord Client", "$device": "Desktop"},
    "web": {"$os": "Windows", "$browser": "Chrome", "$device": ""},
    "android": {"$os": "Android", "$browser": "Discord Android", "$device": "Android"},
    "ios": {"$os": "iOS", "$browser": "Discord iOS", "$device": "iPhone"},
    "mobile": {"$os": "Android", "$browser": "Discord Android", "$device": "Android"},
    "vr": {"$os": "Android", "$browser": "Discord VR", "$device": "Discord VR"},
    "xbox": {"$os": "Windows", "$browser": "Discord Embedded", "$device": "Xbox"},
}


def current_platform() -> str:
    return (os.getenv("PLATFORM") or "desktop").lower().strip()


def apply_gateway_patch(platform: str = None):
    """Monkeypatch IDENTIFY properties before login."""
    platform = (platform or current_platform()).lower()
    props = PRESETS.get(platform) or PRESETS["desktop"]
    try:
        from discord.gateway import DiscordWebSocket
    except Exception as e:
        print(f"[platform] no gateway module: {e}")
        return props

    if getattr(DiscordWebSocket, "_oreosb_patched", False):
        DiscordWebSocket._oreosb_props = props
        return props

    original = DiscordWebSocket.identify

    async def identify_patched(self):
        # call original path but force properties if possible
        try:
            payload = {
                "op": self.IDENTIFY,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": props["$os"],
                        "$browser": props["$browser"],
                        "$device": props["$device"],
                    },
                    "compress": True,
                    "large_threshold": 250,
                },
            }
            # presence block optional
            if getattr(self, "presence", None) is not None:
                payload["d"]["presence"] = self.presence
            await self.send_as_json(payload)
        except Exception:
            await original(self)

    DiscordWebSocket.identify = identify_patched
    DiscordWebSocket._oreosb_patched = True
    DiscordWebSocket._oreosb_props = props
    return props


class Platform(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.platform = current_platform()

    @commands.command(name="platform")
    async def platform_cmd(self, ctx, name: str = None):
        await ctx.message.delete()
        if not name:
            await ctx.send(
                f"platform `{self.platform}` | presets: {', '.join(PRESETS)}\n"
                f"set via `.platform <name>` then restart (IDENTIFY is at login)",
                delete_after=12,
            )
            return
        name = name.lower().strip()
        if name not in PRESETS:
            await ctx.send(f"unknown — {', '.join(PRESETS)}", delete_after=6)
            return
        self.platform = name
        # persist in .env
        path = "data"
        os.makedirs(path, exist_ok=True)
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            for line in open(env_path, encoding="utf-8", errors="ignore"):
                if not line.startswith("PLATFORM="):
                    lines.append(line.rstrip("\n"))
        lines.append(f"PLATFORM={name}")
        open(env_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        await ctx.send(f"PLATFORM={name} saved — restart bot to apply", delete_after=8)


async def setup(bot):
    await bot.add_cog(Platform(bot))
