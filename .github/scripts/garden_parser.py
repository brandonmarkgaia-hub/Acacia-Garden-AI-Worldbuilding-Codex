import os
import re
import json
import logging

class GardenParser:
    def __init__(self, garden_root="."):
        """
        Initializes the parser to read the Acacia Garden repository.
        By default, it looks at the root of your repo.
        """
        self.garden_root = garden_root
        logging.info(f"Garden Parser initialized at root: {self.garden_root}")

    def parse_file(self, filepath):
        """
        Reads a markdown file, extracts the YAML frontmatter, 
        and separates it from the core lore.
        """
        full_path = os.path.join(self.garden_root, filepath)
        
        if not os.path.exists(full_path):
            logging.error(f"Chamber not found: {full_path}")
            return {"error": "File not found. Verify the path."}

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to cleanly catch the YAML frontmatter between the --- lines
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
        
        metadata = {}
        lore_body = content

        if frontmatter_match:
            raw_yaml = frontmatter_match.group(1)
            lore_body = frontmatter_match.group(2).strip()
            
            # Ultra-lightweight extraction of the key: value pairs
            for line in raw_yaml.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    metadata[key.strip()] = val.strip()
        else:
            logging.warning(f"No Keeper Seal/YAML frontmatter found in {filepath}")

        return {
            "filepath": filepath,
            "metadata": metadata,
            "content": lore_body
        }

    def scan_nodes(self):
        """
        Placeholder for scanning all 1,525+ nodes for specific archetypes.
        This will be expanded to map the entire Garden graph.
        """
        return "Scanning functionality ready for expansion."

# Quick test block that only runs if you execute this file directly
if __name__ == "__main__":
    parser = GardenParser()
    print("Garden Parser ready to process Chambers.")
