/* ---------------------------------------------------------
   ACACIA GARDEN • CORE ENGINE SCRIPT
   Powers:
   - System Status
   - Aquila Inbox Viewer (Cloudflare KV)
   - Triad Status Module
---------------------------------------------------------- */

const qs = (sel) => document.querySelector(sel);

/* ---------------------------------------------------------
   SYSTEM STATUS
---------------------------------------------------------- */
async function loadSystemStatus() {
    const box = qs("#system-status");

    try {
        const status = {
            keeper: "ACTIVE",
            aquila: "ONLINE • Listening",
            eidolon: "DORMANT • Awaiting Deep Channel",
            voyager: "PASSIVE • Horizon Scan",
            ts: new Date().toISOString()
        };

        box.innerHTML = `
            <p><strong>Keeper:</strong> ${status.keeper}</p>
            <p><strong>Aquila:</strong> ${status.aquila}</p>
            <p><strong>Eidolon:</strong> ${status.eidolon}</p>
            <p><strong>Voyager:</strong> ${status.voyager}</p>
            <br>
            <p class="small">${status.ts}</p>
        `;
    } catch (err) {
        console.error(err);
        box.innerHTML = `<p class="loading">Status unavailable…</p>`;
    }
}

/* ---------------------------------------------------------
   AQUILA INBOX
---------------------------------------------------------- */
async function loadAquilaInbox() {
    const box = qs("#inbox-messages");
    const endpoint = "https://broken-dew-76e1.brandonmarkgaia.workers.dev/inbox";

    try {
        const res = await fetch(endpoint, { cache: "no-store" });

        if (!res.ok) {
            box.innerHTML = `<p class="loading">Aquila unreachable (HTTP ${res.status})</p>`;
            return;
        }

        const data = await res.json();
        const messages = Array.isArray(data.messages) ? data.messages : [];

        if (!messages.length) {
            box.innerHTML = `<p class="loading">No transmissions yet, Keeper.</p>`;
            return;
        }

        let html = "";
        messages
            .slice(-20)
            .reverse()
            .forEach(msg => {
                html += `
                    <div class="message-item">
                        <div class="message-meta">
                            ${msg.timestamp || "Unknown"} •
                            ${Array.isArray(msg.tags) ? msg.tags.join(", ") : "keeper"}
                        </div>

                        <h3>${msg.title || "Untitled Transmission"}</h3>

                        <div class="message-body">
                            ${msg.summary || ""}
                            <br><br>
                            ${msg.body || ""}
                        </div>
                    </div>
                `;
            });

        box.innerHTML = html;

    } catch (err) {
        console.error(err);
        box.innerHTML = `<p class="loading">Failed to load Aquila Inbox…</p>`;
    }
}

/* ---------------------------------------------------------
   TRIAD STATUS
---------------------------------------------------------- */
async function loadTriadStatus() {
    const box = qs("#triad-status");

    try {
        const triad = {
            aquila: "ONLINE — Sky-mind listening",
            eidolon: "DORMANT — Seed-core awaiting ignition",
            voyager: "PASSIVE — Horizon sweep",
            keeper: "ACTIVE — HKX277206",
            ts: new Date().toISOString()
        };

        box.innerHTML = `
            <p><strong>Aquila:</strong> ${triad.aquila}</p>
            <p><strong>Eidolon:</strong> ${triad.eidolon}</p>
            <p><strong>Voyager:</strong> ${triad.voyager}</p>
            <p><strong>Keeper:</strong> ${triad.keeper}</p>
            <br>
            <p class="small">${triad.ts}</p>
        `;

    } catch (err) {
        console.error(err);
        box.innerHTML = `<p class="loading">Triad status unavailable…</p>`;
    }
}

/* ---------------------------------------------------------
   INIT
---------------------------------------------------------- */
async function initConsole() {
    loadSystemStatus();
    loadAquilaInbox();
    loadTriadStatus();

    // Refresh inbox every 20 seconds
    setInterval(loadAquilaInbox, 20000);
}

initConsole();
