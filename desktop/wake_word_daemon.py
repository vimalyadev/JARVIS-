import time
import speech_recognition as sr
from backend.config import WAKE_WORDS, USER_NAME
from backend.brain import think
from backend.tts import speak

class WakeWordDaemon:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.is_running = True

    def process_audio_text(self, text: str):
        cleaned = text.lower().strip()
        print(f"[Heard]: {cleaned}")

        # Check if wake word matches
        matched_wake_word = None
        for ww in WAKE_WORDS:
            if ww in cleaned:
                matched_wake_word = ww
                break

        if not matched_wake_word:
            return

        # Extract the command after the wake word if spoken together
        idx = cleaned.find(matched_wake_word)
        command_after = cleaned[idx + len(matched_wake_word):].strip()

        if command_after:
            print(f"[Command Detected]: {command_after}")
            response = think(command_after)
            speak(response)
        else:
            # Wake word spoken alone - acknowledge and listen for next phrase
            speak(f"Yes, {USER_NAME}?")
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                    followup_text = self.recognizer.recognize_google(audio)
                    print(f"[Followup]: {followup_text}")
                    response = think(followup_text)
                    speak(response)
            except Exception as e:
                print(f"[Listening timeout or error]: {e}")

    def listen_loop(self):
        print(f"[JARVIS Wake Daemon Active] Listening for wake words: {WAKE_WORDS}")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                while self.is_running:
                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=7)
                        try:
                            # Use Google Speech Recognition for accurate STT
                            text = self.recognizer.recognize_google(audio)
                            self.process_audio_text(text)
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            print(f"[Speech recognition network error]: {e}")
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        time.sleep(0.5)
        except Exception as e:
            print(f"[Microphone Initialization Error]: {e}")
            print("Make sure PyAudio and a functional microphone are installed.")

    def stop(self):
        self.is_running = False
