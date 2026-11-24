import React, { useState, useRef } from 'react';
import {
  Sparkles,
  User,
  Volume2,
  VolumeX,
  FileText,
  Image as ImageIcon,
  Table as TableIcon,
  Copy,
  Check,
  RotateCcw,
  ExternalLink
} from 'lucide-react';

export default function MessageItem({ message }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeSource, setActiveSource] = useState(null);
  const audioRef = useRef(null);

  const isUser = message.role === 'user';

  const toggleAudio = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isUser) {
    return (
      <div className="flex justify-end my-4 px-4">
        <div className="max-w-2xl bg-chalk-200 border border-chalk-300 text-med-950 px-4 py-3 rounded-2xl shadow-sm">
          <div className="flex items-center gap-2 mb-1 text-xs font-semibold text-cognac-700">
            <User size={13} />
            <span>You</span>
            {message.isVoice && (
              <span className="text-[10px] bg-cognac-100 text-cognac-800 px-1.5 py-0.2 rounded-full font-bold">
                Spoken
              </span>
            )}
          </div>
          <p className="text-sm font-medium leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="my-6 px-4 max-w-3xl mx-auto">
      <div className="bg-chalk-50 border border-chalk-300/80 rounded-2xl p-5 shadow-sm space-y-4">
        {/* Header row: Agent Icon + Status Badges */}
        <div className="flex items-center justify-between pb-3 border-b border-chalk-200">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-med-700 text-white flex items-center justify-center shadow-sm">
              <Sparkles size={14} />
            </div>
            <div>
              <span className="font-semibold text-sm text-med-950">NovaCore Intelligence</span>
              <span className="text-xs text-chalk-500 ml-2">Multimodal Engine</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            {message.used_vision && (
              <span className="inline-flex items-center gap-1 bg-med-100 text-med-700 px-2 py-0.5 rounded-md font-medium border border-med-200">
                <ImageIcon size={12} />
                <span>Visual Analysis</span>
              </span>
            )}
            {message.query_rewrites > 0 && (
              <span className="bg-chalk-200 text-chalk-800 px-2 py-0.5 rounded-md font-medium">
                {message.query_rewrites} rewrite{message.query_rewrites > 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>

        {/* Sources Row (Perplexity Style) */}
        {message.sources && message.sources.length > 0 && (
          <div className="space-y-1.5">
            <div className="text-[11px] font-semibold text-chalk-500 uppercase tracking-wider">
              Sources from Ingested PDF ({message.sources.length})
            </div>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((src, idx) => {
                const isSelected = activeSource === idx;
                return (
                  <button
                    key={idx}
                    onClick={() => setActiveSource(isSelected ? null : idx)}
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                      isSelected
                        ? 'bg-med-700 text-white border-med-700 shadow-sm'
                        : 'bg-chalk-100 text-med-900 border-chalk-300 hover:border-med-600 hover:bg-chalk-200'
                    }`}
                  >
                    {src.type === 'visual' ? (
                      <ImageIcon size={12} className={isSelected ? 'text-white' : 'text-cognac-600'} />
                    ) : src.type === 'table' ? (
                      <TableIcon size={12} className={isSelected ? 'text-white' : 'text-med-600'} />
                    ) : (
                      <FileText size={12} className={isSelected ? 'text-white' : 'text-chalk-500'} />
                    )}
                    <span>Page {src.page}</span>
                    <span className="text-[10px] opacity-70 uppercase">({src.type})</span>
                  </button>
                );
              })}
            </div>

            {/* Active Source Expanded Preview */}
            {activeSource !== null && message.sources[activeSource] && (
              <div className="mt-2 p-3 rounded-xl bg-chalk-200/90 border border-chalk-300 text-xs text-med-950 leading-relaxed">
                <div className="font-semibold text-med-900 mb-1 flex items-center justify-between">
                  <span>Source Reference: Page {message.sources[activeSource].page} ({message.sources[activeSource].type})</span>
                  <button
                    onClick={() => setActiveSource(null)}
                    className="text-chalk-500 hover:text-med-950 text-xs font-normal"
                  >
                    Close
                  </button>
                </div>
                <p className="font-mono text-[11px] text-med-800 whitespace-pre-wrap">
                  {message.sources[activeSource].preview}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Answer Content */}
        <div className="text-sm text-med-950 leading-relaxed space-y-2 whitespace-pre-wrap pt-1 font-normal">
          {message.content}
        </div>

        {/* Spoken Audio Player Bar */}
        {message.audio_base64 && (
          <div className="flex items-center justify-between p-3 rounded-xl bg-chalk-200/80 border border-chalk-300">
            <div className="flex items-center gap-3">
              <button
                onClick={toggleAudio}
                className="w-8 h-8 rounded-full bg-cognac-600 hover:bg-cognac-700 text-white flex items-center justify-center shadow-sm transition"
                title={isPlaying ? "Pause voice" : "Play voice"}
              >
                {isPlaying ? <VolumeX size={15} /> : <Volume2 size={15} />}
              </button>
              <div>
                <span className="text-xs font-semibold text-cognac-800">Spoken Answer</span>
                <span className="block text-[10px] text-chalk-500">Edge Neural Audio</span>
              </div>
            </div>

            <audio
              ref={audioRef}
              src={message.audio_base64}
              onEnded={() => setIsPlaying(false)}
              onPause={() => setIsPlaying(false)}
              onPlay={() => setIsPlaying(true)}
            />

            <button
              onClick={() => {
                if (audioRef.current) {
                  audioRef.current.currentTime = 0;
                  audioRef.current.play();
                  setIsPlaying(true);
                }
              }}
              className="text-chalk-500 hover:text-med-900 p-1.5 rounded transition"
              title="Replay from beginning"
            >
              <RotateCcw size={14} />
            </button>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-chalk-200 text-chalk-500 text-xs">
          <span className="text-[11px] font-medium text-chalk-500">Grounded in PDF Knowledge</span>
          <div className="flex items-center gap-2">
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-1 px-2 py-1 rounded hover:bg-chalk-200 transition text-chalk-600 hover:text-med-950"
            >
              {copied ? <Check size={12} className="text-med-600" /> : <Copy size={12} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
