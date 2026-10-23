import argparse
from pathlib import Path
import json
import os
from collections import defaultdict

# 尝试导入 RDKit 用于 SMILES 标准化
try:
    from rdkit import Chem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

def normalize_smiles(smiles):
    """
    对 SMILES 进行规范化处理。
    如果安装了 RDKit，将返回规范化的 Canonical SMILES。
    """
    if not smiles:
        return None

    if HAS_RDKIT:
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                # 返回规范化的、包含手性信息的 SMILES
                return Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
        except Exception:
            pass

    # 如果没有 RDKit 或转换失败，返回去除空格后的原字符串
    return smiles.strip()

def check_and_deduplicate(input_path, output_path=None):
    """
    检查 JSON 文件中是否存在重复的分子，并可选地保存去重后的数据。
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    print(f"正在读取文件: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not HAS_RDKIT:
        print("提示: 未检测到 RDKit，将使用原始字符串进行比对（准确度较低）。")
    else:
        print("已加载 RDKit，将进行规范化 SMILES 比对。")

    # 用于统计重复项
    smiles_map = defaultdict(list)
    # 用于存储去重后的数据（保持顺序）
    deduplicated_data = []
    # 用于记录已处理过的规范化 SMILES
    seen_smiles = set()

    for index, item in enumerate(data):
        raw_smiles = item.get('smiles')
        norm_smiles = normalize_smiles(raw_smiles)

        if norm_smiles:
            # 记录所有出现的 SMILES 用于查重报告
            smiles_map[norm_smiles].append({
                'index': index,
                'name': item.get('molecule_name'),
                'uuid': item.get('uuid'),
                'raw_smiles': raw_smiles
            })

            # 如果是第一次见到这个 SMILES，加入去重后的列表
            if norm_smiles not in seen_smiles:
                deduplicated_data.append(item)
                seen_smiles.add(norm_smiles)
        else:
            # 没有 SMILES 的数据直接保留（或者你可以根据需求调整）
            deduplicated_data.append(item)

    # 找出重复项并打印报告
    duplicates = {s: items for s, items in smiles_map.items() if len(items) > 1}

    if not duplicates:
        print("\n✅ 未发现重复分子。")
    else:
        for norm_smiles, items in duplicates.items():
            print(f"\n--- 标准化 SMILES: {norm_smiles} ---")
            for entry in items:
                print(f"  - [索引 {entry['index']}] 名字: {entry['name']} (UUID: {entry['uuid']})")
        print(f"\n⚠️ 发现 {len(duplicates)} 组重复分子：")
    # 如果指定了输出路径，保存去重后的数据
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deduplicated_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 去重完成！")
        print(f"- 原始数量: {len(data)}")
        print(f"- 去重后数量: {len(deduplicated_data)}")
        print(f"- 结果已保存至: {output_path}")

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/generated/combined_molecules.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/generated/deduplicated_molecules.json")
    args = parser.parse_args()
    check_and_deduplicate(args.input, args.output)
