import discord
from discord.ext import commands

HELP = """```
OreoSB
──────
core        ping | uptime | reload
auth        login | tokens | addtoken | rmtoken | gentoken
manager     tlist | setallpfp | setallbio | setallstatus | setallgame
            joinaltokens | leavealltokens
friends     friends | addfriend | removefriend | block | unblock
snipers     auto nitro/giveaway | vanitywatch
nuke        nuke | masschannel | massrole | banall | kickall
dm          massdm | dmfriends | stopdm | cleardm | clearalldms
scrape      scrape | msgscrape | serverinfo | backup | clone
spam        spam | ghostping | editloop | purge | stopspam
snipe       snipe | editsnipe
status      setstatus | setgame | setstream | setcustom | rotatestatus
presence    spotify | watching | competing | clearpresence
token       checktoken | bulkcheck
webhook     wspam | wdel | wdelall
account     setbio | setpfp | leaveall | hypesquad | friendspam
nick        nick | massnick
farm        owofarm | dankfarm | mee6farm | stopfarm
voice       vcjoin | vcleave | muteall
react       autoreact | massreact
emoji       steal | emojistealall
logger      log on|off
afk         afk [text]
util        userinfo | avatar | servericon | firstmessage | id | pingweb
group       gcreate | gleave
scheduler   schedule <sec> <msg> | loopmsg
anti        antiban on|off
advanced    copycat | autoreply | invitejoin | massleave
grabber     buildgrabber
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
