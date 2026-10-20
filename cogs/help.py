import discord
from discord.ext import commands

HELP = """```
OreoSB
──────
core        ping | uptime | reload
auth        login | tokens | addtoken | rmtoken | gentoken
            setlogin | refresh | checktokenlive
manager     tlist | setallpfp | setallbio | setallstatus | setallgame
            joinaltokens | leavealltokens
friends     friends | addfriend | removefriend | block | unblock
info        serverinfo | channelinfo | roleinfo | roles
text        say | embed | reverse | len | spoiler
mod         kick | ban | unban | timeout
snipers     auto nitro/giveaway | vanitywatch
nuke        nuke | masschannel | massrole | banall | kickall
dm          massdm | dmfriends | stopdm | cleardm | clearalldms
scrape      scrape | msgscrape | backup | clone
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
scheduler   schedule | loopmsg
anti        antiban
rpc         rpc on|off|name|url|refresh
quest       quests | qstart | qstop | qclaim
remind      remind <sec> <msg> | timer <sec>
calc        calc <expr>
crypto      btc | eth
invite      invites | createinvite | delinvites
poll        poll | ypoll
translate   tr <lang> <text>
weather     weather <city>
qr          qr <data>
ascii       fancy | mock | clap
pin         pin | unpin | unpinall
search      urban | define
color       color <hex>
fun         hug | kiss | slap | 8ball | coinflip | roll
advanced    copycat | autoreply | invitejoin | massleave
grabber     buildgrabber
tokenreset  fullreset | settoken | sessions
gctrap      gcwl | gcunwl
export      export | exportdm
watch       watch | unwatch
hotreload   reload | load | unload
copy        copyuser | copystatus
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
