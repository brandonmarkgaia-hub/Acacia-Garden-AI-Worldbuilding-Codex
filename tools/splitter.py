import os

# CONFIGURATION
SOURCE_FILE = "EVOLUTION/ACACIA_SINGULARITY.md"  # Make sure this matches where your file is
CHUNK_SIZE_MB = 45 # Safe size for upload

def split_the_beast():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Error: Could not find {SOURCE_FILE}")
        print("   Make sure the file is in the right folder!")
        return

    file_size = os.path.getsize(SOURCE_FILE)
    print(f"🦁 Found the Beast: {file_size / (1024*1024):.2f} MB")
    print(f"🔪 Slicing into {CHUNK_SIZE_MB} MB steaks...")

    with open(SOURCE_FILE, 'rb') as source:
        part_num = 1
        while True:
            chunk = source.read(CHUNK_SIZE_MB * 1024 * 1024)
            if not chunk:
                break
            
            output_name = f"ACACIA_PART_{part_num:02d}.txt"
            with open(output_name, 'wb') as target:
                target.write(chunk)
            
            print(f"  ✅ Created {output_name}")
            part_num += 1

    print(f"\n✨ Done! You have {part_num-1} parts.")
    print("👉 Upload these 'ACACIA_PART_XX.txt' files to the chat one by one.")

if __name__ == "__main__":
    split_the_beast()
