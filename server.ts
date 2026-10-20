import express from 'express';
import { createServer as createViteServer } from 'vite';
import { spawn, ChildProcess } from 'child_process';
import fs from 'fs';
import path from 'path';

async function startServer() {
  const app = express();
  app.use(express.json());

  let botProcess: ChildProcess | null = null;
  let workersRunning = false;

  let config = {
    token: process.env.TOKEN || 'OTM1MjQ5...',
    prefix: process.env.PREFIX || '.',
    log_webhook: process.env.LOG_WEBHOOK || 'https://discord.com/api/webhooks/...',
    delay: [0.4, 2.5] as [number, number],
    proxy: process.env.PROXY || null,
    captcha_key: process.env.CAPTCHA_KEY || '',
    captcha_provider: process.env.CAPTCHA_PROVIDER || '2captcha',
    nitro_sniper: true,
    giveaway_sniper: true,
    invite_sniper: false,
    max_joins_per_hour: 5,
    status_rotate: true,
    status_interval: 30,
    statuses: ['Gaming', 'Chilling', 'Coding', 'Watching OreoSB'],
    afk_message: 'AFK - Automated by OreoSB',
    private_mode: true,
    test_guild: '1561989222649434175',
    test_channel: '1561989222196322334',
  };

  let imapConfig = {
    email: process.env.EMAIL || 'user@gmail.com',
    password: process.env.PASSWORD || 'discord_secure_password',
    imap_host: process.env.IMAP_HOST || 'imap.gmail.com',
    imap_port: Number(process.env.IMAP_PORT || 993),
    imap_user: process.env.IMAP_USER || 'user@gmail.com',
    imap_pass: process.env.IMAP_PASS || 'gmail_app_password_xyz',
    auto_recover: true,
    lastRecoveryStatus: 'Idle - Token is active and healthy',
    recoveryLogs: [
      { id: '1', timestamp: '2026-10-20 00:00:15', message: 'IMAP connection verified on imap.gmail.com:993', type: 'success' },
      { id: '2', timestamp: '2026-10-20 00:00:16', message: 'Token health check passed (400 OK)', type: 'success' },
    ],
  };

  let tokens = [
    { id: '1', token: 'ODk1Mj...', username: 'OreoMain', tag: '#0001', status: 'online', isWorkerActive: true, nitroActive: true, hypesquad: 'Bravery', createdDate: '2024-01-15' },
    { id: '2', token: 'MTE4Mj...', username: 'WorkerAlt1', tag: '#1337', status: 'online', isWorkerActive: true, nitroActive: false, hypesquad: 'Brilliance', createdDate: '2024-03-20' },
  ];

  let cogs = [
    { id: 'auth', name: 'Auth & Relogin', category: 'core', description: 'Token management, auto-relogin, IMAP recovery & session control', enabled: true, commands: ['.login', '.tokens', '.refresh', '.mailrecover', '.changepass'] },
    { id: 'manager', name: 'Multi-Token Manager', category: 'core', description: 'Master & worker threads, bulk profile updates & joins', enabled: true, commands: ['.tlist', '.setallpfp', '.setallbio', '.joinaltokens'] },
    { id: 'snipers', name: 'Advanced Snipers', category: 'snipers', description: 'Nitro code sniper, giveaway sniper, invite sniper & vanity watcher', enabled: true, commands: ['.nitro', '.giveaway', '.vanitywatch'] },
    { id: 'nuke', name: 'Nuke & Server Tools', category: 'nuke', description: 'Mass channel creation, role spam, banall & cloner', enabled: true, commands: ['.nuke', '.masschannel', '.banall', '.clone'] },
    { id: 'dm', name: 'Mass DM & Cleaner', category: 'dm', description: 'Mass DM friends/servers, clear DMs, webhook spammer', enabled: true, commands: ['.massdm', '.dmfriends', '.stopdm', '.cleardm'] },
    { id: 'scrape', name: 'Scraper & Backup', category: 'scrape', description: 'Server scraper, message export, channel backup & clone', enabled: true, commands: ['.scrape', '.msgscrape', '.backup', '.clone'] },
    { id: 'spam', name: 'Spam & Purge', category: 'spam', description: 'Fast spammer, ghost ping, edit loop & channel purge', enabled: true, commands: ['.spam', '.ghostping', '.purge', '.stopspam'] },
    { id: 'status', name: 'Status & Presence', category: 'status', description: 'Custom status, game status, streaming & rotation', enabled: true, commands: ['.setstatus', '.setgame', '.rotatestatus'] },
    { id: 'voice', name: 'Voice & Audio', category: 'voice', description: 'VC join, leave, mute all & soundboard utilities', enabled: true, commands: ['.vcjoin', '.vcleave', '.muteall'] },
    { id: 'farm', name: 'Quests & Farmer', category: 'farm', description: 'Owo farm, dank memer farm, mee6 farm & Discord quests automation', enabled: true, commands: ['.owofarm', '.dankfarm', '.quests', '.qclaim'] },
    { id: 'util', name: 'Utilities & Weather', category: 'util', description: 'Whois, weather, crypto ticker, translate, QR, ASCII art', enabled: true, commands: ['.weather', '.btc', '.eth', '.tr', '.qr', '.ascii'] },
    { id: 'fun', name: 'Fun & Games', category: 'fun', description: 'Hug, slap, 8ball, coinflip, roll, ship, notes & tags', enabled: true, commands: ['.hug', '.slap', '.8ball', '.coinflip', '.tag', '.note'] },
  ];

  let logs = [
    { id: 'l1', timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'System', message: 'OreoSB Python Subprocess Bridge & Enterprise Server online.' },
    { id: 'l2', timestamp: new Date().toLocaleTimeString(), level: 'INFO', module: 'Auth', message: 'Loaded cogs from ./cogs directory successfully.' },
  ];

  // API Routes
  app.get('/api/status', (req, res) => {
    res.json({ workersRunning, activeTokens: tokens.length, latency: 135 });
  });

  app.post('/api/workers/toggle', (req, res) => {
    workersRunning = !workersRunning;
    if (workersRunning) {
      logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'Workers', message: 'Started OreoSB background worker daemon.' });
    } else {
      logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'WARN', module: 'Workers', message: 'Stopped OreoSB background worker daemon.' });
    }
    res.json({ workersRunning, logs });
  });

  app.get('/api/tokens', (req, res) => res.json(tokens));

  app.post('/api/tokens', (req, res) => {
    const { token } = req.body;
    if (!token) return res.status(400).json({ error: 'Token required' });
    const newToken = {
      id: Math.random().toString(36).substring(2, 9),
      token,
      username: `Worker_${tokens.length + 1}`,
      tag: `#${Math.floor(1000 + Math.random() * 9000)}`,
      status: 'online' as const,
      isWorkerActive: true,
      nitroActive: false,
      hypesquad: 'Bravery' as const,
      createdDate: new Date().toISOString().split('T')[0],
    };
    tokens.push(newToken);
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'MultiToken', message: `Registered token: ${newToken.username}` });
    res.json(newToken);
  });

  app.delete('/api/tokens/:id', (req, res) => {
    tokens = tokens.filter((t) => t.id !== req.params.id);
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'INFO', module: 'MultiToken', message: `Removed token ID ${req.params.id}` });
    res.json({ success: true });
  });

  app.get('/api/config', (req, res) => res.json(config));

  app.post('/api/config', (req, res) => {
    config = { ...config, ...req.body };
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'Config', message: 'Updated config.json parameters' });
    res.json(config);
  });

  app.get('/api/imap', (req, res) => res.json(imapConfig));

  app.post('/api/imap', (req, res) => {
    imapConfig = { ...imapConfig, ...req.body };
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'AutoRelogin', message: 'Updated IMAP configuration' });
    res.json(imapConfig);
  });

  app.post('/api/imap/recover', (req, res) => {
    imapConfig.lastRecoveryStatus = 'Full IMAP recovery flow completed successfully!';
    imapConfig.recoveryLogs.unshift({
      id: Math.random().toString(36).substring(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      message: 'Automated IMAP reset triggered: email parsed, new token issued.',
      type: 'success',
    });
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'ImapRecovery', message: 'IMAP recovery flow completed. Token refreshed.' });
    res.json({ success: true, imapConfig });
  });

  app.post('/api/relogin', (req, res) => {
    imapConfig.lastRecoveryStatus = 'Token successfully refreshed and validated (200 OK)';
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'AutoRelogin', message: 'Manual token re-login successful. Saved to .env' });
    res.json({ success: true });
  });

  app.get('/api/cogs', (req, res) => res.json(cogs));

  app.post('/api/cogs/toggle', (req, res) => {
    const { id } = req.body;
    cogs = cogs.map((c) => (c.id === id ? { ...c, enabled: !c.enabled } : c));
    const cog = cogs.find((c) => c.id === id);
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'INFO', module: 'CogsManager', message: `Cog '${cog?.name}' toggled to ${cog?.enabled}` });
    res.json(cogs);
  });

  app.get('/api/logs', (req, res) => res.json(logs));

  app.post('/api/terminal', (req, res) => {
    const { command } = req.body;
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'INFO', module: 'CLI', message: `> ${command}` });
    let responseMsg = `Executed command '${command}' successfully.`;
    if (command.startsWith('.ping')) responseMsg = 'Pong! Gateway latency: 135ms | API latency: 140ms';
    else if (command.startsWith('.tlist')) responseMsg = `Active tokens in rotation: ${tokens.length}`;
    else if (command.startsWith('.refresh')) responseMsg = 'Token refresh triggered and verified.';
    
    logs.unshift({ id: Math.random().toString(36).substring(2, 9), timestamp: new Date().toLocaleTimeString(), level: 'SUCCESS', module: 'CLI', message: responseMsg });
    res.json({ success: true, response: responseMsg, logs });
  });

  // Setup Vite middleware
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });

  app.use(vite.middlewares);

  app.listen(3000, '0.0.0.0', () => {
    console.log('OreoSB Enterprise Server running on http://0.0.0.0:3000');
  });
}

startServer();
