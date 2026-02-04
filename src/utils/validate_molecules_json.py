from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


def calc_formula_and_exact_mw_from_smiles(smiles: str) -> Tuple[bool, str, Optional[float]]:
    """
    用 RDKit 从 SMILES 计算分子式与分子量：
    - smiles_ok=False 表示 RDKit 无法解析该 SMILES
    - 分子量采用 RDKit 的 Descriptors.ExactMolWt（单同位素精确质量）
    """
    s = (smiles or "").strip()
    if not s:
        return False, "", None

    mol = Chem.MolFromSmiles(s)
    if mol is None:
        return False, "", None

    formula = CalcMolFormula(mol)
    mw = float(Descriptors.ExactMolWt(mol))
    return True, formula, mw


def load_molecules_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"molecules.json 顶层必须是 list，但读到的是: {type(data).__name__}")
    return data


def write_molecules_json(path: str, molecules: List[Dict[str, Any]]) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(molecules, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def recompute_formula_and_weight_inplace(
    molecules: List[Dict[str, Any]],
    *,
    max_rows: Optional[int] = None,
) -> Dict[str, int]:
    cache: Dict[str, Tuple[bool, str, Optional[float]]] = {}
    invalid_smiles_count = 0
    processed = 0

    items = molecules if max_rows is None else molecules[: max(0, max_rows)]
    for item in items:
        if not isinstance(item, dict):
            continue

        smiles = str(item.get("smiles") or "").strip()
        if smiles in cache:
            smiles_ok, formula, mw = cache[smiles]
        else:
            smiles_ok, formula, mw = calc_formula_and_exact_mw_from_smiles(smiles)
            cache[smiles] = (smiles_ok, formula, mw)

        if not smiles_ok:
            invalid_smiles_count += 1
            item["molecular_formula"] = ""
            item["molecular_weight"] = 0.0
        else:
            item["molecular_formula"] = formula
            item["molecular_weight"] = float(mw) if mw is not None else 0.0

        processed += 1

    return {"processed": processed, "invalid_smiles": invalid_smiles_count}
