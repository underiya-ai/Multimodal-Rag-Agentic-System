import base64
import io

import edge_tts
from groq import Groq

from multimodel_rag.config import get_settings


def get_groq_client() -> Groq:
    """Client for Groq cloud operations."""
    settings = get_settings()
    return Groq(api_key=settings.groq_api_key)


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Converts spoken audio into text using Groq's high-speed Whisper model."""
    client = get_groq_client()
    settings = get_settings()

    transcription = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=settings.whisper_model,
        response_format="text",
    )
    if isinstance(transcription, str):
        return transcription.strip()
    return getattr(transcription, "text", "").strip()


async def synthesize_speech(text: str, voice: str | None = None) -> bytes:
    """Synthesizes text into high-quality human-sounding speech using Edge Neural TTS."""
    settings = get_settings()
    selected_voice = voice or settings.tts_voice

    communicate = edge_tts.Communicate(text, selected_voice)
    buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk.get("type") == "audio":
            buffer.write(chunk["data"])

    return buffer.getvalue()


def audio_to_data_uri(audio_bytes: bytes) -> str:
    """Encodes MP3 audio bytes as a base64 data URI for direct web/app playback."""
    encoded = base64.b64encode(audio_bytes).decode("utf-8")
    return f"data:audio/mp3;base64,{encoded}"
