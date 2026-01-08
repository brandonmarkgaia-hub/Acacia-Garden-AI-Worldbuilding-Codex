import json
import os
import glob

def generate_sharded_monolith():
    # Configuration
    MAX_BYTES = 99 * 1024 * 1024  # 99MB Limit
    OUTPUT_PATTERN = "CODEX_MONOLITH_PART_{}.md"
    
    # 1. Define Priority (The "Core")
    priority_files = [
        "STATUS.json",
        "README.md",
        "codex.md",
        "gardenos.md",
        "elias.md",
        "r9x2.md",
        "machine-index.json"
    ]
    
    # 2. Gather remaining lore and logs
    all_other_mds = [f for f in glob.glob("**/*.md", recursive=True) if f not in priority_files and "MONOLITH" not in f]
    all_json_logs = [f for f in glob.glob("ACACIA_LOGS/*.json")]
    
    # Combine into a single processing queue
    processing_queue = priority_files + all_other_mds + all_json_logs
    
    part_num = 1
    current_bytes = 0
    
    # Helper to start a new file
    def start_new_part(num):
        f = open(OUTPUT_PATTERN.format(num), "w", encoding="utf-8")
        f.write(f"# 🌿 ACACIA GARDEN CODEX | PART {num}\n")
        f.write(f"**Sequence:** Canonical Monolith Shard\n")
        f.write("---\n\n")
        return f

    current_file = start_new_part(part_num)

    for path in processing_queue:
        if not os.path.exists(path):
            continue
            
        # Read content based on file type
        try:
            if path.endswith(".json"):
                with open(path, "r") as src:
                    content = f"### 📄 DATA: {path}\n```json\n{json.dumps(json.load(src), indent=2)}\n```\n\n"
            else:
                with open(path, "r", encoding="utf-8") as src:
                    content = f"### 📄 DOC: {path}\n\n{src.read()}\n\n---\n\n"
        except Exception as e:
            print(f"Skipping {path} due to error: {e}")
            continue

        content_bytes = len(content.encode('utf-8'))

        # If this file pushes the current shard over 99MB, rotate to next part
        if current_bytes + content_bytes > MAX_BYTES:
            current_file.close()
            part_num += 1
            print(f"Shard {part_num-1} full. Starting Shard {part_num}...")
            current_file = start_new_part(part_num)
            current_bytes = 0

        current_file.write(content)
        current_bytes += content_bytes

    current_file.close()
    print(f"Generation Complete. Total Shards: {part_num}")

if __name__ == "__main__":
    generate_sharded_monolith()
