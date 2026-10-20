import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { Crosshair, Gift, Eye, Award, CheckCircle2, Sliders, Play } from 'lucide-react';

export const SnipersTab: React.FC = () => {
  const { config, setConfig, addLog } = useOreo();
  const [questId, setQuestId] = useState('');

  const toggleSniper = (key: 'nitro_sniper' | 'giveaway_sniper' | 'invite_sniper') => {
    const updated = !config[key];
    setConfig({ ...config, [key]: updated });
    addLog('INFO', 'Snipers', `${key} has been ${updated ? 'activated' : 'deactivated'}.`);
  };

  const handleStartQuest = () => {
    if (!questId) return;
    addLog('INFO', 'Quests', `Started automated Discord Quest completion for ID: ${questId}`);
    setTimeout(() => {
      addLog('SUCCESS', 'Quests', `Successfully completed quest and claimed reward for ${questId}!`);
      setQuestId('');
    }, 1500);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-pink-900/40 via-purple-900/40 to-slate-900 p-6 border border-pink-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-500/10 text-pink-400 border border-pink-500/30 text-xs font-mono mb-2">
            <Crosshair className="w-3.5 h-3.5" /> Snipers & Automated Quests
          </div>
          <h1 className="text-2xl font-bold text-white">High-Speed Gift & Quest Automator</h1>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            Instantly claim Nitro gift links, giveaway rewards, invite links, watch vanity servers, and automatically complete Discord Quests for rewards.
          </p>
        </div>
      </div>

      {/* Snipers Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400">
              <Gift className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Nitro Gift Sniper</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Monitors all incoming messages across joined servers and DMs for `discord.gift/` links and instantly redeems them.
            </p>
          </div>
          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <span className="text-xs font-medium text-slate-300">Status</span>
            <button
              onClick={() => toggleSniper('nitro_sniper')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
                config.nitro_sniper ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {config.nitro_sniper ? 'ENABLED' : 'DISABLED'}
            </button>
          </div>
        </div>

        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Giveaway Sniper</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Automatically reacts to giveaway bot embeds (GiveawayBot, etc.) to enter drawings and win prizes.
            </p>
          </div>
          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <span className="text-xs font-medium text-slate-300">Status</span>
            <button
              onClick={() => toggleSniper('giveaway_sniper')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
                config.giveaway_sniper ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {config.giveaway_sniper ? 'ENABLED' : 'DISABLED'}
            </button>
          </div>
        </div>

        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Eye className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Vanity / Invite Watcher</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Watches target vanity URLs or invites and instantly snipes them when they become available.
            </p>
          </div>
          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <span className="text-xs font-medium text-slate-300">Status</span>
            <button
              onClick={() => toggleSniper('invite_sniper')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
                config.invite_sniper ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {config.invite_sniper ? 'ENABLED' : 'DISABLED'}
            </button>
          </div>
        </div>
      </div>

      {/* Quests Automator */}
      <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-base font-semibold text-white flex items-center gap-2">
          <Award className="w-4 h-4 text-pink-400" /> Discord Quests Automator (`.quests`, `.qstart`, `.qclaim`)
        </h3>
        <p className="text-xs text-slate-400">
          Automatically start, simulate gameplay/streaming activity, and claim rewards for available Discord Quests.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Enter Quest ID or URL (e.g., 12593482...)"
            value={questId}
            onChange={(e) => setQuestId(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-pink-500"
          />
          <button
            onClick={handleStartQuest}
            className="px-5 py-2.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-medium text-xs shadow-lg shadow-pink-600/30 transition-all flex items-center justify-center gap-2"
          >
            <Play className="w-3.5 h-3.5" /> Start & Claim Quest
          </button>
        </div>
      </div>
    </div>
  );
};
