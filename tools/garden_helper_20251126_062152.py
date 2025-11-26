```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    vault_index_path = ROOT / 'garden_vault_indexer.py'
    summary_report = []

    if vault_index_path.exists():
        with open(vault_index_path, 'r') as file:
            data = json.load(file)
            for item in data.get('vaults', []):
                vault_name = item.get('name', 'Unknown Vault')
                item_count = item.get('item_count', 0)
                summary_report.append(f"{vault_name}: {item_count} items")

    return "\n".join(summary_report)

def main():
    report = summarize_vault_index()
    print("Garden Vault Summary Report:")
    print(report)

if __name__ == "__main__":
    main()
```
