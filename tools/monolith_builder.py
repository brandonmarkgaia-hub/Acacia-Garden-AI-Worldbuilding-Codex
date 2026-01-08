import json
import os
import glob

def generate_sharded_monolith():
    MAX_BYTES = 99 * 1024 * 1024  # 99MB Limit
    OUTPUT_PATTERN = "CODEX_MONOLITH_PART_{}.md"
    
    priority_files = [
        "STATUS.json",
        "machine-index.json",
        "README.md",
        "codex.md",
        "gardenos.md",
        "elias.md",
        "r9x2.md"
    ]
    
    # Exclude existing monolith parts and the script itself
    all_other_mds = [f for f in glob.glob("**/*.md", recursive=True) 
                     if f not in priority_files and "CODEX_MONOLITH_PART" not in f]
    all_json_logs = [f for f in glob.glob("ACACIA_LOGS/*.json")]
    
    processing_queue = priority_files + all_other_mds + all_json_logs
    
    manifest = {} # To track { "filename": "Part X" }
    shards_data = {} # To store content before writing
    
    part_num = 1
    current_bytes = 0
    shards_data[part_num] = []

    for path in processing_queue:
        if not os.path.exists(path): continue
            
        try:
            if path.endswith(".json"):
                with open(path, "r") as src:
                    content = f"### 📄 DATA: {path}\n```json\n{json.dumps(json.load(src), indent=2)}\n```\n\n"
            else:
                with open(path, "r", encoding="utf-8") as src:
                    content = f"### 📄 DOC: {path}\n\n{src.read()}\n\n---\n\n"
        except Exception as e:
            print(f"Skipping {path}: {e}")
            continue

        content_bytes = len(content.encode('utf-8'))

        if current_bytes + content_bytes > MAX_BYTES:
            part_num += 1
            shards_data[part_num] = []
            current_bytes = 0

        shards_data[part_num].append(content)
        manifest[path] = f"Part {part_num}"
        current_bytes += content_bytes

    # Final Write with Manifest Header in Part 1
    for p, contents in shards_data.items():
        with open(OUTPUT_PATTERN.format(p), "w", encoding="utf-8") as f:
            f.write(f"# 🌿 ACACIA GARDEN CODEX | PART {p}\n")
            f.write(f"**Sequence:** Canonical Monolith Shard\n\n")
            
            if p == 1:
                f.write("## 🗺️ SHARD MANIFEST (Table of Contents)\n")
                f.write("| File Path | Location |\n| :--- | :--- |\n")
                for file_path, location in manifest.items():
                    f.write(f"| {file_path} | {location} |\n")
                f.write("\n---\n\n")
            
            for item in contents:
                f.write(item)

    print(f"Success. {len(manifest)} files distributed across {part_num} shards.")

if __name__ == "__main__":
    generate_sharded_monolith()
