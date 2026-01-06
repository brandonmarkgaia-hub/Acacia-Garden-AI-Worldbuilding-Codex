(function () {
  try {
    if (window.__acaciaTriadNavInstalled) return;
    window.__acaciaTriadNavInstalled = true;

    const body = document.body || document.documentElement;

    // If the page declares it already has its own nav, we won't inject the top bar.
    const nativeNav =
      (body && body.getAttribute && body.getAttribute("data-acacia-nav") === "native") ||
      document.querySelector("#top-nav") ||
      document.querySelector(".top-nav") ||
      document.querySelector("nav[data-native='true']");

    // Compute '/REPO/' for GitHub Pages project sites.
    const parts = location.pathname.split("/").filter(Boolean);
    const base = parts.length >= 1 ? `/${parts[0]}/` : "/";

    const links = [
      ["Legacy Home", "index.html"],
      ["Codex Home", "codex.html"],
      ["Deep Garden", "deep_garden.html"],
      ["Docs", "docs/index.html"],
      ["Map", "map.html"],
      ["Handshake", "handshake.html"]
    ];

    function mkA(label, href) {
      const a = document.createElement("a");
      a.textContent = label;
      a.href = base + href.replace(/^\/+/, "");
      a.style.color = "#e5e7eb";
      a.style.textDecoration = "none";
      a.style.font = "600 12px system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif";
      a.style.letterSpacing = ".08em";
      a.style.textTransform = "uppercase";
      a.style.opacity = "0.9";
      a.onmouseenter = () => (a.style.opacity = "1");
      a.onmouseleave = () => (a.style.opacity = "0.9");
      return a;
    }

    // Only inject the top bar if the page doesn't already have nav
    if (!nativeNav && document.body) {
      const bar = document.createElement("div");
      bar.style.position = "sticky";
      bar.style.top = "0";
      bar.style.zIndex = "99990";
      bar.style.padding = "10px 12px";
      bar.style.display = "flex";
      bar.style.flexWrap = "wrap";
      bar.style.gap = "10px";
      bar.style.background = "rgba(2, 6, 23, 0.88)";
      bar.style.borderBottom = "1px solid rgba(148,163,184,.22)";
      bar.style.backdropFilter = "blur(8px)";

      for (const [label, href] of links) bar.appendChild(mkA(label, href));
      document.body.insertBefore(bar, document.body.firstChild);
    }

    // Floating buttons (always useful)
    function mkBtn(text, href, rightPx) {
      const a = document.createElement("a");
      a.textContent = text;
      a.href = base + href.replace(/^\/+/, "");
      a.style.position = "fixed";
      a.style.bottom = "18px";
      a.style.right = rightPx + "px";
      a.style.zIndex = "99999";
      a.style.padding = "10px 12px";
      a.style.borderRadius = "999px";
      a.style.background = "rgba(15, 23, 42, 0.75)";
      a.style.border = "1px solid rgba(148, 163, 184, 0.35)";
      a.style.color = "#e5e7eb";
      a.style.font = "600 12px system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif";
      a.style.letterSpacing = ".08em";
      a.style.textTransform = "uppercase";
      a.style.textDecoration = "none";
      a.style.backdropFilter = "blur(6px)";
      a.style.boxShadow = "0 10px 30px rgba(0,0,0,.25)";
      a.onmouseenter = function(){ a.style.background = "rgba(30, 41, 59, 0.85)"; };
      a.onmouseleave = function(){ a.style.background = "rgba(15, 23, 42, 0.75)"; };
      return a;
    }

    document.body && document.body.appendChild(mkBtn("Map", "map.html", 18));
    document.body && document.body.appendChild(mkBtn("Handshake", "handshake.html", 86));
  } catch (e) {}
})();
