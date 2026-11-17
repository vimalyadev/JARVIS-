import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

JARVIS_NAME = os.getenv("JARVIS_NAME", "Jarvis")
USER_NAME = os.getenv("USER_NAME", "Sir")
WAKE_WORDS = [w.strip().lower() for w in os.getenv("WAKE_WORDS", "jarvis,hey jarvis,ok jarvis").split(",") if w.strip()]

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

TTS_ENGINE = os.getenv("TTS_ENGINE", "edge").lower()
EDGE_VOICE = os.getenv("EDGE_VOICE", "en-GB-RyanNeural")
SPEECH_RATE = os.getenv("SPEECH_RATE", "+0%")
SPEECH_PITCH = os.getenv("SPEECH_PITCH", "+0Hz")
