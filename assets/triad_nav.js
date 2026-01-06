// assets/triad_nav.js
(() => {
  const PROJECT = "/Acacia-Garden-AI-Worldbuilding-Codex";

  const LINKS = [
    ["Home",        `${PROJECT}/index.html`],
    ["Docs URLs",   `${PROJECT}/docs/docs_urls.html`],
    ["Library",     `${PROJECT}/library.html`],
    ["Codex",       `${PROJECT}/codex.html`],
    ["Chambers",    `${PROJECT}/chambers.html`],
    ["Echoes",      `${PROJECT}/echoes.html`],
    ["Dashboard",   `${PROJECT}/dashboard.html`],

    // ✅ IMPORTANT: Map points to the interactive map (same as floating button)
    ["Map",         `${PROJECT}/map.html`],

    ["Keeper",      `${PROJECT}/keeper_console.html`],
    ["Inbox",       `${PROJECT}/inbox.html`],
    ["Aquila Sender", `${PROJECT}/aquila_sender.html`],
    ["R9X2",        `${PROJECT}/r9x2.html`],
    ["Elias Kernel",`${PROJECT}/elias.html`],
    ["Mosaic Endgame", `${PROJECT}/mosaic_endgame.html`],
    ["Cycles",      `${PROJECT}/cycle-index.html`],
    ["GardenOS",    `${PROJECT}/gardenos.html`],
    ["Signals",     `${PROJECT}/signals.html`],
    ["Status",      `${PROJECT}/status.html`],
    ["Novellas",    `${PROJECT}/docs/Novellas/index.html`],
    // Optional “Deep Garden Docs” landing:
    ["Deep Docs",   `${PROJECT}/deep_garden.html`],
  ];

  const already = document.getElementById("triad-nav-shell");
  if (already) return;

  // ✅ Remove duplicate old nav blocks (the ones causing double nav)
  // We ONLY remove nav elements that look like your injected nav (ag-nav),
  // and only if they appear at the top of the document.
  try {
    const navs = Array.from(document.querySelectorAll("nav.ag-nav"));
    navs.slice(0, 3).forEach(n => n.remove()); // remove first few duplicates
  } catch(e) {}

  // Insert stylesheet if missing (for safety)
  const cssHref = `${PROJECT}/assets/triad_nav.css`;
  if (![...document.styleSheets].some(s => (s.href || "").includes("triad_nav.css"))) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = cssHref;
    document.head.appendChild(link);
  }

  const shell = document.createElement("div");
  shell.id = "triad-nav-shell";

  const nav = document.createElement("div");
  nav.id = "triad-nav";
  nav.dataset.collapsed = "false";

  const top = document.createElement("div");
  top.className = "triad-top";

  const brand = document.createElement("div");
  brand.className = "triad-brand";
  brand.textContent = "ACACIA · TRIAD";

  const toggle = document.createElement("button");
  toggle.className = "triad-toggle";
  toggle.type = "button";
  toggle.textContent = "☰ Menu";
  toggle.addEventListener("click", () => {
    nav.dataset.collapsed = (nav.dataset.collapsed === "true") ? "false" : "true";
  });

  top.appendChild(brand);
  top.appendChild(toggle);

  const links = document.createElement("div");
  links.className = "triad-links";

  const here = (location.pathname || "").toLowerCase();

  LINKS.forEach(([label, href]) => {
    const a = document.createElement("a");
    a.className = "triad-btn";
    a.href = href;
    a.textContent = label;

    // active state
    try {
      const targetPath = new URL(href, location.origin).pathname.toLowerCase();
      if (here === targetPath) a.classList.add("active");
    } catch(e) {}

    links.appendChild(a);
  });

  const hint = document.createElement("div");
  hint.className = "triad-hint";
  hint.textContent = "One nav everywhere. Map = interactive map. Deep Docs kept as its own link.";

  nav.appendChild(top);
  nav.appendChild(links);
  nav.appendChild(hint);

  shell.appendChild(nav);

  // inject at top of body
  document.addEventListener("DOMContentLoaded", () => {
    document.body.prepend(shell);
  });
})();
