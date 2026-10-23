import argparse
from pathlib import Path
import json
import uuid
import os

def merge_data(file1_path, file2_path, output_path):
    """
    合并两个分子数据 JSON 文件，并为缺失 UUID 的项生成唯一的 UUID。
    """
    # 检查文件是否存在
    for path in [file1_path, file2_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(path)

    # 读取第一个文件
    with open(file1_path, 'r', encoding='utf-8') as f:
        data1 = json.load(f)

    # 读取第二个文件
    with open(file2_path, 'r', encoding='utf-8') as f:
        data2 = json.load(f)

    # 合并数据
    combined_data = data1 + data2

    # 收集所有现有的 UUID，以防冲突（虽然概率极低）
    existing_uuids = {item.get('uuid') for item in combined_data if item.get('uuid')}

    new_count = 0
    # 为没有 UUID 的项生成新的 UUID
    for item in combined_data:
        if not item.get('uuid'):
            new_uuid = str(uuid.uuid4())
            # 确保生成的 UUID 不重复
            while new_uuid in existing_uuids:
                new_uuid = str(uuid.uuid4())
            item['uuid'] = new_uuid
            existing_uuids.add(new_uuid)
            new_count += 1

    # 保存合并后的数据
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)

    print(f"成功合并数据！")
    print(f"- 文件 1 ({os.path.basename(file1_path)}) 数量: {len(data1)}")
    print(f"- 文件 2 ({os.path.basename(file2_path)}) 数量: {len(data2)}")
    print(f"- 合并后总数: {len(combined_data)}")
    print(f"- 新生成的 UUID 数量: {new_count}")
    print(f"- 结果已保存至: {output_path}")

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input1", type=Path, default=ROOT / "data/raw/molecules.json")
    parser.add_argument("--input2", type=Path, default=ROOT / "data/generated/NMRdata-2-260112_molecules.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/generated/combined_molecules.json")
    args = parser.parse_args()
    merge_data(args.input1, args.input2, args.output)
