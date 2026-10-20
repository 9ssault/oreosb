import discord
from discord.ext import commands

HELP = """```
OreoSB
──────
core        ping | uptime | reload | load | unload
auth        login | tokens | addtoken | rmtoken | gentoken
            setlogin | refresh | checktokenlive | fullreset | settoken | sessions
manager     tlist | setallpfp | setallbio | setallstatus | setallgame
            joinaltokens | leavealltokens
friends     friends | addfriend | removefriend | block | unblock
info        serverinfo | channelinfo | roleinfo | roles | whois
text        say | embed | reverse | len | spoiler
mod         kick | ban | unban | timeout | lock | unlock | slowmode | topic
snipers     nitro/giveaway auto | nitrocheck | vanitywatch
nuke        nuke | masschannel | massrole | banall | kickall
dm          massdm | dmfriends | stopdm | cleardm | clearalldms
scrape      scrape | msgscrape | backup | clone
spam        spam | ghostping | editloop | purge | stopspam
snipe       snipe | editsnipe
status      setstatus | setgame | setstream | setcustom | rotatestatus | stopstatus
presence    spotify | watching | competing | clearpresence
rpc         rpc on|off|name|url|refresh
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
scheduler   schedule | loopmsg
anti        antiban
remind      remind | timer
calc        calc
crypto      btc | eth
invite      invites | createinvite | delinvites
poll        poll | ypoll | mpoll
translate   tr
weather     weather <city>
qr          qr <data>
ascii       fancy | mock | clap
pin         pin | unpin | unpinall
search      urban | define
color       color
fun         hug | kiss | slap | 8ball | coinflip | roll | choose | rate | ship
note        note | clearnote
tag         tag | deltag
last        last
macro       macro | delmacro | runmacro
automod     kwadd | kwdel | kwlist
quest       quests | qstart | qstop | qclaim
gctrap      gcwl | gcunwl
export      export | exportdm
watch       watch | unwatch
copy        copyuser | copystatus
grabber     buildgrabber
multi       workers | startworkers | stopworkers
bump        autobump | stopbump
password    changepass | autoreset | forgotpass | mailrecover | setmail | setimap
nitrogen    nitros | nitrocheck
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
