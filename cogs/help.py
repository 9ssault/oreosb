# cogs/help.py
import discord
from discord.ext import commands

HELP = """
```
OreoSB
──────

core
  ping            latency
  uptime          uptime
  reload [cog]    reload cog(s)

auth
  login email:pass
  login token <tok>
  tokens          list managed
  addtoken <tok>
  rmtoken <part>
  gentoken

manager
  tlist                 list tokens + status
  setallpfp <url>       set pfp on all tokens
  setallbio <text>      set bio on all
  setallstatus <st>     online/dnd/idle/invisible
  setallgame <name>     set playing on all
  joinaltokens <code>   join invite with all
  leavealltokens <gid>  leave guild with all

snipers
  (auto nitro + giveaway)
  vanitywatch <code>
  vanityunwatch <code>

nuke
  nuke
  masschannel [n] [name]
  massrole [n] [name]
  banall
  kickall

dm
  massdm <gid> <msg>
  dmfriends <msg>
  stopdm

scrape
  scrape [gid] [json|csv]
  msgscrape [cid] [limit]
  serverinfo [gid]
  backup [gid]
  clone <src> [tgt]

spam
  spam <count> <delay> <msg>
  ghostping @user
  editloop <n> <msg|msg>
  purge [n]
  stopspam

snipe
  snipe
  editsnipe

status
  setstatus <st>
  setgame <name>
  setstream <url> [name]
  setcustom <text>
  rotatestatus [sec]
  stopstatus

token
  checktoken <tok>
  bulkcheck

webhook
  wspam <url> <n> <delay> <msg>
  wdel <url>
  wdelall

account
  setbio <text>
  setpfp [url]
  leaveall [delay]
  hypesquad <1-3>
  friendspam <user> [n]

farm
  owofarm [cid]
  dankfarm [cid]
  mee6farm [delay]
  stopfarm [name]

voice
  vcjoin [cid]
  vcleave
  muteall

advanced
  copycat [@user]
  autoreply [text]
  serverclone [id]
  invitejoin <code>
  massleave [delay]

grabber
  buildgrabber <webhook>

multi
  workers
  startworkers
  stopworkers
```
"""

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"])
    async def help(self, ctx):
        await ctx.message.delete()
        # split if needed
        if len(HELP) > 1900:
            parts = [HELP[i:i+1900] for i in range(0, len(HELP), 1900)]
            for p in parts:
                await ctx.send(p, delete_after=60)
        else:
            await ctx.send(HELP, delete_after=60)

async def setup(bot):
    await bot.add_cog(Help(bot))
