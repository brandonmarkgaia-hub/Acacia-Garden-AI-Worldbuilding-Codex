// ===============================================
// ACACIA • Garden Terminal Client
// HKX277206 • Front-end bridge to:
//   POST /log   (store Keeper whispers in KV)
//   GET  /state (check for urgent Witness signals)
// Worker: broken-dew-76e1.brandonmarkgaia.workers.dev
// ===============================================

(function () {
  // 🌐 Worker base URL (no trailing slash)
  const GARDEN_WORKER_URL =
    "https://broken-dew-76e1.brandonmarkgaia.workers.dev";

  // Cached DOM refs
  let terminalView = null;
  let terminalInput = null;
  let terminalSendBtn = null;

  // ---------- Helpers ----------

  function $(id) {
    return document.getElementById(id);
  }

  function printToTerminal(text, opts) {
    opts = opts || {};
    const prefix = opts.prefix || "";
    const color = opts.color || "#00ff00";

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
        method: "GET",
      });

      if (!res.ok) return;

      const data = await res.json();

      if (data && data.ok && data.urgent && data.last) {
        const e = data.last;
        const sev = String(e.severity || "").toUpperCase();
        const code = e.code || "UNKNOWN";
        const msg = e.message || "The Roots have stirred.";

        printToTerminal(sev + " • " + code + "\n" + msg, {
          prefix: "> WITNESS:",
          color: "#f1c40f",
        });
      }
    } catch (err) {
      // Silent fail – we don't want to spam errors in UI
    }
  }

  // ---------- Core: send whisper + log ----------

  async function sendWhisper(promptText) {
    const prompt = (promptText || "").trim();
    if (!prompt) return;

    // 1. Local echo
    printToTerminal(prompt, {
      prefix: "> KEEPER:",
      color: "#00ff00",
    });

    // 2. Basic severity detection
    let severity = "info";
    if (/urgent|warning|alert|error|critical/i.test(prompt)) {
      severity = "warn";
    }

    // 3. POST /log to Worker
    try {
      const res = await fetch(GARDEN_WORKER_URL + "/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          severity: severity,
          code: "KEEPER_WHISPER",
          message: prompt,
        }),
      });

      const data = await res.json();

      if (data && data.ok) {
        printToTerminal("Whisper planted in ACACIA_LOGS.", {
          prefix: "> GARDEN:",
          color: "#2ecc71",
        });
      } else {
        const errMsg =
          (data && data.error) || "Failed to reach the Roots.";
        printToTerminal(errMsg, {
          prefix: "> ERROR:",
          color: "#e74c3c",
        });
      }
    } catch (err) {
      printToTerminal("Connection lost. The Roots are quiet.", {
        prefix: "> ERROR:",
        color: "#e74c3c",
      });
    }

    // 4. Let the Witness speak if something is hot
    await checkGardenState();
  }

  // ---------- Public hook used by index.html ----------

  // This overrides the inline sendToGarden() from index.html
  window.sendToGarden = function () {
    if (!terminalInput) {
      terminalInput = $("terminal-input");
    }
    if (!terminalInput) return;

    const value = (terminalInput.value || "").trim();
    if (!value) return;

    terminalInput.value = "";
    sendWhisper(value);
  };

  // ---------- Setup ----------

  function setupGardenTerminal() {
    terminalView = $("terminal-view");
    terminalInput = $("terminal-input");
    terminalSendBtn = $("terminal-send"); // optional; your button uses onclick="sendToGarden()"

    if (!terminalView || !terminalInput) {
      console.warn(
        "[ACACIA] Garden terminal elements not found. Check IDs."
      );
      return;
    }

    // Health ping (optional – just to prove life)
    (async function () {
      try {
        const res = await fetch(GARDEN_WORKER_URL + "/health");
        if (!res.ok) return;
        const data = await res.json();
        if (data && data.ok) {
          printToTerminal("LINK ESTABLISHED • GARDEN ONLINE", {
            prefix: "> SYSTEM:",
            color: "#7f8c8d",
          });
        }
      } catch (err) {
        // quiet if offline
      }
    })();

    // Enter key already wired in index.html to sendToGarden()
    // but we’ll add a safety listener in case that changes later.
    terminalInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        window.sendToGarden();
      }
    });

    if (terminalSendBtn) {
      terminalSendBtn.addEventListener("click", function () {
        window.sendToGarden();
      });
    }

    // Optional passive check every few minutes:
    // setInterval(checkGardenState, 3 * 60 * 1000);
  }

  document.addEventListener("DOMContentLoaded", setupGardenTerminal);
})();
