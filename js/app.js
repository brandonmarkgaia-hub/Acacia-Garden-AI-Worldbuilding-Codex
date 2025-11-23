// ===============================================
// ACACIA • Garden Terminal Client (v2)
// Talks to your Cloudflare Worker whisper endpoint
// HKX277206 • Local-use only
// ===============================================

// ⚙️ Config
const GARDEN_CONFIG = {
  // 🌐 Your Worker URL (backend)
  workerUrl: "https://broken-dew-76e1.brandonmarkgaia.workers.dev/",

  // 🔐 Local whisper key (must match PART2 in the Worker)
  // NOTE: Prefer keeping the real key out of public repos.
  whisperKey: "iy5uy_mSJXvYWRw7mW1nxH-vaKmPoCJl68HM2X-J0A",

  // ⏱ Timeouts & rate limits
  requestTimeoutMs: 45_000,       // 45 sec max per request
  minSendIntervalMs: 800,         // min gap between whispers
  maxHistory: 50                  // how many past commands to remember
};

// ---------- Helper: get elements safely ----------
function $(id) {
  return document.getElementById(id);
}

// Terminal elements (IDs must match your HTML)
let terminalView;
let terminalInput;
let terminalSendBtn;

// State
let isBusy = false;
let lastSendAt = 0;
let history = [];
let historyIndex = -1;

// ---------- Helper: print to terminal ----------
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

  // Support multi-line replies
  const parts = String(line).split(/\r?\n/);
  parts.forEach((part, idx) => {
    span.appendChild(document.createTextNode(part));
    if (idx < parts.length - 1) {
      span.appendChild(document.createElement("br"));
    }
  });

  terminalView.appendChild(span);
  terminalView.appendChild(document.createElement("br"));
  terminalView.scrollTop = terminalView.scrollHeight;
}

// ---------- Slash commands ----------
function handleLocalCommand(cmd) {
  const command = cmd.trim().toLowerCase();

  if (command === "/clear") {
    terminalView.innerHTML = "";
    printToTerminal("Terminal cleared. Roots listening.", {
      prefix: "> SYSTEM:",
      color: "#8e44ad",
      italic: true
    });
    return true;
  }

  if (command === "/help") {
    printToTerminal(
      [
        "Local commands:",
        "  /help   – show this list",
        "  /clear  – clear the terminal",
        "  /ping   – quick round-trip check"
      ].join("\n"),
      { prefix: "> SYSTEM:", color: "#8e44ad" }
    );
    return true;
  }

  if (command === "/ping") {
    printToTerminal("Pulse sent through the Roots…", {
      prefix: "> SYSTEM:",
      color: "#8e44ad"
    });
    // Let it fall through to actual sendWhisper (the Garden will answer)
    return false;
  }

  return false;
}

// ---------- Core: send whisper to the Garden ----------
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
  if (now - lastSendAt < GARDEN_CONFIG.minSendIntervalMs) {
    printToTerminal("Too many whispers at once. Breathe, Keeper.", {
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

  // 2. Show thinking line
  const thinkingSpan = document.createElement("span");
  thinkingSpan.style.color = "#f1c40f";
  thinkingSpan.style.fontStyle = "italic";
  thinkingSpan.textContent = "> GARDEN: Listening…";
  terminalView.appendChild(thinkingSpan);
  terminalView.appendChild(document.createElement("br"));
  terminalView.scrollTop = terminalView.scrollHeight;

  // 3. Call your Worker with timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), GARDEN_CONFIG.requestTimeoutMs);

  try {
    const res = await fetch(GARDEN_CONFIG.workerUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        key: GARDEN_CONFIG.whisperKey,
        prompt
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    thinkingSpan.remove();

    if (!res.ok) {
      printToTerminal(`HTTP ${res.status} – the wind hit a wall.`, {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
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
      return;
    }

    if (data.ok && data.reply) {
      printToTerminal(data.reply, {
        prefix: "> GARDEN:",
        color: "#00ff00"
      });
    } else {
      const errMsg = data && (data.error || data.message) || "Unknown response from Garden.";
      printToTerminal(errMsg, {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
    }
  } catch (err) {
    clearTimeout(timeoutId);
    thinkingSpan.remove();

    if (err.name === "AbortError") {
      printToTerminal("The whisper timed out. No echo returned.", {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
    } else {
      console.error("Whisper error:", err);
      printToTerminal("Connection lost. The Roots are quiet.", {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
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

  if (!terminalView || !terminalInput) {
    console.warn("Garden terminal elements not found. Check IDs.");
    return;
  }

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

  // Enter key -> send + history navigation
  terminalInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const value = terminalInput.value;
      terminalInput.value = "";
      sendWhisper(value);
      return;
    }

    // Command history (↑ / ↓)
    if (event.key === "ArrowUp") {
      if (history.length === 0) return;
      historyIndex = Math.max(0, historyIndex - 1);
      terminalInput.value = history[historyIndex] || "";
      event.preventDefault();
    } else if (event.key === "ArrowDown") {
      if (history.length === 0) return;
      historyIndex = Math.min(history.length, historyIndex + 1);
      terminalInput.value = history[historyIndex] || "";
      event.preventDefault();
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
