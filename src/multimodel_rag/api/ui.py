from fastapi import APIRouter
from fastapi.responses import HTMLResponse

ui_router = APIRouter()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Multimodal RAG - Live Voice Agent</title>
  <style>
    :root {
      --bg: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent: #10b981;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 2rem 1rem; }
    .container { width: 100%; max-width: 720px; display: flex; flex-direction: column; gap: 1.5rem; }
    header { text-align: center; margin-bottom: 0.5rem; }
    header h1 { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    header p { color: var(--muted); margin-top: 0.25rem; font-size: 0.95rem; }

    .card { background: var(--card); border: 1px solid var(--border); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
    .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }

    .input-group { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }
    label { font-size: 0.85rem; color: var(--muted); font-weight: 500; }
    input[type="text"], input[type="password"] { background: #0b1120; border: 1px solid var(--border); border-radius: 0.5rem; color: var(--text); padding: 0.65rem 0.85rem; font-size: 0.9rem; }
    input:focus { outline: none; border-color: var(--primary); }

    /* Voice Centerpiece */
    .mic-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 1rem; gap: 1.25rem; }
    .mic-btn {
      width: 110px; height: 110px; border-radius: 50%; border: none; cursor: pointer;
      background: linear-gradient(135deg, #3b82f6, #6366f1); color: white;
      font-size: 2.5rem; display: flex; align-items: center; justify-content: center;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 0 25px rgba(59, 130, 246, 0.4);
      outline: none;
    }
    .mic-btn:hover { transform: scale(1.06); box-shadow: 0 0 35px rgba(59, 130, 246, 0.6); }
    .mic-btn.recording {
      background: linear-gradient(135deg, #ef4444, #dc2626);
      animation: pulse 1.4s infinite;
      box-shadow: 0 0 35px rgba(239, 68, 68, 0.7);
    }
    .mic-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

    @keyframes pulse {
      0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
      70% { transform: scale(1.08); box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
      100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    .mic-status { font-size: 1rem; font-weight: 500; color: var(--text); min-height: 1.5rem; }

    /* Results */
    .result-box { display: flex; flex-direction: column; gap: 1rem; }
    .transcript-bubble { background: #0b1120; border-left: 3px solid var(--primary); padding: 0.85rem 1rem; border-radius: 0.5rem; font-size: 0.95rem; }
    .answer-bubble { background: #0f2027; border-left: 3px solid var(--accent); padding: 1rem 1.25rem; border-radius: 0.5rem; line-height: 1.6; font-size: 1rem; }
    .sources-list { font-size: 0.85rem; color: var(--muted); display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
    .source-tag { background: #1e3a5f; color: #93c5fd; padding: 0.2rem 0.5rem; border-radius: 0.3rem; }

    /* File upload */
    .upload-row { display: flex; gap: 0.5rem; align-items: center; }
    .upload-row input[type="file"] { flex: 1; color: var(--muted); font-size: 0.85rem; }
    .btn { background: var(--primary); color: white; border: none; padding: 0.65rem 1.2rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
    .btn:hover { background: var(--primary-hover); }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-secondary { background: #334155; }
    .btn-secondary:hover { background: #475569; }

    .audio-player { width: 100%; margin-top: 0.5rem; border-radius: 0.5rem; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🎙️ Multimodal Voice Agent</h1>
      <p>Speak naturally into your microphone — answers are retrieved from your PDF and spoken aloud.</p>
    </header>

    <!-- Settings Card -->
    <div class="card">
      <div class="card-title">🔐 API Configuration</div>
      <div class="input-group">
        <label for="apiKey">Your Server X-API-Key</label>
        <input type="text" id="apiKey" value="jjTecnZ4YJh4OWKvPfFFpjqwhWFP7R9gGRABtS8l61U" placeholder="Paste your API_KEY from .env">
      </div>
    </div>

    <!-- PDF Ingest Card -->
    <div class="card">
      <div class="card-title">📄 Ingest PDF Document</div>
      <div class="upload-row">
        <input type="file" id="pdfFile" accept="application/pdf">
        <button class="btn" id="uploadBtn" onclick="uploadPDF()">Upload & Index</button>
      </div>
      <div id="uploadStatus" style="margin-top: 0.75rem; font-size: 0.85rem; color: var(--muted);"></div>
    </div>

    <!-- Live Voice Interaction Card -->
    <div class="card">
      <div class="card-title">🗣️ Live Human Voice Conversation</div>
      <div class="mic-container">
        <button class="mic-btn" id="micBtn" onclick="toggleRecording()">🎙️</button>
        <div class="mic-status" id="micStatus">Click the microphone and ask your question</div>
      </div>

      <!-- Result Section -->
      <div id="resultSection" class="result-box" style="display: none;">
        <div>
          <label>You Said (Transcribed):</label>
          <div class="transcript-bubble" id="userTranscript"></div>
        </div>
        <div>
          <label>Voice Agent Answer:</label>
          <div class="answer-bubble" id="agentAnswer"></div>
        </div>
        <div>
          <audio id="answerAudio" class="audio-player" controls autoplay></audio>
        </div>
        <div>
          <label>Citations & Sources:</label>
          <div class="sources-list" id="sourcesList"></div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    // Load saved API key if present
    const savedKey = localStorage.getItem("rag_api_key");
    if (savedKey) document.getElementById("apiKey").value = savedKey;

    function getApiKey() {
      const key = document.getElementById("apiKey").value.trim();
      localStorage.setItem("rag_api_key", key);
      return key;
    }

    async function uploadPDF() {
      const fileInput = document.getElementById("pdfFile");
      const statusEl = document.getElementById("uploadStatus");
      const uploadBtn = document.getElementById("uploadBtn");

      if (!fileInput.files.length) {
        alert("Please select a PDF file first.");
        return;
      }

      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append("file", file);

      uploadBtn.disabled = true;
      statusEl.style.color = "#60a5fa";
      statusEl.textContent = "Uploading & processing PDF in background...";

      try {
        const res = await fetch("/api/v1/ingest", {
          method: "POST",
          headers: { "X-API-Key": getApiKey() },
          body: formData
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Upload failed");
        }

        const data = await res.json();
        statusEl.style.color = "#34d399";
        statusEl.textContent = `PDF uploaded successfully! Ingestion job started (ID: ${data.job_id}). Extraction running...`;
      } catch (err) {
        statusEl.style.color = "#f87171";
        statusEl.textContent = `Error: ${err.message}`;
      } finally {
        uploadBtn.disabled = false;
      }
    }

    async function toggleRecording() {
      if (isRecording) {
        stopRecording();
      } else {
        await startRecording();
      }
    }

    async function startRecording() {
      const micBtn = document.getElementById("micBtn");
      const micStatus = document.getElementById("micStatus");

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];

        // Check supported MIME type
        let mimeType = "audio/webm";
        if (!MediaRecorder.isTypeSupported("audio/webm")) {
          if (MediaRecorder.isTypeSupported("audio/mp4")) mimeType = "audio/mp4";
          else mimeType = "";
        }

        mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendAudioToAgent;

        mediaRecorder.start();
        isRecording = true;
        micBtn.classList.add("recording");
        micBtn.textContent = "⏹️";
        micStatus.textContent = "Listening... Speak your question, then click again to send.";
        micStatus.style.color = "#f87171";
      } catch (err) {
        alert("Microphone permission denied or not available: " + err.message);
      }
    }

    function stopRecording() {
      if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;

        const micBtn = document.getElementById("micBtn");
        const micStatus = document.getElementById("micStatus");
        micBtn.classList.remove("recording");
        micBtn.textContent = "⏳";
        micBtn.disabled = true;
        micStatus.textContent = "Thinking & Synthesizing Voice Response...";
        micStatus.style.color = "#fbbf24";
      }
    }

    async function sendAudioToAgent() {
      const micBtn = document.getElementById("micBtn");
      const micStatus = document.getElementById("micStatus");
      const resultSection = document.getElementById("resultSection");

      try {
        const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || "audio/webm" });
        const ext = mediaRecorder.mimeType.includes("mp4") ? "m4a" : "webm";
        const formData = new FormData();
        formData.append("file", audioBlob, `live_speech.${ext}`);

        const res = await fetch("/api/v1/voice/ask", {
          method: "POST",
          headers: { "X-API-Key": getApiKey() },
          body: formData
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Voice request failed");
        }

        const data = await res.json();

        // Render response
        resultSection.style.display = "flex";
        document.getElementById("userTranscript").textContent = data.transcribed_question || "No speech detected";
        document.getElementById("agentAnswer").textContent = data.answer;

        // Auto-play the synthesized speech aloud
        const audioPlayer = document.getElementById("answerAudio");
        if (data.audio_base64) {
          audioPlayer.src = data.audio_base64;
          audioPlayer.play().catch(e => console.log("Audio autoplay prevented by browser policy:", e));
        }

        // Render sources
        const sourcesEl = document.getElementById("sourcesList");
        sourcesEl.innerHTML = "";
        if (data.sources && data.sources.length) {
          data.sources.forEach(src => {
            const span = document.createElement("span");
            span.className = "source-tag";
            span.textContent = `Page ${src.page} (${src.type})`;
            sourcesEl.appendChild(span);
          });
        } else {
          sourcesEl.innerHTML = "<span>No specific document sources cited.</span>";
        }

        micStatus.textContent = "Click the microphone to speak another question";
        micStatus.style.color = "#34d399";
      } catch (err) {
        micStatus.textContent = `Error: ${err.message}`;
        micStatus.style.color = "#f87171";
      } finally {
        micBtn.disabled = false;
        micBtn.textContent = "🎙️";
      }
    }
  </script>
</body>
</html>
"""


@ui_router.get("/", response_class=HTMLResponse)
@ui_router.get("/voice", response_class=HTMLResponse)
def get_voice_ui():
    """Serves the live interactive microphone voice agent web application."""
    return HTMLResponse(content=HTML_CONTENT)
