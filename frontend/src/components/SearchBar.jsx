import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Mic, Square, Paperclip, Sparkles, Volume2 } from 'lucide-react';

export default function SearchBar({
  onSendMessage,
  onStartVoice,
  onStopVoice,
  isRecording,
  isLoading,
  mode,
  onOpenIngest
}) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!text.trim() || isLoading || isRecording) return;
    onSendMessage(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      <div className="relative rounded-2xl bg-chalk-50 border border-chalk-300 shadow-lg shadow-med-950/5 transition-all focus-within:border-med-600 focus-within:ring-2 focus-within:ring-med-600/20">
        {/* Top bar indicators */}
        <div className="flex items-center justify-between px-4 pt-3 pb-1 border-b border-chalk-200/60">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide ${
              mode === 'voice'
                ? 'bg-cognac-100 text-cognac-700 border border-cognac-300'
                : 'bg-med-100 text-med-800 border border-med-200'
            }`}>
              {mode === 'voice' ? <Mic size={11} /> : <Sparkles size={11} />}
              {mode === 'voice' ? 'Direct Voice Active' : 'Multimodal Agent'}
            </span>
            <span className="text-xs text-chalk-500 hidden sm:inline">NovaCore FY2026 RAG</span>
          </div>

          <button
            type="button"
            onClick={onOpenIngest}
            className="flex items-center gap-1 text-[11px] font-medium text-med-700 hover:text-med-900 px-2 py-0.5 rounded hover:bg-chalk-200/80 transition"
          >
            <Paperclip size={12} />
            <span>Attach PDF</span>
          </button>
        </div>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="p-3">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              mode === 'voice'
                ? "Click the microphone to speak, or type here to get a spoken answer..."
                : "Ask about financial metrics, charts, tables, or text in your documents..."
            }
            className="w-full bg-transparent resize-none text-sm text-med-950 placeholder:text-chalk-500 focus:outline-none pr-28 max-h-44 py-1.5 leading-relaxed"
            disabled={isLoading || isRecording}
          />

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-1">
              {/* Mic Button */}
              <button
                type="button"
                onClick={isRecording ? onStopVoice : onStartVoice}
                disabled={isLoading}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  isRecording
                    ? 'bg-cognac-600 text-white animate-pulse shadow-md shadow-cognac-600/40'
                    : 'bg-chalk-200 text-cognac-700 hover:bg-cognac-100 border border-chalk-300'
                }`}
                title={isRecording ? "Stop recording and submit" : "Click to speak your question"}
              >
                {isRecording ? <Square size={14} className="fill-white" /> : <Mic size={14} />}
                <span>{isRecording ? 'Listening... Click to Send' : 'Speak'}</span>
              </button>
            </div>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!text.trim() || isLoading || isRecording}
              className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                text.trim() && !isLoading && !isRecording
                  ? 'bg-med-700 text-white shadow-md shadow-med-700/30 hover:bg-med-800'
                  : 'bg-chalk-300 text-chalk-500 cursor-not-allowed'
              }`}
            >
              <ArrowUp size={18} strokeWidth={2.5} />
            </button>
          </div>
        </form>
      </div>

      <p className="text-[11px] text-center text-chalk-500 mt-2">
        Direct human voice & text retrieval powered by Groq Whisper, LangGraph, and Edge Neural TTS.
      </p>
    </div>
  );
}
