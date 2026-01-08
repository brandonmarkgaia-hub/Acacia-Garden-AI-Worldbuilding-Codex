import json
import os
import glob
import datetime

def generate_sharded_monolith():
    MAX_BYTES = 99 * 1024 * 1024  # 99MB Limit
    OUTPUT_PATTERN = "CODEX_MONOLITH_PART_{}.md"
    
    # Priority order for the "Bible"
    priority_files = [
        "STATUS.json",
        "machine-index.json",
        "README.md",
        "codex.md",
        "gardenos.md",
        "elias.md",
        "r9x2.md"
    ]
    
    # Gather all lore and logs
    all_other_mds = [f for f in glob.glob("**/*.md", recursive=True) 
                     if f not in priority_files and "CODEX_MONOLITH_PART" not in f]
    all_json_logs = [f for f in glob.glob("ACACIA_LOGS/*.json")]
    
    processing_queue = priority_files + all_other_mds + all_json_logs
    
    manifest = [] # List of dicts for the ToC
    shards_data = {} # To store content
    
    part_num = 1
    current_bytes = 0
    shards_data[part_num] = []

    for path in processing_queue:
        if not os.path.exists(path): continue
            
        # Get last modified time
        mtime = os.path.getmtime(path)
        last_mod = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

        try:
            if path.endswith(".json"):
                with open(path, "r") as src:
                    content = f"### 📄 DATA: {path}\n```json\n{json.dumps(json.load(src), indent=2)}\n```\n\n"
            else:
                with open(path, "r", encoding="utf-8") as src:
                    content = f"### 📄 DOC: {path}\n\n{src.read()}\n\n---\n\n"
        except Exception as e:
            continue

        content_bytes = len(content.encode('utf-8'))

        # Check for shard overflow
        if current_bytes + content_bytes > MAX_BYTES:
            part_num += 1
            shards_data[part_num] = []
            current_bytes = 0

        shards_data[part_num].append(content)
        manifest.append({
            "path": path,
            "shard": f"Part {part_num}",
            "mod": last_mod
        })
        current_bytes += content_bytes

    # Final Write: Prepend Manifest to Part 1
    for p, contents in shards_data.items():
        with open(OUTPUT_PATTERN.format(p), "w", encoding="utf-8") as f:
            f.write(f"# 🌿 ACACIA GARDEN CODEX | PART {p}\n")
            f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            if p == 1:
                f.write("## 🗺️ GLOBAL MANIFEST (The Bible Index)\n")
                f.write("| File Path | Shard Location | Last Modified |\n| :--- | :--- | :--- |\n")
                for entry in manifest:
                    f.write(f"| {entry['path']} | {entry['shard']} | {entry['mod']} |\n")
                f.write("\n---\n\n")
            
            for item in contents:
                f.write(item)

    print(f"Codex Bible generated: {part_num} shards created.")

if __name__ == "__main__":
    generate_sharded_monolith()
