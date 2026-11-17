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
                # Try finding a male or British voice if available
                for voice in voices:
                    if "david" in voice.name.lower() or "george" in voice.name.lower() or "english" in voice.name.lower():
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
    return b"".join(audio_chunks)

def speak(text: str):
    """High-level call to vocalize response."""
    print(f"[JARVIS SPEAKS]: {text}")
    if TTS_ENGINE == "edge":
        try:
            import edge_tts
            import subprocess
            import sys
            
            async def _generate_and_play():
                temp_file = os.path.join(tempfile.gettempdir(), "jarvis_voice.mp3")
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=EDGE_VOICE,
                    rate=SPEECH_RATE,
                    pitch=SPEECH_PITCH
                )
                await communicate.save(temp_file)
                if sys.platform == "win32":
                    # Use Windows Media Player or powershell sound player
                    ps_cmd = f'(New-Object Media.SoundPlayer "{temp_file}").PlaySync();'
                    # Or launch default media player hidden
                    subprocess.run(
                        ["powershell", "-c", f'Add-Type -AssemblyName presentationCore; $p = New-Object System.Windows.Media.MediaPlayer; $p.Open([System.Uri]"{temp_file}"); $p.Play(); Start-Sleep -Seconds 4'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            
            # Run in event loop or background thread
            threading.Thread(target=lambda: asyncio.run(_generate_and_play()), daemon=True).start()
            return
        except Exception as e:
            print(f"[Edge TTS failed, using fallback]: {e}")
            
    # Fallback to pyttsx3
    speak_local_pyttsx3(text)
