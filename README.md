# OreoSB

Python Discord selfbot — modular cogs, multi-token, auto-relogin, mail recover, snipers, nuke, stealth, farms, webhooks.

Selfbots violate Discord ToS. Use only on accounts you accept losing.

## Setup

```bash
git clone https://github.com/9ssault/oreosb.git && cd oreosb
chmod +x setup.sh run.sh
./setup.sh
# edit .env → TOKEN=your_user_token
./run.sh
```

Manual:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # TOKEN=...
.venv/bin/python main.py
```

## Token management

```
.addtoken <token>     validate + append tokens.txt
.rmtoken <partial>    remove matching lines
.tlist                list status of all tokens
.tokens               auth cog list
.bulkcheck            write valid_tokens.txt
.checktoken [token]   inspect one token
```

Multi-token runner:

```bash
# tokens.txt one per line
.venv/bin/python multi_token.py
# .startworkers .stopworkers .workers
```

## Auto-relogin / mail recover

```env
TOKEN=
EMAIL=
PASSWORD=
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=
IMAP_PASS=
AUTO_RECOVER=1
```

`.setlogin` · `.refresh` · `.fullreset` · `.setmail` · `.mailrecover`

## Feature groups

| Area | Commands |
|------|----------|
| Core | ping uptime reload load unload cfg prefix |
| Auth / token | login addtoken rmtoken tlist bulkcheck checktoken settoken sessions |
| Account | setbio setpfp setbanner setpronouns hypesquad me leaveall |
| Friends | friends addfriend removefriend block unblock incoming acceptall |
| Snipers | nitro/giveaway auto nitrocheck vanitywatch |
| Nuke | nuke masschannel massrole banall kickall |
| DM | massdm dmfriends cleardm clearalldms |
| Spam | spam ghostping editloop purge selfpurge ghost |
| Farm | owofarm dankfarm mee6farm customfarm stopfarm |
| Status | setstatus setgame setstream setcustom rotatestatus |
| Mod | kick ban timeout lock unlock slowmode topic |
| Util | userinfo avatar whois guilds snowflake pingweb |
| Stealth | silent selfpurge ghost |
| Multi | workers startworkers stopworkers joinaltokens leavealltokens setall* |

Full list: `.help`

## Layout

```
main.py multi_token.py run.sh setup.sh
config.json .env
cogs/          all modules
evasion/       fingerprint rate_limiter delay headers proxy
tokens.txt     multi-token (gitignored)
```

## Notes

- No stubs — modules load and run
- Humanized delays on mass actions
- Secrets stay in `.env` / `tokens.txt` (gitignored)
