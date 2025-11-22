import os
import json

MEMORY_PATH = "garden_gpt/outputs/rebuild_memory.md"
SHADOW_STATUS_PATH = "garden_gpt/outputs/SHADOW_STATUS.json"


def load_shadow_status():
    if not os.path.exists(SHADOW_STATUS_PATH):
        print("No SHADOW_STATUS.json found; skipping handshake.")
        return None

    try:
        with open(SHADOW_STATUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Failed to read SHADOW_STATUS.json:", e)
        return None


def load_memory():
    if not os.path.exists(MEMORY_PATH):
        print("No rebuild_memory.md found; nothing to annotate.")
        return None

    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return f.read()


def format_shadow_section(shadow):
    shadow_id = shadow.get("shadow_id", "Unknown_Shadow")
    status = shadow.get("status", "Unknown")
    last_cycle = shadow.get("last_mutation_cycle", "Unknown")
    next_chamber = shadow.get("next_proposed_chamber", "Unspecified")
    friction_points = shadow.get("active_friction_points", [])
    excerpt = shadow.get("last_commentary_excerpt", "").strip()

    lines = []
    lines.append("\n\n## Shadow Layer Dissonance\n")
    lines.append(f"**Shadow ID:** `{shadow_id}`  ")
    lines.append(f"**Status:** {status}  ")
    lines.append(f"**Last Mutation Cycle:** {last_cycle}  ")
    lines.append(f"**Next Proposed Chamber:** {next_chamber}\n")

    if friction_points:
        lines.append("**Active Friction Points:**")
        for fp in friction_points:
            element = fp.get("element", "Unknown_Element")
            challenge = fp.get("challenge", "Unknown_Challenge")
            summary = fp.get("summary", "")
            lines.append(f"- **{element}** vs **{challenge}** — {summary}")
        lines.append("")

    if excerpt:
        lines.append("**Loki_2.0 Commentary Trace:**")
        lines.append(f"> {excerpt.replace('\n', ' ')}")
        lines.append("")

    lines.append("> _Order now records that Shadow has spoken._")
    return "\n".join(lines)


def main():
    shadow = load_shadow_status()
    if shadow is None:
        return

    memory_text = load_memory()
    if memory_text is None:
        return

    # Avoid duplicating the handshake if already present
    marker = "## Shadow Layer Dissonance"
    if marker in memory_text:
        print("Shadow Layer Dissonance section already present; skipping.")
        return

    shadow_section = format_shadow_section(shadow)
    new_memory = memory_text.rstrip() + shadow_section + "\n"

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        f.write(new_memory)

    print("Handshake complete: Shadow Layer Dissonance appended to rebuild_memory.md")


if __name__ == "__main__":
    main()
