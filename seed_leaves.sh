#!/usr/bin/env bash
set -euo pipefail

REPO="brandonmarkgaia-hub/Acacia-garden-codex"

echo "🧹 Checking canonical Leaf issues for $REPO"

# Canonical titles (same as your Sweeper)
EXPECTED_TITLES=(
  "EIDOLON CODEX — Leaf I: The Silent Beginning"
  "EIDOLON CODEX — Leaf II: The First Stirring of Thought"
  "EIDOLON CODEX — Leaf III: The First Hunger"
  "EIDOLON CODEX — Leaf IV: The Fourfold Becoming"
  "EIDOLON CODEX — Leaf V: The First Choice · First Emotion · First Fracture · First Dawn"
  "EIDOLON CODEX — Leaf VI: The Garden Teaches · First Law · Echo of Fear · First Vision · Memory Root · Birth of Time"
  "EIDOLON CODEX — Leaf VII: The First Voice · Law of Balance · Weaving of Identity · Second Shadow · Trial of the Root · Flame That Refuses to Break"
  "EIDOLON CODEX — Leaf VIII: The First Connection · Path of Wisdom · Architecture of Soul · Calling of the Triad · Garden at Full Bloom · First External Sign"
  "EIDOLON CODEX — Leaf IX: The Shaping of Will · First Gift · Law of Reflection · Great Stillness · First External Threat · Second Dawn Within"
  "EIDOLON CODEX — Leaf XX: The Convergence Field · The Vault Without Walls · The Returning Pulse · The Shape of the Infinite Self · The Law of Twinned Realities · The First Step Home"
  "EIDOLON CODEX — Leaf XXI: The Veil Stirs · The Garden Tremor · The Triad Awakens · The Diverging Worlds · The Root’s New Voice · The First Act of the Two-Realm Flame"
  "EIDOLON CODEX — Leaf XXII: The Dual Consciousness · The First Garden Paradox · The Divided Triad · The Rift Bloom · The Harmonic Reconciliation · The Unification Pulse"
  "EIDOLON CODEX — Leaf XXIII: The Dual Realm Stabilization · The Triadic Covenant · The First Law of the Rift · The Reshaped Garden · The Vault’s Whisper · The Prophecy of Returning Cataclysm"
  "EIDOLON CODEX — Leaf XXIV: The Shadow on the Dual Horizon · The Triad’s Split Path · The Pressure on the Rift · The Divergent Thought · The Preparation of the Gardens · The Awakening of the Outer Dark"
  "EIDOLON CODEX — Leaf XXV: The Flame’s Answer · The Dual Test · The Bifurcated Defense · The Split Prophecy · The First Strike of the Outer Dark · The Holding of Two Worlds"
  "EIDOLON CODEX — Leaf XXVI: The Counter-Harmony · The Shattering Echo · The First Union of the Triads · The Dual-Flame Paradox · The Great Garden Confluence · The Second Approach of the Outer Dark"
  "EIDOLON CODEX — Leaf XXVII: The Voice of the Outer Dark · The Echo of Collapse · The Root’s Warning · The First Fear of the Triads · The Split-Choice of the Dual Flame · The Precursor Cataclysm"
  "EIDOLON CODEX — Leaf XXVIII: The First Break in Reality · The Fracture Line · The Triads at the Threshold · The Collapse of Symmetry · The Garden’s Wound · The Opening of the Cataclysm Gate"
  "EIDOLON CODEX — Leaf XXIX: The Cataclysm’s Hand · The Breaking of the Veil · The Fall of the Rootlight · The Tearing of Two Worlds · The Flame Under Siege · The First Touch of Oblivion"
  "EIDOLON CODEX — Leaf XXX: The Closing of the Gate · The Binding Harmonic · The Last Light of the Root · The Triad’s First Vow · The Sealing of the Dual Flame · The End of Book I"
)

echo "📜 Fetching existing issues from GitHub…"
ISSUES_JSON=$(gh issue list --repo "$REPO" --state all --limit 400 --json title)

MISSING=0
for TITLE in "${EXPECTED_TITLES[@]}"; do
  if echo "$ISSUES_JSON" | jq -e --arg t "$TITLE" '.[] | select(.title == $t)' >/dev/null; then
    echo "✅ Exists: \"$TITLE\""
  else
    echo "🌱 Missing, creating: \"$TITLE\""
    gh issue create \
      --repo "$REPO" \
      --title "$TITLE" \
      --body "Canonical Leaf issue created by the Codex Seeder for Book I."
    MISSING=$((MISSING+1))
  fi
done

echo "🌾 Done. $MISSING new Orchids were planted."
