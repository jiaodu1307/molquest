import argparse
from pathlib import Path
import json
import os
from rdkit import Chem

def has_carbonyl(smiles):
    """Detect carbonyl groups from molecular connectivity."""
    mol = Chem.MolFromSmiles(smiles or "")
    return bool(mol and mol.HasSubstructMatch(Chem.MolFromSmarts("[C,c]=[O]")))

def transform_raw_data(raw_data):
    """
    将原始的 raw_data 格式转换为目标格式，统一键名
    适应新格式中带有空格的键名，如 "1H NMR" -> "1H_NMR"
    """
    if not raw_data:
        return {}

    # 定义从新格式键名到目标格式键名的映射
    mapping = {
        "1H NMR": "1H_NMR",
        "13C NMR": "13C_NMR",
        "19 F NMR": "19F_NMR",
        "19F NMR": "19F_NMR",
        "31P NMR": "31P_NMR",
        "31 P NMR": "31P_NMR",
        "FT-IR (film)": "IR_film",
        "TLC": "TLC",
        "Optical Rotation": "Optical_Rotation",
        "HRMS (ESI+)": "HRMS_ESI",
        "MS (EI)": "MS_EI",
        "HRMS (EI)": "HRMS_EI",
        "MS (APCI)": "MS_APCI",
        "HRMS (APCI)": "HRMS_APCI",
        "HRMS (CI)": "HRMS_CI"
    }

    new_raw_data = {}
    # 遍历映射表提取数据
    for old_key, target_key in mapping.items():
        if old_key in raw_data:
            new_raw_data[target_key] = raw_data.get(old_key)
        elif target_key not in new_raw_data and target_key not in raw_data:
            new_raw_data[target_key] = None

    for target_key in mapping.values():
        if target_key in raw_data:
            new_raw_data[target_key] = raw_data[target_key]

    # 补全目标格式中可能缺失的固定键
    target_keys = ["IR_neat", "Melting_Point"]
    for key in target_keys:
        if key not in new_raw_data:
            new_raw_data[key] = raw_data.get(key)

    return new_raw_data

def process_json(input_path, output_path):
    """
    处理输入文件并保存到输出路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_molecules = []

    # 新格式中 data 直接是分子列表
    for item in data:
        # 提取分子信息，适配新字段名
        molecule = {
            "molecule_name": item.get('molecule_name'),
            "uuid": item.get('uuid'), # 如果新数据没提供 uuid，这里会是 None
            "smiles": item.get('smiles'),
            "molecular_formula": item.get('molecular_formula'),
            "molecular_weight": item.get('molecular_weight'),
            "inchi": item.get('inchi', ""),
            "inchi_key": item.get('inchi_key', ""),
            "raw_data": transform_raw_data(item.get('raw_data', {})),
            "properties": {
                "has_carbonyl": has_carbonyl(item.get('smiles'))
            }
        }
        processed_molecules.append(molecule)

    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_molecules, f, indent=2, ensure_ascii=False)

    print(f"成功: 已将数据整理并保存至 {output_path}")
    print(f"共处理了 {len(processed_molecules)} 个分子数据")

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/NMRdata-2-260112.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/generated/NMRdata-2-260112_molecules.json")
    args = parser.parse_args()
    process_json(args.input, args.output)
