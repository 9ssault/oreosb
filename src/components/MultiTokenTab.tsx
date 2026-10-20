import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { Users, Plus, Trash2, CheckCircle, RefreshCw, Zap } from 'lucide-react';

export const MultiTokenTab: React.FC = () => {
  const { tokens, setTokens, addLog } = useOreo();
  const [newTokenInput, setNewTokenInput] = useState('');
  const [bulkInput, setBulkInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAddToken = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTokenInput.trim()) return;
    setIsLoading(true);
    try {
      const res = await fetch('/api/tokens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: newTokenInput.trim() }),
      });
      const data = await res.json();
      if (data.id) {
        setTokens((prev) => [...prev, data]);
        setNewTokenInput('');
        addLog('SUCCESS', 'MultiToken', `Successfully registered token: ${data.username} (${data.tag})`);
      }
    } catch (err) {
      console.error('Failed to add token:', err);
      addLog('ERROR', 'MultiToken', 'Failed to register token via API.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveToken = async (id: string) => {
    try {
      const res = await fetch(`/api/tokens/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setTokens((prev) => prev.filter((t) => t.id !== id));
        addLog('INFO', 'MultiToken', `Removed token ID ${id} from rotation.`);
      }
    } catch (err) {
      console.error('Failed to remove token:', err);
    }
  };

  const handleBulkAdd = async () => {
    if (!bulkInput.trim()) return;
    const lines = bulkInput.split('\n').filter((l) => l.trim().length > 10);
    setIsLoading(true);
    for (const line of lines) {
      try {
        await fetch('/api/tokens', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: line.trim() }),
        });
      } catch (err) {
        console.error('Bulk token add error:', err);
      }
    }
    // Refresh tokens list
    const res = await fetch('/api/tokens');
    setTokens(await res.json());
    setBulkInput('');
    setIsLoading(false);
    addLog('SUCCESS', 'MultiToken', `Imported ${lines.length} tokens into active worker rotation.`);
  };

  const handleMassAction = async (action: string) => {
    addLog('INFO', 'MultiTokenManager', `Executing mass action across all ${tokens.length} active worker threads: ${action}`);
    await fetch('/api/terminal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: `massaction ${action}` }),
    });
    const logRes = await fetch('/api/logs');
    // logs updated via context or fetch if needed
    addLog('SUCCESS', 'MultiTokenManager', `Mass action '${action}' completed across all active workers.`);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 p-8 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-mono text-indigo-400 mb-2">
            <Users className="w-3.5 h-3.5" /> MULTI-TOKEN WORKER POOL · TOKENS.TXT STORAGE
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Worker Account Management</h1>
          <p className="text-sm text-slate-400 max-w-2xl mt-1">
            Real-time multi-account synchronization, avatar updates, bio rotation, and guild join orchestration.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button onClick={() => handleMassAction('setallpfp')} className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-medium border border-slate-700 flex items-center gap-2 transition-colors">
            <RefreshCw className="w-3.5 h-3.5 text-indigo-400" /> Sync All Avatars
          </button>
          <button onClick={() => handleMassAction('joinaltokens')} className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition-all">
            <Zap className="w-3.5 h-3.5" /> Force Join All
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Add Token Form */}
        <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-6">
          <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
            <Plus className="w-4 h-4 text-indigo-400" /> Register New Token
          </h3>
          <form onSubmit={handleAddToken} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Discord User Token</label>
              <input
                type="text"
                placeholder="MTE4Mj... (Encrypted Auth Token)"
                value={newTokenInput}
                onChange={(e) => setNewTokenInput(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 transition-all disabled:opacity-50"
            >
              {isLoading ? 'Registering...' : 'Add to tokens.txt'}
            </button>
          </form>

          <div className="pt-4 border-t border-slate-800 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300">Bulk Import tokens.txt</h4>
            <textarea
              rows={4}
              placeholder="token_1&#10;token_2"
              value={bulkInput}
              onChange={(e) => setBulkInput(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleBulkAdd}
              disabled={isLoading}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-medium border border-slate-700 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Importing...' : 'Import Bulk Tokens'}
            </button>
          </div>
        </div>

        {/* Tokens Table */}
        <div className="lg:col-span-2 bg-slate-900/90 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <Users className="w-4 h-4 text-indigo-400" /> Active Worker Pool ({tokens.length})
            </h3>
            <span className="text-xs text-slate-400 font-mono">multi_token.py daemon</span>
          </div>

          <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
            {tokens.map((t) => (
              <div key={t.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between gap-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-sm font-mono">
                    {t.username[0]}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">{t.username}</span>
                      <span className="text-xs text-slate-400 font-mono">{t.tag}</span>
                      {t.nitroActive && <span className="px-1.5 py-0.5 rounded bg-pink-500/10 text-pink-400 border border-pink-500/20 text-[10px] font-mono">Nitro</span>}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                      <span className="font-mono text-[10px] bg-slate-900 px-2 py-0.5 rounded text-indigo-300 border border-slate-800">{t.token}</span>
                      <span className="font-mono">Hypesquad: {t.hypesquad}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" /> {t.status}
                  </span>
                  <button
                    onClick={() => handleRemoveToken(t.id)}
                    className="p-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
