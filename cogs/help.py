import discord
from discord.ext import commands

HELP = """```
OreoSB
──────
core        ping | uptime | reload [cog]
auth        login email:pass | login token <t>
            tokens | addtoken | rmtoken | gentoken
manager     tlist | setallpfp <url> | setallbio <txt>
            setallstatus <st> | setallgame <name>
            joinaltokens <code> | leavealltokens <gid>
snipers     (auto nitro/giveaway) | vanitywatch <c>
nuke        nuke | masschannel | massrole | banall | kickall
dm          massdm <gid> <msg> | dmfriends <msg> | stopdm
scrape      scrape | msgscrape | serverinfo | backup | clone
spam        spam | ghostping | editloop | purge | stopspam
snipe       snipe | editsnipe
status      setstatus | setgame | setstream | setcustom | rotatestatus
token       checktoken | bulkcheck
webhook     wspam | wdel | wdelall
account     setbio | setpfp | leaveall | hypesquad | friendspam
farm        owofarm | dankfarm | mee6farm | stopfarm
voice       vcjoin | vcleave | muteall
react       autoreact [emoji] | massreact <emoji> [n]
emoji       steal [emoji|attach] [name] | emojistealall <gid>
logger      log on|off
afk         afk [text]
util        userinfo | avatar | servericon | firstmessage | id | pingweb
group       gcreate @u... | gleave
advanced    copycat | autoreply | invitejoin | massleave
grabber     buildgrabber <webhook>
multi       workers | startworkers | stopworkers
```"""

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"])
    async def help(self, ctx):
        await ctx.message.delete()
        await ctx.send(HELP, delete_after=90)

async def setup(bot):
    await bot.add_cog(Help(bot))
