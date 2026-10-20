import React from 'react';
import { OreoProvider, useOreo } from './context/OreoContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardTab } from './components/DashboardTab';
import { AutoReloginTab } from './components/AutoReloginTab';
import { MultiTokenTab } from './components/MultiTokenTab';
import { SnipersTab } from './components/SnipersTab';
import { MassDmTab } from './components/MassDmTab';
import { ScraperClonerTab } from './components/ScraperClonerTab';
import { CogsTab } from './components/CogsTab';
import { TerminalTab } from './components/TerminalTab';
import { SettingsTab } from './components/SettingsTab';

const AppContent: React.FC = () => {
  const { activeTab } = useOreo();

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && <DashboardTab />}
          {activeTab === 'autorelogin' && <AutoReloginTab />}
          {activeTab === 'multitoken' && <MultiTokenTab />}
          {activeTab === 'snipers' && <SnipersTab />}
          {activeTab === 'massdm' && <MassDmTab />}
          {activeTab === 'scraper' && <ScraperClonerTab />}
          {activeTab === 'cogs' && <CogsTab />}
          {activeTab === 'terminal' && <TerminalTab />}
          {activeTab === 'settings' && <SettingsTab />}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <OreoProvider>
      <AppContent />
    </OreoProvider>
  );
}
