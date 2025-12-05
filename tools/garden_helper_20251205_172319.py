```python
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def summarize_garden_vault_index():
    vault_index_path = ROOT / 'garden_vault_index.json'
    
    if not vault_index_path.is_file():
        print("garden_vault_index.json not found.")
        return
    
    with open(vault_index_path, 'r') as file:
        data = json.load(file)
    
    summary = {
        'total_entries': len(data),
        'unique_signatures': len(set(entry.get('signature') for entry in data if 'signature' in entry)),
        'total_size': sum(entry.get('size', 0) for entry in data if 'size' in entry)
    }
    
    report = (
        f"Garden Vault Index Summary:\n"
        f"Total Entries: {summary['total_entries']}\n"
        f"Unique Signatures: {summary['unique_signatures']}\n"
        f"Total Size: {summary['total_size']} bytes\n"
    )
    
    print(report)

def main():
    summarize_garden_vault_index()

if __name__ == "__main__":
    main()
```
