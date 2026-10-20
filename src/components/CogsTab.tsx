import React from 'react';
import { useOreo } from '../context/OreoContext';
import { Cpu, CheckCircle, Power, Terminal } from 'lucide-react';

export const CogsTab: React.FC = () => {
  const { cogs, toggleCog } = useOreo();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-indigo-900/40 via-purple-900/40 to-slate-900 p-6 border border-indigo-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 text-xs font-mono mb-2">
            <Cpu className="w-3.5 h-3.5" /> Modular Cogs Management (60+ Modules)
          </div>
          <h1 className="text-2xl font-bold text-white">OreoSB Cogs Control</h1>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            Enable or disable specific cogs and commands loaded in `cogs/`. Changes take effect instantly without restarting the container.
          </p>
        </div>
      </div>

      {/* Cogs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cogs.map((cog) => (
          <div key={cog.id} className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase font-mono text-[10px]">
                  {cog.category}
                </span>
                <button
                  onClick={() => toggleCog(cog.id)}
                  className={`px-3 py-1 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 ${
                    cog.enabled ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  <Power className="w-3 h-3" />
                  <span>{cog.enabled ? 'Active' : 'Disabled'}</span>
                </button>
              </div>

              <h3 className="text-base font-bold text-white">{cog.name}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{cog.description}</p>
            </div>

            <div className="pt-3 border-t border-slate-800/80 space-y-2">
              <p className="text-[11px] text-slate-500 font-medium">Commands:</p>
              <div className="flex flex-wrap gap-1.5 font-mono text-[11px]">
                {cog.commands.map((cmd) => (
                  <span key={cmd} className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-indigo-300">
                    {cmd}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
