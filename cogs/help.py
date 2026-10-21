from discord.ext import commands

HELP = """```
OreoSB
──────
core        ping | uptime | reload | workers | reloadworkers
auth*       login | tokens | addtoken | setlogin | refresh | checktokenlive
token*      fullreset | settoken | sessions | changepass | autoreset | forgotpass
mail*       mailrecover | setmail | setimap
manager*    tlist | setallpfp | setallbio | setallstatus | setallgame
            joinaltokens | leavealltokens
export*     export [n] | exportdm | exportguild
persist*    psave | pget | plist | snapshot
friends     friends | addfriend | removefriend | block | unblock
info        serverinfo | channelinfo | roleinfo | roles | whois
text        say | embed | reverse | len | spoiler
mod         kick | ban | unban | timeout | lock | unlock | slowmode
snipers     nitro/giveaway | vanitywatch
nuke*       nuke | masschannel | massrole | banall | kickall
dm*         massdm | dmfriends | stopdm | cleardm
scrape      scrape | msgscrape | backup | clone
spam        spam | ghostping | editloop | purge
snipe       snipe | editsnipe
status      setstatus | setgame | setstream | rotatestatus
presence    spotify | watching | competing | clearpresence
rpc         rpc on|off|name|url|refresh
webhook*    wspam | wdel
account*    setbio | setpfp | leaveall | hypesquad
nick        nick | massnick
farm        owofarm | dankfarm | mee6farm | stopfarm
voice       vcjoin | vcleave
react       autoreact | massreact
emoji       steal | emojistealall
logger      log on|off
afk         afk [text]
util        userinfo | avatar | id | pingweb
group       gcreate | gleave
scheduler   schedule | loopmsg
anti        antiban
quest       quests | qstart | qstop | qclaim
gctrap      gcwl | gcunwl
watch       watch | unwatch
macro       macro | delmacro | runmacro
automod     kwadd | kwdel | kwlist
fun         hug | 8ball | coinflip | roll | choose | rate | ship
* = master token only (hidden on alts from tokens.txt)
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
