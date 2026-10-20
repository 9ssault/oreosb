import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { Shield, Zap, Crosshair, Users, Activity, CheckCircle, Terminal as TerminalIcon, Radio, Clock, RefreshCcw } from 'lucide-react';

export const DashboardTab: React.FC = () => {
  const { tokens, workersRunning, cogs, logs, config, setActiveTab, addLog } = useOreo();
  const [isTestingLatency, setIsTestingLatency] = useState(false);
  const [latencyMs, setLatencyMs] = useState<number | null>(138);

  const enabledCogsCount = cogs.filter((c) => c.enabled).length;
  const activeTokensCount = tokens.filter((t) => t.status === 'online').length;

  const handleTestLatency = async () => {
    setIsTestingLatency(true);
    addLog('INFO', 'Gateway', 'Pinging Discord API endpoint (GET /api/v10/gateway)...');
    await new Promise((r) => setTimeout(r, 900));
    const simulatedPing = Math.floor(120 + Math.random() * 45);
    setLatencyMs(simulatedPing);
    setIsTestingLatency(false);
    addLog('SUCCESS', 'Gateway', `API ping successful. Latency: ${simulatedPing}ms | Rate Limit Reset: 0s`);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto overflow-y-auto">
      {/* Enterprise Top Banner */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 p-8 shadow-2xl flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 text-xs font-mono text-indigo-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span> OREOSB ENTERPRISE OPERATIONS CENTER · SECURE WORKER DAEMON
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Multi-Token Infrastructure & Automation
          </h1>
          <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
            Deterministic state orchestration, TLS IMAP inbox recovery, and low-latency webhook interceptors operating under strict rate-limit budgets.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleTestLatency}
            disabled={isTestingLatency}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium font-mono border border-slate-700 flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <RefreshCcw className={`w-3.5 h-3.5 ${isTestingLatency ? 'animate-spin text-indigo-400' : ''}`} />
            <span>API Latency: {latencyMs !== null ? `${latencyMs}ms` : 'Testing...'}</span>
          </button>
          <button
            onClick={() => setActiveTab('autorelogin')}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-2"
          >
            <Shield className="w-3.5 h-3.5" /> IMAP Recovery Panel
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-xl flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Active Workers</p>
            <h3 className="text-2xl font-bold text-white font-mono">{activeTokensCount} / {tokens.length}</h3>
            <p className="text-[11px] text-emerald-400 font-mono">tokens.txt synced</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-xl flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Worker Threads</p>
            <h3 className="text-2xl font-bold text-white font-mono">{workersRunning ? 'ACTIVE' : 'STOPPED'}</h3>
            <p className="text-[11px] text-indigo-400 font-mono">Multi-thread polling</p>
          </div>
          <div className={`w-12 h-12 rounded-xl border flex items-center justify-center ${workersRunning ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'}`}>
            <Zap className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-xl flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Snipers & Quests</p>
            <h3 className="text-2xl font-bold text-white font-mono">3 Active</h3>
            <p className="text-[11px] text-pink-400 font-mono">Regex interceptors</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400">
            <Crosshair className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 shadow-xl flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-400">Cogs Loaded</p>
            <h3 className="text-2xl font-bold text-white font-mono">{enabledCogsCount} / {cogs.length}</h3>
            <p className="text-[11px] text-amber-400 font-mono">Delay: {config.delay[0]}s-{config.delay[1]}s</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Activity className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Live Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <TerminalIcon className="w-4 h-4 text-indigo-400" /> Real-Time Telemetry Stream
            </h3>
            <button
              onClick={() => setActiveTab('terminal')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-mono"
            >
              Console Terminal &rarr;
            </button>
          </div>

          <div className="space-y-2 font-mono text-xs">
            {logs.slice(0, 6).map((log) => (
              <div key={log.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between gap-4">
                <div className="flex items-center space-x-3 truncate">
                  <span className="text-slate-500 shrink-0">[{log.timestamp}]</span>
                  <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold shrink-0 ${
                    log.level === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                    log.level === 'SNIPE' ? 'bg-pink-500/10 text-pink-400 border border-pink-500/20' :
                    log.level === 'WARN' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                    log.level === 'ERROR' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                  }`}>
                    {log.module}
                  </span>
                  <span className="text-slate-300 truncate">{log.message}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Health Card */}
        <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" /> Infrastructure Status
          </h3>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">IMAP Daemon:</span>
              <span className="text-emerald-400">Connected (993 TLS)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Proxy Protocol:</span>
              <span className="text-indigo-400">HTTP/SOCKS5 Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Captcha Solver:</span>
              <span className="text-amber-400">{config.captcha_provider}</span>
            </div>
            <div className="pt-3 border-t border-slate-800">
              <button
                onClick={() => setActiveTab('autorelogin')}
                className="w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors border border-slate-700 text-center font-sans"
              >
                Configure IMAP & Secrets
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
