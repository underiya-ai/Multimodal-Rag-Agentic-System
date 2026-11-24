import React, { useState } from 'react';
import { Settings, X, Key, Check } from 'lucide-react';
import { getStoredApiKey, setStoredApiKey } from '../services/api';

export default function SettingsModal({ isOpen, onClose }) {
  const [apiKey, setApiKey] = useState(getStoredApiKey());
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setStoredApiKey(apiKey.trim());
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-med-950/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-md bg-chalk-50 border border-chalk-300 rounded-3xl p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full text-chalk-500 hover:text-med-950 hover:bg-chalk-200 transition"
        >
          <X size={18} />
        </button>

        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-8 h-8 rounded-xl bg-med-700 text-white flex items-center justify-center shadow-sm">
            <Key size={16} />
          </div>
          <div>
            <h3 className="font-bold text-base text-med-950">Security & API Key</h3>
            <p className="text-xs text-chalk-500">Configures the X-API-Key sent to your backend</p>
          </div>
        </div>

        <div className="space-y-3 mb-5">
          <label className="text-xs font-semibold text-med-900 block">
            API Secret Key (from your .env)
          </label>
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="jjTecnZ4YJh4OWKvPfFFpjqwhWFP7R9gGRABtS8l61U"
            className="w-full text-xs font-mono p-3 bg-chalk-100 border border-chalk-300 rounded-xl text-med-950 focus:outline-none focus:border-med-600 focus:ring-1 focus:ring-med-600"
          />
          <p className="text-[11px] text-chalk-500 leading-normal">
            Stored locally in your browser. This header authorizes access to protected RAG and Voice endpoints.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-xl text-xs font-semibold text-chalk-800 bg-chalk-200 hover:bg-chalk-300 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 py-2 rounded-xl text-xs font-semibold text-white bg-med-700 hover:bg-med-800 transition flex items-center justify-center gap-1.5"
          >
            {saved ? <Check size={14} /> : null}
            <span>{saved ? 'Saved!' : 'Save Key'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
