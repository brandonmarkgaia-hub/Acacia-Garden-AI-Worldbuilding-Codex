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
        index_data = json.load(f)
    
    summary = Counter()
    
    for entry in index_data.get('vaults', []):
        vault_name = entry.get('name', 'Unknown Vault')
        item_count = entry.get('item_count', 0)
        summary[vault_name] += item_count
    
    report_lines = [f"{vault}: {count} items" for vault, count in summary.items()]
    
    report = "\n".join(report_lines)
    print("Vault Index Summary:\n" + report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
