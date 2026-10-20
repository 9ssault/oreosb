import React, { useState, useRef, useEffect } from 'react';
import { useOreo } from '../context/OreoContext';
import { Terminal as TerminalIcon, Send, Trash2 } from 'lucide-react';

export const TerminalTab: React.FC = () => {
  const { logs, addLog, clearLogs } = useOreo();
  const [inputVal, setInputVal] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const cmd = inputVal.trim();
    addLog('INFO', 'CLI', `> ${cmd}`);

    // Simulate responses based on command
    setTimeout(() => {
      if (cmd.startsWith('.help')) {
        addLog('SUCCESS', 'CLI', 'Available cogs: auth, manager, snipers, nuke, dm, scrape, spam, status, voice, farm, util, fun.');
      } else if (cmd.startsWith('.ping')) {
        addLog('SUCCESS', 'CLI', 'Pong! Gateway latency: 138ms | API latency: 142ms');
      } else if (cmd.startsWith('.tlist')) {
        addLog('SUCCESS', 'CLI', 'Active tokens loaded: 3 workers online.');
      } else if (cmd.startsWith('.refresh')) {
        addLog('SUCCESS', 'CLI', 'Token refreshed successfully via IMAP / email login.');
      } else {
        addLog('SUCCESS', 'CLI', `Executed command '${cmd}' successfully.`);
      }
    }, 400);

    setInputVal('');
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 border border-slate-800 shadow-xl flex items-center justify-between shrink-0">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 text-xs font-mono mb-2">
            <TerminalIcon className="w-3.5 h-3.5" /> Interactive CLI Terminal (`main.py`)
          </div>
          <h1 className="text-2xl font-bold text-white">Live Command Console</h1>
        </div>
        <button
          onClick={clearLogs}
          className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5 text-rose-400" /> Clear Console
        </button>
      </div>

      {/* Terminal Window */}
      <div className="flex-1 bg-slate-950 rounded-2xl border border-slate-800 shadow-2xl p-4 flex flex-col font-mono text-xs overflow-hidden">
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {logs.slice().reverse().map((log) => (
            <div key={log.id} className="flex items-start space-x-3">
              <span className="text-slate-600 shrink-0">[{log.timestamp}]</span>
              <span className={`px-1.5 py-0.2 rounded text-[10px] uppercase font-bold shrink-0 ${
                log.level === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-400' :
                log.level === 'SNIPE' ? 'bg-pink-500/20 text-pink-400' :
                log.level === 'WARN' ? 'bg-amber-500/20 text-amber-400' :
                log.level === 'ERROR' ? 'bg-rose-500/20 text-rose-400' : 'bg-indigo-500/20 text-indigo-400'
              }`}>
                {log.module}
              </span>
              <span className="text-slate-300 break-all">{log.description || log.message}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleCommand} className="mt-4 pt-3 border-t border-slate-900 flex items-center space-x-3 shrink-0">
          <span className="text-indigo-400 font-bold">.</span>
          <input
            type="text"
            placeholder="Type a command (e.g., .help, .ping, .tlist, .refresh)..."
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5"
          >
            <Send className="w-3.5 h-3.5" /> Send
          </button>
        </form>
      </div>
    </div>
  );
};
