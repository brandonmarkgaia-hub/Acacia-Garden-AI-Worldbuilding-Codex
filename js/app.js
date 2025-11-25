// ===============================================
// ACACIA • Garden Terminal Client (v2 + STATUS)
// Talks to your Cloudflare Worker whisper endpoint
// HKX277206 • Local-use only
// ===============================================

// ⚙️ Config
const GARDEN_CONFIG = {
  // 🌐 Your Worker URL (backend)
  workerUrl: "https://broken-dew-76e1.brandonmarkgaia.workers.dev/",

  // 🔐 Shared whisper key (optional, NOT your OpenAI key)
  // If you set WHISPER_KEY in the Worker env, it must match this value.
  // Safe to keep this as a short random string – your real API key stays on Cloudflare only.
  whisperKey: "iy5uy_mSJXvYWRw7mW1nxH-vaKmPoCJl68HM2X-J0A",

  // ⏱ Timeouts & rate limits
  minDelayMs: 2000, // minimum delay between whispers
  requestTimeoutMs: 20000, // max time to wait for Worker response

  // 🧠 Behaviour
  maxHistory: 20, // how many prompts to remember locally (arrow up/down)
};

// ---------- DOM helpers ----------
function $(id) {
  return document.getElementById(id);
}

// ---------- Terminal state ----------
let terminalView = null;
let terminalInput = null;
let terminalSendBtn = null;

let statusDot = null;
let statusText = null;

let isBusy = false;
let lastSendAt = 0;

// history for up/down arrow recall
let history = [];
let historyIndex = 0;

// ---------- STATUS handling ----------
function setGardenStatus(state, label) {
  // state: "idle" | "online" | "offline" | "error"
  if (!statusDot || !statusText) return;

  let color = "#7f8c8d";
  let text = label || "";

  switch (state) {
    case "online":
      color = "#2ecc71";
      text = text || "Online";
      break;
    case "offline":
      color = "#e67e22";
      text = text || "Offline";
      break;
    case "error":
      color = "#e74c3c";
      text = text || "Error";
      break;
    case "idle":
    default:
      color = "#7f8c8d";
      text = text || "Idle";
      break;
  }

  statusDot.style.backgroundColor = color;
  statusText.textContent = text;
}

// ---------- Terminal print helpers ----------
function printToTerminal(text, options = {}) {
  if (!terminalView) return;
  const {
    prefix = "",
    color = "#00ff00",
    italic = false,
    bold = false
  } = options;

  const line = prefix ? `${prefix} ${text}` : text;
  const span = document.createElement("span");
  span.style.color = color;
  if (italic) span.style.fontStyle = "italic";
  if (bold) span.style.fontWeight = "600";

  // Support multi-line content
  const parts = line.split("\n");
  parts.forEach((part, idx) => {
    const lineSpan = span.cloneNode();
    lineSpan.textContent = part;
    terminalView.appendChild(lineSpan);
    if (idx < parts.length - 1) {
      terminalView.appendChild(document.createElement("br"));
    }
  });

  terminalView.appendChild(document.createElement("br"));
  terminalView.scrollTop = terminalView.scrollHeight;
}

// ---------- Local commands (/help, /clear, etc.) ----------
function handleLocalCommand(cmd) {
  const command = cmd.trim().toLowerCase();

  if (command === "/clear") {
    terminalView.innerHTML = "";
    printToTerminal("Terminal cleared. Roots listening.", {
      prefix: "> SYSTEM:",
      color: "#8e44ad",
      italic: true
    });
    setGardenStatus("idle");
    return true;
  }

  if (command === "/help") {
    printToTerminal(
      [
        "Local commands:",
        "  /help   – show this help",
        "  /clear  – clear the terminal view",
        "",
        "All other inputs are whispered to the Garden Worker.",
      ].join("\n"),
      {
        prefix: "> SYSTEM:",
        color: "#8e44ad"
      }
    );
    return true;
  }

  return false;
}

// ---------- Whisper to Cloudflare Worker ----------
async function sendWhisper(promptText) {
  const prompt = (promptText || "").trim();
  if (!prompt) return;

  // --- Local slash-commands (/clear, /help, etc.)
  if (prompt.startsWith("/")) {
    const handled = handleLocalCommand(prompt);
    if (handled) return;
  }

  // --- Rate limit + busy guard
  const now = Date.now();
  if (isBusy) {
    printToTerminal("Channel is already open. Wait for the Garden to answer.", {
      prefix: "> SYSTEM:",
      color: "#f1c40f"
    });
    return;
  }
  if (now - lastSendAt < GARDEN_CONFIG.minDelayMs) {
    printToTerminal("Slow down, Keeper. The Roots need a breath.", {
      prefix: "> SYSTEM:",
      color: "#f1c40f"
    });
    return;
  }

  isBusy = true;
  lastSendAt = now;

  // --- History tracking
  history.push(prompt);
  if (history.length > GARDEN_CONFIG.maxHistory) {
    history.shift();
  }
  historyIndex = history.length;

  // 1. Print user line
  printToTerminal(prompt, {
    prefix: "> KEEPER:",
    color: "#00ff00",
    bold: true
  });

  // 2. Show "thinking" status
  setGardenStatus("online", "Whispering…");

  // 3. Build payload
  const payload = {
    whisperKey: GARDEN_CONFIG.whisperKey,
    message: prompt,
    keeperId: "HKX277206",
    node: "Broken Dew",
    channel: "terminal",
    clientMeta: {
      agent: navigator.userAgent || "unknown",
      ts: new Date().toISOString()
    }
  };

  // 4. Send to Worker
  let timeoutId;
  try {
    const controller = new AbortController();
    timeoutId = setTimeout(() => controller.abort(), GARDEN_CONFIG.requestTimeoutMs);

    const thinkingSpan = document.createElement("span");
    thinkingSpan.style.color = "#95a5a6";
    thinkingSpan.textContent = "> GARDEN: ...";
    terminalView.appendChild(thinkingSpan);
    terminalView.appendChild(document.createElement("br"));
    terminalView.scrollTop = terminalView.scrollHeight;

    const res = await fetch(GARDEN_CONFIG.workerUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    thinkingSpan.remove();

    if (!res.ok) {
      setGardenStatus("error", `HTTP ${res.status}`);
      printToTerminal(
        `The Garden Worker refused the whisper (HTTP ${res.status}).`,
        {
          prefix: "> ERROR:",
          color: "#e74c3c"
        }
      );
      return;
    }

    let data;
    try {
      data = await res.json();
    } catch (parseErr) {
      printToTerminal("The Garden replied in broken glyphs (invalid JSON).", {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
      setGardenStatus("error", "Broken glyphs");
      return;
    }

    if (data.ok && data.reply) {
      printToTerminal(data.reply, {
        prefix: "> GARDEN:",
        color: "#00ff00"
      });
      setGardenStatus("online", "Last whisper OK");
    } else {
      const errMsg =
        (data && (data.error || data.message)) ||
        "Unknown response from Garden.";
      printToTerminal(errMsg, {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
      setGardenStatus("error");
    }
  } catch (err) {
    clearTimeout(timeoutId);
    // Remove thinking line if still visible
    const spans = terminalView.querySelectorAll("span");
    if (spans.length) {
      const lastSpan = spans[spans.length - 1];
      if (lastSpan.textContent && lastSpan.textContent.includes("...")) {
        lastSpan.remove();
      }
    }

    if (err.name === "AbortError") {
      printToTerminal("The whisper timed out. No echo returned.", {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
      setGardenStatus("offline", "Timed out");
    } else {
      console.error("Whisper error:", err);
      printToTerminal("Connection lost. The Roots are quiet.", {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
      setGardenStatus("offline");
    }
  } finally {
    isBusy = false;
  }
}

// ---------- Event wiring ----------
function setupGardenTerminal() {
  terminalView = $("terminal-view");
  terminalInput = $("terminal-input");
  terminalSendBtn = $("terminal-send"); // if you have a SEND button

  statusDot = $("garden-status-dot");
  statusText = $("garden-status-text");

  if (!terminalView || !terminalInput) {
    console.warn("Garden terminal elements not found. Check IDs.");
    return;
  }

  setGardenStatus("idle");

  // Initial banner
  printToTerminal("LINK: HKX277206 • CHANNEL: LOCAL • STATUS: LUCID", {
    prefix: "> SYSTEM:",
    color: "#8e44ad"
  });
  printToTerminal("Type /help for local commands.", {
    prefix: "> SYSTEM:",
    color: "#8e44ad",
    italic: true
  });

  // Enter to send
  terminalInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const value = terminalInput.value;
      terminalInput.value = "";
      sendWhisper(value);
    } else if (e.key === "ArrowUp") {
      // history back
      if (history.length === 0) return;
      historyIndex = Math.max(0, historyIndex - 1);
      terminalInput.value = history[historyIndex] || "";
      setTimeout(() => {
        terminalInput.setSelectionRange(
          terminalInput.value.length,
          terminalInput.value.length
        );
      }, 0);
    } else if (e.key === "ArrowDown") {
      // history forward
      if (history.length === 0) return;
      historyIndex = Math.min(history.length, historyIndex + 1);
      if (historyIndex === history.length) {
        terminalInput.value = "";
      } else {
        terminalInput.value = history[historyIndex] || "";
      }
      setTimeout(() => {
        terminalInput.setSelectionRange(
          terminalInput.value.length,
          terminalInput.value.length
        );
      }, 0);
    }
  });

  // Click on SEND button -> send (if button exists)
  if (terminalSendBtn) {
    terminalSendBtn.addEventListener("click", () => {
      const value = terminalInput.value;
      terminalInput.value = "";
      sendWhisper(value);
    });
  }
}

// ---------- Bootstrap ----------
document.addEventListener("DOMContentLoaded", setupGardenTerminal);
