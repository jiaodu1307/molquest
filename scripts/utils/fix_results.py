import json
import os
import sys
import glob
import argparse
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utils.trace import parse_final_result


def fix_run_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        final_answer = data.get("final_answer")
        uuid = data.get("uuid", "unknown")
        
        # Original result
        old_result = data.get("final_result", {})
        
        # New result
        new_result = parse_final_result(final_answer, uuid)
        
        # Compare and update if necessary
        # We check if key fields are different
        if (new_result.get("predicted_smiles") != old_result.get("predicted_smiles") or
            new_result.get("confidence") != old_result.get("confidence") or
            new_result.get("reason_brief") != old_result.get("reason_brief")):
            
            print(f"Updating {file_path}...")
            print(f"  Old SMILES: {old_result.get('predicted_smiles')}")
            print(f"  New SMILES: {new_result.get('predicted_smiles')}")
            
            data["final_result"] = new_result
            
            # Create a backup just in case
            # shutil.copy(file_path, file_path + ".bak")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        # else:
            # print(f"No changes needed for {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fix parsed results in run files.")
    parser.add_argument("runs_dir", type=str, nargs="?", default="runs", help="Directory containing run JSON files.")
    args = parser.parse_args()
    
    if not os.path.exists(args.runs_dir):
        print(f"Directory {args.runs_dir} does not exist.")
        return

    files = glob.glob(os.path.join(args.runs_dir, "run_*.json"))
    print(f"Found {len(files)} run files in {args.runs_dir}")
    
    count = 0
    for file_path in files:
        fix_run_file(file_path)
        count += 1
        
    print(f"Processed {count} files.")

if __name__ == "__main__":
    main()