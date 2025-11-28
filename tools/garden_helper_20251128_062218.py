```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_file = ROOT / 'garden_vault_index.json'
    if not index_file.exists():
        print("Vault index file does not exist.")
        return

    with open(index_file, 'r') as f:
        vault_data = json.load(f)

    summary = Counter()
    for entry in vault_data.get('vault_entries', []):
        category = entry.get('category', 'Uncategorized')
        summary[category] += 1

    report_lines = [f"{category}: {count}" for category, count in summary.items()]
    report = "\n".join(report_lines)
    
    print("Vault Index Summary:")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
