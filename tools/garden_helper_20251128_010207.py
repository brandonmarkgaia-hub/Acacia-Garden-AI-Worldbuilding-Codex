```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_file = ROOT / 'garden_vault_indexer.py'
    report = []

    if index_file.exists():
        with open(index_file, 'r') as f:
            data = json.load(f)
            for item in data.get('vaults', []):
                report.append(f"Vault: {item['name']}, Items: {len(item.get('items', []))}")

    return "\n".join(report)

def main():
    summary_report = summarize_vault_index()
    print("Garden Vault Index Summary:")
    print(summary_report)

if __name__ == "__main__":
    main()
```
