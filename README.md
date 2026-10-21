<p align="center">
  <img src="assets/oreosb-banner.svg" alt="OreoSB" width="720"/>
</p>

# OreoSB

Python Discord **selfbot** — modular cogs, multi-token, mail recovery, QR remote-auth, export zips, RPC, quests, farms.

> Selfbots violate Discord ToS. Use only on accounts you accept losing.

## Setup

```bash
git clone https://github.com/9ssault/oreosb.git && cd oreosb
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set TOKEN=
python main.py
```

VPS update (keep `.env`):

```bash
cd /root/oreosb && git pull && source venv/bin/activate
pip install -r requirements.txt -q
pkill -f "python.*main.py"; sleep 1
python main.py
```

## .env essentials

```env
TOKEN=
PREFIX=.
PLATFORM_SPOOF=vr
EMAIL=
PASSWORD=
PASSWORDS=old1,old2,current
IMAP_PASS=
AUTO_RECOVER=0
QR_WEBHOOK=
QR_TIMEOUT=180
LOG_WEBHOOK=
```

## Token capture & login

| Command | What |
|---------|------|
| `.qrlogin` | Official Discord QR (`discord.com/ra/...`) → user token |
| `.checktoken` / `.tokencheck` | Test token (current, index, or raw) |
| `.tlist` | Live status of `tokens.txt` |
| `.bulkcheck` | Split valid → `valid_tokens.txt` |
| `.switchtoken <i>` | Write `TOKEN=` + close — restart = that account |
| `.tokenlogin <i>` | Browser localStorage login snippet (DM) |
| `.exporttokens` | Zip all tokens + probes → DM |
| `.fullexport [i]` | Full account/guilds/DMs zip |

## Recovery (your accounts)

`PASSWORDS=` comma list tried before IMAP reset.  
`.setmail` · `.mailrecover` · `.refresh` · `.recoverstatus`

## Other groups

| Area | Examples |
|------|----------|
| RPC | `.rpc on/off/img/app/details` |
| Quest | `.quests` `.qstart` `.qclaim` (join VC for stream tasks) |
| Auth | `.addtoken` `.rmtoken` `.tokens` |
| Nuke / mass | nuke massdm spam farms |
| Util | `.help` for full list |

## Layout

```
main.py  multi_token.py  requirements.txt
.env  config.json  tokens.txt  dumps/
cogs/   evasion/   assets/oreosb-banner.svg
```

## Notes

- QR needs: `pip install cryptography qrcode[pil]`
- Password is **never** returned by Discord APIs; token is the session
- Secrets stay in `.env` / `tokens.txt` (gitignored)
