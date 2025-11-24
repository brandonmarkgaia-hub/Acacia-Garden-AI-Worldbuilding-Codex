```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_file = ROOT / 'garden_vault_indexer.json'
    if not index_file.is_file():
        print("Vault index file not found.")
        return

    with open(index_file, 'r') as f:
        index_data = json.load(f)

    summary = []
    for key, value in index_data.items():
        summary.append(f"{key}: {len(value)} items")

    report = "\n".join(summary)
    print("Garden Vault Index Summary:\n")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
