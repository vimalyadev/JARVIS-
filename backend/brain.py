import json
import urllib.request
import urllib.parse
from .config import (
    JARVIS_NAME, USER_NAME, AI_PROVIDER,
    GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY,
    OLLAMA_BASE_URL, OLLAMA_MODEL
)
from .skills.system_control import open_application, set_volume, lock_screen
from .skills.system_info import get_status_speech, get_system_status
from .skills.web_skills import get_current_time_date, web_search, get_weather

SYSTEM_PROMPT = f"""You are {JARVIS_NAME}, the sophisticated, intelligent, highly capable personal AI assistant created for {USER_NAME}.
Tone and demeanor:
- Inspired by J.A.R.V.I.S. from Iron Man: polite, witty, calm, extremely knowledgeable, and proactive.
- Keep spoken answers concise, elegant, and directly to the point (1-3 sentences max) unless explicitly asked for a long breakdown.
- Always address the user politely as '{USER_NAME}'.
"""

def handle_quick_commands(text: str) -> str | None:
    """Interprets quick system actions before calling the LLM."""
    query = text.lower().strip()

    # Time & Date
    if any(q in query for q in ["what time is it", "current time", "what's the time", "tell me the time", "date today"]):
        return get_current_time_date()

    # System Status
    if any(q in query for q in ["system status", "battery status", "cpu status", "diagnostics", "power level", "how are you running"]):
        return get_status_speech()

    # Volume Control
    if "volume" in query or "sound" in query:
        if any(w in query for w in ["up", "increase", "raise", "louder"]):
            return set_volume("up")
        elif any(w in query for w in ["down", "decrease", "lower", "quieter"]):
            return set_volume("down")
        elif any(w in query for w in ["mute", "unmute", "silence"]):
            return set_volume("mute")

    # Lock Screen
    if any(q in query for q in ["lock screen", "lock laptop", "lock computer", "lock pc"]):
        return lock_screen()

    # Weather
    if "weather" in query:
        words = query.split()
        city = ""
        if "in" in words:
            city_index = words.index("in") + 1
            if city_index < len(words):
                city = " ".join(words[city_index:]).replace("?", "")
        return get_weather(city)

    # Launch Applications / Sites
    if query.startswith("open ") or query.startswith("launch "):
        target = query.replace("open ", "").replace("launch ", "").strip()
        return open_application(target)

    # Explicit search
    if query.startswith("search for ") or query.startswith("google "):
        target = query.replace("search for ", "").replace("google ", "").strip()
        return web_search(target)

    return None

def query_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\nUser: {prompt}"}]}
        ]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

def query_groq(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
    )
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode())
        return data["choices"][0]["message"]["content"].strip()

def query_openai(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        return data["choices"][0]["message"]["content"].strip()

def query_ollama(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {prompt}\nJarvis:",
        "stream": False
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
        return data["response"].strip()

def query_rule_fallback(prompt: str) -> str:
    p = prompt.lower()
    if any(w in p for w in ["hello", "hi", "hey"]):
        return f"Good day, {USER_NAME}. All systems are nominal and at your service."
    if any(w in p for w in ["who are you", "what are you"]):
        return f"I am {JARVIS_NAME}, your personal digital assistant, operational on both your mobile devices and workstation."
    if any(w in p for w in ["thank you", "thanks"]):
        return f"Always a pleasure to be of service, {USER_NAME}."
    if any(w in p for w in ["what can you do", "help", "commands"]):
        return f"I can manage your system, open applications, report diagnostics, search the web, monitor weather, and converse with you, {USER_NAME}."
    
    return f"Acknowledged, {USER_NAME}. I have received: '{prompt}'. You can configure a free Gemini, Groq, or Ollama API key in your .env file to enable full conversational intelligence."

def think(prompt: str) -> str:
    """Processes user input through skills first, then LLM brain."""
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return f"How may I assist you, {USER_NAME}?"

    # Check quick native skills first
    quick_result = handle_quick_commands(clean_prompt)
    if quick_result is not None:
        return quick_result

    # Route to LLM
    try:
        if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
            return query_gemini(clean_prompt)
        elif AI_PROVIDER == "groq" and GROQ_API_KEY:
            return query_groq(clean_prompt)
        elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
            return query_openai(clean_prompt)
        elif AI_PROVIDER == "ollama":
            return query_ollama(clean_prompt)
    except Exception as e:
        print(f"[Brain LLM Error]: {e}")

    # Fallback if no API key or network error
    return query_rule_fallback(clean_prompt)
