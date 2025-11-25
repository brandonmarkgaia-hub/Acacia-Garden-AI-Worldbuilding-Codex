```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_file = ROOT / 'garden_vault_index.json'
    if not index_file.is_file():
        print("Vault index file not found.")
        return

    with index_file.open('r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Error decoding JSON from vault index file.")
            return

    summary = Counter()
    for item in data.get('vaults', []):
        vault_name = item.get('name', 'Unnamed Vault')
        item_count = item.get('item_count', 0)
        summary[vault_name] += item_count

    report_lines = [f"{vault}: {count} items" for vault, count in summary.items()]
    report = "\n".join(report_lines)

    print("Vault Index Summary:")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
