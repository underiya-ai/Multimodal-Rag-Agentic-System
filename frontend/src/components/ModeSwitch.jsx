import React from 'react';
import { MessageSquare, Mic } from 'lucide-react';

export default function ModeSwitch({ mode, setMode }) {
  return (
    <div className="inline-flex p-1 rounded-2xl bg-chalk-200 border border-chalk-300 shadow-inner">
      <button
        onClick={() => setMode('text')}
        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 ${
          mode === 'text'
            ? 'bg-med-700 text-chalk-50 shadow-md shadow-med-900/20'
            : 'text-med-900 hover:text-med-700'
        }`}
      >
        <MessageSquare size={16} />
        <span>Text Conversation</span>
      </button>

      <button
        onClick={() => setMode('voice')}
        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 ${
          mode === 'voice'
            ? 'bg-cognac-600 text-chalk-50 shadow-md shadow-cognac-900/20'
            : 'text-cognac-800 hover:text-cognac-600'
        }`}
      >
        <Mic size={16} />
        <span>Voice Conversation</span>
        <span className="ml-1 text-[10px] bg-cognac-800 text-chalk-100 px-1.5 py-0.2 rounded-full uppercase tracking-wider">
          Direct
        </span>
      </button>
    </div>
  );
}
