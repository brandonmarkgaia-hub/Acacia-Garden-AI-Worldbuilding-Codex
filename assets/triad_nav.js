(function () {
  try {
    if (window.__acaciaTriadDockInstalled) return;
    window.__acaciaTriadDockInstalled = true;

    // Compute '/REPO/' for GitHub Pages project sites.
    const parts = location.pathname.split("/").filter(Boolean);
    const base = parts.length >= 1 ? `/${parts[0]}/` : "/";

    function href(path) {
      return base + path.replace(/^\/+/, "");
    }

    // Dock container
    const dock = document.createElement("div");
    dock.style.position = "fixed";
    dock.style.right = "18px";
    dock.style.bottom = "18px";
    dock.style.zIndex = "99999";
    dock.style.display = "flex";
    dock.style.flexDirection = "column";
    dock.style.gap = "10px";

    function mkBtn(text, path) {
      const a = document.createElement("a");
      a.textContent = text;
      a.href = href(path);
      a.style.display = "inline-block";
      a.style.padding = "10px 12px";
      a.style.borderRadius = "999px";
      a.style.background = "rgba(15, 23, 42, 0.78)";
      a.style.border = "1px solid rgba(148, 163, 184, 0.35)";
      a.style.color = "#e5e7eb";
      a.style.font = "600 12px system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif";
      a.style.letterSpacing = ".08em";
      a.style.textTransform = "uppercase";
      a.style.textDecoration = "none";
      a.style.backdropFilter = "blur(6px)";
      a.style.boxShadow = "0 10px 30px rgba(0,0,0,.25)";
      a.style.opacity = "0.92";
      a.onmouseenter = function(){ a.style.opacity = "1"; a.style.background = "rgba(30, 41, 59, 0.88)"; };
      a.onmouseleave = function(){ a.style.opacity = "0.92"; a.style.background = "rgba(15, 23, 42, 0.78)"; };
      return a;
    }

    // Buttons (order matters)
    dock.appendChild(mkBtn("Map", "map.html"));
    dock.appendChild(mkBtn("Docs", "docs/index.html"));
    dock.appendChild(mkBtn("Codex", "codex.html"));
    dock.appendChild(mkBtn("Home", "index.html"));
    dock.appendChild(mkBtn("Handshake", "handshake.html"));

    // Prevent duplicate docks if some pages already have it
    if (!document.querySelector("[data-acacia-dock='true']")) {
      dock.setAttribute("data-acacia-dock", "true");
      document.body.appendChild(dock);
    }
  } catch (e) {}
})();
