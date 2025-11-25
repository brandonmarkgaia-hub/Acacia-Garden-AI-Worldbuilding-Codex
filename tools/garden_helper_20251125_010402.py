```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    vault_index_path = ROOT / 'garden_vault_index.json'
    
    if not vault_index_path.is_file():
        print("Vault index file not found.")
        return
    
    with open(vault_index_path, 'r') as f:
        vault_index = json.load(f)
    
    summary = []
    for key, value in vault_index.items():
        summary.append(f"{key}: {len(value)} items")
    
    report = "\n".join(summary)
    print("Garden Vault Index Summary:\n")
    print(report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
