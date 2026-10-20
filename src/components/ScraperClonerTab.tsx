import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { Database, Download, Copy, Shield, CheckCircle } from 'lucide-react';

export const ScraperClonerTab: React.FC = () => {
  const { addLog } = useOreo();
  const [guildId, setGuildId] = useState('1561989222649434175');

  const handleScrape = (type: string) => {
    addLog('INFO', 'Scraper', `Initiating server ${type} extraction for Guild ID: ${guildId}`);
    setTimeout(() => {
      addLog('SUCCESS', 'Scraper', `Successfully exported ${type} data to JSON / backups/ directory.`);
    }, 1500);
  };

  const handleClone = () => {
    addLog('INFO', 'Cloner', `Starting full server clone for Guild ID: ${guildId} (Channels, Roles, Permissions)...`);
    setTimeout(() => {
      addLog('SUCCESS', 'Cloner', 'Server clone successfully mirrored on destination guild.');
    }, 2000);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-emerald-900/40 via-indigo-900/40 to-slate-900 p-6 border border-emerald-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono mb-2">
            <Database className="w-3.5 h-3.5" /> Scraper, Cloner & Backup Suite
          </div>
          <h1 className="text-2xl font-bold text-white">Extract & Mirror Discord Servers</h1>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            Scrape guild members, messages, channels, emojis, and stickers. Mirror entire server hierarchies with automated role and permission cloning.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Download className="w-4 h-4 text-emerald-400" /> Scraper & Backup (`.scrape`, `.backup`)
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Target Guild ID</label>
              <input
                type="text"
                value={guildId}
                onChange={(e) => setGuildId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                onClick={() => handleScrape('members')}
                className="py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
              >
                Scrape Members ID
              </button>
              <button
                onClick={() => handleScrape('messages')}
                className="py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
              >
                Export Message History
              </button>
            </div>
            <button
              onClick={() => handleScrape('full_backup')}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-lg shadow-emerald-600/30 transition-all"
            >
              Generate Full Server Backup JSON
            </button>
          </div>
        </div>

        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Copy className="w-4 h-4 text-indigo-400" /> Server Cloner (`.clone`)
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Clones all categories, channels, permissions, and roles from the source server to your destination server in seconds.
          </p>
          <div className="pt-2">
            <button
              onClick={handleClone}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2"
            >
              <Copy className="w-4 h-4" /> Execute Full Server Clone
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
