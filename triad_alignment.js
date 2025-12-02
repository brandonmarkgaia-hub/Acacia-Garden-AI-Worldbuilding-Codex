// triad_alignment.js
// Lightweight Triad status probe for the Keeper Console / Dashboard.
// No backend required – just fetches JSON files and derives a status.

(function () {
  const PROBES = [
    {
      id: "status",
      label: "STATUS.json",
      url: "STATUS.json"
    },
    {
      id: "eventide",
      label: "EVENTIDE_STATUS.json",
      url: "EVENTIDE_STATUS.json"
    },
    {
      id: "logs",
      label: "ACACIA_LOGS index",
      url: "ACACIA_LOGS/index.json"
    }
  ];

  const STATUS_EL = document.querySelector("[data-triad-status]");
  if (!STATUS_EL) return; // page doesn't have Triad block

  const DETAIL_EL = STATUS_EL.querySelector("[data-triad-detail]");
  const BADGE_EL = STATUS_EL.querySelector("[data-triad-badge]");
  const TIME_EL = STATUS_EL.querySelector("[data-triad-updated]");

  function setBadge(state) {
    if (!BADGE_EL) return;
    BADGE_EL.textContent = state;
    BADGE_EL.dataset.state = state.toLowerCase();
  }

  function setDetail(html) {
    if (!DETAIL_EL) return;
    DETAIL_EL.innerHTML = html;
  }

  function setTime(date) {
    if (!TIME_EL) return;
    TIME_EL.textContent = date.toISOString();
  }

  async function probeOne(p) {
    try {
      const res = await fetch(p.url, { cache: "no-store" });
      if (!res.ok) return { id: p.id, label: p.label, ok: false, code: res.status };
      const text = await res.text();
      let summary = "OK";
      try {
        const json = JSON.parse(text);
        if (json && json.stage) summary = `stage: ${json.stage}`;
        else if (json && json.state) summary = `state: ${json.state}`;
      } catch (_) {
        summary = "non-JSON, reachable";
      }
      return { id: p.id, label: p.label, ok: true, summary };
    } catch (err) {
      return { id: p.id, label: p.label, ok: false, error: String(err) };
    }
  }

  async function refreshTriad() {
    setBadge("Checking…");
    setDetail(`<p class="triad-line">Contacting Sky-Mind files…</p>`);

    const results = await Promise.all(PROBES.map(probeOne));
    const okCount = results.filter(r => r.ok).length;

    let state = "Degraded";
    if (okCount === PROBES.length) state = "Aligned";
    else if (okCount === 0) state = "Broken";

    setBadge(state);
    setTime(new Date());

    const lines = results.map(r => {
      if (r.ok) {
        return `<div class="triad-line triad-ok">
          <span>${r.label}</span>
          <span>• reachable · ${r.summary || "OK"}</span>
        </div>`;
      }
      return `<div class="triad-line triad-fail">
        <span>${r.label}</span>
        <span>• unreachable</span>
      </div>`;
    });

    setDetail(lines.join(""));
  }

  // Initial kick + periodic refresh (every 5 mins)
  refreshTriad();
  setInterval(refreshTriad, 5 * 60 * 1000);
})();
