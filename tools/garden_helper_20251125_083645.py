```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def summarize_vault_index():
    vault_index_path = ROOT / 'garden_vault_index.json'
    
    if not vault_index_path.is_file():
        print(f"Vault index file not found: {vault_index_path}")
        return

    with open(vault_index_path, 'r') as file:
        vault_index = json.load(file)

    summary = []
    total_entries = len(vault_index.get('entries', []))
    summary.append(f"Total entries in vault index: {total_entries}")

    for entry in vault_index.get('entries', []):
        entry_name = entry.get('name', 'Unnamed')
        entry_type = entry.get('type', 'Unknown')
        summary.append(f" - {entry_name} (Type: {entry_type})")

    report = "\n".join(summary)
    print("Vault Index Summary:\n" + report)

def main():
    summarize_vault_index()

if __name__ == "__main__":
    main()
```
