(() => {
  // ===== Triad Nav (idempotent, dedupe-safe, works across /docs and /docs/Archives) =====

  const REPO = "Acacia-Garden-AI-Worldbuilding-Codex";

  function computeBase() {
    // Works on GitHub Pages: https://<user>.github.io/<REPO>/...
    // Also works locally: /...
    const p = location.pathname || "/";
    const idx = p.indexOf("/" + REPO + "/");
    if (idx >= 0) return p.slice(0, idx + REPO.length + 2); // includes trailing slash
    return "/"; // local/dev
  }

  const BASE = computeBase();

  function abs(href) {
    // Accept already-absolute http(s) or root-relative
    if (/^https?:\/\//i.test(href)) return href;
    if (href.startsWith("/")) return href;
    return BASE + href.replace(/^\.?\//, "");
  }

  function ensureStyles() {
    if (document.getElementById("triad-nav-style")) return;
    const s = document.createElement("style");
    s.id = "triad-nav-style";
    s.textContent = `
      .triad-nav-wrap{position:sticky;top:0;z-index:9999;background:rgba(5,8,18,.82);backdrop-filter:blur(10px);
        border-bottom:1px solid rgba(255,255,255,.08)}
      .triad-nav{max-width:1100px;margin:0 auto;padding:12px 14px;display:flex;flex-direction:column;gap:10px}
      .triad-brand{display:flex;align-items:center;gap:10px;justify-content:space-between}
      .triad-title{letter-spacing:.22em;font-size:14px;color:#9effb6;font-weight:700}
      .triad-menu-btn{appearance:none;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.05);
        color:#d7deff;border-radius:12px;padding:10px 14px;font-weight:600}
      .triad-links{display:flex;flex-wrap:wrap;gap:10px}
      .triad-a{display:inline-flex;align-items:center;justify-content:center;padding:10px 14px;border-radius:14px;
        border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);color:#d7deff;text-decoration:none;
        font-weight:650}
      .triad-a:hover{border-color:rgba(158,255,182,.45)}
      .triad-a.active{outline:2px solid rgba(158,255,182,.35);border-color:rgba(158,255,182,.35)}
      .triad-links[hidden]{display:none !important}
      @media (max-width:540px){
        .triad-links{gap:8px}
        .triad-a{padding:9px 12px;border-radius:12px;font-weight:700}
      }
    `;
    document.head.appendChild(s);
  }

  function buildNavHTML() {
    // Add the pages you explicitly asked about:
    const items = [
      ["Home", "index.html"],
      ["Docs URLs", "docs/docs_urls.html"],
      ["Library", "library.html"],
      ["Codex", "codex.html"],
      ["Chambers", "chambers.html"],
      ["Echoes", "echoes.html"],
      ["Dashboard", "dashboard.html"],
      ["Map", "deep_garden.html"],
      ["Keeper", "keeper_console.html"],
      ["Inbox", "inbox.html"],

      // Your “missing” ones:
      ["Aquila Sender", "aquila_sender.html"],
      ["R9X2", "r9x2.html"],
      ["Elias Kernel", "elias.html"],
      ["Mosaic Endgame", "mosaic_endgame.html"],

      // Optional / common:
      ["Cycles", "cycle-index.html"],
      ["GardenOS", "gardenos.html"],
      ["Signals", "signals.html"],
      ["Status", "status.html"],
      ["Novellas", "docs/Novellas/index.html"],
    ];

    const current = (location.pathname || "").toLowerCase();

    const links = items.map(([label, href]) => {
      const url = abs(href);
      const active = current.includes("/" + href.toLowerCase()) ? "active" : "";
      return `<a class="triad-a ${active}" href="${url}">${label}</a>`;
    }).join("");

    return `
      <div class="triad-nav-wrap" data-triad-nav="1">
        <div class="triad-nav">
          <div class="triad-brand">
            <div class="triad-title">ACACIA · TRIAD</div>
            <button class="triad-menu-btn" type="button" data-triad-toggle="1">☰ Menu</button>
          </div>
          <div class="triad-links" data-triad-links="1">
            ${links}
          </div>
        </div>
      </div>
    `;
  }

  function removeDuplicateNavs() {
    const navs = Array.from(document.querySelectorAll("[data-triad-nav='1']"));
    if (navs.length <= 1) return;
    // Keep the first, remove the rest
    navs.slice(1).forEach(n => n.remove());
  }

  function mountNav() {
    ensureStyles();

    // If a nav already exists (from older injected HTML), do not add another.
    if (document.querySelector("[data-triad-nav='1']")) {
      removeDuplicateNavs();
      return;
    }

    const html = buildNavHTML();

    // Prefer a dedicated mount point (nav_block.html has one)
    const mount = document.getElementById("triad-nav-mount");
    if (mount) {
      mount.innerHTML = html;
    } else {
      // Otherwise inject at top of body
      document.body.insertAdjacentHTML("afterbegin", html);
    }

    // Wire toggle
    const toggle = document.querySelector("[data-triad-toggle='1']");
    const links = document.querySelector("[data-triad-links='1']");
    if (toggle && links) {
      toggle.addEventListener("click", () => {
        links.hidden = !links.hidden;
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountNav);
  } else {
    mountNav();
  }
})();
