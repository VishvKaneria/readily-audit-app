import json
import os

INPUT_FILE = "policy_index.json"   # your big JSON file in same folder
OUTPUT_DIR = "policy_parts"        # folder where parts will be saved
ITEMS_PER_PART = 5000              # adjust if parts are still >100MB

def split_json():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load full JSON (assumes it's a list of dicts)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_items = len(data)
    print(f"Loaded {total_items} items from {INPUT_FILE}")

    # Split into chunks
    part = 1
    for i in range(0, total_items, ITEMS_PER_PART):
        chunk = data[i:i + ITEMS_PER_PART]
        out_path = os.path.join(OUTPUT_DIR, f"policy_index_part{part}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(chunk)} items to {out_path}")
        part += 1

if __name__ == "__main__":
    split_json()
