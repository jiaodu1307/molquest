import csv
import json
import os
import uuid
from typing import Any, Dict, List
import re

import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

from src.utils.molecule_types import MoleculeData, RawData, Properties


def load_llm() -> ChatOpenAI:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    llm_config = config.get("llm", {})
    model_name = llm_config.get("model_name", "gpt-4o")
    temperature = float(llm_config.get("temperature", 0))
    base_url = llm_config.get("base_url") or os.getenv("IDEALAB_BASE_URL") or os.getenv("OPENAI_API_BASE")

    load_dotenv()
    api_key = os.getenv("IDEALAB_API_KEY") or os.getenv("OPENAI_API_KEY")

    is_o_series = bool(re.match(r"^o\d", str(model_name).strip().lower()))
    kwargs = {
        "model": model_name,
        "api_key": api_key,
        "base_url": base_url,
    }
    if not is_o_series:
        kwargs["temperature"] = temperature

    return ChatOpenAI(**kwargs)


def compute_formula_and_mw(smiles: str) -> Dict[str, Any]:
    smiles = (smiles or "").strip()
    if not smiles:
        return {"molecular_formula": "", "molecular_weight": 0.0}

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"molecular_formula": "", "molecular_weight": 0.0}

    formula = CalcMolFormula(mol)
    mw = float(Descriptors.ExactMolWt(mol))
    return {"molecular_formula": formula, "molecular_weight": mw}


def build_messages(row: Dict[str, str]) -> List[Dict[str, Any]]:
    spectra = (row.get("spectra_inf") or "").strip()
    iupac = (row.get("IUPAC_name") or "").strip()
    smiles = (row.get("SMILES") or "").strip()

    system_content = (
        "你是有机波谱和数据整理助手。"
        "根据给定的谱图文本描述、IUPAC 名称和 SMILES，"
        "只负责从中提取与原始谱图和物性相关的信息，"
        "并整理为 JSON 中的 raw_data 和 properties 两个字段。"
        "不要推断或编造不存在的数据。"
        "所有无法从输入中确定的信息使用 null。"
        "输出时只返回一个 JSON 对象，不要包含任何额外文本。"
        "JSON 结构示例如下（仅为结构示例，具体值由你填充或设为 null）："
        "{"
        "\"raw_data\": {"
        "\"1H_NMR\": \"...\" 或 null,"
        "\"13C_NMR\": \"...\" 或 null,"
        "\"19F_NMR\": \"...\" 或 null,"
        "\"31P_NMR\": \"...\" 或 null,"
        "\"IR_film\": \"...\" 或 null,"
        "\"IR_neat\": \"...\" 或 null,"
        "\"HRMS_ESI\": \"...\" 或 null,"
        "\"MS_EI\": \"...\" 或 null,"
        "\"HRMS_EI\": \"...\" 或 null,"
        "\"MS_APCI\": \"...\" 或 null,"
        "\"HRMS_APCI\": \"...\" 或 null,"
        "\"HRMS_CI\": \"...\" 或 null,"
        "\"Melting_Point\": \"...\" 或 null,"
        "\"TLC\": \"...\" 或 null,"
        "\"Optical_Rotation\": \"...\" 或 null"
        "},"
        "\"properties\": {"
        "\"has_carbonyl\": true/false 或 null"
        "}"
        "}"
    )

    user_content_lines: List[str] = []
    if iupac:
        user_content_lines.append(f"IUPAC_name: {iupac}")
    if smiles:
        user_content_lines.append(f"SMILES: {smiles}")
    if spectra:
        user_content_lines.append(f"spectra_inf: {spectra}")
    else:
        user_content_lines.append("spectra_inf: (空)")

    user_content_lines.append(
        "请严格按照上面的 JSON 结构，从输入中提取信息。"
        "注意："
        "1. raw_data 中的键名必须和示例完全一致，例如 \"1H_NMR\"、\"13C_NMR\"。"
        "2. properties 只包含一个键 \"has_carbonyl\"。"
        "3. 只返回 JSON，不要添加解释性文字。"
    )

    user_content = "\n".join(user_content_lines)

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


def call_llm(model: ChatOpenAI, row: Dict[str, str]) -> Dict[str, Any]:
    messages = build_messages(row)
    resp = model.invoke(messages)
    content = resp.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    try:
        data = json.loads(content)
    except Exception:
        data = {"raw_data": {"1H_NMR": row.get("spectra_inf") or ""}, "properties": {"has_carbonyl": None}}
    if "raw_data" not in data or not isinstance(data["raw_data"], dict):
        data["raw_data"] = {"1H_NMR": row.get("spectra_inf") or ""}
    if "properties" not in data or not isinstance(data["properties"], dict):
        data["properties"] = {"has_carbonyl": None}
    return data


def build_molecule(row: Dict[str, str], parsed: Dict[str, Any]) -> MoleculeData:
    smiles = (row.get("SMILES") or "").strip()
    name = (row.get("IUPAC_name") or "").strip() or smiles or "Unknown"

    mw_info = compute_formula_and_mw(smiles)
    molecular_formula = mw_info["molecular_formula"]
    molecular_weight = mw_info["molecular_weight"]

    raw_data_payload = parsed.get("raw_data") or {}
    properties_payload = parsed.get("properties") or {}

    raw_data = RawData.model_validate(raw_data_payload)
    properties = Properties(**properties_payload)

    molecule = MoleculeData(
        molecule_name=name,
        uuid=str(uuid.uuid4()),
        smiles=smiles,
        molecular_formula=molecular_formula,
        molecular_weight=molecular_weight,
        raw_data=raw_data,
        properties=properties,
    )
    return molecule


def _write_molecules(output_path: str, molecules: List[MoleculeData]) -> None:
    data: List[Dict[str, Any]] = [m.model_dump(by_alias=True) for m in molecules]
    directory = os.path.dirname(output_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp_path = output_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, output_path)


def process_csv(
    input_path: str,
    output_path: str,
    max_rows: int | None = None,
    checkpoint_every: int | None = None,
) -> None:
    model = load_llm()
    molecules: List[MoleculeData] = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if max_rows is not None and idx > max_rows:
                break
            parsed = call_llm(model, row)
            molecule = build_molecule(row, parsed)
            molecules.append(molecule)
            if checkpoint_every and idx % checkpoint_every == 0:
                _write_molecules(output_path, molecules)

    _write_molecules(output_path, molecules)


__all__ = [
    "process_csv",
    "compute_formula_and_mw",
    "load_llm",
    "build_messages",
    "call_llm",
    "build_molecule",
]
