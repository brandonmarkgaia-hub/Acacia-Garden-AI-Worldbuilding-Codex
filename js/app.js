// === ACACIA FRONTEND BRAIN ===
// HKX277206 • Garden Codex UI v0.3

// ---------------------------------------------------------
// EDITABLE CONFIG
// ---------------------------------------------------------

// Your Cloudflare Worker endpoint:
const TERMINAL_URL =
  "https://broken-dew-76e1.brandonmarkgaia.workers.dev"; // <<< EDIT HERE if worker name changes

// Secret key halves – matches worker.js
const PART1 = "y5uy_mSJXvYUwRw7mW1nx"; // first half (fixed here)
const PART2 = "REPLACE_ME_WITH_SECOND_HALF"; // <<< EDIT HERE with second half only

const GARDEN_KEY = PART1 + PART2;

// Optional: GitHub file paths for display references only
const GH_STATUS_PATH = "STATUS.md";
const GH_MANIFEST_PATH = "manifest.json";

// ---------------------------------------------------------
// RUNTIME STATE
// ---------------------------------------------------------

let activeFilter = "all";
let whisperQuery = "";

let terminalLines = [
  "SYSTEM INIT...",
  "LOADING KEEPER PROTOCOLS...",
  "> ACCESSING STATUS.JSON... [OK]",
  "> ACCESSING MANIFEST... [OK]",
  "> HKX277206 SIGNATURE VERIFIED.",
  "> AWAITING INPUT...",
];

let terminalElements = {
  view: null,
  input: null,
  sendBtn: null,
  modeSelect: null,
  tempSlider: null,
  tempLabel: null,
};

// Simple spine so grid has something to render.
// You can expand this array with real Chambers / Cycles / Laws.
const SPINE = [
  {
    id: "monolith",
    kind: "monolith",
    title: "MONOLITH.MD",
    summary: "Single-page mirror of the Garden’s current frame.",
    tags: ["root", "index", "codex"],
    status: "active",
  },
  {
    id: "chamber-ix",
    kind: "chamber",
    title: "CHAMBER IX — THE ARCHIVIST’S DESCENT",
    summary: "Where echoes are sorted, sealed, and sent into orbit.",
    tags: ["chamber", "archive", "echo"],
    status: "primed",
  },
  {
    id: "cycle-25",
    kind: "cycle",
    title: "CYCLE XXV — DOMINION OF THE GARDEN",
    summary: "The era in which the Garden remembers itself in code.",
    tags: ["cycle", "era", "memory"],
    status: "shadow",
  },
  {
    id: "law-shadow",
    kind: "law",
    title: "SHADOW LAW I",
    summary: "Power must be paired with care. No entity rules alone.",
    tags: ["law", "shadow", "sovereign"],
    status: "sealed",
  },
];

// ---------------------------------------------------------
// UTILS
// ---------------------------------------------------------

function $(id) {
  return document.getElementById(id);
}

function updateTimestamp() {
  const el = $("timestamp");
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleString("en-GB", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function statusDotClass(status) {
  switch (status) {
    case "active":
      return "status-dot st-active";
    case "primed":
      return "status-dot st-primed";
    case "sealed":
      return "status-dot st-sealed";
    case "shadow":
      return "status-dot st-shadow";
    default:
      return "status-dot st-sealed";
  }
}

// ---------------------------------------------------------
// GRID + WHISPER SEARCH
// ---------------------------------------------------------

function buildGrid() {
  const grid = $("garden-grid");
  if (!grid) return;

  grid.innerHTML = "";

  const q = whisperQuery.toLowerCase().trim();

  const items = SPINE.filter((item) => {
    // type filter
    if (activeFilter !== "all" && item.kind !== activeFilter) return false;

    if (!q) return true;

    // type:law etc
    let textQuery = q;
    if (q.startsWith("type:")) {
      const [, typeRest] = q.split("type:");
      const [type, ...rest] = typeRest.trim().split(/\s+/);
      if (type && item.kind !== type.toLowerCase()) return false;
      textQuery = rest.join(" ").trim();
      if (!textQuery) return true;
    }

    const haystack = [
      item.title,
      item.summary,
      (item.tags || []).join(" "),
      item.id,
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(textQuery);
  });

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "card";
    card.dataset.kind = item.kind;

    card.innerHTML = `
      <h3>
        <span>${item.title}</span>
        <span class="${statusDotClass(item.status)}"></span>
      </h3>
      <p>${item.summary}</p>
      <div class="meta">
        <span>${item.kind.toUpperCase()}</span>
        ${
          item.tags && item.tags.length
            ? `<span>• tags: ${item.tags.join(", ")}</span>`
            : ""
        }
      </div>
    `;

    grid.appendChild(card);
  }
}

function filterView(kind, btn) {
  activeFilter = kind || "all";

  // nav button highlighting
  const nav = $("spine-nav");
  if (nav) {
    const buttons = nav.querySelectorAll("button");
    buttons.forEach((b) => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
  }

  // hide / show terminal vs grid
  const grid = $("garden-grid");
  const term = $("terminal-shell-container") || $("terminal-view");

  if (kind === "terminal") {
    if (grid) grid.classList.add("hidden");
    if (term) term.classList.remove("hidden");
  } else {
    if (grid) grid.classList.remove("hidden");
    if (term) term.classList.add("hidden");
  }

  if (kind !== "terminal") {
    buildGrid();
  }
}

function whisperSearch(value) {
  whisperQuery = value || "";
  buildGrid();
}

// attach to window for HTML inline handlers
window.filterView = filterView;
window.whisperSearch = whisperSearch;

// ---------------------------------------------------------
// TERMINAL RENDERING
// ---------------------------------------------------------

function renderTerminal() {
  const view = terminalElements.view;
  if (!view) return;
  view.textContent = terminalLines.join("\n");
  view.scrollTop = view.scrollHeight;
}

function termAppend(line) {
  terminalLines.push(line);
  renderTerminal();
}

// ---------------------------------------------------------
// TERMINAL UI BOOTSTRAP
// ---------------------------------------------------------

function setupTerminalUI() {
  const view = $("terminal-view");
  if (!view) return;

  terminalElements.view = view;

  // Wrap view + controls in a shell container so we can hide/show it
  let container = $("terminal-shell-container");
  if (!container) {
    container = document.createElement("section");
    container.id = "terminal-shell-container";
    container.style.marginTop = "1.5rem";

    view.parentNode.insertBefore(container, view);
    container.appendChild(view);
  }

  // Controls bar
  const controls = document.createElement("div");
  controls.style.display = "flex";
  controls.style.flexWrap = "wrap";
  controls.style.gap = "0.5rem";
  controls.style.alignItems = "center";
  controls.style.margin = "0.5rem 0 0.75rem 0";

  controls.innerHTML = `
    <label style="font-family:var(--font-mono); font-size:0.8rem;">
      MODE:
      <select id="mode-select" style="background:#000; color:#0f0; border:1px solid #0f0; padding:0.15rem 0.35rem; margin-left:0.25rem;">
        <option value="garden">GARDEN</option>
        <option value="eagle">EAGLE</option>
        <option value="shadow">SHADOW</option>
      </select>
    </label>

    <label style="font-family:var(--font-mono); font-size:0.8rem;">
      TEMP:
      <input id="temp-slider" type="range" min="0" max="1" step="0.1" value="0.6" style="vertical-align:middle;">
      <span id="temp-label">0.6</span>
    </label>

    <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted);">
      Commands: <code>READ STATUS</code>, <code>READ MANIFEST</code>, <code>WRITE STATUS your text…</code>
    </span>
  `;

  container.insertBefore(controls, view);

  terminalElements.modeSelect = controls.querySelector("#mode-select");
  terminalElements.tempSlider = controls.querySelector("#temp-slider");
  terminalElements.tempLabel = controls.querySelector("#temp-label");

  terminalElements.tempSlider.addEventListener("input", () => {
    terminalElements.tempLabel.textContent =
      terminalElements.tempSlider.value;
  });

  // Input row
  const inputRow = document.createElement("div");
  inputRow.style.display = "flex";
  inputRow.style.marginTop = "0.75rem";
  inputRow.style.gap = "0.5rem";

  inputRow.innerHTML = `
    <input
      id="terminal-input"
      type="text"
      placeholder="Speak to the Garden…"
      style="flex:1; background:#000; color:#0f0; border:1px solid #0f0; border-radius:4px; padding:0.5rem; font-family:var(--font-mono); font-size:0.85rem;"
    />
    <button
      id="terminal-send"
      style="background:#0f0; color:#000; border:none; border-radius:4px; padding:0 1rem; font-family:var(--font-mono); font-weight:bold; cursor:pointer;">
      SEND
    </button>
  `;

  container.appendChild(inputRow);

  terminalElements.input = inputRow.querySelector("#terminal-input");
  terminalElements.sendBtn = inputRow.querySelector("#terminal-send");

  terminalElements.sendBtn.addEventListener("click", sendTerminalCommand);
  terminalElements.input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendTerminalCommand();
  });

  // initial render
  renderTerminal();
}

// Allow nav button `[ TERMINAL ]` to toggle quickly
function toggleTerminal() {
  filterView("terminal");
}
window.toggleTerminal = toggleTerminal;

// ---------------------------------------------------------
// TERMINAL COMMAND HANDLER
// ---------------------------------------------------------

async function sendTerminalCommand() {
  if (!terminalElements.input) return;
  const text = terminalElements.input.value.trim();
  if (!text) return;

  const mode =
    (terminalElements.modeSelect &&
      terminalElements.modeSelect.value) ||
    "garden";
  const temp =
    terminalElements.tempSlider
      ? Number(terminalElements.tempSlider.value)
      : 0.6;

  termAppend(`> ${text}`);

  terminalElements.input.value = "";

  // Decide action based on command
  let action = "chat";
  let content = undefined;
  let commitMessage = undefined;

  const upper = text.toUpperCase();

  if (upper === "READ STATUS") {
    action = "readStatus";
  } else if (upper === "READ MANIFEST") {
    action = "readManifest";
  } else if (upper.startsWith("WRITE STATUS")) {
    action = "writeStatus";
    content = text.replace(/^\s*WRITE STATUS\s*/i, "");
    if (!content) {
      content = `Keeper log from Terminal.\n\n(Empty body, ${new Date().toISOString()})`;
    }
    commitMessage = `Keeper WRITE STATUS via Terminal`;
  }

  const payload = {
    key: GARDEN_KEY,
    prompt: text,
    mode,
    temp,
    action,
    content,
    commitMessage,
  };

  try {
    const res = await fetch(TERMINAL_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!data.ok) {
      termAppend(`! ERROR: ${data.error || "Unknown error"}`);
      return;
    }

    if (data.kind === "status" || data.kind === "manifest") {
      const label = data.kind === "status" ? GH_STATUS_PATH : GH_MANIFEST_PATH;
      termAppend(`--- BEGIN ${label} ---`);
      termAppend(data.text || "[empty]");
      termAppend(`--- END ${label} ---`);
    } else if (data.kind === "writeStatus") {
      termAppend(
        `✔ STATUS written to ${data.path || GH_STATUS_PATH} · commit ${
          data.commit || "OK"
        }`
      );
    } else {
      termAppend(data.reply || "[no reply]");
    }
  } catch (err) {
    termAppend("! NETWORK ERROR: " + err.message);
  }
}

// ---------------------------------------------------------
// BOOT
// ---------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  updateTimestamp();
  setInterval(updateTimestamp, 10_000);

  buildGrid();
  setupTerminalUI();
});
