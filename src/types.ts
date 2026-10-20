export interface TokenInfo {
  id: string;
  token: string;
  username: string;
  tag: string;
  status: 'online' | 'idle' | 'dnd' | 'offline' | 'dead';
  isWorkerActive: boolean;
  nitroActive: boolean;
  hypesquad: 'Bravery' | 'Brilliance' | 'Balance' | 'None';
  createdDate: string;
}

export interface ConfigData {
  token: string;
  prefix: string;
  log_webhook: string;
  delay: [number, number];
  proxy: string | null;
  captcha_key: string;
  captcha_provider: string;
  nitro_sniper: boolean;
  giveaway_sniper: boolean;
  invite_sniper: boolean;
  max_joins_per_hour: number;
  status_rotate: boolean;
  status_interval: number;
  statuses: string[];
  afk_message: string;
  private_mode: boolean;
  test_guild: string;
  test_channel: string;
}

export interface ImapConfig {
  email: string;
  password: string;
  imap_host: string;
  imap_port: number;
  imap_user: string;
  imap_pass: string;
  auto_recover: boolean;
  lastRecoveryStatus: string;
  recoveryLogs: { id: string; timestamp: string; message: string; type: 'success' | 'error' | 'info' }[];
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR' | 'SNIPE';
  module: string;
  message: string;
  description?: string;
}

export interface CogItem {
  id: string;
  name: string;
  category: 'core' | 'mod' | 'snipers' | 'nuke' | 'dm' | 'scrape' | 'spam' | 'status' | 'voice' | 'util' | 'farm' | 'fun';
  description: string;
  enabled: boolean;
  commands: string[];
}
