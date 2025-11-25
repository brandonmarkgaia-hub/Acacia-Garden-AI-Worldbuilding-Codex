```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_file = ROOT / 'garden_vault_index.json'
    report = []

    if index_file.exists():
        with open(index_file, 'r') as f:
            data = json.load(f)
            for item in data.get('vaults', []):
                vault_name = item.get('name', 'Unknown Vault')
                item_count = item.get('item_count', 0)
                report.append(f"{vault_name}: {item_count} items")

    return report

def main():
    report = summarize_vault_index()
    if report:
        print("Garden Vault Index Summary:")
        for line in report:
            print(line)
    else:
        print("No vaults found or index file is missing.")

if __name__ == "__main__":
    main()
```
