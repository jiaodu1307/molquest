from typing import Optional, Any, Dict, List, Callable
from pydantic import BaseModel, Field
from src.core.tool import BaseTool
from src.core.logger import logger
from src.utils.molecule_manager import MoleculeManager

# Try importing RDKit
try:
    from rdkit import Chem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False
    logger.warning("RDKit not found. Some tools will be unavailable.")

# --- Schemas ---

class UUIDInput(BaseModel):
    uuid: str = Field(..., description="The UUID of the sample to analyze")


_manager: Optional[MoleculeManager] = None


def _get_manager() -> MoleculeManager:
    global _manager
    if _manager is None:
        _manager = MoleculeManager()
    return _manager


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    return False


def _get_sample_data(uuid: str) -> Dict[str, Any]:
    item = _get_manager().get_molecule(uuid)
    if item is None:
        raise ValueError(f"Sample {uuid} not found.")

    raw = item.raw_data
    properties = item.properties

    has_carbonyl = properties.has_carbonyl
    if has_carbonyl is None:
        ir_data = str(raw.ir_film or raw.ir_neat or "")
        has_carbonyl = "17" in ir_data or ("16" in ir_data and "cm-1" in ir_data)

    hrms_parts = [part for part in [raw.hrms_esi, raw.hrms_ei, raw.hrms_apci, raw.hrms_ci] if part]
    ms_parts = [part for part in [raw.ms_ei, raw.ms_apci] if part]

    return {
        "smiles": item.smiles,
        "mw": item.molecular_weight,
        "formula": item.molecular_formula,
        "1h_nmr": raw.h1_nmr or "",
        "13c_nmr": raw.c13_nmr or "",
        "ir": raw.ir_film or raw.ir_neat or "",
        "n19f_nmr": raw.f19_nmr or "",
        "n31p_nmr": raw.p31_nmr or "",
        "hrms": " | ".join(hrms_parts),
        "ms": " | ".join(ms_parts),
        "melting_point": raw.melting_point or "",
        "tlc": raw.tlc or "",
        "optical_rotation": raw.optical_rotation or "",
        "has_carbonyl": has_carbonyl,
    }


def _get_required_value(
    uuid: str,
    key: str,
    treat_empty_as_missing: bool = True,
) -> Any:
    data = _get_sample_data(uuid)
    value = data.get(key)
    if treat_empty_as_missing:
        if _is_missing(value):
            raise ValueError(f"Sample {uuid} has no '{key}' data.")
        return value

    if value is None:
        raise ValueError(f"Sample {uuid} has no '{key}' data.")
    return value


# --- Implementations ---

class MeasureMWTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Measure_MW",
            description="Get molecular weight. Returns a float in Da.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> float:
        return _get_required_value(
            uuid=uuid,
            key="mw",
            treat_empty_as_missing=False,
        )

class MeasureFormulaTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Measure_Formula",
            description="Get molecular formula. Returns a string, e.g. \"C22H32N2O3S\".",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="formula",
        )

class Get1HNMRTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_1H_NMR",
            description="Get 1H NMR peak list/description text. Returns a string, e.g. \"1H NMR (300 MHz, CDCl3): δ ...\".",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="1h_nmr",
        )

class Get13CNMRTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_13C_NMR",
            description="Get 13C NMR peak list/description text. Returns a string, e.g. \"13C NMR (75 MHz, CDCl3): δ ...\".",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="13c_nmr",
        )


class GetIRTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_IR",
            description="Get IR spectrum description text. Commonly used to confirm functional groups (e.g., C=O, O-H).",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="ir",
        )


class Get19FNMRTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_19F_NMR",
            description="Get 19F NMR description text. Typically meaningful only when the molecule contains F.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="n19f_nmr",
        )


class Get31PNMRTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_31P_NMR",
            description="Get 31P NMR description text. Typically meaningful only when the molecule contains P.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="n31p_nmr",
        )


class GetHRMSTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_HRMS",
            description="Get HRMS description text/peak info. Commonly used to confirm molecular formula, isotopic pattern, or exact mass.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="hrms",
        )


class GetMSTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_MS",
            description="Get MS (non-HRMS) description text/peak info. Commonly used to estimate molecular weight and inspect fragment peaks.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="ms",
        )


class GetMeltingPointTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_Melting_Point",
            description="Get melting point information. Returns a string (typically includes unit and range, e.g. \"mp 120–122 °C\").",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="melting_point",
        )


class GetTLCTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_TLC",
            description="Get TLC information (Rf, eluent/solvent system, etc.). Returns a string.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="tlc",
        )


class GetOpticalRotationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Get_Optical_Rotation",
            description="Get optical rotation information (e.g., [α]D value, solvent, concentration). Returns a string.",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> str:
        return _get_required_value(
            uuid=uuid,
            key="optical_rotation",
        )

class CalculateDBETool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Calculate_DBE",
            description="Calculate degrees of unsaturation (DBE). Requires sample SMILES and RDKit. Returns a float; returns -1.0 if unavailable (unknown).",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> float:
        data = _get_sample_data(uuid)
        smiles = (data.get("smiles") or "").strip()
        if not HAS_RDKIT or not smiles:
            return -1.0

        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return -1.0

        num_C = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == "C")
        num_H = sum(a.GetTotalNumHs() for a in mol.GetAtoms())
        num_N = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == "N")
        num_X = sum(1 for a in mol.GetAtoms() if a.GetSymbol() in {"F", "Cl", "Br", "I"})

        dbe = num_C + 1 - num_H / 2 - num_X / 2 + num_N / 2
        return float(dbe)

class CheckDataTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="Check_Data",
            description="List which experimental data are available for the sample. Returns a list of tool names, e.g. [\"Measure_MW\", \"Get_13C_NMR\", \"Get_IR\"].",
            args_schema=UUIDInput
        )

    def _run(self, uuid: str) -> List[str]:
        data = _get_sample_data(uuid)
        available: List[str] = []
        if data.get("mw") is not None:
            available.append("Measure_MW")
        if not _is_missing(data.get("formula")):
            available.append("Measure_Formula")
        if not _is_missing(data.get("1h_nmr")):
            available.append("Get_1H_NMR")
        if not _is_missing(data.get("13c_nmr")):
            available.append("Get_13C_NMR")
        if not _is_missing(data.get("ir")):
            available.append("Get_IR")
        if not _is_missing(data.get("n19f_nmr")):
            available.append("Get_19F_NMR")
        if not _is_missing(data.get("n31p_nmr")):
            available.append("Get_31P_NMR")
        if not _is_missing(data.get("hrms")):
            available.append("Get_HRMS")
        if not _is_missing(data.get("ms")):
            available.append("Get_MS")
        if not _is_missing(data.get("melting_point")):
            available.append("Get_Melting_Point")
        if not _is_missing(data.get("tlc")):
            available.append("Get_TLC")
        if not _is_missing(data.get("optical_rotation")):
            available.append("Get_Optical_Rotation")

        return available
