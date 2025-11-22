// ===============================================
// ACACIA • Garden Terminal Client
// Talks to your Cloudflare Worker whisper endpoint
// HKX277206 • Local-use only
// ===============================================

// 🌐 Your Worker URL (backend)
const GARDEN_WORKER_URL = "https://broken-dew-76e1.brandonmarkgaia.workers.dev/";

// 🔐 Local whisper key (must match PART2 in the Worker)
const LOCAL_WHISPER_KEY = "iy5uy_mSJXvYWRw7mW1nxH-vaKmPoCJl68HM2X-J0A";

// ---------- Helper: get elements safely ----------
function $(id) {
  return document.getElementById(id);
}

// Terminal elements (IDs must match your HTML)
let terminalView;
let terminalInput;
let terminalSendBtn;

// ---------- Helper: print to terminal ----------
function printToTerminal(text, options = {}) {
  if (!terminalView) return;
  const { prefix = "", color = "#00ff00" } = options;

  // Ensure we keep the existing text and append new line
  const line = prefix ? `${prefix} ${text}` : text;
  const span = document.createElement("span");
  span.style.color = color;
  span.textContent = line + "\n";

  terminalView.appendChild(span);
  terminalView.scrollTop = terminalView.scrollHeight;
}

// ---------- Core: send whisper to the Garden ----------
async function sendWhisper(promptText) {
  const prompt = (promptText || "").trim();
  if (!prompt) return;

  // 1. Print user line
  printToTerminal(prompt, { prefix: "> KEEPER:", color: "#00ff00" });

  // 2. Show thinking line
  const thinkingId = "thinking-" + Date.now();
  const thinkingSpan = document.createElement("span");
  thinkingSpan.id = thinkingId;
  thinkingSpan.style.color = "#f1c40f";
  thinkingSpan.textContent = "> GARDEN: Listening…\n";
  terminalView.appendChild(thinkingSpan);
  terminalView.scrollTop = terminalView.scrollHeight;

  try {
    // 3. Call your Worker
    const res = await fetch(GARDEN_WORKER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        key: LOCAL_WHISPER_KEY,
        prompt
      })
    });

    if (!res.ok) {
      throw new Error("HTTP " + res.status);
    }

    const data = await res.json();

    // Remove the thinking line
    thinkingSpan.remove();

    if (data.ok && data.reply) {
      printToTerminal(data.reply, { prefix: "> GARDEN:", color: "#00ff00" });
    } else {
      const errMsg = data.error || "Unknown response from Garden.";
      printToTerminal(errMsg, { prefix: "> ERROR:", color: "#e74c3c" });
    }
  } catch (err) {
    console.error("Whisper error:", err);
    thinkingSpan.remove();
    printToTerminal("Connection lost. The Roots are quiet.", {
      prefix: "> ERROR:",
      color: "#e74c3c"
    });
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

  // Initial banner line (optional; your HTML already prints some)
  // printToTerminal("LINK: HKX277206 • CHANNEL: LOCAL", { prefix: ">", color: "#00ff00" });

  // Enter key -> send
  terminalInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const value = terminalInput.value;
      terminalInput.value = "";
      sendWhisper(value);
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
