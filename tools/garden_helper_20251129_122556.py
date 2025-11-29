```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    vault_index_path = ROOT / 'garden_vault_indexer.py'
    if not vault_index_path.exists():
        print("Vault index file not found.")
        return

    with open(vault_index_path, 'r') as file:
        data = json.load(file)

    summary = Counter()
    for entry in data.get('vault_entries', []):
        summary[entry.get('category', 'Unknown')] += 1

    report = "Garden Vault Summary:\n"
    for category, count in summary.items():
        report += f"{category}: {count}\n"

    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
