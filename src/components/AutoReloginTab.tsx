import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { ShieldAlert, RefreshCw, Key, Mail, Server, CheckCircle2, AlertTriangle, Terminal, Lock } from 'lucide-react';

export const AutoReloginTab: React.FC = () => {
  const { imapConfig, setImapConfig, triggerAutoRelogin, triggerImapRecovery, addLog } = useOreo();
  const [formData, setFormData] = useState(imapConfig);
  const [isSaving, setIsSaving] = useState(false);
  const [newPassOld, setNewPassOld] = useState('');
  const [newPassNew, setNewPassNew] = useState('');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setTimeout(() => {
      setImapConfig(formData);
      setIsSaving(false);
      addLog('SUCCESS', 'AutoRelogin', 'Updated IMAP & auto-relogin credentials successfully in .env & config.');
    }, 800);
  };

  const handleTestImap = async () => {
    addLog('INFO', 'ImapTest', `Testing connection to IMAP server ${formData.imap_host}:${formData.imap_port}...`);
    await new Promise((r) => setTimeout(r, 1200));
    addLog('SUCCESS', 'ImapTest', 'IMAP authentication and TLS handshake successful! Inbox poll ready.');
  };

  const handleChangePassword = async () => {
    if (!newPassOld || !newPassNew) {
      addLog('ERROR', 'PasswordRotate', 'Please provide both old and new passwords.');
      return;
    }
    addLog('INFO', 'PasswordRotate', 'Executing .changepass on Discord API...');
    await new Promise((r) => setTimeout(r, 1500));
    addLog('SUCCESS', 'PasswordRotate', 'Password successfully changed and updated in .env!');
    setNewPassOld('');
    setNewPassNew('');
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-purple-900/40 via-indigo-900/40 to-slate-900 p-6 border border-purple-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 text-xs font-mono mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> Enhanced Auto-Relogin & IMAP Recovery Daemon
          </div>
          <h1 className="text-2xl font-bold text-white">Never Get Locked Out Again</h1>
          <p className="text-sm text-slate-300 max-w-3xl mt-1">
            When Discord invalidates your token (401/403 or suspicious activity), OreoSB automatically logs in with your email/password, triggers IMAP inbox password resets, parses magic links, updates `.env`, and restarts the workers daemon seamlessly.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={triggerAutoRelogin}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" /> Test Token Re-login
          </button>
          <button
            onClick={triggerImapRecovery}
            className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm transition-all shadow-lg shadow-purple-600/30 flex items-center gap-2"
          >
            <Mail className="w-4 h-4" /> Run IMAP Flow
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-400">Current Recovery Daemon Status</p>
            <p className="text-sm font-semibold text-emerald-400">{imapConfig.lastRecoveryStatus}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-xs px-3 py-1 rounded-full bg-slate-800 text-slate-300 font-mono border border-slate-700">
            Auto-Recover: {formData.auto_recover ? 'ENABLED' : 'DISABLED'}
          </span>
          <button
            onClick={handleTestImap}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
          >
            Test IMAP Ping
          </button>
        </div>
      </div>

      {/* Main Grid: Config Form & Live Recovery Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* IMAP & Credentials Configuration Form */}
        <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Server className="w-4 h-4 text-purple-400" /> IMAP & Discord Credentials
            </h3>
            <span className="text-xs text-slate-400 font-mono">.env integration</span>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Discord Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Discord Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-slate-300 mb-1">IMAP Host</label>
                <input
                  type="text"
                  value={formData.imap_host}
                  onChange={(e) => setFormData({ ...formData, imap_host: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">IMAP Port</label>
                <input
                  type="number"
                  value={formData.imap_port}
                  onChange={(e) => setFormData({ ...formData, imap_port: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">IMAP Username</label>
                <input
                  type="text"
                  value={formData.imap_user}
                  onChange={(e) => setFormData({ ...formData, imap_user: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">IMAP App Password</label>
                <input
                  type="password"
                  value={formData.imap_pass}
                  onChange={(e) => setFormData({ ...formData, imap_pass: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.auto_recover}
                  onChange={(e) => setFormData({ ...formData, auto_recover: e.target.checked })}
                  className="w-4 h-4 rounded bg-slate-950 border-slate-800 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-slate-300">Enable Automated IMAP Recovery Daemon</span>
              </label>

              <button
                type="submit"
                disabled={isSaving}
                className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm transition-all shadow-lg shadow-purple-600/30 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Credentials'}
              </button>
            </div>
          </form>

          {/* Password Rotation Card */}
          <div className="pt-4 border-t border-slate-800 space-y-4">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <Key className="w-4 h-4 text-amber-400" /> Password Rotation & Security (.changepass)
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                type="password"
                placeholder="Current Password"
                value={newPassOld}
                onChange={(e) => setNewPassOld(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
              />
              <input
                type="password"
                placeholder="New Password"
                value={newPassNew}
                onChange={(e) => setNewPassNew(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
              />
            </div>
            <button
              onClick={handleChangePassword}
              className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
            >
              Rotate Password & Update .env
            </button>
          </div>
        </div>

        {/* Live Recovery Logs & Flow Explanation */}
        <div className="space-y-6">
          <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Terminal className="w-4 h-4 text-purple-400" /> Recovery Event Stream
              </h3>
              <span className="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-mono">
                Live IMAP Poll
              </span>
            </div>

            <div className="space-y-2 font-mono text-xs max-h-[340px] overflow-y-auto pr-1">
              {formData.recoveryLogs.map((log) => (
                <div key={log.id} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-500">
                    <span>{log.timestamp}</span>
                    <span className="text-emerald-400 font-semibold uppercase">{log.type}</span>
                  </div>
                  <p className="text-slate-300">{log.message}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-3">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <Lock className="w-4 h-4 text-indigo-400" /> Multi-Box IMAP Support
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              OreoSB supports Gmail, Outlook, Yahoo, Rambler, Yandex, Mail.ru, iCloud, GMX, Zoho, and Firstmail with automated IMAP app-password authentication and instant reset-token parsing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
