import discord
from discord.ext import commands

# ANSI help pages (Discord ansi codeblock)
# colors: 30 black | 31 red | 32 green | 33 yellow | 34 blue | 35 magenta | 36 cyan | 37 white

PAGES = [
    (
        "Utility",
        [
            ("afk", "Set AFK status"),
            ("banner", "Show user banner"),
            ("closealldms", "Close all DMs"),
            ("count", "Count to a number"),
            ("define", "Urban Dictionary"),
            ("export", "Export channel history"),
            ("exportdm", "Export a DM"),
            ("exportguild", "Export guild messages"),
            ("firstmessage", "Jump to first message"),
            ("help", "This menu"),
            ("id", "Copy an ID"),
            ("last", "Last message from user"),
            ("note", "Save a note"),
            ("ping", "Latency"),
            ("remind", "Set a reminder"),
            ("snipe", "Snipe deleted message"),
            ("editsnipe", "Snipe edited message"),
            ("uptime", "Bot uptime"),
            ("userinfo", "User info"),
            ("avatar", "User avatar"),
            ("weather", "Weather lookup"),
        ],
    ),
    (
        "Moderation",
        [
            ("ban", "Ban a member"),
            ("kick", "Kick a member"),
            ("timeout", "Timeout a member"),
            ("unban", "Unban a user"),
            ("lock", "Lock channel"),
            ("unlock", "Unlock channel"),
            ("slowmode", "Set slowmode"),
            ("purge", "Purge messages"),
            ("nick", "Change nickname"),
            ("massnick", "Mass nickname"),
            ("muteall", "Server-mute VC members"),
            ("unmuteall", "Unmute VC members"),
        ],
    ),
    (
        "Tokens / Auth",
        [
            ("login", "Login email:pass or token"),
            ("tokens", "List managed tokens"),
            ("addtoken", "Add token"),
            ("tlist", "Validate tokens.txt"),
            ("setlogin", "Save email/password"),
            ("refresh", "Refresh token via login"),
            ("fullreset", "Full session reset"),
            ("settoken", "Write token to .env"),
            ("sessions", "List sessions"),
            ("checktokenlive", "Validate current token"),
            ("changepass", "Change password"),
            ("autoreset", "Rotate password"),
            ("forgotpass", "Trigger forgot email"),
            ("mailrecover", "IMAP auto recovery"),
            ("setmail", "Auto IMAP from domain"),
            ("setimap", "Manual IMAP settings"),
            ("workers", "List workers"),
            ("startworkers", "Start tokens.txt workers"),
        ],
    ),
    (
        "Manager / Mass",
        [
            ("setallpfp", "Set all tokens pfp"),
            ("setallbio", "Set all tokens bio"),
            ("setallstatus", "Set all status"),
            ("setallgame", "Set all game"),
            ("joinaltokens", "All tokens join invite"),
            ("leavealltokens", "All tokens leave guild"),
            ("massdm", "Mass DM"),
            ("dmfriends", "DM all friends"),
            ("stopdm", "Stop mass DM"),
            ("nuke", "Nuke tools"),
            ("scrape", "Scrape members"),
            ("clone", "Clone server"),
            ("backup", "Backup guild"),
        ],
    ),
    (
        "Presence / VC / Quest",
        [
            ("rpc", "Stream presence on|off|name|url"),
            ("platform", "Spoof desktop|web|android|ios|vr"),
            ("setstatus", "online|idle|dnd|invisible"),
            ("setgame", "Playing status"),
            ("setstream", "Streaming status"),
            ("setcustom", "Custom status"),
            ("spotify", "Listening status"),
            ("watching", "Watching status"),
            ("clearpresence", "Clear activity"),
            ("vcjoin", "Join voice"),
            ("vcleave", "Leave voice"),
            ("vcmove", "Move voice channel"),
            ("vcmute", "Self mute"),
            ("vcdeaf", "Self deaf"),
            ("vclist", "List voice channels"),
            ("quests", "List Discord quests"),
            ("qstart", "Run quest engine"),
            ("qstop", "Stop quests"),
            ("qclaim", "Claim quest rewards"),
        ],
    ),
    (
        "Auto / Social",
        [
            ("autojoin", "Save+join invite code"),
            ("joinall", "Join saved invites"),
            ("autoleave", "Mark guild autoleave"),
            ("leaveguild", "Leave a guild"),
            ("leaveallguilds", "Leave all guilds"),
            ("gcwl", "GC trap whitelist"),
            ("gcunwl", "Remove GC whitelist"),
            ("watch", "Watch user presence"),
            ("unwatch", "Stop watch"),
            ("kwadd", "Automod keyword"),
            ("kwdel", "Remove keyword"),
            ("autoreact", "Auto react"),
            ("friends", "List friends"),
            ("addfriend", "Add friend"),
            ("block", "Block user"),
            ("macro", "Save macro"),
            ("runmacro", "Run macro"),
        ],
    ),
    (
        "Fun / Extra",
        [
            ("hug", "Hug someone"),
            ("kiss", "Kiss"),
            ("slap", "Slap"),
            ("8ball", "Magic 8ball"),
            ("coinflip", "Coin flip"),
            ("roll", "Roll dice"),
            ("choose", "Choose options"),
            ("rate", "Rate something"),
            ("ship", "Ship two users"),
            ("ascii", "ASCII text"),
            ("mock", "MoCk TeXt"),
            ("clap", "clap text"),
            ("poll", "Create poll"),
            ("qr", "QR code"),
            ("calc", "Calculator"),
            ("btc", "BTC price"),
            ("eth", "ETH price"),
            ("translate", "Translate text"),
            ("urban", "Urban define"),
        ],
    ),
]


def _ansi_page(title: str, rows: list, page: int, total: int) -> str:
    lines = ["```ansi", f"\u001b[33m{title}\u001b[0m", "```"]
    body = ["```ansi"]
    for cmd, desc in rows:
        body.append(
            f"\u001b[0;37m{cmd:<12} \u001b[30m| \u001b[0;34m{desc}\u001b[0m"
        )
    body.append("```")
    foot = [
        "```ansi",
        f"\u001b[0;37mPage  \u001b[30m| \u001b[0;34m{page}/{total}\u001b[0m",
        "```",
    ]
    return "\n".join(lines + body + foot)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"])
    async def help(self, ctx, page: int = 1):
        await ctx.message.delete()
        total = len(PAGES)
        page = max(1, min(page, total))
        title, rows = PAGES[page - 1]
        text = _ansi_page(title, rows, page, total)
        msg = await ctx.send(text)

        # simple reaction pager if we can add reactions
        try:
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")
        except Exception:
            return

        def check(reaction, user):
            return (
                user.id == ctx.author.id
                and reaction.message.id == msg.id
                and str(reaction.emoji) in ("⬅️", "➡️")
            )

        import asyncio

        current = page
        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
            except asyncio.TimeoutError:
                break
            try:
                await msg.remove_reaction(reaction.emoji, user)
            except Exception:
                pass
            if str(reaction.emoji) == "➡️":
                current = current + 1 if current < total else 1
            else:
                current = current - 1 if current > 1 else total
            title, rows = PAGES[current - 1]
            try:
                await msg.edit(content=_ansi_page(title, rows, current, total))
            except Exception:
                break

    @commands.command(name="helplist")
    async def helplist(self, ctx):
        """Plain text fallback."""
        await ctx.message.delete()
        lines = [f"**{t}** — {len(r)} cmds" for t, r in PAGES]
        await ctx.send("\n".join(lines) + f"\nuse `.help [1-{len(PAGES)}]`", delete_after=20)


async def setup(bot):
    await bot.add_cog(Help(bot))
