import asyncio
import aiohttp
import email
import imaplib
import json
import os
import re
import secrets
import string
from email.header import decode_header
from pathlib import Path
import discord
from discord.ext import commands, tasks

API = "https://discord.com/api/v10"
RESET_LINK_RE = re.compile(r"https://(?:click\.)?discord(?:app)?\.com/[^\"'\s]*reset[^\"'\s]*", re.I)
VERIFY_LINK_RE = re.compile(r"https://(?:click\.)?discord(?:app)?\.com/[^\"'\s]*(?:verify|email)[^\"'\s]*", re.I)
TOKEN_IN_URL_RE = re.compile(r"[?&]token=([A-Za-z0-9._\-~]+)")

class MailRecover(commands.Cog):
    """
    Optional full recovery when Discord disables / resets session.
    Requires IMAP access to the same mailbox as Discord EMAIL.
    .env:
      EMAIL=
      PASSWORD=          # Discord password
      IMAP_HOST=imap.gmail.com
      IMAP_PORT=993
      IMAP_USER=         # often same as EMAIL
      IMAP_PASS=         # mailbox password or app password
      AUTO_RECOVER=1
    """

    def __init__(self, bot):
        self.bot = bot
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")
        self.imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.imap_user = os.getenv("IMAP_USER", self.email)
        self.imap_pass = os.getenv("IMAP_PASS", "")
        self.auto = os.getenv("AUTO_RECOVER", "0") in ("1", "true", "yes")
        self._busy = False
        if self.auto and self.imap_pass:
            self.mail_loop.start()

    def cog_unload(self):
        if self.mail_loop.is_running():
            self.mail_loop.cancel()

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
        payload = {"token": token, "password": new_password}
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API}/auth/reset", json=payload, headers=headers) as r:
                data = await r.json(content_type=None)
                if r.status == 200 and isinstance(data, dict) and data.get("token"):
                    return data["token"]
                return None

    def _fetch_discord_links(self):
        """Return list of (kind, url) from recent unseen Discord emails. kind=reset|verify"""
        if not self.imap_pass:
            return []
        out = []
        try:
            M = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            M.login(self.imap_user, self.imap_pass)
            M.select("INBOX")
            # search recent from discord
            typ, data = M.search(None, '(FROM "discord" UNSEEN)')
            if typ != "OK":
                typ, data = M.search(None, '(FROM "discord")')
            ids = data[0].split() if data and data[0] else []
            for num in ids[-8:]:
                typ, msg_data = M.fetch(num, "(RFC822)")
                if typ != "OK":
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype in ("text/plain", "text/html"):
                            try:
                                body += part.get_payload(decode=True).decode(errors="ignore")
                            except Exception:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                    except Exception:
                        body = str(msg.get_payload())
                for m in RESET_LINK_RE.findall(body):
                    out.append(("reset", m.replace("&amp;", "&")))
                for m in VERIFY_LINK_RE.findall(body):
                    out.append(("verify", m.replace("&amp;", "&")))
            M.logout()
        except Exception as e:
            print("[MAIL] imap error", e)
        return out

    async def follow_verify(self, url: str):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, allow_redirects=True, timeout=20) as r:
                    print("[MAIL] verify click", r.status)
                    return r.status < 400
        except Exception as e:
            print("[MAIL] verify err", e)
            return False

    async def full_recover(self):
        if self._busy:
            return
        self._busy = True
        print("[MAIL] full_recover start")
        try:
            if not self.email:
                print("[MAIL] no EMAIL")
                return
            # 1) try normal login first
            tok, meta = await self.discord_login(self.email, self.password)
            if tok:
                self.save_env(TOKEN=tok)
                print("[MAIL] login ok with existing password")
                await self.bot.close()
                return
            # 2) trigger forgot
            print("[MAIL] login failed — sending forgot")
            await self.discord_forgot(self.email)
            await asyncio.sleep(8)
            # 3) poll IMAP for reset link
            reset_token = None
            for attempt in range(12):
                links = await asyncio.to_thread(self._fetch_discord_links)
                for kind, url in links:
                    if kind == "verify":
                        await self.follow_verify(url)
                    if kind == "reset":
                        m = TOKEN_IN_URL_RE.search(url)
                        if m:
                            reset_token = m.group(1)
                            break
                        # sometimes token is path segment
                        parts = url.split("token=")
                        if len(parts) > 1:
                            reset_token = parts[1].split("&")[0]
                            break
                if reset_token:
                    break
                await asyncio.sleep(5)
            if not reset_token:
                print("[MAIL] no reset token in mail — check IMAP settings / app password")
                return
            new_pw = self._gen_pw()
            new_tok = await self.discord_reset(reset_token, new_pw)
            if not new_tok:
                print("[MAIL] auth/reset failed")
                return
            self.save_env(TOKEN=new_tok, PASSWORD=new_pw)
            print("[MAIL] password reset + new token saved — restarting")
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
                async with s.get(f"{API}/users/@me", headers={"Authorization": token}, timeout=10) as r:
                    if r.status == 200:
                        return
                    if r.status in (401, 403):
                        print("[MAIL] token dead/disabled — recover")
                        await self.full_recover()
        except Exception:
            pass

    @mail_loop.before_loop
    async def before_mail(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_disconnect(self):
        await asyncio.sleep(3)
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
        await ctx.send("starting mail recover…", delete_after=5)
        await self.full_recover()

    @commands.command(name="setimap")
    async def setimap(self, ctx, host: str, user: str, password: str, port: int = 993):
        await ctx.message.delete()
        self.imap_host = host
        self.imap_user = user
        self.imap_pass = password
        self.imap_port = port
        self.save_env(IMAP_HOST=host, IMAP_USER=user, IMAP_PASS=password, IMAP_PORT=str(port), AUTO_RECOVER="1")
        self.auto = True
        if not self.mail_loop.is_running():
            self.mail_loop.start()
        await ctx.send("imap saved + AUTO_RECOVER on", delete_after=5)

async def setup(bot):
    await bot.add_cog(MailRecover(bot))
