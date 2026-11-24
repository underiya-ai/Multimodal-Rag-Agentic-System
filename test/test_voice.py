from unittest.mock import MagicMock, patch
import pytest

from multimodel_rag.services.voice import audio_to_data_uri, transcribe_audio


def test_audio_to_data_uri():
    fake_audio = b"ID3v2fakeaudiobytes"
    uri = audio_to_data_uri(fake_audio)
    assert uri.startswith("data:audio/mp3;base64,")


def test_transcribe_audio_with_mock():
    mock_groq = MagicMock()
    mock_groq.audio.transcriptions.create.return_value = "What is the net profit?"

    with patch("multimodel_rag.services.voice.get_groq_client", return_value=mock_groq):
        text = transcribe_audio(b"audio content", filename="voice.wav")
        assert text == "What is the net profit?"
