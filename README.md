# ⚡ J.A.R.V.I.S. - Personal AI Assistant

> **"Just A Rather Very Intelligent System"**  
> A true hands-free, always-listening personal AI assistant engineered for both **Laptops** and **Mobile Devices (Android & iOS)**. Inspired by the architectural concepts of [OpenJarvis](https://github.com/open-jarvis/openjarvis) and Iron Man's J.A.R.V.I.S.

---

## 🌟 Key Features

- **🎙️ Zero-Touch Hands-Free Activation ("JARVIS")**:
  - **On Laptop**: Runs as a silent background listener. Simply say *"JARVIS"* or *"Hey Jarvis"* anytime to issue instructions.
  - **On Mobile**: Open or install the Progressive Web App (PWA) to your home screen with always-listening mode enabled.
- **🥷 Invisible Background Service (No Open Windows)**:
  - Registers directly into Windows Startup (`shell:startup`) via silent VBScript launcher. Boots with your computer and resides quietly in the system tray without cluttering your desktop with terminal windows.
- **📱 True Cross-Device Experience (Laptop & Mobile)**:
  - Full-featured **Progressive Web App (PWA)** styled like Tony Stark's holographic Arc Reactor HUD.
  - Tap **"Add to Home Screen"** on Chrome (Android) or Safari (iOS) to install it like a native mobile app.
- **🧠 Multi-Model Brain Engine**:
  - **Cloud Super-Speed**: Google Gemini API, Groq (sub-300ms lightning-fast Llama 3.1 voice replies), or OpenAI.
  - **100% Offline Local Mode**: Connects directly to [Ollama](https://ollama.ai) (`llama3.2`, `mistral`, `gemma`) for complete local privacy.
  - **Built-in Offline Fallback**: Works instantly with local heuristic skills even without an API key!
- **🔊 Natural Neural Voice (British Jarvis Persona)**:
  - Real-time Microsoft Edge neural voice synthesis (`en-GB-RyanNeural`) for natural cinematic vocal delivery, with offline `pyttsx3` fallback.
- **💻 Desktop System Control & Automation**:
  - Real-time system telemetry (CPU, RAM, Disk, and Battery diagnostics).
  - Voice-controlled volume adjustments (louder, quieter, mute).
  - Launch applications (Chrome, VS Code, Spotify, Notepad, YouTube, etc.).
  - Workstation lock screen and web search.

---

## 🏗️ Architecture

```
JARVIS/
├── backend/                  # Core Intelligence Server (FastAPI + AI Brain)
│   ├── brain.py              # LLM routing (Gemini / Groq / OpenAI / Ollama / Fallback)
│   ├── config.py             # Environment configuration loader
│   ├── server.py             # REST API, WebSockets, & PWA static file server
│   ├── tts.py                # Neural Edge-TTS and offline pyttsx3 voice synthesis
│   └── skills/               # Extensible skill modules
│       ├── system_control.py # App launching, volume control, screen lock
│       ├── system_info.py    # Hardware telemetry (CPU, RAM, Battery)
│       └── web_skills.py     # Weather, Wikipedia, Web Search, Date/Time
├── desktop/                  # Laptop Silent Background Service
│   ├── run_desktop.py        # Master runner (starts server + listener + tray icon)
│   ├── wake_word_daemon.py   # Continuous microphone listener for "JARVIS"
│   ├── tray_icon.py          # Arc Reactor Windows system tray icon
│   └── install_startup.py    # Registers silent startup into Windows boot
├── frontend/                 # Holographic Mobile & Laptop Web Client (PWA)
│   ├── index.html            # Futuristic Iron Man Arc Reactor HUD interface
│   ├── style.css             # Cyberpunk cyan glowing theme & responsive layout
│   ├── app.js                # Web Speech wake-word detector, audio visualizer, TTS
│   ├── manifest.json         # PWA configuration for Android & iOS
│   └── sw.js                 # Service worker for offline caching
├── start_jarvis.bat          # 1-Click launcher with automatic dependency install
├── start_jarvis_silent.vbs   # Silent launcher (no black command prompt window)
├── install_autostart.bat     # 1-Click setup to start Jarvis when laptop turns on
├── requirements.txt          # Python dependencies
└── .env.example              # Configuration template
```

---

## 🚀 Quick Start (Laptop Setup)

### 1. Prerequisites
- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/)) with *"Add Python to PATH"* checked.
- A functional microphone and speakers/headphones.

### 2. Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your free API key if desired:
- **Google Gemini API Key** (Free tier from [Google AI Studio](https://aistudio.google.com/))
- **Groq API Key** (Ultra-fast voice inference from [groq.com](https://groq.com/))
- Or leave empty to run the built-in offline skill rules or Ollama!

### 3. One-Click Launch
Double-click:
```bash
start_jarvis.bat
```
*(The first run automatically installs dependencies via `pip install -r requirements.txt`)*

### 4. Enable Silent Boot (Works without running any other app)
To have Jarvis start automatically every time you turn on your laptop without any terminal windows:
- Double-click **`install_autostart.bat`**
- That's it! Jarvis will now start silently in the background on every boot and listen for *"JARVIS"*.

---

## 📱 Mobile Setup (Android & iPhone)

You can interact with your Personal Jarvis from your smartphone on the same Wi-Fi network:

1. **Find your Laptop's Local IP**:
   - Open Command Prompt and type `ipconfig` (e.g. `192.168.1.15`).
2. **Open on your Phone's Browser**:
   - Navigate to: `http://<YOUR-LAPTOP-IP>:8000` (e.g. `http://192.168.1.15:8000`).
3. **Install as Native Mobile App**:
   - **Android (Chrome)**: Tap the 3 dots menu `⋮` ➔ **"Add to Home Screen"** or **"Install App"**.
   - **iOS (Safari)**: Tap the Share button `⎙` ➔ **"Add to Home Screen"**.
4. **Hands-Free Listening on Mobile**:
   - Tap **"Auto-Listen"** or tap the glowing **Arc Reactor** in the center.
   - Say **"JARVIS"** followed by your command!

---

## 🗣️ Voice Commands Cheatsheet

| Spoken Phrase | Action |
|---|---|
| *"Jarvis, system status"* | Reports live CPU load, RAM usage, and battery power level |
| *"Jarvis, what time is it?"* | Speaks current time and today's date |
| *"Jarvis, open YouTube"* | Opens YouTube in your default browser |
| *"Jarvis, open Chrome / Spotify / VS Code"* | Launches the specified desktop application |
| *"Jarvis, volume up / volume down / mute"* | Adjusts your laptop's master audio level |
| *"Jarvis, what is the weather in London?"* | Fetches current meteorological conditions |
| *"Jarvis, lock the screen"* | Immediately secures your workstation |
| *"Jarvis, who was Nikola Tesla?"* | Synthesizes an intelligent conversational summary |

---

## ⚙️ Configuration Reference (`.env`)

```ini
JARVIS_NAME=Jarvis
USER_NAME=Sir
WAKE_WORDS=jarvis,hey jarvis,ok jarvis

HOST=0.0.0.0
PORT=8000

# Choose: "gemini", "groq", "openai", "ollama", or "fallback"
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Neural Voice
TTS_ENGINE=edge
EDGE_VOICE=en-GB-RyanNeural
```

---

## 🛡️ License & Acknowledgements

Created with passion by [vimalyadev](https://github.com/vimalyadev).  
Architectural inspirations from [OpenJarvis](https://github.com/open-jarvis/openjarvis).
Licensed under the MIT License.
