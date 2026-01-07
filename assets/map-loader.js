// Acacia Universal Map Loader — Keeper HKX277206 Edition

(function () {
  // Always resolve relative to repo root, no matter where the HTML lives
  function resolve(path) {
    const root = window.location.pathname.split("Acacia-Garden-AI-Worldbuilding-Codex")[0];
    return root + "Acacia-Garden-AI-Worldbuilding-Codex/" + path;
  }

  function injectButton() {
    const mapUrl = resolve("map.html");

    // 1 — Insert Map into Triad NAV if present
    const triad = document.getElementById("triad-nav");
    if (triad && !document.getElementById("acacia-map-btn")) {
      const btn = document.createElement("button");
      btn.id = "acacia-map-btn";
      btn.className = "triad-item";
      btn.textContent = "Map";
      btn.onclick = () => (window.location.href = mapUrl);
      triad.appendChild(btn);
    }

    // 2 — Floating bottom-right Map button (always visible)
    if (!document.getElementById("acacia-map-float")) {
      const wrap = document.createElement("div");
      wrap.id = "acacia-map-float";
      wrap.style = `
        position: fixed;
        bottom: 22px;
        right: 22px;
        z-index: 99999;
      `;

      wrap.innerHTML = `
        <button
          style="
            padding: 7px 16px;
            border-radius: 999px;
            background: #0f172a;
            color: #22c55e;
            border: 1px solid #22c55e;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.3);
          "
          onclick="window.location.href = '${mapUrl}'"
        >
          MAP
        </button>
      `;
      document.body.appendChild(wrap);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectButton);
  } else {
    injectButton();
  }
})();
