```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_file = ROOT / 'garden_vault_index.json'
    if not index_file.exists():
        print("Vault index file does not exist.")
        return

    with open(index_file, 'r') as f:
        index_data = json.load(f)

    summary = []
    for item in index_data.get('vaults', []):
        vault_name = item.get('name', 'Unknown Vault')
        item_count = len(item.get('items', []))
        summary.append(f"{vault_name}: {item_count} items")

    report = "\n".join(summary)
    print("Garden Vault Summary:")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
