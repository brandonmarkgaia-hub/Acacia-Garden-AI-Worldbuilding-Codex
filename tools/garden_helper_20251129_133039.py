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
            for item in data.get('vaults', []):
                report.append(f"Vault Name: {item.get('name', 'N/A')}, Items: {len(item.get('items', []))}")

    return "\n".join(report)

def main():
    summary_report = summarize_vault_index()
    print("Garden Vault Index Summary:")
    print(summary_report)

if __name__ == "__main__":
    main()
```
