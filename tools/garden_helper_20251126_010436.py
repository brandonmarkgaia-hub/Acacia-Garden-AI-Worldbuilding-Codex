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
        vault_data = json.load(file)

    summary = Counter()
    for entry in vault_data.get('vaults', []):
        summary[entry['type']] += 1

    report_lines = [f"{vault_type}: {count}" for vault_type, count in summary.items()]
    report = "\n".join(report_lines)

    print("Garden Vault Summary Report:")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
