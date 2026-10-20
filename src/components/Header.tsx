import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { ShieldCheck, RefreshCcw, Power, CheckCircle2 } from 'lucide-react';

export const Header: React.FC = () => {
  const { workersRunning, setWorkersRunning, triggerAutoRelogin, addLog } = useOreo();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleGlobalRefresh = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      addLog('SUCCESS', 'System', `Global token health check passed. Latency: ${data.latency}ms | Active workers: ${data.activeTokens}`);
    } catch {
      addLog('ERROR', 'System', 'Failed to reach API health endpoint.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleToggleWorkers = async () => {
    try {
      const res = await fetch('/api/workers/toggle', { method: 'POST' });
      const data = await res.json();
      setWorkersRunning(data.workersRunning);
    } catch (err) {
      console.error('Failed to toggle workers:', err);
    }
  };

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-8 flex items-center justify-between shrink-0 select-none">
      <div className="flex items-center space-x-4">
        <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2 font-mono">
          <span>OREOSB // COMMAND CENTER</span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 flex items-center gap-1 font-mono font-normal">
            <ShieldCheck className="w-3.5 h-3.5" /> SECURE DAEMON ACTIVE
          </span>
        </h2>
      </div>

      <div className="flex items-center space-x-3">
        <button
          onClick={handleGlobalRefresh}
          disabled={isRefreshing}
          className="flex items-center space-x-2 px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-medium font-mono transition-colors border border-slate-700 disabled:opacity-50"
        >
          <RefreshCcw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
          <span>Health Check</span>
        </button>

        <button
          onClick={triggerAutoRelogin}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs font-medium font-mono transition-colors border border-indigo-500/30"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Force Relogin</span>
        </button>

        <button
          onClick={handleToggleWorkers}
          className={`flex items-center space-x-2 px-4 py-1.5 rounded-xl text-xs font-medium font-mono transition-all shadow-sm ${
            workersRunning
              ? 'bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30'
              : 'bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30'
          }`}
        >
          <Power className="w-3.5 h-3.5" />
          <span>{workersRunning ? 'Stop Daemon' : 'Start Daemon'}</span>
        </button>
      </div>
    </header>
  );
};
