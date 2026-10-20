import React, { useState } from 'react';
import { useOreo } from '../context/OreoContext';
import { Send, MessageSquare, Trash2, Zap, Radio } from 'lucide-react';

export const MassDmTab: React.FC = () => {
  const { addLog } = useOreo();
  const [dmMessage, setDmMessage] = useState('Hey! Check out OreoSB v2.');
  const [spamMessage, setSpamMessage] = useState('@everyone Raid / Spam test');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookMsg, setWebhookMsg] = useState('OreoSB Webhook Spammer active');

  const handleMassDm = () => {
    if (!dmMessage.trim()) return;
    addLog('INFO', 'MassDM', `Launching mass DM to all friends with message: "${dmMessage}"`);
    setTimeout(() => {
      addLog('SUCCESS', 'MassDM', 'Successfully sent mass DM to 42 friends.');
    }, 1500);
  };

  const handleSpam = () => {
    if (!spamMessage.trim()) return;
    addLog('INFO', 'Spam', `Starting high-speed channel spammer...`);
    setTimeout(() => {
      addLog('SUCCESS', 'Spam', 'Spam sequence executed successfully (Delay: 0.4s).');
    }, 1200);
  };

  const handleWebhookSpam = () => {
    if (!webhookUrl.trim()) return;
    addLog('INFO', 'Webhook', `Spamming webhook URL with message: "${webhookMsg}"`);
    setTimeout(() => {
      addLog('SUCCESS', 'Webhook', 'Webhook spam completed (100 requests sent).');
    }, 1500);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-r from-amber-900/40 via-indigo-900/40 to-slate-900 p-6 border border-amber-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono mb-2">
            <Send className="w-3.5 h-3.5" /> Spam, Mass DM & Webhook Toolkit
          </div>
          <h1 className="text-2xl font-bold text-white">Broadcast & Messaging Engine</h1>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            Execute mass direct messages, channel spamming with ratelimit evasion, ghost pinging, channel purging, and webhook flood utilities.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mass DM Alts */}
        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-amber-400" /> Mass DM Friends (`.dmfriends` / `.massdm`)
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Message Content</label>
              <textarea
                rows={3}
                value={dmMessage}
                onChange={(e) => setDmMessage(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-amber-500"
              />
            </div>
            <button
              onClick={handleMassDm}
              className="w-full py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs shadow-lg shadow-amber-600/30 transition-all"
            >
              Start Mass DM to All Friends
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300">Fast Channel Spammer (`.spam`)</h4>
            <input
              type="text"
              value={spamMessage}
              onChange={(e) => setSpamMessage(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-amber-500"
            />
            <button
              onClick={handleSpam}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
            >
              Launch Spammer (With Anti-RateLimit)
            </button>
          </div>
        </div>

        {/* Webhook Tools */}
        <div className="bg-slate-900/85 rounded-2xl p-6 border border-slate-800 shadow-xl space-y-4">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Radio className="w-4 h-4 text-pink-400" /> Webhook Spammer & Deleter (`.wspam`, `.wdel`)
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Webhook URL</label>
              <input
                type="text"
                placeholder="https://discord.com/api/webhooks/..."
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-pink-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Webhook Message</label>
              <input
                type="text"
                value={webhookMsg}
                onChange={(e) => setWebhookMsg(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-pink-500"
              />
            </div>
            <button
              onClick={handleWebhookSpam}
              className="w-full py-2.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-medium text-xs shadow-lg shadow-pink-600/30 transition-all"
            >
              Spam Webhook
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
