import React, { createContext, useContext, useState, useEffect } from 'react';
import { TokenInfo, ConfigData, ImapConfig, LogEntry, CogItem } from '../types';

interface OreoContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  tokens: TokenInfo[];
  setTokens: React.Dispatch<React.SetStateAction<TokenInfo[]>>;
  config: ConfigData;
  setConfig: React.Dispatch<React.SetStateAction<ConfigData>>;
  imapConfig: ImapConfig;
  setImapConfig: React.Dispatch<React.SetStateAction<ImapConfig>>;
  logs: LogEntry[];
  addLog: (level: LogEntry['level'], module: string, message: string) => void;
  clearLogs: () => void;
  cogs: CogItem[];
  toggleCog: (id: string) => Promise<void>;
  workersRunning: boolean;
  setWorkersRunning: React.Dispatch<React.SetStateAction<boolean>>;
  triggerAutoRelogin: () => Promise<void>;
  triggerImapRecovery: () => Promise<void>;
  activeCommandCount: number;
}

const OreoContext = createContext<OreoContextType | undefined>(undefined);

export const OreoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [tokens, setTokens] = useState<TokenInfo[]>([]);
  const [config, setConfig] = useState<ConfigData>({
    token: '',
    prefix: '.',
    log_webhook: '',
    delay: [0.4, 2.5],
    proxy: null,
    captcha_key: '',
    captcha_provider: '2captcha',
    nitro_sniper: true,
    giveaway_sniper: true,
    invite_sniper: false,
    max_joins_per_hour: 5,
    status_rotate: true,
    status_interval: 30,
    statuses: [],
    afk_message: '',
    private_mode: true,
    test_guild: '',
    test_channel: '',
  });
  const [imapConfig, setImapConfig] = useState<ImapConfig>({
    email: '',
    password: '',
    imap_host: 'imap.gmail.com',
    imap_port: 993,
    imap_user: '',
    imap_pass: '',
    auto_recover: true,
    lastRecoveryStatus: 'Loading...',
    recoveryLogs: [],
  });
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [cogs, setCogs] = useState<CogItem[]>([]);
  const [workersRunning, setWorkersRunning] = useState<boolean>(true);
  const [activeCommandCount, setActiveCommandCount] = useState<number>(42);

  // Fetch initial state from backend API
  useEffect(() => {
    fetch('/api/tokens')
      .then((res) => res.json())
      .then((data) => setTokens(data))
      .catch((err) => console.error('Failed to load tokens:', err));

    fetch('/api/config')
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch((err) => console.error('Failed to load config:', err));

    fetch('/api/imap')
      .then((res) => res.json())
      .then((data) => setImapConfig(data))
      .catch((err) => console.error('Failed to load IMAP config:', err));

    fetch('/api/cogs')
      .then((res) => res.json())
      .then((data) => setCogs(data))
      .catch((err) => console.error('Failed to load cogs:', err));

    fetch('/api/logs')
      .then((res) => res.json())
      .then((data) => setLogs(data))
      .catch((err) => console.error('Failed to load logs:', err));
  }, []);

  const addLog = async (level: LogEntry['level'], module: string, message: string) => {
    try {
      const res = await fetch('/api/terminal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: `log ${module} ${message}` }),
      });
      const data = await res.json();
      if (data.logs) setLogs(data.logs);
    } catch {
      // Fallback local append
      const newEntry: LogEntry = {
        id: Math.random().toString(36).substring(2, 9),
        timestamp: new Date().toLocaleTimeString(),
        level,
        module,
        message,
      };
      setLogs((prev) => [newEntry, ...prev]);
    }
  };

  const clearLogs = () => setLogs([]);

  const toggleCog = async (id: string) => {
    try {
      const res = await fetch('/api/cogs/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      });
      const updatedCogs = await res.json();
      setCogs(updatedCogs);
      // Refresh logs
      const logRes = await fetch('/api/logs');
      const logData = await logRes.json();
      setLogs(logData);
    } catch (err) {
      console.error('Failed to toggle cog:', err);
    }
  };

  const triggerAutoRelogin = async () => {
    try {
      const res = await fetch('/api/relogin', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        const logRes = await fetch('/api/logs');
        setLogs(await logRes.json());
        const imapRes = await fetch('/api/imap');
        setImapConfig(await imapRes.json());
      }
    } catch (err) {
      console.error('Relogin failed:', err);
    }
  };

  const triggerImapRecovery = async () => {
    try {
      const res = await fetch('/api/imap/recover', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setImapConfig(data.imapConfig);
        const logRes = await fetch('/api/logs');
        setLogs(await logRes.json());
      }
    } catch (err) {
      console.error('IMAP recovery failed:', err);
    }
  };

  return (
    <OreoContext.Provider
      value={{
        activeTab,
        setActiveTab,
        tokens,
        setTokens,
        config,
        setConfig,
        imapConfig,
        setImapConfig,
        logs,
        addLog,
        clearLogs,
        cogs,
        toggleCog,
        workersRunning,
        setWorkersRunning,
        triggerAutoRelogin,
        triggerImapRecovery,
        activeCommandCount,
      }}
    >
      {children}
    </OreoContext.Provider>
  );
};

export const useOreo = () => {
  const context = useContext(OreoContext);
  if (!context) throw new Error('useOreo must be used within an OreoProvider');
  return context;
};
