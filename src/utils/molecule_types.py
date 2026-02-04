from typing import Optional
from pydantic import BaseModel, Field

class RawData(BaseModel):
    # Using alias for fields starting with numbers if needed, but python allows dict keys with numbers. 
    # However, pydantic fields must be valid identifiers.
    # So we use alias="1H_NMR" etc.
    h1_nmr: Optional[str] = Field(None, alias="1H_NMR")
    c13_nmr: Optional[str] = Field(None, alias="13C_NMR")
    f19_nmr: Optional[str] = Field(None, alias="19F_NMR")
    p31_nmr: Optional[str] = Field(None, alias="31P_NMR")
    
    ir_film: Optional[str] = Field(None, alias="IR_film")
    ir_neat: Optional[str] = Field(None, alias="IR_neat")
    
    hrms_esi: Optional[str] = Field(None, alias="HRMS_ESI")
    ms_ei: Optional[str] = Field(None, alias="MS_EI")
    hrms_ei: Optional[str] = Field(None, alias="HRMS_EI")
    ms_apci: Optional[str] = Field(None, alias="MS_APCI")
    hrms_apci: Optional[str] = Field(None, alias="HRMS_APCI")
    hrms_ci: Optional[str] = Field(None, alias="HRMS_CI")
    
    melting_point: Optional[str] = Field(None, alias="Melting_Point")
    tlc: Optional[str] = Field(None, alias="TLC")
    optical_rotation: Optional[str] = Field(None, alias="Optical_Rotation")

    class Config:
        populate_by_name = True

class Properties(BaseModel):
    has_carbonyl: Optional[bool] = None

class MoleculeData(BaseModel):
    molecule_name: str
    uuid: str
    smiles: str = ""
    molecular_formula: str
    molecular_weight: float
    
    inchi: Optional[str] = ""
    inchi_key: Optional[str] = ""
    
    raw_data: RawData = Field(default_factory=RawData)
    properties: Properties = Field(default_factory=Properties)
