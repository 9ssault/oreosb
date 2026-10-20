# OreoSB

full-stack discord selfbot — python / discord.py-self

## features

- nitro + giveaway + invite snipers
- guild nuker / mass ban / kick / channel+role spam
- mass dm (guild + friends)
- member / message / server scrapers
- token checker + bulk validator
- webhook spam + mass delete
- status / rich presence rotator
- owo / dank / mee6 farmers
- voice join / muteall
- account tools (bio, pfp, leaveall, hypesquad, friendspam)
- grabber builder (token stealer stub)
- anti-detection (live build number, rate buckets, human delays)

## setup

```bash
git clone https://github.com/9ssault/oreosb
cd oreosb
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on windows
pip install -r requirements.txt
cp .env.example .env
# edit .env → put your user token
python main.py
```

## config

edit `config.json` or `.env`

| key | desc |
|-----|------|
| token | user token |
| prefix | command prefix (default `.`) |
| nitro_sniper | bool |
| giveaway_sniper | bool |
| status_rotate | bool |
| statuses | list of custom statuses |

## commands (prefix `.`)

| cmd | what |
|-----|------|
| ping / uptime / reload | core |
| nuke / masschannel / massrole / banall / kickall | nuke |
| massdm / stopdm / dmfriends | dm |
| scrape / msgscrape / serverinfo | scrape |
| spam / ghostping / editloop / purge / stopspam | spam |
| setstatus / setgame / setstream / setcustom / rotatestatus | presence |
| checktoken / bulkcheck | tokens |
| wspam / wdel / wdelall | webhooks |
| setbio / setpfp / leaveall / hypesquad / friendspam | account |
| owofarm / dankfarm / mee6farm / stopfarm | farm |
| vcjoin / vcleave / muteall | voice |
| buildgrabber | stealer |

## notes

- put extra tokens in `tokens.txt` for bulkcheck
- grabber output → `grabber.py` (compile with pyinstaller)
- private_mode in config hides command echoes when possible

---

MADE BY ".LOLIFLOP." — ON DISCORD – CONTACT ME FOR ANY PROBLEMS.

## auth & token management (new)

| cmd | what |
|-----|------|
| login email:pass | login via email+password, saves token |
| login token <tok> | validate + save token |
| tokens | list managed tokens status |
| addtoken <tok> | add to tokens.txt |
| rmtoken <partial> | remove matching |
| gentoken | generate realistic fake token pattern |

## advanced

| cmd | what |
|-----|------|
| copycat @user | mirror messages |
| autoreply <text> | set auto reply |
| serverclone [id] | dump guild structure |
| invitejoin <code> | join invite |
| massleave | leave all guilds |
