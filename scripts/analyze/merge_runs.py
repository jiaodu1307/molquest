import json
import os
import argparse
from typing import List, Dict, Any

def merge_runs(runs_dir: str, output_file: str):
    """
    Merge all JSON files in runs_dir into a single JSON file.
    """
    if not os.path.isdir(runs_dir):
        print(f"Error: Directory '{runs_dir}' does not exist.")
        return

    merged_data: List[Dict[str, Any]] = []
    
    files = [f for f in os.listdir(runs_dir) if f.endswith(".json")]
    files.sort() # Ensure deterministic order if needed, or by time

    print(f"Found {len(files)} run files in '{runs_dir}'. Merging...")

    for filename in files:
        filepath = os.path.join(runs_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged_data.append(data)
        except Exception as e:
            print(f"Warning: Failed to read {filepath}: {e}")

    # Save merged data
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully merged {len(merged_data)} records into '{output_file}'.")

def main():
    parser = argparse.ArgumentParser(description="Merge individual run JSON files into one.")
    parser.add_argument(
        "--runs-dir",
        type=str,
        default="runs",
        help="Directory containing individual run JSON files",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="merged_runs.json",
        help="Path to the output merged JSON file",
    )
    
    args = parser.parse_args()
    merge_runs(args.runs_dir, args.output)

if __name__ == "__main__":
    main()
