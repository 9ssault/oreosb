import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { Settings, Save, Shield, Sliders } from 'lucide-react';

export const SettingsTab: React.FC = () => {
  const { config, setConfig, addLog } = useOreo();
  const [formData, setFormData] = useState(config);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setTimeout(() => {
      setConfig(formData);
      setIsSaving(false);
      addLog('SUCCESS', 'Settings', 'config.json updated successfully.');
    }, 800);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 p-6 border border-slate-800 shadow-xl flex items-center justify-between">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 text-xs font-mono mb-2">
            <Settings className="w-3.5 h-3.5" /> Configuration & Settings (`config.json`)
          </div>
          <h1 className="text-2xl font-bold text-white">Framework Preferences</h1>
        </div>
      </div>

      <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-6">
        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Command Prefix</label>
              <input
                type="text"
                value={formData.prefix}
                onChange={(e) => setFormData({ ...formData, prefix: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 font-mono focus:outline-none focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Max Joins Per Hour</label>
              <input
                type="number"
                value={formData.max_joins_per_hour}
                onChange={(e) => setFormData({ ...formData, max_joins_per_hour: Number(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 font-mono focus:outline-none focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Captcha Provider</label>
              <select
                value={formData.captcha_provider}
                onChange={(e) => setFormData({ ...formData, captcha_provider: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 font-mono focus:outline-none focus:border-purple-500"
              >
                <option value="2captcha">2Captcha</option>
                <option value="capsolver">CapSolver</option>
                <option value="anticaptcha">Anti-Captcha</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Proxy (HTTP / SOCKS5)</label>
              <input
                type="text"
                value={formData.proxy || ''}
                onChange={(e) => setFormData({ ...formData, proxy: e.target.value })}
                placeholder="http://user:pass@ip:port"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 font-mono focus:outline-none focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Log Webhook URL</label>
              <input
                type="text"
                value={formData.log_webhook}
                onChange={(e) => setFormData({ ...formData, log_webhook: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 font-mono focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-800">
            <button
              type="submit"
              disabled={isSaving}
              className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {isSaving ? 'Saving Configuration...' : 'Save config.json'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
