// ===============================================
// ACACIA • Garden Terminal Client (logs + signals)
// Worker base: broken-dew-76e1.brandonmarkgaia.workers.dev
// Routes used:
//   POST /log   -> store Keeper whisper in ACACIA_LOGS
//   GET  /state -> check latest urgent signal (Witness)
// ===============================================

// 🌐 Your Worker base URL (no trailing slash)
const GARDEN_WORKER_URL = "https://broken-dew-76e1.brandonmarkgaia.workers.dev";

// ---------- Helper: get elements ----------
function $(id) {
  return document.getElementById(id);
}

// Terminal elements
let terminalView;
let terminalInput;
let terminalSendBtn;

// ---------- Helper: print to terminal ----------
function printToTerminal(text, options) {
  options = options || {};
  const prefix = options.prefix || "";
  const color = options.color || "#00ff00";

  if (!terminalView) return;

  const line = prefix ? prefix + " " + text : text;
  const span = document.createElement("span");
  span.style.color = color;
  span.textContent = line + "\n";
  terminalView.appendChild(span);
  terminalView.scrollTop = terminalView.scrollHeight;
}

// ---------- Witness: check Garden state ----------
async function checkGardenState() {
  try {
    const res = await fetch(GARDEN_WORKER_URL + "/state", {
      method: "GET"
    });
    const data = await res.json();

    if (data && data.ok && data.urgent && data.last) {
      const e = data.last;
      const sev = String(e.severity || "").toUpperCase();
      const code = e.code || "UNKNOWN";
      const msg = e.message || "The Roots have stirred.";

      printToTerminal(sev + " • " + code + "\n" + msg, {
        prefix: "> WITNESS:",
        color: "#f1c40f"
      });
    }
  } catch (err) {
    // Silent failure is fine, we don't want to spam errors
  }
}

// ---------- Core: send a whisper (log entry) ----------
async function sendWhisper(promptText) {
  const prompt = (promptText || "").trim();
  if (!prompt) return;

  // 1. Print Keeper line locally
  printToTerminal(prompt, {
    prefix: "> KEEPER:",
    color: "#00ff00"
  });

  // 2. Decide severity (super simple heuristic for now)
  let severity = "info";
  if (/urgent|error|alert|warning/i.test(prompt)) {
    severity = "warn";
  }

  // 3. Send log to Garden
  try {
    const res = await fetch(GARDEN_WORKER_URL + "/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        severity: severity,
        code: "KEEPER_WHISPER",
        message: prompt
      })
    });

    const data = await res.json();

    if (data && data.ok) {
      printToTerminal("Whisper planted in ACACIA_LOGS.", {
        prefix: "> GARDEN:",
        color: "#2ecc71"
      });
    } else {
      const errMsg = (data && data.error) || "Failed to reach the Roots.";
      printToTerminal(errMsg, {
        prefix: "> ERROR:",
        color: "#e74c3c"
      });
    }
  } catch (err) {
    printToTerminal("Connection lost. The Roots are quiet.", {
      prefix: "> ERROR:",
      color: "#e74c3c"
    });
  }

  // 4. After every whisper, let the Witness speak if needed
  await checkGardenState();
}

// ---------- Event wiring ----------
function setupGardenTerminal() {
  terminalView = $("terminal-view");
  terminalInput = $("terminal-input");
  terminalSendBtn = $("terminal-send");

  if (!terminalView || !terminalInput) {
    console.warn("Garden terminal elements not found. Check IDs.");
    return;
  }

  // OPTIONAL: initial banner (if your HTML doesn't already print one)
  // printToTerminal("LINK: HKX277206 • CHANNEL: LOCAL", {
  //   prefix: "> SYSTEM:",
  //   color: "#7f8c8d"
  // });

  // Enter key -> send
  terminalInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      const value = terminalInput.value;
      terminalInput.value = "";
      sendWhisper(value);
    }
  });

  // Click on SEND button -> send (if button exists)
  if (terminalSendBtn) {
    terminalSendBtn.addEventListener("click", function () {
      const value = terminalInput.value;
      terminalInput.value = "";
      sendWhisper(value);
    });
  }

  // OPTIONAL: periodic passive check every few minutes
  // setInterval(checkGardenState, 3 * 60 * 1000);
}

// ---------- Bootstrap ----------
document.addEventListener("DOMContentLoaded", setupGardenTerminal);
