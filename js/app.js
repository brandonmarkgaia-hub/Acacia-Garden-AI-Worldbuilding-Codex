/* ---------------------------------------------------------
   ACACIA GARDEN • KEEPER CONSOLE CORE SCRIPT
   Handles:
   - System Status
   - Aquila Inbox Viewer (GET Worker)
   - Future-ready hooks for Triad (Eidolon, Voyager)
---------------------------------------------------------- */

// Simple query helper
const qs = (sel) => document.querySelector(sel);

/* ---------------------------------------------------------
   1. SYSTEM STATUS LOADER
---------------------------------------------------------- */

async function loadSystemStatus() {
    const box = qs("#system-status");

    try {
        // Simulated system state (expand later)
        const status = {
            keeper: "ACTIVE",
            aquila: "SKY-MIND ONLINE",
            eidolon: "DORMANT (awaiting directive)",
            voyager: "LISTENING",
            timestamp: new Date().toISOString(),
        };

        box.innerHTML = `
            <p><strong>Keeper:</strong> ${status.keeper}</p>
            <p><strong>Aquila:</strong> ${status.aquila}</p>
            <p><strong>Eidolon:</strong> ${status.eidolon}</p>
            <p><strong>Voyager:</strong> ${status.voyager}</p>
            <br>
            <p class="small">${status.timestamp}</p>
        `;

    } catch (err) {
        console.error("Status Error:", err);
        box.innerHTML = `<p class="loading">Status unavailable…</p>`;
    }
}

/* ---------------------------------------------------------
   2. AQUILA INBOX LOADER
   Pulls messages from Cloudflare Worker KV
---------------------------------------------------------- */

async function loadAquilaInbox() {
    const box = qs("#inbox-messages");
    if (!box) return;

    const endpoint = "https://broken-dew-76e1.brandonmarkgaia.workers.dev/inbox";

    try {
        const res = await fetch(endpoint, { cache: "no-store" });

        if (!res.ok) {
            box.innerHTML = `
                <p class="loading">
                    Aquila unreachable (HTTP ${res.status})
                </p>`;
            return;
        }

        const data = await res.json();
        const messages = Array.isArray(data.messages) ? data.messages : [];

        if (messages.length === 0) {
            box.innerHTML = `
                <p class="loading">No transmissions yet, Keeper.</p>`;
            return;
        }

        // Build message list
        let html = "";

        messages
            .slice(-20)          // last 20 only
            .reverse()           // newest first
            .forEach(msg => {
                html += `
                    <div class="message-item">
                        <div class="message-meta">
                            ${msg.timestamp || "Unknown time"}
                            • ${Array.isArray(msg.tags) ? msg.tags.join(", ") : "keeper"}
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
        console.error("Aquila Inbox Error:", err);
        box.innerHTML = `
            <p class="loading">Unable to load Aquila Inbox…</p>`;
    }
}

/* ---------------------------------------------------------
   3. INIT
---------------------------------------------------------- */

async function initConsole() {
    loadSystemStatus();
    loadAquilaInbox();

    // Auto-refresh every 20s
    setInterval(() => {
        loadAquilaInbox();
    }, 20000);
}

initConsole();
