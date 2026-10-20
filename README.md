# OreoSB

Python Discord selfbot — modular cogs, multi-token, auto-relogin, mail recover, snipers, nuke tools, RPC, export.

Selfbots violate Discord ToS. Use only on accounts you accept losing.

## Setup (one shot)

```bash
git clone https://github.com/9ssault/oreosb.git
cd oreosb
chmod +x setup.sh run.sh
./setup.sh
# edit .env → TOKEN=your_user_token
./run.sh
```

Manual:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# TOKEN=...
.venv/bin/python main.py
```

Restart loop (needed for auto-relogin to pick new TOKEN):

```bash
./run.sh
```

## .env

| Key | Purpose |
|-----|---------|
| `TOKEN` | User token (required) |
| `PREFIX` | Command prefix (default `.`) |
| `EMAIL` / `PASSWORD` | Auto-relogin when token dies |
| `IMAP_*` + `AUTO_RECOVER=1` | Full password reset via mailbox |
| `CAPTCHA_KEY` | Optional captcha solver |
| `LOG_WEBHOOK` | Optional log webhook |
| `PROXY` | Optional proxy URL |

## Multi-token

```bash
# tokens.txt — one token per line
.venv/bin/python multi_token.py
```

Master commands: `.workers` `.startworkers` `.stopworkers`

## Auto-relogin

When token is 401/403:
1. login with EMAIL/PASSWORD
2. write new TOKEN to `.env`
3. exit → `run.sh` restarts

Commands: `.setlogin email pass` · `.refresh` · `.checktokenlive` · `.fullreset email pass` · `.settoken <token>` · `.sessions`

## Mail recover (password invalid)

```env
EMAIL=you@gmail.com
PASSWORD=discord_password
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=you@gmail.com
IMAP_PASS=app_password
AUTO_RECOVER=1
```

`.setmail email mailpass [discordpass]` · `.setimap host user pass [port]` · `.mailrecover`

## Commands

```
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
poll        poll | ypoll
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
```

## Layout

```
main.py           entry
multi_token.py    multi-account
run.sh / setup.sh easy run + venv
config.json       feature toggles
.env              secrets (gitignored)
cogs/             modules
evasion/          fingerprint + rate limit
tokens.txt        multi-token list (gitignored)
```

## Notes

- No stubs — cogs load and run
- Keep secrets out of git
- Heavy automation gets limited or disabled by Discord
