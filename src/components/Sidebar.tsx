import React from 'react';
import { useOreo } from '../context/OreoContext';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  Users, 
  Crosshair, 
  Send, 
  Database, 
  Cpu, 
  Terminal, 
  Settings, 
  Activity,
  TerminalSquare
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, tokens } = useOreo();

  const navItems = [
    { id: 'dashboard', label: '01. Telemetry', icon: LayoutDashboard },
    { id: 'autorelogin', label: '02. IMAP & Relogin', icon: ShieldAlert, badge: 'AUTO' },
    { id: 'multitoken', label: '03. Worker Pool', icon: Users, count: tokens.length },
    { id: 'snipers', label: '04. Snipers & Quests', icon: Crosshair },
    { id: 'massdm', label: '05. Broadcast / DM', icon: Send },
    { id: 'scraper', label: '06. Scraper & Cloner', icon: Database },
    { id: 'cogs', label: '07. Modular Cogs', icon: Cpu, count: '60+' },
    { id: 'terminal', label: '08. CLI Console', icon: Terminal },
    { id: 'settings', label: '09. Configuration', icon: Settings },
  ];

  return (
    <aside className="w-72 bg-gray-950 border-r border-gray-800/80 flex flex-col h-screen select-none shrink-0 font-mono">
      {/* Brand Header */}
      <div className="p-6 border-b border-gray-800/80 flex items-center space-x-3 bg-gray-900/45">
        <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10">
          <TerminalSquare className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-widest text-white flex items-center gap-2">
            OREOSB <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">v2.0</span>
          </h1>
          <p className="text-[10px] text-gray-400 tracking-wider">SECURE SELF-BOT SUITE</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-4 py-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-lg text-xs tracking-wider transition-all duration-150 group ${
                isActive
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-lg shadow-emerald-500/5 font-semibold'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/60 border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-gray-500 group-hover:text-gray-300'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {item.badge}
                </span>
              )}
              {item.count !== undefined && (
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${isActive ? 'bg-emerald-500/20 text-emerald-300' : 'bg-gray-900 text-gray-500'}`}>
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-800/80 bg-gray-900/30 text-[10px] text-gray-500 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-emerald-400">
          <Activity className="w-3 h-3 animate-pulse" />
          <span>TLS 1.3 Active</span>
        </span>
        <span className="font-mono text-gray-400">PORT: 3000</span>
      </div>
    </aside>
  );
};
