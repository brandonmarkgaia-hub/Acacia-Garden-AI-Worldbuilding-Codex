import re
from datetime import datetime, timezone
import os

MEMORY_PATH = "garden_gpt/outputs/rebuild_memory.md"

ORIGIN_RE = re.compile(r"\[HANDSHAKE_ORIGIN seq=(\d+) ts=([^\]]+)\]")

def find_last_origin_seq(text: str) -> int:
    matches = list(ORIGIN_RE.finditer(text))
    if not matches:
        return 0
    return int(matches[-1].group(1))

def read_memory() -> str:
    if not os.path.exists(MEMORY_PATH):
        return ""
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return f.read()

def append_origin(seq: int) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write("\n\n---\n\n")
        f.write("## 🤝 GARDEN ↔ LOKI HANDSHAKE\n\n")
        f.write(f"[HANDSHAKE_ORIGIN seq={seq} ts={ts}]\n")

def main():
    current = read_memory()
    last_seq = find_last_origin_seq(current)
    new_seq = last_seq + 1
    append_origin(new_seq)
    print(f"Added HANDSHAKE_ORIGIN seq={new_seq}")

if __name__ == "__main__":
    main()
