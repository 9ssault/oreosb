# OreoSB

Python Discord selfbot — modular cogs, multi-token manager, auto-relogin, quests, RPC, traps, export.

> Selfbots violate Discord ToS. Use only on accounts you accept losing.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # or edit .env
# TOKEN=...
# EMAIL=...          # optional, for auto-relogin
# PASSWORD=...
# PREFIX=.
python main.py
```

Restart loop (required for auto-relogin to apply new tokens):

```bash
chmod +x run.sh
./run.sh
# or: while true; do python main.py; sleep 4; done
```

When Discord resets your token, the bot detects it (periodic check + disconnect), logs in with EMAIL/PASSWORD, writes the new TOKEN to `.env`, exits, and `run.sh` brings it back up.

## Config

| Key | Purpose |
|-----|---------|
| `TOKEN` | User token |
| `EMAIL` / `PASSWORD` | Auto-relogin when token dies |
| `PREFIX` | Command prefix (default `.`) |
| `config.json` | Feature toggles, delays, snipers |

## Auto-relogin / token reset

- Background check every 5 minutes
- On dead token + EMAIL/PASSWORD set → login → write new token → exit (loop restarts)
- `.setlogin email password` — save credentials
- `.refresh` — force new token from email/pass
- `.fullreset email password` — logout path + fresh login
- `.settoken <token>` — manual write
- `.checktokenlive` / `.sessions`

## Multi-token

- `tokens.txt` — one token per line
- `python multi_token.py` — master + workers
- `.tlist` `.setallpfp` `.setallbio` `.setallstatus` `.setallgame` `.joinaltokens` `.leavealltokens`
- `.workers` `.startworkers` `.stopworkers`

## Command map

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
snipers     nitro/giveaway auto | vanitywatch
nuke        nuke | masschannel | massrole | banall | kickall
dm          massdm | dmfriends | stopdm | cleardm | clearalldms
scrape      scrape | msgscrape | backup | clone
spam        spam | ghostping | editloop | purge | stopspam
snipe       snipe | editsnipe
status      setstatus | setgame | setstream | setcustom | rotatestatus
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
weather     weather
qr          qr
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
```

## Layout

```
main.py              entry
multi_token.py       multi-account runner
config.json
.env
cogs/                all modules
evasion/             fingerprint + rate limit helpers
tokens.txt
```

## Notes

- No stubs — cogs are meant to run
- Keep secrets out of git (`.env`, tokens)
- Discord will limit/disable accounts that automate heavily
