import React from 'react';
import { Mic, Square, X, Volume2, Sparkles } from 'lucide-react';

export default function VoiceOverlay({
  isOpen,
  onClose,
  isRecording,
  onStartRecording,
  onStopRecording,
  statusText,
  lastTranscript,
  lastAnswer,
  isPlayingAudio
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-med-950/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="relative w-full max-w-lg bg-chalk-50 border border-chalk-300 rounded-3xl p-6 sm:p-8 shadow-2xl flex flex-col items-center text-center">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full text-chalk-500 hover:text-med-950 hover:bg-chalk-200 transition"
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cognac-100 text-cognac-800 text-xs font-bold uppercase tracking-wider mb-2">
          <Sparkles size={12} />
          Direct Voice Conversation
        </div>
        <h2 className="text-xl font-bold text-med-950">Talk to Your Document</h2>
        <p className="text-xs text-chalk-500 mt-1 max-w-sm">
          Speak naturally into your mic. The multimodal agent answers aloud from the uploaded PDF.
        </p>

        {/* Center Mic Visualizer */}
        <div className="my-8 flex flex-col items-center justify-center relative">
          {/* Animated Halo Rings */}
          {isRecording && (
            <div className="absolute w-44 h-44 rounded-full bg-cognac-500/20 animate-ping" />
          )}
          {isPlayingAudio && (
            <div className="absolute w-44 h-44 rounded-full bg-med-500/20 animate-pulse" />
          )}

          <button
            onClick={isRecording ? onStopRecording : onStartRecording}
            className={`relative z-10 w-28 h-28 rounded-full flex items-center justify-center text-3xl font-bold shadow-xl transition-all duration-300 ${
              isRecording
                ? 'bg-cognac-600 text-white shadow-cognac-600/50 scale-105'
                : isPlayingAudio
                ? 'bg-med-700 text-white shadow-med-700/50'
                : 'bg-gradient-to-tr from-med-700 to-cognac-600 text-white hover:scale-105 shadow-med-900/30'
            }`}
          >
            {isRecording ? <Square size={32} className="fill-white" /> : isPlayingAudio ? <Volume2 size={36} className="animate-pulse" /> : <Mic size={36} />}
          </button>
        </div>

        {/* Live Status Label */}
        <div className="min-h-8 flex items-center justify-center">
          <span className={`text-sm font-semibold tracking-wide ${
            isRecording ? 'text-cognac-700' : isPlayingAudio ? 'text-med-700' : 'text-med-900'
          }`}>
            {statusText || (isRecording ? "Listening... Click to Send" : "Tap the microphone to speak")}
          </span>
        </div>

        {/* Last Transcript & Answer Preview */}
        {(lastTranscript || lastAnswer) && (
          <div className="w-full mt-4 p-4 rounded-2xl bg-chalk-200/70 border border-chalk-300 text-left space-y-2 max-h-48 overflow-y-auto text-xs">
            {lastTranscript && (
              <div>
                <span className="font-bold text-cognac-800">You: </span>
                <span className="text-med-950 font-medium">"{lastTranscript}"</span>
              </div>
            )}
            {lastAnswer && (
              <div className="pt-1 border-t border-chalk-300">
                <span className="font-bold text-med-800">Agent: </span>
                <span className="text-med-950">{lastAnswer}</span>
              </div>
            )}
          </div>
        )}

        {/* Footer info */}
        <div className="mt-6 flex items-center gap-3 text-[11px] text-chalk-500">
          <span>Groq Whisper</span>
          <span>•</span>
          <span>LangGraph RAG</span>
          <span>•</span>
          <span>Edge Neural TTS</span>
        </div>
      </div>
    </div>
  );
}
