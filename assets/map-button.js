// assets/map-button.js
// Creates a floating Map button on every page.
// Idempotent and safe across all your docs/* and root pages.

(() => {
  if (document.getElementById("acacia-map-fab")) return;

  const href = "/Acacia-Garden-AI-Worldbuilding-Codex/map.html";

  const a = document.createElement("a");
  a.id = "acacia-map-fab";
  a.href = href;
  a.title = "Open Garden Map";
  a.setAttribute("aria-label", "Open Garden Map");

  // style (no external css required)
  Object.assign(a.style, {
    position: "fixed",
    right: "16px",
    bottom: "16px",
    zIndex: "999999",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 12px",
    borderRadius: "999px",
    textDecoration: "none",
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    border: "1px solid rgba(34,197,94,0.55)",
    background: "rgba(2,6,23,0.72)",
    color: "#22c55e",
    backdropFilter: "blur(6px)",
    WebkitBackdropFilter: "blur(6px)",
    boxShadow: "0 8px 24px rgba(0,0,0,0.35)",
  });

  a.innerHTML = `
    <span style="display:inline-block;width:10px;height:10px;border-radius:999px;background:#22c55e;box-shadow:0 0 10px rgba(34,197,94,0.8)"></span>
    MAP
  `;

  // avoid interfering with pages that already have fixed UI at bottom right
  // you can change bottom/right later if needed.
  document.body.appendChild(a);
})();
