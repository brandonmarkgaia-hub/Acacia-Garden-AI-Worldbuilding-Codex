(() => {
  const ROOT = "/Acacia-Garden-AI-Worldbuilding-Codex/";

  // Prevent double-inject
  if (document.getElementById("triad-nav")) return;

  // Build once
  const nav = document.createElement("div");
  nav.id = "triad-nav";
  nav.setAttribute("data-triad-nav", "1");

  const style = document.createElement("style");
  style.textContent = `
    #triad-nav{
      position: sticky;
      top: 0;
      z-index: 99999;
      background: rgba(2,6,23,0.92);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid rgba(148,163,184,0.18);
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    #triad-nav .tn-wrap{
      display:flex;
      align-items:center;
      gap:12px;
      padding:10px 12px;
      max-width:1100px;
      margin:0 auto;
      box-sizing:border-box;
    }
    #triad-nav .tn-title{
      font-weight:800;
      letter-spacing:.12em;
      text-transform:uppercase;
      font-size:12px;
      color:#22c55e;
      white-space:nowrap;
    }
    #triad-nav .tn-links{
      display:flex;
      flex-wrap:wrap;
      gap:10px;
      align-items:center;
    }
    #triad-nav a{
      color:#cbd5e1;
      text-decoration:none;
      font-size:13px;
      padding:6px 8px;
      border-radius:10px;
      border:1px solid rgba(148,163,184,0.12);
      background: rgba(15,23,42,0.35);
    }
    #triad-nav a:hover{
      border-color: rgba(34,197,94,0.45);
      background: rgba(34,197,94,0.08);
      color:#e2e8f0;
    }
    #triad-nav a.tn-current{
      border-color: rgba(34,197,94,0.6);
      color:#22c55e;
      background: rgba(34,197,94,0.10);
    }
    #triad-nav .tn-spacer{ flex:1; }
    #triad-nav button.tn-menu{
      display:none;
      background: rgba(15,23,42,0.35);
      border:1px solid rgba(148,163,184,0.18);
      color:#e2e8f0;
      padding:6px 10px;
      border-radius:10px;
      font-size:13px;
    }
    @media (max-width: 720px){
      #triad-nav .tn-links{ display:none; }
      #triad-nav button.tn-menu{ display:inline-flex; align-items:center; gap:8px; }
      #triad-nav[data-open="1"] .tn-links{
        display:flex;
        width:100%;
        padding:0 12px 12px;
      }
      #triad-nav[data-open="1"] .tn-wrap{ flex-wrap:wrap; }
    }
  `;

  const here = location.pathname.replace(/\/+$/, "");
  const items = [
    ["Home", ROOT + "index.html"],
    ["Docs URLs", ROOT + "docs/docs_urls.html"],
    ["Library", ROOT + "library.html"],
    ["Codex", ROOT + "codex.html"],
    ["Chambers", ROOT + "chambers.html"],
    ["Echoes", ROOT + "echoes.html"],
    ["Dashboard", ROOT + "dashboard.html"],
    ["Map", ROOT + "map.html"],
    ["Keeper", ROOT + "keeper_console.html"],
    ["Inbox", ROOT + "inbox.html"]
  ];

  nav.innerHTML = `
    <div class="tn-wrap">
      <div class="tn-title">ACACIA · TRIAD</div>
      <button class="tn-menu" type="button" aria-label="Toggle navigation">☰ Menu</button>
      <div class="tn-links"></div>
      <div class="tn-spacer"></div>
    </div>
  `;

  const linksBox = nav.querySelector(".tn-links");
  items.forEach(([label, href]) => {
    const a = document.createElement("a");
    a.href = href;
    a.textContent = label;
    // current-page highlight (best-effort)
    try {
      const targetPath = new URL(href, location.origin).pathname.replace(/\/+$/, "");
      if (targetPath === here) a.classList.add("tn-current");
    } catch {}
    linksBox.appendChild(a);
  });

  nav.querySelector(".tn-menu").addEventListener("click", () => {
    nav.dataset.open = nav.dataset.open === "1" ? "0" : "1";
  });

  // Insert at top of body
  document.head.appendChild(style);
  document.body.insertBefore(nav, document.body.firstChild);
})();
