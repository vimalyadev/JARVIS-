// ==========================================================
// J.A.R.V.I.S. Client Controller & Wake Word Engine
// ==========================================================

const WAKE_WORDS = ["jarvis", "hey jarvis", "ok jarvis"];
let isListening = false;
let recognition = null;
let rotationAngle = 0;
let isSpeaking = false;
let audioUnlocked = false;

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

// ----------------------------------------------------------
// Audio Unlock - MUST happen on first user interaction
// ----------------------------------------------------------
let audioCtx = null;
function unlockAudio() {
  if (audioUnlocked) return;
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    // Play a silent buffer to unlock audio playback
    const buffer = audioCtx.createBuffer(1, 1, 22050);
    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(audioCtx.destination);
    source.start(0);
    audioUnlocked = true;
    console.log("[Audio] Playback unlocked");
  } catch (e) {
    console.warn("[Audio] Unlock failed:", e);
  }
}

// Unlock audio on ANY user interaction
document.addEventListener("click", unlockAudio, { once: false });
document.addEventListener("touchstart", unlockAudio, { once: false });
document.addEventListener("keydown", unlockAudio, { once: false });

function playChime(freq = 587.33) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.4);
  } catch (e) {
    console.warn("Chime error:", e);
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

  const gradient = ctx.createRadialGradient(cx, cy, 10, cx, cy, 55 * currentPulse);
  gradient.addColorStop(0, isSpeaking ? "#ffffff" : "#b3f0ff");
  gradient.addColorStop(0.4, isListening ? "#00ffff" : "#00d2ff");
  gradient.addColorStop(1, "rgba(0, 119, 255, 0.1)");

  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(cx, cy, 50 * currentPulse, 0, Math.PI * 2);
  ctx.fill();

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

// Small debug label showing what mic heard (shows below wake status)
function showHeard(text) {
  const heardEl = document.getElementById("heardDebug");
  if (heardEl) {
    heardEl.innerText = `🎤 Heard: "${text}"`;
    heardEl.style.opacity = "1";
    setTimeout(() => { heardEl.style.opacity = "0.4"; }, 2000);
  }
}

// ----------------------------------------------------------
// Voice Synthesis (TTS) - FIXED for browser autoplay
// ----------------------------------------------------------
function speakWithBrowser(text) {
  return new Promise((resolve) => {
    if (!("speechSynthesis" in window)) {
      console.warn("[TTS] Browser speechSynthesis not available");
      resolve();
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 0.9;
    utterance.volume = 1.0;
    utterance.lang = "en-GB";

    // Try to pick a good English voice
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v =>
      v.name.toLowerCase().includes("google uk english male") ||
      v.name.toLowerCase().includes("daniel") ||
      v.name.toLowerCase().includes("ryan") ||
      v.name.toLowerCase().includes("english") && v.lang.startsWith("en")
    );
    if (preferred) {
      utterance.voice = preferred;
    } else if (voices.length > 0) {
      // Find any English voice
      const enVoice = voices.find(v => v.lang.startsWith("en"));
      if (enVoice) utterance.voice = enVoice;
    }

    utterance.onend = () => {
      isSpeaking = false;
      reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
      resolve();
    };
    utterance.onerror = (e) => {
      console.warn("[TTS] Speech error:", e);
      isSpeaking = false;
      reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
      resolve();
    };

    isSpeaking = true;
    reactorLabel.innerText = "SPEAKING";
    window.speechSynthesis.speak(utterance);

    // Safety timeout - if speech doesn't end in 15 seconds, resolve anyway
    setTimeout(() => {
      if (isSpeaking) {
        isSpeaking = false;
        reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
        resolve();
      }
    }, 15000);
  });
}

async function vocalizeResponse(text) {
  isSpeaking = true;
  reactorLabel.innerText = "SPEAKING";

  // METHOD 1: Try server-side Edge neural TTS (sounds best)
  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (res.ok) {
      const blob = await res.blob();
      if (blob.size > 0) {
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.volume = 1.0;

        await new Promise((resolve) => {
          audio.onended = () => {
            isSpeaking = false;
            reactorLabel.innerText = isListening ? "LISTENING" : "STANDBY";
            URL.revokeObjectURL(audioUrl);
            resolve();
          };
          audio.onerror = (err) => {
            console.warn("[TTS Audio] Playback error, falling back to browser voice:", err);
            URL.revokeObjectURL(audioUrl);
            resolve();
          };
          audio.play().catch((playErr) => {
            console.warn("[TTS Audio] Autoplay blocked, using browser voice:", playErr);
            resolve();
          });
        });

        // If audio played successfully, we're done
        if (!isSpeaking) return;
      }
    }
  } catch (err) {
    console.warn("[TTS] Server TTS failed:", err);
  }

  // METHOD 2: Browser built-in speech synthesis (always works, no network needed)
  console.log("[TTS] Using browser speechSynthesis fallback");
  await speakWithBrowser(text);
}

// ----------------------------------------------------------
// Command Execution
// ----------------------------------------------------------
async function executeCommand(cmdText) {
  if (!cmdText.trim()) return;

  appendMessage("User", cmdText);
  commandInput.value = "";
  reactorLabel.innerText = "PROCESSING";

  // Pause recognition while processing to avoid hearing Jarvis's own voice
  if (recognition && isListening) {
    try { recognition.stop(); } catch (e) {}
  }

  try {
    const res = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cmdText, vocalize: false })
    });

    const data = await res.json();
    appendMessage("Jarvis", data.response);
    await vocalizeResponse(data.response);
    if (data.status) updateTelemetry(data.status);
  } catch (err) {
    const errorMsg = "Apologies Sir, I encountered difficulty processing that request.";
    appendMessage("Jarvis", errorMsg);
    await speakWithBrowser(errorMsg);
  }

  // Resume listening after speaking
  if (isListening) {
    try { recognition.start(); } catch (e) {}
  }
}

function executeQuick(text) {
  unlockAudio();
  executeCommand(text);
}

// ----------------------------------------------------------
// Web Speech Recognition & Wake-Word Engine
// ----------------------------------------------------------
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    wakeStatus.innerText = "Voice not supported in this browser. Use Chrome for voice commands, or type below.";
    micToggleBtn.disabled = true;
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;  // Show what's being heard in real-time
  recognition.lang = "en-US";
  recognition.maxAlternatives = 3;    // Check multiple interpretations

  recognition.onstart = () => {
    isListening = true;
    reactorLabel.innerText = "LISTENING";
    wakeStatus.className = "wake-status listening";
    wakeStatus.innerHTML = `Active Listener On &bull; Say <strong style="color:var(--accent-cyan);">"JARVIS"</strong>`;
    micToggleBtn.classList.add("active");
    micToggleBtn.innerText = "🛑 Stop Listening";
  };

  recognition.onend = () => {
    if (isListening && !isSpeaking) {
      // Auto-restart when it times out (browser stops after ~5s silence)
      setTimeout(() => {
        if (isListening && !isSpeaking) {
          try { recognition.start(); } catch (e) {}
        }
      }, 300);
    } else if (!isListening) {
      reactorLabel.innerText = "STANDBY";
      wakeStatus.className = "wake-status";
      wakeStatus.innerHTML = `Say <strong style="color:var(--accent-cyan);">"JARVIS"</strong> or tap the core to speak`;
      micToggleBtn.classList.remove("active");
      micToggleBtn.innerText = "🎙️ Auto-Listen";
    }
  };

  recognition.onresult = (event) => {
    // Get the latest final or interim result
    let finalTranscript = "";
    let interimTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      const text = result[0].transcript.trim().toLowerCase();

      if (result.isFinal) {
        finalTranscript = text;
      } else {
        interimTranscript = text;
      }
    }

    // Show what's being heard in real-time
    if (interimTranscript) {
      showHeard(interimTranscript);
    }

    // Only process final results to avoid duplicate triggers
    if (!finalTranscript) return;

    showHeard(finalTranscript);
    console.log("[Speech Final]:", finalTranscript);

    // Check ALL alternative transcriptions for the wake word
    let matched = false;
    let cleanCommand = "";

    // Check primary and alternative results
    const lastResult = event.results[event.results.length - 1];
    for (let alt = 0; alt < lastResult.length; alt++) {
      const altText = lastResult[alt].transcript.trim().toLowerCase();

      for (const ww of WAKE_WORDS) {
        if (altText.includes(ww)) {
          matched = true;
          const idx = altText.indexOf(ww);
          cleanCommand = altText.substring(idx + ww.length).trim();
          // Remove leading punctuation or filler
          cleanCommand = cleanCommand.replace(/^[,.\s]+/, "").trim();
          break;
        }
      }
      if (matched) break;
    }

    // Also check for common misheard variants of "Jarvis"
    if (!matched) {
      const misheardVariants = ["jarvis", "jarves", "jarvus", "jarwis", "javis", "jarby", "job is", "service"];
      for (const variant of misheardVariants) {
        if (finalTranscript.includes(variant)) {
          matched = true;
          const idx = finalTranscript.indexOf(variant);
          cleanCommand = finalTranscript.substring(idx + variant.length).trim();
          cleanCommand = cleanCommand.replace(/^[,.\s]+/, "").trim();
          break;
        }
      }
    }

    if (matched) {
      playChime(880);
      if (cleanCommand.length > 1) {
        executeCommand(cleanCommand);
      } else {
        // Just said "Jarvis" with no command - acknowledge and wait
        appendMessage("Jarvis", "Yes, Sir? How may I assist you?");
        vocalizeResponse("Yes, Sir?");
      }
    }
  };

  recognition.onerror = (event) => {
    console.warn("[Speech Error]:", event.error);
    if (event.error === "not-allowed") {
      isListening = false;
      wakeStatus.innerHTML = `<span style="color:#ff3366;">⚠️ Microphone blocked!</span> Click the lock icon 🔒 in the address bar → Allow Microphone`;
    } else if (event.error === "no-speech") {
      // Normal - just means silence, will auto-restart
    } else if (event.error === "aborted") {
      // We stopped it on purpose
    }
  };
}

function toggleListening() {
  unlockAudio();

  if (!recognition) setupSpeechRecognition();
  if (!recognition) return;

  if (isListening) {
    isListening = false;
    try { recognition.stop(); } catch (e) {}
  } else {
    isListening = true;
    playChime(440);
    try { recognition.start(); } catch (e) {
      console.warn("Recognition start error:", e);
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
  } catch (e) {}
}

// ----------------------------------------------------------
// Preload voices (Chrome loads them asynchronously)
// ----------------------------------------------------------
if ("speechSynthesis" in window) {
  speechSynthesis.getVoices(); // Trigger voice loading
  speechSynthesis.onvoiceschanged = () => {
    const voices = speechSynthesis.getVoices();
    console.log(`[TTS] ${voices.length} voices available`);
  };
}

// ----------------------------------------------------------
// Event Listeners
// ----------------------------------------------------------
sendBtn.addEventListener("click", () => { unlockAudio(); executeCommand(commandInput.value); });
commandInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") { unlockAudio(); executeCommand(commandInput.value); }
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
