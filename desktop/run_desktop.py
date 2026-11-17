import sys
import threading
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import uvicorn
from backend.config import HOST, PORT, USER_NAME
from backend.server import app
from desktop.wake_word_daemon import WakeWordDaemon
from desktop.tray_icon import launch_tray
from backend.tts import speak

def start_api_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")

def main():
    print("=" * 60)
    print("  J.A.R.V.I.S. Personal AI Assistant - Desktop Daemon")
    print(f"  Mobile & Web Interface: http://localhost:{PORT}")
    print("=" * 60)

    # 1. Start Web & Mobile API Backend in background
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()

    # 2. Start Microphone Wake-Word Listener in background
    daemon = WakeWordDaemon()
    voice_thread = threading.Thread(target=daemon.listen_loop, daemon=True)
    voice_thread.start()

    # 3. Vocal greeting
    speak(f"Systems online, {USER_NAME}. Standing by.")

    # 4. Run System Tray
    try:
        def on_quit():
            daemon.stop()
            os._exit(0)

        launch_tray(on_quit_callback=on_quit)
    except Exception as e:
        print(f"[Tray icon unavailable, running in console mode]: {e}")
        try:
            while True:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            daemon.stop()
            print("\nShutting down J.A.R.V.I.S.")

if __name__ == "__main__":
    main()
