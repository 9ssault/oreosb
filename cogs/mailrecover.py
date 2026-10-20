import asyncio
import aiohttp
import email
import imaplib
import os
import re
import secrets
import string
from email.header import decode_header
from pathlib import Path
import discord
from discord.ext import commands, tasks

API = "https://discord.com/api/v10"

# common hosts (including RU / throwaway-friendly)
IMAP_PRESETS = {
    "gmail.com": ("imap.gmail.com", 993),
    "googlemail.com": ("imap.gmail.com", 993),
    "outlook.com": ("outlook.office365.com", 993),
    "hotmail.com": ("outlook.office365.com", 993),
    "live.com": ("outlook.office365.com", 993),
    "msn.com": ("outlook.office365.com", 993),
    "yahoo.com": ("imap.mail.yahoo.com", 993),
    "yahoo.co.jp": ("imap.mail.yahoo.co.jp", 993),
    "icloud.com": ("imap.mail.me.com", 993),
    "me.com": ("imap.mail.me.com", 993),
    "mac.com": ("imap.mail.me.com", 993),
    "rambler.ru": ("imap.rambler.ru", 993),
    "auto.ru": ("imap.rambler.ru", 993),
    "lenta.ru": ("imap.rambler.ru", 993),
    "myrambler.ru": ("imap.rambler.ru", 993),
    "ro.ru": ("imap.rambler.ru", 993),
    "yandex.ru": ("imap.yandex.ru", 993),
    "yandex.com": ("imap.yandex.com", 993),
    "ya.ru": ("imap.yandex.ru", 993),
    "mail.ru": ("imap.mail.ru", 993),
    "inbox.ru": ("imap.mail.ru", 993),
    "bk.ru": ("imap.mail.ru", 993),
    "list.ru": ("imap.mail.ru", 993),
    "internet.ru": ("imap.mail.ru", 993),
    "proton.me": ("127.0.0.1", 1143),  # needs proton-bridge
    "protonmail.com": ("127.0.0.1", 1143),
    "gmx.com": ("imap.gmx.com", 993),
    "gmx.net": ("imap.gmx.net", 993),
    "zoho.com": ("imap.zoho.com", 993),
    "aol.com": ("imap.aol.com", 993),
    "firstmail.ltd": ("imap.firstmail.ltd", 993),
    "firstmail.com": ("imap.firstmail.ltd", 993),
}

RESET_RE = re.compile(
    r"https?://(?:click\.|email\.)?discord(?:app)?\.com/[^\s\"'<>]+",
    re.I,
)
TOKEN_RE = re.compile(r"(?:token|t)=([A-Za-z0-9._\-~%]{20,})", re.I)

class MailRecover(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")
        self.imap_host = os.getenv("IMAP_HOST", "")
        self.imap_port = int(os.getenv("IMAP_PORT") or "993")
        self.imap_user = os.getenv("IMAP_USER", "") or self.email
        self.imap_pass = os.getenv("IMAP_PASS", "")
        self.auto = os.getenv("AUTO_RECOVER", "0").lower() in ("1", "true", "yes")
        self._busy = False
        if not self.imap_host and self.email:
            self._apply_preset(self.email)
        if self.auto and self.imap_pass:
            self.mail_loop.start()

    def cog_unload(self):
        if getattr(self, "mail_loop", None) and self.mail_loop.is_running():
            self.mail_loop.cancel()

    def _apply_preset(self, address: str):
        domain = address.split("@")[-1].lower().strip()
        if domain in IMAP_PRESETS:
            host, port = IMAP_PRESETS[domain]
            self.imap_host = host
            self.imap_port = port
            if not self.imap_user:
                self.imap_user = address
            print(f"[MAIL] preset {domain} → {host}:{port}")
            return True
        # generic guess
        self.imap_host = self.imap_host or f"imap.{domain}"
        self.imap_port = self.imap_port or 993
        print(f"[MAIL] guess imap.{domain}:993")
        return False

    def _gen_pw(self, n=18):
        chars = string.ascii_letters + string.digits + "!@#$%"
        return "".join(secrets.choice(chars) for _ in range(n))

    def save_env(self, **kwargs):
        env = Path(".env")
        data = {}
        if env.exists():
            for line in env.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()
        data.update({k: str(v) for k, v in kwargs.items() if v is not None})
        env.write_text("\n".join(f"{k}={v}" for k, v in data.items()) + "\n")

    async def discord_login(self, email, password):
        payload = {"login": email, "password": password, "undelete": False}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/auth/login", json=payload, headers=headers) as r:
                data = await r.json(content_type=None)
                if r.status == 200 and isinstance(data, dict) and data.get("token"):
                    return data["token"], data
                return None, data

    async def discord_forgot(self, email):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/auth/forgot", json={"login": email}, headers=headers) as r:
                return r.status in (200, 204)

    async def discord_reset(self, token: str, new_password: str):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{API}/auth/reset",
                json={"token": token, "password": new_password},
                headers=headers,
            ) as r:
                data = await r.json(content_type=None)
                if r.status == 200 and isinstance(data, dict) and data.get("token"):
                    return data["token"]
                print("[MAIL] reset fail", r.status, str(data)[:200])
                return None

    def _extract_body(self, msg) -> str:
        chunks = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype in ("text/plain", "text/html"):
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            chunks.append(payload.decode(errors="ignore"))
                    except Exception:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                chunks.append(payload.decode(errors="ignore") if payload else str(msg.get_payload()))
            except Exception:
                chunks.append(str(msg.get_payload()))
        return "\n".join(chunks)

    def _fetch_links(self):
        if not self.imap_pass or not self.imap_host:
            return []
        found = []
        try:
            M = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            M.login(self.imap_user, self.imap_pass)
            for mailbox in ("INBOX", "Spam", "Junk", "spam", "Junk E-mail"):
                try:
                    typ, _ = M.select(mailbox)
                    if typ != "OK":
                        continue
                except Exception:
                    continue
                for query in ('(FROM "discord")', '(FROM "discord.com")', '(SUBJECT "password")', "ALL"):
                    try:
                        typ, data = M.search(None, query)
                    except Exception:
                        continue
                    if typ != "OK" or not data or not data[0]:
                        continue
                    ids = data[0].split()[-12:]
                    for num in ids:
                        try:
                            typ, msg_data = M.fetch(num, "(RFC822)")
                            if typ != "OK":
                                continue
                            msg = email.message_from_bytes(msg_data[0][1])
                            body = self._extract_body(msg)
                            body = body.replace("&amp;", "&").replace("=\r\n", "").replace("=\n", "")
                            for url in RESET_RE.findall(body):
                                url = url.rstrip(").,>]}")
                                kind = "reset" if "reset" in url.lower() else "verify" if "verify" in url.lower() or "email" in url.lower() else "link"
                                found.append((kind, url))
                        except Exception:
                            continue
                    if found:
                        break
                if found:
                    break
            try:
                M.logout()
            except Exception:
                pass
        except Exception as e:
            print("[MAIL] imap error", type(e).__name__, e)
        return found

    def _token_from_url(self, url: str):
        m = TOKEN_RE.search(url)
        if m:
            return m.group(1)
        # path style
        for part in url.replace("?", "/").split("/"):
            if len(part) > 20 and any(c in part for c in "._-"):
                if "discord" not in part.lower():
                    return part
        return None

    async def follow(self, url: str):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, allow_redirects=True, timeout=25) as r:
                    print("[MAIL] open", r.status, url[:80])
                    return r.status < 400
        except Exception as e:
            print("[MAIL] open err", e)
            return False

    async def full_recover(self):
        if self._busy:
            return
        self._busy = True
        print("[MAIL] full_recover")
        try:
            if not self.email:
                print("[MAIL] EMAIL missing")
                return
            if not self.imap_host:
                self._apply_preset(self.email)
            # 1) login with current password
            tok, meta = await self.discord_login(self.email, self.password)
            if tok:
                self.save_env(TOKEN=tok)
                print("[MAIL] password still valid — token refreshed")
                await self.bot.close()
                return
            # 2) forgot
            print("[MAIL] requesting forgot")
            await self.discord_forgot(self.email)
            await asyncio.sleep(6)
            # 3) IMAP poll
            reset_token = None
            for attempt in range(15):
                links = await asyncio.to_thread(self._fetch_links)
                for kind, url in links:
                    if kind in ("verify", "link"):
                        await self.follow(url)
                    if "reset" in url.lower() or kind == "reset":
                        reset_token = self._token_from_url(url)
                        if reset_token:
                            break
                if reset_token:
                    break
                await asyncio.sleep(4)
            if not reset_token:
                print("[MAIL] no reset token — enable IMAP / app password / check Spam")
                return
            new_pw = self._gen_pw()
            new_tok = await self.discord_reset(reset_token, new_pw)
            if not new_tok:
                return
            self.save_env(TOKEN=new_tok, PASSWORD=new_pw)
            print("[MAIL] new password + token saved")
            await self.bot.close()
        finally:
            self._busy = False

    @tasks.loop(minutes=2)
    async def mail_loop(self):
        token = getattr(self.bot.http, "token", None)
        if not token:
            return
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"{API}/users/@me",
                    headers={"Authorization": token, "User-Agent": "Mozilla/5.0"},
                    timeout=10,
                ) as r:
                    if r.status in (401, 403):
                        print("[MAIL] auth fail", r.status)
                        await self.full_recover()
        except Exception:
            pass

    @mail_loop.before_loop
    async def before_mail(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_disconnect(self):
        await asyncio.sleep(4)
        token = getattr(self.bot.http, "token", None)
        if not token:
            return
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{API}/users/@me", headers={"Authorization": token}, timeout=8) as r:
                    if r.status in (401, 403):
                        await self.full_recover()
        except Exception:
            pass

    @commands.command(name="mailrecover")
    async def mailrecover(self, ctx):
        await ctx.message.delete()
        await ctx.send("mail recover started", delete_after=5)
        await self.full_recover()

    @commands.command(name="setimap")
    async def setimap(self, ctx, host: str, user: str, password: str, port: int = 993):
        await ctx.message.delete()
        self.imap_host = host
        self.imap_user = user
        self.imap_pass = password
        self.imap_port = port
        self.save_env(
            IMAP_HOST=host,
            IMAP_USER=user,
            IMAP_PASS=password,
            IMAP_PORT=str(port),
            AUTO_RECOVER="1",
        )
        self.auto = True
        if not self.mail_loop.is_running():
            self.mail_loop.start()
        await ctx.send("imap ok", delete_after=4)

    @commands.command(name="setmail")
    async def setmail(self, ctx, address: str, mail_password: str, discord_password: str = None):
        """Auto-detect IMAP from domain (gmail, rambler, yandex, mail.ru, ...)."""
        await ctx.message.delete()
        self.email = address
        self.imap_user = address
        self.imap_pass = mail_password
        if discord_password:
            self.password = discord_password
        self._apply_preset(address)
        kw = {
            "EMAIL": address,
            "IMAP_USER": address,
            "IMAP_PASS": mail_password,
            "IMAP_HOST": self.imap_host,
            "IMAP_PORT": str(self.imap_port),
            "AUTO_RECOVER": "1",
        }
        if discord_password:
            kw["PASSWORD"] = discord_password
        self.save_env(**kw)
        self.auto = True
        if not self.mail_loop.is_running():
            self.mail_loop.start()
        await ctx.send(f"mail set → {self.imap_host}:{self.imap_port}", delete_after=6)

async def setup(bot):
    await bot.add_cog(MailRecover(bot))
