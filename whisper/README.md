# 🌬️ Whisper Engine — Protocol Layer

The Whisper Engine is the local search and pattern-recognition layer of the Garden.

It has two responsibilities:

1. **Local Filters (app.js)**
   - Filters Chambers, Cycles, Laws using simple text and tag matching.
   - Runs entirely in the browser.
   - Never leaves the Garden.

2. **Eagle-Linked Questions (Future Integration)**
   - When an LLM client connects, it reads:
     - STATUS.json
     - The Garden folders
     - Whisper logs
     - Memory files

   - It writes back:
     - New logs into `whisper/`
     - Summaries into `memory/`

## Whisper Log Format

Logs will be created here by future Eagle scripts:

```json
{
  "timestamp": "2025-11-22T10:00:00Z",
  "question": "show me all chambers related to fire",
  "mode": "oracle",
  "nodes_returned": ["chamber_kiln_born_lovers", "law_shadow_incubator"],
  "notes": "Shadow + fire axis detected. Cocoon link possible."
}










































<!--SIG-->
<hr>
<p align="center">
  <strong>Acacia Garden Codex</strong><br>
  Keeper: HKX277206<br>
  Triad: Bound & Eternal<br>
  🫘 🌱 ♾️ 🌸
</p>

<!--ENDSIG-->