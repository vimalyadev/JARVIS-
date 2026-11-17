// ==========================================================
// J.A.R.V.I.S. Client Controller & Wake Word Engine
// ==========================================================

const WAKE_WORDS = ["jarvis", "hey jarvis", "ok jarvis"];
let isListening = false;
let recognition = null;
let rotationAngle = 0;
let pulseIntensity = 1;
let isSpeaking = false;

// Elements
const reactorCanvas = document.getElementById("reactorCanvas");
const ctx = reactorCanvas.getContext("2d");
const reactorLabel = document.getElementById("reactorLabel");
const wakeStatus = document.getElementById("wakeStatus");
const transcript = document.getElementById("transcript");
const commandInput = document.getElementById("commandInput");
const sendBtn = document.getElementById("sendBtn");
const micToggleBtn = document.getElementById("micToggleBtn");
const cpuStat = document.getElementById("cpuStat");
const ramStat = document.getElementById("ramStat");
const batteryStat = document.getElementById("batteryStat");
const osStat = document.getElementById("osStat");

// Audio Context for sound effects
let audioCtx = null;
function playChime(freq = 587.33, type = "sine") {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.4);
  } catch (e) {
    console.warn("Audio chime error:", e);
  }
}

// ----------------------------------------------------------
// Arc Reactor Canvas Animation
// ----------------------------------------------------------
function drawArcReactor() {
  const w = reactorCanvas.width;
  const h = reactorCanvas.height;
  const cx = w / 2;
  const cy = h / 2;

  ctx.clearRect(0, 0, w, h);

  rotationAngle += isListening ? 0.04 : 0.01;
  const currentPulse = isSpeaking ? 1 + Math.sin(Date.now() / 100) * 0.15 : (isListening ? 1 + Math.sin(Date.now() / 250) * 0.08 : 1);

  // Outer segmented ring
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rotationAngle);
  ctx.strokeStyle = isListening ? "#00ffff" : "rgba(0, 210, 255, 0.4)";
  ctx.lineWidth = 3;
  ctx.setLineDash([12, 8]);
  ctx.beginPath();
  ctx.arc(0, 0, 95 * currentPulse, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // Inner counter-rotating ring
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(-rotationAngle * 1.5);
  ctx.strokeStyle = "rgba(0, 119, 255, 0.6)";
  ctx.lineWidth = 4;
  ctx.setLineDash([20, 15]);
  ctx.beginPath();
  ctx.arc(0, 0, 75 * currentPulse, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // Core Glowing Circle
  const gradient = ctx.createRadialGradient(cx, cy, 10, cx, cy, 55 * currentPulse);
  gradient.addColorStop(0, isSpeaking ? "#ffffff" : "#b3f0ff");
  gradient.addColorStop(0.4, isListening ? "#00ffff" : "#00d2ff");
  gradient.addColorStop(1, "rgba(0, 119, 255, 0.1)");

  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(cx, cy, 50 * currentPulse, 0, Math.PI * 2);
  ctx.fill();

  // Central crossbars
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rotationAngle * 0.5);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.8)";
  ctx.lineWidth = 2;
  for (let i = 0; i < 4; i++) {
    ctx.rotate(Math.PI / 2);
    ctx.beginPath();
    ctx.moveTo(0, 25);
    ctx.lineTo(0, 48 * currentPulse);
    ctx.stroke();
  }
  ctx.restore();

  requestAnimationFrame(drawArcReactor);
}
drawArcReactor();

// ----------------------------------------------------------
// UI Message Log
// ----------------------------------------------------------
function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.className = `message ${sender.toLowerCase()}`;
  msg.innerText = text;
  transcript.appendChild(msg);
  transcript.scrollTop = transcript.scrollHeight;
}

// ----------------------------------------------------------
// Voice Synthesis (TTS)
// ----------------------------------------------------------
async function vocalizeResponse(text) {
  isSpeaking = true;
  reactorLabel.innerText = "SPEAKING";

  try {
    // Try streaming neural Edge-TTS from backend
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (res.ok) {
      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      audio.onended = () => {
        isSpeaking = false;
        reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
      };
      await audio.play();
      return;
    }
  } catch (err) {
    console.warn("Backend TTS stream fallback to browser voice:", err);
  }

  // Browser speech synthesis fallback
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 0.95;
    utterance.onend = () => {
      isSpeaking = false;
      reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
    };
    window.speechSynthesis.speak(utterance);
  } else {
    isSpeaking = false;
    reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
  }
}

// ----------------------------------------------------------
// Command Execution
// ----------------------------------------------------------
async function executeCommand(cmdText) {
  if (!cmdText.trim()) return;

  appendMessage("User", cmdText);
  commandInput.value = "";
  reactorLabel.innerText = "PROCESSING";

  try {
    const res = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cmdText, vocalize: false })
    });

    const data = await res.json();
    appendMessage("Jarvis", data.response);
    vocalizeResponse(data.response);
    if (data.status) updateTelemetry(data.status);
  } catch (err) {
    const errorMsg = "Apologies Sir, I encountered difficulty processing that request.";
    appendMessage("Jarvis", errorMsg);
    vocalizeResponse(errorMsg);
  }
}

function executeQuick(text) {
  executeCommand(text);
}

// ----------------------------------------------------------
// Web Speech Recognition & Wake-Word Engine
// ----------------------------------------------------------
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    wakeStatus.innerText = "Speech Recognition not natively supported in this browser. Use manual input.";
    micToggleBtn.disabled = true;
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    isListening = true;
    reactorLabel.innerText = "LISTENING";
    wakeStatus.className = "wake-status listening";
    wakeStatus.innerHTML = `Active Listener On &bull; Say <strong style="color:var(--accent-cyan);">"JARVIS"</strong>`;
    micToggleBtn.classList.add("active");
    micToggleBtn.innerText = "🛑 Stop Listening";
  };

  recognition.onend = () => {
    // If user intended auto-listening, automatically restart it (always listening mode)
    if (isListening) {
      try {
        recognition.start();
      } catch (e) {
        // Ignored if already started
      }
    } else {
      reactorLabel.innerText = "STANDBY";
      wakeStatus.className = "wake-status";
      wakeStatus.innerHTML = `Say <strong style="color:var(--accent-cyan);">"JARVIS"</strong> or tap the core to speak`;
      micToggleBtn.classList.remove("active");
      micToggleBtn.innerText = "🎙️ Auto-Listen";
    }
  };

  recognition.onresult = (event) => {
    const lastResultIndex = event.results.length - 1;
    const transcriptText = event.results[lastResultIndex][0].transcript.trim().toLowerCase();
    console.log("Transcribed speech:", transcriptText);

    // Detect wake word
    let matched = false;
    let cleanCommand = transcriptText;

    for (const ww of WAKE_WORDS) {
      if (transcriptText.includes(ww)) {
        matched = true;
        playChime(880); // Activation sound
        const idx = transcriptText.indexOf(ww);
        cleanCommand = transcriptText.substring(idx + ww.length).trim();
        break;
      }
    }

    if (matched) {
      if (cleanCommand.length > 0) {
        executeCommand(cleanCommand);
      } else {
        appendMessage("Jarvis", "Yes, Sir? How may I assist you?");
        vocalizeResponse("Yes, Sir?");
      }
    }
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    if (event.error === "not-allowed") {
      isListening = false;
      wakeStatus.innerText = "Microphone access blocked. Please allow mic permissions in browser settings.";
    }
  };
}

function toggleListening() {
  if (!recognition) setupSpeechRecognition();
  if (!recognition) return;

  if (isListening) {
    isListening = false;
    recognition.stop();
  } else {
    isListening = true;
    playChime(440);
    try {
      recognition.start();
    } catch (e) {
      console.warn("Recognition already active", e);
    }
  }
}

// ----------------------------------------------------------
// Telemetry Updates
// ----------------------------------------------------------
function updateTelemetry(data) {
  if (data.cpu_percent !== undefined) cpuStat.innerText = `${data.cpu_percent}%`;
  if (data.ram_percent !== undefined) ramStat.innerText = `${data.ram_percent}%`;
  if (data.battery_text) batteryStat.innerText = data.battery_text;
  if (data.os) osStat.innerText = data.os;
}

async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    if (res.ok) {
      const data = await res.json();
      updateTelemetry(data);
    }
  } catch (e) {
    // Backend offline or reconnecting
  }
}

// ----------------------------------------------------------
// Event Listeners
// ----------------------------------------------------------
sendBtn.addEventListener("click", () => executeCommand(commandInput.value));
commandInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") executeCommand(commandInput.value);
});
document.getElementById("reactorButton").addEventListener("click", toggleListening);
micToggleBtn.addEventListener("click", toggleListening);

// Register Service Worker for Mobile PWA
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}

// Initialize
setupSpeechRecognition();
fetchStatus();
setInterval(fetchStatus, 5000);
