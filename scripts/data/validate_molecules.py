import argparse
from pathlib import Path
import json
import os
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

def get_calculated_formula(mol):
    """计算分子的分子式"""
    return rdMolDescriptors.CalcMolFormula(mol)

def validate_and_fix_molecules(input_path, output_path, error_output_path):
    """
    校验并修复 JSON 文件中的分子式和分子量。
    如果 SMILES 缺失或无法解析，则将其移动到错误文件中。
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    print(f"正在读取文件: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    valid_data = []
    invalid_data = []
    fix_count = 0

    print("开始校验并修复数据...")

    for index, item in enumerate(data):
        smiles = item.get('smiles')

        # 1. 检查 SMILES 是否存在
        if not smiles:
            item['error_reason'] = "Missing SMILES"
            invalid_data.append(item)
            continue

        # 2. 检查 SMILES 是否合法
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            print(f"  - [索引 {index}] 错误: SMILES 无法解析 ({smiles})")
            item['error_reason'] = f"Invalid SMILES: {smiles}"
            invalid_data.append(item)
            continue

        # 复制数据准备修复
        new_item = item.copy()

        # 计算理论值
        calc_formula = get_calculated_formula(mol)
        calc_weight = round(Descriptors.MolWt(mol), 4)

        # 获取原始值
        orig_formula = str(item.get('molecular_formula', '')).strip().replace(" ", "")
        orig_weight = item.get('molecular_weight')

        has_change = False

        # 校验并修复分子式
        if orig_formula != calc_formula:
            new_item['molecular_formula'] = calc_formula
            has_change = True

        # 校验并修复分子量 (容差 0.1)
        if orig_weight is None or abs(float(orig_weight) - calc_weight) > 0.1:
            new_item['molecular_weight'] = calc_weight
            has_change = True

        if has_change:
            fix_count += 1

        # 将有效且修复后的数据加入列表
        valid_data.append(new_item)

    # 保存有效数据
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(valid_data, f, indent=2, ensure_ascii=False)

    # Always write the error report so reruns cannot leave stale failures.
    Path(error_output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(error_output_path, 'w', encoding='utf-8') as f:
        json.dump(invalid_data, f, indent=2, ensure_ascii=False)

    print(f"\n处理完成！")
    print(f"- 原始总数: {len(data)}")
    print(f"- 有效数据 (已保存至 {output_path}): {len(valid_data)}")
    print(f"- 无效数据 (已保存至 {error_output_path}): {len(invalid_data)}")
    print(f"- 修复了信息的分子数: {fix_count}")

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/generated/deduplicated_molecules.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/generated/validated_molecules.json")
    parser.add_argument("--errors", type=Path, default=ROOT / "data/generated/invalid_molecules.json")
    args = parser.parse_args()
    validate_and_fix_molecules(args.input, args.output, args.errors)
