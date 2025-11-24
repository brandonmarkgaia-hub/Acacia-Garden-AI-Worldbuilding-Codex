```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    vault_index_path = ROOT / 'garden_vault_index.json'
    
    if not vault_index_path.exists():
        print("Vault index file does not exist.")
        return
    
    with open(vault_index_path, 'r') as file:
        vault_index = json.load(file)
    
    summary = []
    total_items = len(vault_index.get('items', []))
    total_size = sum(item.get('size', 0) for item in vault_index.get('items', []))
    
    summary.append(f"Total items in vault: {total_items}")
    summary.append(f"Total size of vault: {total_size} bytes")
    
    print("\n".join(summary))

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
