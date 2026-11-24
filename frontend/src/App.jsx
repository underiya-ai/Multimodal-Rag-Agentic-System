import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ModeSwitch from './components/ModeSwitch';
import SearchBar from './components/SearchBar';
import MessageItem from './components/MessageItem';
import VoiceOverlay from './components/VoiceOverlay';
import IngestModal from './components/IngestModal';
import SettingsModal from './components/SettingsModal';
import { askText, askVoice, streamSpeech } from './services/api';
import { Sparkles, FileText, Mic, Volume2, ShieldCheck, Compass } from 'lucide-react';

export default function App() {
  const [mode, setMode] = useState('text'); // 'text' or 'voice'
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isIngestOpen, setIsIngestOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isVoiceOverlayOpen, setIsVoiceOverlayOpen] = useState(false);

  // Conversation state
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState('');
  const [threads, setThreads] = useState([
    { id: '1', title: 'Multimodal Document Query' }
  ]);
  const [activeThreadId, setActiveThreadId] = useState('1');

  // Media recording refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatBottomRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleNewChat = () => {
    const newId = Date.now().toString();
    setThreads(prev => [{ id: newId, title: 'New Conversation' }, ...prev]);
    setActiveThreadId(newId);
    setMessages([]);
  };

  // Text submit handler
  const handleSendMessage = async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      isVoice: false
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const data = await askText(text);

      let audioDataUri = null;
      // If in voice mode or if spoken requested, synthesize audio
      if (mode === 'voice') {
        try {
          const audioBlob = await streamSpeech(text);
          audioDataUri = URL.createObjectURL(audioBlob);
          const autoAudio = new Audio(audioDataUri);
          autoAudio.play().catch(() => {});
        } catch {
          // Fallback if voice stream has issues
        }
      }

      const agentMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        audio_base64: audioDataUri,
        used_vision: data.used_vision,
        query_rewrites: data.query_rewrites,
        sources: data.sources || [],
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ Error generating answer: ${err.message}. Please check your API key and verify that your document has been ingested.`,
          sources: [],
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Live Microphone Handlers
  const handleStartVoice = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      let mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
        else mimeType = '';
      }

      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = handleProcessVoiceRecording;

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setVoiceStatus('Listening to your voice... Speak your question.');
    } catch (err) {
      alert('Microphone access denied: ' + err.message);
    }
  };

  const handleStopVoice = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
      setIsRecording(false);
      setVoiceStatus('Transcribing speech with Groq Whisper & reasoning over PDF...');
    }
  };

  const handleProcessVoiceRecording = async () => {
    const mimeType = mediaRecorderRef.current?.mimeType || 'audio/webm';
    const ext = mimeType.includes('mp4') ? 'm4a' : 'webm';
    const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });

    setIsLoading(true);

    try {
      const data = await askVoice(audioBlob, undefined, ext);

      // Add transcribed user question
      const userMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: data.transcribed_question || 'Spoken Question',
        isVoice: true
      };

      // Add agent answer with speech
      const agentMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        audio_base64: data.audio_base64,
        used_vision: data.used_vision,
        query_rewrites: data.query_rewrites,
        sources: data.sources || [],
      };

      setMessages(prev => [...prev, userMessage, agentMessage]);

      // Automatically play the voice response
      if (data.audio_base64) {
        const autoAudio = new Audio(data.audio_base64);
        autoAudio.play().catch(e => console.log('Autoplay policy prevented audio:', e));
      }

      setVoiceStatus('Click microphone to speak again');
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ Voice request failed: ${err.message}`,
          sources: []
        }
      ]);
      setVoiceStatus('Voice processing failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-chalk-100 text-med-950 font-sans">
      {/* Perplexity-style Left Sidebar */}
      <Sidebar
        mode={mode}
        setMode={setMode}
        onNewChat={handleNewChat}
        onOpenIngest={() => setIsIngestOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
        threads={threads}
        activeThreadId={activeThreadId}
        onSelectThread={setActiveThreadId}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Top Header */}
        <header className="h-16 px-6 border-b border-chalk-300 flex items-center justify-between bg-chalk-50/80 backdrop-blur-md z-10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-base font-bold text-med-950 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-med-700 animate-pulse"></span>
              NovaCore Engine
            </h1>
            <span className="text-xs text-chalk-500 hidden md:inline border-l border-chalk-300 pl-3">
              Multimodal Document Reasoning
            </span>
          </div>

          {/* Centered Mode Switch */}
          <div className="flex items-center gap-3">
            <ModeSwitch mode={mode} setMode={setMode} />
          </div>

          {/* Right Header Status */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsIngestOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-med-700 hover:bg-med-800 text-white shadow-sm transition"
            >
              <FileText size={14} />
              <span className="hidden sm:inline">Upload PDF</span>
            </button>
          </div>
        </header>

        {/* Scrollable Conversation Stream */}
        <div className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth">
          {messages.length === 0 ? (
            /* Perplexity-Style Empty State */
            <div className="max-w-2xl mx-auto mt-16 text-center space-y-6">
              <div className="inline-flex p-3 rounded-2xl bg-med-50 border border-med-200 text-med-700 shadow-sm">
                <Compass size={28} />
              </div>
              <div>
                <h2 className="text-3xl font-extrabold text-med-950 tracking-tight">
                  Where knowledge begins.
                </h2>
                <p className="text-sm text-chalk-500 mt-2 max-w-md mx-auto">
                  Ask questions about ingested PDFs, financial tables, diagrams, or resumes.
                  Choose <strong>Text</strong> or <strong>Voice</strong> conversation above.
                </p>
              </div>

              {/* Sample Query Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 text-left max-w-xl mx-auto">
                {[
                  "What is the key revenue growth visible in the charts?",
                  "Summarize the table data and financial metrics.",
                  "What technical skills and work experience are detailed?",
                  "Explain the architecture diagram from the document."
                ].map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(query)}
                    className="p-3.5 rounded-xl bg-chalk-50 border border-chalk-300 hover:border-med-700 hover:shadow-md transition text-xs font-medium text-med-950 flex flex-col justify-between"
                  >
                    <span>"{query}"</span>
                    <span className="text-[10px] text-cognac-600 font-semibold mt-2 flex items-center gap-1">
                      <Sparkles size={10} /> Ask Agent
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Message History */
            <div className="max-w-3xl mx-auto space-y-2">
              {messages.map((msg) => (
                <MessageItem key={msg.id} message={msg} />
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="max-w-3xl mx-auto my-4 px-4">
                  <div className="p-4 rounded-2xl bg-chalk-50 border border-chalk-300 flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full border-2 border-med-700 border-t-transparent animate-spin"></div>
                    <span className="text-xs font-semibold text-med-900">
                      Searching Pinecone vectors & synthesizing answer...
                    </span>
                  </div>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>
          )}
        </div>

        {/* Sticky Perplexity-style Search/Voice Bar */}
        <div className="p-4 bg-gradient-to-t from-chalk-100 via-chalk-100 to-transparent flex-shrink-0">
          <SearchBar
            onSendMessage={handleSendMessage}
            onStartVoice={handleStartVoice}
            onStopVoice={handleStopVoice}
            isRecording={isRecording}
            isLoading={isLoading}
            mode={mode}
            onOpenIngest={() => setIsIngestOpen(true)}
          />
        </div>
      </main>

      {/* Voice Immersive Overlay Modal */}
      <VoiceOverlay
        isOpen={isVoiceOverlayOpen}
        onClose={() => setIsVoiceOverlayOpen(false)}
        isRecording={isRecording}
        onStartRecording={handleStartVoice}
        onStopRecording={handleStopVoice}
        statusText={voiceStatus}
      />

      {/* Ingest PDF Modal */}
      <IngestModal
        isOpen={isIngestOpen}
        onClose={() => setIsIngestOpen(false)}
        onIngestSuccess={() => {}}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}
