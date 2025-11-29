```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    vault_index_path = ROOT / 'garden_vault_indexer.py'
    report = []

    if vault_index_path.exists():
        with open(vault_index_path, 'r') as file:
            data = json.load(file)
            total_entries = len(data)
            report.append(f"Total entries in vault index: {total_entries}")

            if total_entries > 0:
                # Count occurrences of each entry type
                entry_types = Counter(entry.get('type', 'Unknown') for entry in data)
                for entry_type, count in entry_types.items():
                    report.append(f"{entry_type}: {count} entries")

    return "\n".join(report)

def main():
    report = summarize_vault_index()
    print(report)

if __name__ == "__main__":
    main()
```
