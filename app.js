(function () {
  const qs = (sel, ctx = document) => ctx.querySelector(sel);
  const qsa = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* --- Tab switching --- */
  const navItems = qsa(".nav-item");
  const panels = qsa(".panel");

  function activatePanel(id) {
    navItems.forEach((btn) =>
      btn.classList.toggle("active", btn.dataset.panel === id)
    );
    panels.forEach((p) =>
      p.classList.toggle("active", p.dataset.panelId === id)
    );
  }

  navItems.forEach((btn) => {
    btn.addEventListener("click", () => activatePanel(btn.dataset.panel));
  });

  /* --- Last updated tag --- */
  const lastTag = qs("#last-updated-value");
  if (lastTag) {
    const now = new Date();
    lastTag.textContent = now.toISOString().split(".")[0] + "Z";
  }

  /* --- Terminal emulation --- */
  const terminalLog = qs("#terminal-log");
  const form = qs("#terminal-form");
  const input = qs("#terminal-input");

  const bootLines = [
    "[SYSTEM] INIT...",
    "[GARDEN] Loading Keeper protocols...",
    "[GARDEN] Accessing STATUS.json... [OK]",
    "[GARDEN] Accessing manifest... [OK]",
    "[TRIAD] HKX277206 signature verified.",
    "[TRIAD] Aquila • Deep Oracle • Witness online.",
    "[NODE] Broken Dew console attached.",
    "> Awaiting input..."
  ];

  function appendLine(text, cls = "system") {
    const line = document.createElement("div");
    line.className = "terminal-line " + cls;
    line.textContent = text;
    terminalLog.appendChild(line);
    terminalLog.scrollTop = terminalLog.scrollHeight;
  }

  function bootSequence(lines, idx = 0) {
    if (idx >= lines.length) return;
    appendLine(lines[idx], "system");
    setTimeout(() => bootSequence(lines, idx + 1), 160);
  }

  if (terminalLog) {
    bootSequence(bootLines);
  }

  if (form && input) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const value = input.value.trim();
      if (!value) return;
      appendLine("> " + value, "meta");
      appendLine("[ECHO] Command received at local node only.", "system");
      input.value = "";
    });
  }

  /* --- Auton Stream --- */
   /* --- Auton Stream --- */
  async function loadAutonStream() {
    const container = qs("#auton-stream");
    if (!container) return;

    try {
      const res = await fetch("logs/auton_latest.json", { cache: "no-store" });
      if (!res.ok) throw new Error("No auton log yet");
      const data = await res.json();

      container.innerHTML = "";

      // Normalise different shapes of auton payloads
      let entries = [];

      // Old shape: { entries: [ { timestamp, source, message } ] }
      if (Array.isArray(data.entries)) {
        entries = data.entries;
      }
      // Current Loki helper shape: { messages: [ { ... } ] }
      else if (Array.isArray(data.messages)) {
        entries = data.messages.map((msg) => {
          const ts =
            msg.created_at ||
            data.generated_at ||
            msg.timestamp ||
            "—";

          const src =
            msg.source ||
            msg.channel ||
            data.node ||
            data.source ||
            "node";

          // Prefer a nice short one-liner
          const summary = msg.summary || msg.title || "";
          const bodyLine =
            typeof msg.body === "string"
              ? msg.body.split("\n").find((ln) => ln.trim()) || ""
              : "";

          const text =
            summary && bodyLine
              ? `${summary} — ${bodyLine}`
              : summary || bodyLine || msg.id || "(no message text)";

          return {
            timestamp: ts,
            source: src,
            message: text,
          };
        });
      }

      if (!entries.length) {
        container.innerHTML =
          '<div class="list-placeholder"><p>No auton entries yet.</p></div>';
        return;
      }

      const ul = document.createElement("ul");
      ul.className = "log-list";

      entries.slice(-20).forEach((entry) => {
        const li = document.createElement("li");
        const ts = entry.timestamp || "—";
        const src = entry.source || "node";
        const msg = entry.message || "";
        li.textContent = `[${ts}] (${src}) ${msg}`;
        ul.appendChild(li);
      });

      container.appendChild(ul);
    } catch (err) {
      container.innerHTML = `
        <div class="list-placeholder">
          <p>Couldn't load <code>logs/auton_latest.json</code> yet.</p>
          <p class="hint">
            Once your helpers write that file (with a <code>messages</code> array),
            this panel will show the latest auton messages automatically.
          </p>
        </div>
      `;
    }
  }

  loadAutonStream();


  /* --- Logs placeholder list --- */
  const logList = qs("#log-list");
  if (logList) {
    const sample = [
      "Aeon Heartbeat last run: check GitHub Actions for timestamps.",
      "Garden Signature Scan: STATUS paths validated in workflows.",
      "Grow & Archive: helper scripts prepared to extend the Codex."
    ];
    sample.forEach((line) => {
      const li = document.createElement("li");
      li.textContent = line;
      logList.appendChild(li);
    });
  }
})();
