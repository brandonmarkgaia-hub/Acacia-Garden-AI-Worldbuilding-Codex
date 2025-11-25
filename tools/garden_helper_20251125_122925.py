```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    index_path = ROOT / 'garden_vault_index.json'
    
    if not index_path.is_file():
        print("Vault index file not found.")
        return

    with open(index_path, 'r') as f:
        vault_data = json.load(f)

    summary = Counter()
    
    for item in vault_data.get('vault', []):
        category = item.get('category', 'Unknown')
        summary[category] += 1

    report_lines = [f"{category}: {count}" for category, count in summary.items()]
    report = "\n".join(report_lines)

    print("Garden Vault Summary Report:")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
