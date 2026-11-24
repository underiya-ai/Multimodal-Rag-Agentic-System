import React from 'react';
import { MessageSquare, Mic, FileText, Plus, Settings, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Sidebar({
  mode,
  setMode,
  onNewChat,
  onOpenIngest,
  onOpenSettings,
  isCollapsed,
  setIsCollapsed,
  threads = [],
  activeThreadId,
  onSelectThread
}) {
  return (
    <aside
      className={`fixed md:static inset-y-0 left-0 z-40 flex flex-col justify-between bg-med-950 text-chalk-100 border-r border-med-900 transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Top Header */}
      <div>
        <div className="flex items-center justify-between p-4 border-b border-med-900">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-med-600 to-cognac-600 flex items-center justify-center font-bold text-white shadow-md shadow-med-950/50 flex-shrink-0">
              N
            </div>
            {!isCollapsed && (
              <div className="leading-tight">
                <span className="font-bold tracking-tight text-chalk-50 text-base">NovaCore</span>
                <span className="block text-[10px] uppercase tracking-wider text-cognac-400 font-semibold">Multimodal RAG</span>
              </div>
            )}
          </div>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-chalk-400 hover:text-white hover:bg-med-900 transition"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* New Thread Button */}
        <div className="p-3">
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-med-800 hover:bg-med-700 text-chalk-50 font-medium text-sm transition shadow-sm border border-med-700/60"
          >
            <Plus size={16} />
            {!isCollapsed && <span>New Thread</span>}
          </button>
        </div>

        {/* Mode Selector */}
        <div className="px-3 py-2">
          {!isCollapsed && (
            <p className="text-[11px] font-semibold text-chalk-500 uppercase tracking-wider px-2 mb-2">
              Conversation Mode
            </p>
          )}
          <div className="space-y-1">
            <button
              onClick={() => setMode('text')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition ${
                mode === 'text'
                  ? 'bg-med-700 text-chalk-50 shadow-sm border border-med-600'
                  : 'text-chalk-400 hover:text-chalk-100 hover:bg-med-900'
              }`}
            >
              <MessageSquare size={17} className={mode === 'text' ? 'text-chalk-50' : 'text-chalk-400'} />
              {!isCollapsed && <span>Text Chat</span>}
            </button>

            <button
              onClick={() => setMode('voice')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition ${
                mode === 'voice'
                  ? 'bg-cognac-700 text-chalk-50 shadow-sm border border-cognac-600'
                  : 'text-chalk-400 hover:text-chalk-100 hover:bg-med-900'
              }`}
            >
              <Mic size={17} className={mode === 'voice' ? 'text-chalk-50' : 'text-cognac-400'} />
              {!isCollapsed && (
                <div className="flex items-center justify-between flex-1">
                  <span>Voice Mode</span>
                  <span className="text-[10px] bg-cognac-900/60 text-cognac-300 px-1.5 py-0.5 rounded-full font-bold">LIVE</span>
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Thread History */}
        {!isCollapsed && threads.length > 0 && (
          <div className="px-3 py-3 border-t border-med-900/70">
            <p className="text-[11px] font-semibold text-chalk-500 uppercase tracking-wider px-2 mb-2">
              Recent Threads
            </p>
            <div className="space-y-1 max-h-56 overflow-y-auto pr-1">
              {threads.map((t) => (
                <button
                  key={t.id}
                  onClick={() => onSelectThread(t.id)}
                  className={`w-full text-left truncate px-2.5 py-1.5 rounded-lg text-xs transition ${
                    activeThreadId === t.id
                      ? 'bg-med-900 text-chalk-100 font-medium'
                      : 'text-chalk-400 hover:text-chalk-200 hover:bg-med-900/40'
                  }`}
                >
                  {t.title || 'Untitled Thread'}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Actions */}
      <div className="p-3 border-t border-med-900 space-y-1">
        <button
          onClick={onOpenIngest}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium text-chalk-300 hover:text-chalk-50 hover:bg-med-900 transition"
        >
          <FileText size={16} className="text-med-500" />
          {!isCollapsed && <span>Ingest PDF</span>}
        </button>

        <button
          onClick={onOpenSettings}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium text-chalk-300 hover:text-chalk-50 hover:bg-med-900 transition"
        >
          <Settings size={16} className="text-chalk-400" />
          {!isCollapsed && <span>API Key Settings</span>}
        </button>
      </div>
    </aside>
  );
}
