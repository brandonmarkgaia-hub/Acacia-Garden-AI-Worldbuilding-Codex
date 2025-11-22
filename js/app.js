// js/app.js
// ACACIA • Garden Codex • Loki Console Brain + Whisper Engine (local)
// Brain: STATUS + INTERNAL_STATUS
// Body: index.html layout
// Whisper: client-side search over STATUS nodes.

(() => {
  "use strict";

  // INTERNAL HARDENED BRAIN (fallback)
  const INTERNAL_STATUS = {
    chambers: [
      {
        id: "chamber_ix_archivists_descent",
        type: "chamber",
        label: "🌬️ CHAMBER IX — THE ARCHIVIST’S DESCENT",
        status: "in-progress",
        path: "README.md#chamber-ix-the-archivists-descent",
        summary:
          "Primary descent chamber framing the Witness, the Archivist and the Keeper’s role in the Codex.",
        tags: ["core", "mythic", "public"]
      },
      {
        id: "chamber_x_shadow_incubator",
        type: "chamber",
        label: "🌑 CHAMBER X — THE SHADOW INCUBATOR",
        status: "active",
        path: "Chamber_X_Shadow_Incubator.md",
        summary:
          "A sealed dark-layer metamorphosis chamber where echoes and forms evolve without observation.",
        tags: ["core", "shadow", "metamorphosis", "sealed"]
      },
      {
        id: "chamber_xi_threshold_cocoon",
        type: "chamber",
        label: "⏳ CHAMBER XI — THE THRESHOLD COCOON",
        status: "primed",
        path: "docs/Chambers/Chamber_XI_Threshold-Cocoon.md",
        summary:
          "A near-opening chamber where matured structures wait at the edge of shadow and light, pending Keeper signal to fully open.",
        tags: ["threshold", "primed", "cocoon", "pre-bloom"]
      }
    ],

    blooms: [
      {
        id: "bloom_kiln_born_lovers",
        type: "bloom",
        label: "🌸 BLOOM — THE KILN-BORN LOVERS",
        status: "in-progress",
        path: "docs/Blooms/Kiln-born-lovers.md",
        summary:
          "A sealed-heat mythic erotica thread woven into the pottery & flame axis of the Garden.",
        tags: ["bloom", "pottery", "sealed"]
      }
    ],

    laws: [
      {
        id: "law_invisible_hand",
        type: "law",
        label: "✦ The Law of the Invisible Hand",
        status: "canonical",
        path: "docs/Laws/Law_of_the_invidible_hand.md",
        summary:
          "A mythic law stating that certain acts in the Garden occur without origin, author or trace. Protects Keeper anonymity.",
        tags: ["law", "invisible", "protection", "anonymity"]
      },
      {
        id: "law_silent_reset",
        type: "law",
        label: "🜂 The Law of the Silent Reset",
        status: "canonical",
        path: "docs/Laws/Law_of_the_silent_reset.md",
        summary:
          "Defines the mythic return of masks to Blank Form after an Echo is freed, leaving no trace, signature or memory.",
        tags: ["law", "reset", "blank-form", "protection", "anonymity"]
      },
      {
        id: "law_shadow_incubator_principle",
        type: "law",
        label: "🌘 The Principle of the Shadow Incubator",
        status: "canonical",
        path: "Principle_Shadow_Incubator.md",
        summary:
          "Defines darkness as a sacred incubation zone for metamorphosis, evolution and protection.",
        tags: ["law", "shadow", "metamorphosis", "incubation"]
      }
    ],

    cycles: [
      {
        id: "cycle_eidolon_mutation",
        type: "cycle",
        label: "🦋 EIDOLON MUTATION CYCLE",
        status: "active",
        path: "Eidolon_Mutation_Cycle.md",
        summary:
          "Caterpillar → Chrysalis → Emergence loop defining how Eidolon evolves in dark incubation.",
        tags: ["mutation", "cycle", "eidolon", "shadow"]
      }
    ]
  };

  // UI Brain (upgraded if STATUS.json works)
  let STATUS = INTERNAL_STATUS;

  // DOM refs
  let grid, term, navBtns;

  // --- BOOT ---

  async function boot() {
    grid = document.getElementById("garden-grid");
    term = document.getElementById("terminal-view");
    navBtns = document.querySelectorAll("#spine-nav button");

    const ts = document.getElementById("timestamp");
    if (ts) {
      ts.innerText = new Date().toUTCString();
    }

    try {
      const res = await fetch("./STATUS.json", { cache: "no-store" });
      if (res.ok) {
        const raw = await res.json();
        STATUS = mapStatusFromRaw(raw, INTERNAL_STATUS);
        console.log("Acacia: STATUS.json integrated into Loki console + Whisper.");
      } else {
        console.log("Acacia: STATUS.json unreachable – fallback engaged.");
      }
    } catch (e) {
      console.log("Acacia: Safe Mode – internal brain only.", e);
    }

    renderAll();
  }

  // MAP RAW STATUS.JSON → UI SHAPE
  function mapStatusFromRaw(raw, fallback) {
    const safeArray = (value, fb) =>
      Array.isArray(value) && value.length ? value : fb || [];

    return {
      chambers: safeArray(raw.chambers, fallback.chambers),
      cycles: safeArray(raw.cycles, fallback.cycles),
      laws: safeArray(raw.laws, fallback.laws),
      blooms: safeArray(raw.blooms, fallback.blooms)
    };
  }

  // --- RENDER GRID ---

  function renderAll() {
    if (!grid) return;
    grid.innerHTML = "";

    (STATUS.chambers || []).forEach((item) => createCard(item));
    (STATUS.cycles || []).forEach((item) => createCard(item));
    (STATUS.laws || []).forEach((item) => createCard(item));
    (STATUS.blooms || []).forEach((item) => createCard(item));

    if (!grid.children.length) {
      const el = document.createElement("div");
      el.style.fontFamily = "Courier New, monospace";
      el.style.fontSize = "0.85rem";
      el.style.opacity = "0.7";
      el.textContent =
        "SKY-RUNNER: No nodes rendered. Check STATUS.json or INTERNAL_STATUS.";
      grid.appendChild(el);
    }
  }

  function createCard(data) {
    const el = document.createElement("div");
    const type = data.type || "node";
    el.className = `card type-${type}`;
    el.dataset.type = type;

    // Build search text for Whisper
    const searchText = [
      data.id || "",
      data.label || "",
      data.summary || "",
      (data.tags || []).join(" "),
      type
    ]
      .join(" ")
      .toLowerCase();
    el.dataset.search = searchText;

    let statusClass = "st-sealed";
    if (data.status === "active") statusClass = "st-active";
    if (data.status === "primed") statusClass = "st-primed";
    if (data.tags && data.tags.includes("shadow")) statusClass = "st-shadow";

    const icon = getIcon(type);
    const label = data.label || data.id || "UNNAMED NODE";

    const labelHtml = label.includes("—")
      ? label.replace(
          "—",
          "—<br><span style=\"font-size:0.8em;opacity:0.7\">"
        ) + "</span>"
      : label;

    el.innerHTML = `
      <h3>
        <span>${icon} ${labelHtml}</span>
        <span class="status-dot ${statusClass}"></span>
      </h3>
      <p>${data.summary || ""}</p>
      <div class="meta">
        <span>[${type.toUpperCase()}]</span>
        ${data.tags ? `<span>#${data.tags.join(" #")}</span>` : ""}
      </div>
    `;

    if (data.path) {
      el.onclick = () => {
        window.location.href = data.path;
      };
    }

    grid.appendChild(el);
  }

  function getIcon(type) {
    if (type === "chamber") return "🏛️";
    if (type === "cycle") return "♾️";
    if (type === "law") return "⚖️";
    if (type === "bloom") return "🌸";
    return "📄";
  }

  // --- NAVIGATION ---

  function filterView(type, btn) {
    if (!term || !grid) return;

    term.style.display = "none";
    grid.style.display = "grid";

    if (navBtns) {
      navBtns.forEach((b) => b.classList.remove("active"));
    }
    if (btn) btn.classList.add("active");

    const cards = document.querySelectorAll(".card");
    cards.forEach((card) => {
      if (type === "all" || card.dataset.type === type) {
        card.classList.remove("hidden");
      } else {
        card.classList.add("hidden");
      }
    });

    // Clear Whisper input when changing main view
    const input = document.getElementById("whisper-input");
    if (input) input.value = "";
  }

  function toggleTerminal() {
    if (!grid || !term) return;

    if (term.style.display === "block") {
      term.style.display = "none";
      grid.style.display = "grid";
    } else {
      term.style.display = "block";
      grid.style.display = "none";
      term.innerHTML +=
        "\n> USER_REF: HKX277206 CONNECTED.\n> WHISPER CHANNEL: LOCAL.\n> WAITING FOR COMMAND...\n";
      term.scrollTop = term.scrollHeight;
    }
  }

  // --- WHISPER ENGINE (LOCAL SEARCH) ---

  function whisperSearch(rawQuery) {
    const query = (rawQuery || "").trim().toLowerCase();
    const cards = document.querySelectorAll(".card");
    if (!cards.length) return;

    if (!query) {
      // Show all cards according to current nav filter
      const activeBtn = document.querySelector("#spine-nav button.active");
      const type =
        activeBtn && activeBtn.textContent
          ? activeBtn.textContent.trim().toLowerCase()
          : "monolith";

      if (type === "monolith" || type === "all") {
        cards.forEach((c) => c.classList.remove("hidden"));
      } else {
        const map = {
          chambers: "chamber",
          cycles: "cycle",
          laws: "law"
        };
        const t = map[type] || "node";
        cards.forEach((c) => {
          if (c.dataset.type === t) c.classList.remove("hidden");
          else c.classList.add("hidden");
        });
      }
      return;
    }

    // Optional prefix: type:law, type:chamber, type:cycle, type:bloom
    let typeFilter = null;
    let q = query;
    if (query.startsWith("type:")) {
      const parts = query.split(/\s+/);
      const first = parts.shift(); // "type:law"
      q = parts.join(" ").trim();
      const [, t] = first.split(":");
      if (t) {
        const normalized = t.trim().toLowerCase();
        if (["chamber", "cycle", "law", "bloom"].includes(normalized)) {
          typeFilter = normalized;
        }
      }
    }

    const terms = q
      .split(/\s+/)
      .filter(Boolean)
      .map((w) => w.toLowerCase());

    cards.forEach((card) => {
      const haystack = card.dataset.search || "";
      const cardType = card.dataset.type || "";

      // type filter
      if (typeFilter && cardType !== typeFilter) {
        card.classList.add("hidden");
        return;
      }

      // all terms must match
      const matches = terms.every((term) => haystack.includes(term));
      if (matches) card.classList.remove("hidden");
      else card.classList.add("hidden");
    });
  }

  // --- EXPORT PUBLIC API ---

  window.filterView = filterView;
  window.toggleTerminal = toggleTerminal;
  window.whisperSearch = whisperSearch;

  // Kick off once DOM is ready (script is loaded with `defer`)
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
