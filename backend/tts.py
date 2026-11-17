import os
import asyncio
import tempfile
import threading
from pathlib import Path
from .config import TTS_ENGINE, EDGE_VOICE, SPEECH_RATE, SPEECH_PITCH

_pyttsx_lock = threading.Lock()

def speak_local_pyttsx3(text: str):
    """Fallback local offline text-to-speech engine."""
    def _run():
        try:
            import pyttsx3
            with _pyttsx_lock:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "david" in voice.name.lower() or "george" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.setProperty('rate', 185)
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            print(f"[TTS Fallback Error] {e}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

async def synthesize_edge_tts_bytes(text: str) -> bytes:
    """Uses edge-tts to generate high-fidelity neural audio bytes."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(
            text=text,
            voice=EDGE_VOICE,
            rate=SPEECH_RATE,
            pitch=SPEECH_PITCH
        )
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        result = b"".join(audio_chunks)
        if len(result) > 0:
            return result
        raise ValueError("Empty audio from Edge TTS")
    except Exception as e:
        print(f"[Edge TTS Error] {e}")
        raise

def speak(text: str):
    """High-level call to vocalize response on the server/desktop side."""
    print(f"[JARVIS SPEAKS]: {text}")
    speak_local_pyttsx3(text)
