import os
import shutil
import re
from pathlib import Path
import argparse

# Regex to extract UUID from filename
# Matches pattern like ..._uuid.json
UUID_PATTERN = re.compile(r"_([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\.json$")

def get_uuid_map(directory: Path):
    """
    Scans a directory for JSON files and returns a map of {uuid: file_path}.
    """
    uuid_map = {}
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return uuid_map

    for file_path in directory.glob("*.json"):
        match = UUID_PATTERN.search(file_path.name)
        if match:
            uuid = match.group(1)
            uuid_map[uuid] = file_path
    
    return uuid_map

def copy_intersection(dir1_path: str, dir2_path: str, target_base_path: str):
    dir1 = Path(dir1_path)
    dir2 = Path(dir2_path)
    target_base = Path(target_base_path)

    print(f"Scanning {dir1}...")
    map1 = get_uuid_map(dir1)
    print(f"Found {len(map1)} files with UUIDs in {dir1.name}")

    print(f"Scanning {dir2}...")
    map2 = get_uuid_map(dir2)
    print(f"Found {len(map2)} files with UUIDs in {dir2.name}")

    # Find intersection
    common_uuids = set(map1.keys()) & set(map2.keys())
    print(f"Found {len(common_uuids)} common UUIDs.")

    if not common_uuids:
        print("No common files found.")
        return

    # Create target directories
    target_dir1 = target_base / dir1.name
    target_dir2 = target_base / dir2.name
    
    os.makedirs(target_dir1, exist_ok=True)
    os.makedirs(target_dir2, exist_ok=True)
    print(f"Created target directories: \n  {target_dir1}\n  {target_dir2}")

    # Copy files
    count = 0
    for uuid in common_uuids:
        src1 = map1[uuid]
        src2 = map2[uuid]
        
        dst1 = target_dir1 / src1.name
        dst2 = target_dir2 / src2.name
        
        shutil.copy2(src1, dst1)
        shutil.copy2(src2, dst2)
        count += 1
        
        if count % 100 == 0:
            print(f"Copied {count} files...")

    print(f"Successfully copied {count} pairs of files to {target_base}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy files with common UUIDs from two directories to a new location.")
    parser.add_argument("--dir1", type=str, required=True, help="Path to first source directory")
    parser.add_argument("--dir2", type=str, required=True, help="Path to second source directory")
    parser.add_argument("--output", type=str, required=True, help="Path to output base directory")
    
    args = parser.parse_args()
    
    copy_intersection(args.dir1, args.dir2, args.output)