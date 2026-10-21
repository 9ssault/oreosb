from discord.ext import commands

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
            ("mailrecover", "IMAP auto recovery"),
            ("setmail", "Auto IMAP from domain"),
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


def render_page(page: int) -> str:
    total = len(PAGES)
    page = max(1, min(int(page), total))
    title, rows = PAGES[page - 1]
    ESC = "\x1b"
    out = []
    out.append(">")
    out.append(">")
    out.append(f"> *```*ansi")
    out.append(f"> {ESC}[33m{title}{ESC}[0m")
    out.append(f"> ``````ansi")
    for cmd, desc in rows:
        out.append(
            f"> {ESC}[0;37m{cmd:<12} {ESC}[30m| {ESC}[0;34m{desc}{ESC}[0m"
        )
    out.append(f"> ``````ansi")
    out.append(f"> {ESC}[0;37mPage  {ESC}[30m| {ESC}[0;34m{page}/{total}{ESC}[0m")
    out.append(f"> *```*")
    out.append(">")
    nxt = page + 1 if page < total else 1
    out.append(f"> `.help {nxt}` next")
    return "\n".join(out)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"])
    async def help(self, ctx, page: int = 1):
        await ctx.message.delete()
        await ctx.send(render_page(page))


async def setup(bot):
    await bot.add_cog(Help(bot))
