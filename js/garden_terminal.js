// ===============================================
// ACACIA • Garden Terminal Client
// HKX277206 • Front-end bridge to:
//   POST /log   (store Keeper whispers in KV)
//   GET  /state (check for urgent Witness signals)
//   GET  /health (initial ping)
// Worker: broken-dew-76e1.brandonmarkgaia.workers.dev
// ===============================================

(function () {
  const GARDEN_WORKER_URL =
    "https://broken-dew-76e1.brandonmarkgaia.workers.dev";

  let terminalView = null;
  let terminalInput = null;
  let terminalSendBtn = null;

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

        const badge = document.getElementById("global-status");
        if (badge) {
          badge.textContent = "SYSTEM: SIGNAL";
          badge.style.borderColor = "#f1c40f";
          badge.style.color = "#f1c40f";
        }
      }
    } catch (err) {
      // Silent fail
    }
  }

  async function sendWhisper(promptText) {
    const prompt = (promptText || "").trim();
    if (!prompt) return;

    printToTerminal(prompt, {
      prefix: "> KEEPER:",
      color: "#00ff00",
    });

    let severity = "info";
    if (/urgent|warning|alert|error|critical/i.test(prompt)) {
      severity = "warn";
    }

    try {
      const res = await fetch(GARDEN_WORKER_URL + "/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          severity: severity,
          code: "KEEPER_WHISPER",
          message: prompt,
          source: "KEEPER",
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

    await checkGardenState();
  }

  // Public hook used by index.html
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

  function setupGardenTerminal() {
    terminalView = $("terminal-view");
    terminalInput = $("terminal-input");
    terminalSendBtn = $("terminal-send");

    if (!terminalView || !terminalInput) {
      console.warn("[ACACIA] Garden terminal elements not found.");
      return;
    }

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
        // quiet
      }
    })();

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
  }

  document.addEventListener("DOMContentLoaded", setupGardenTerminal);
})();
