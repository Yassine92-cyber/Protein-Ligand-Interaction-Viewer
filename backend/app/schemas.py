from typing import List, Literal, Optional
from pydantic import BaseModel


class ContactParams(BaseModel):
    """Parameters for contact detection"""
    hbond_max_dist: float = 3.5
    hbond_min_angle: float = 120.0
    hydrophobic_max_dist: float = 4.0
    pi_stack: bool = True
    salt_bridge_max_dist: float = 4.0
    metal_max_dist: float = 2.8


class Contact(BaseModel):
    """A single protein-ligand contact"""
    type: Literal["HBOND", "HYDROPHOBIC", "PI-PI", "SALT_BRIDGE", "METAL"]
    ligand_atom: int
    protein_resi: int
    protein_resn: str
    protein_atom: str
    distance: float
    angle: Optional[float] = None


class AnalyzeRequest(BaseModel):
    """Request for protein-ligand interaction analysis"""
    pdb_text: str
    sdf_text: str
    params: ContactParams


class AnalyzeResponse(BaseModel):
    """Response from protein-ligand interaction analysis"""
    contacts: List[Contact]
    ligand_summary: dict[str, int]  # {"atoms": int, "bonds": int}
    protein_summary: dict[str, int]  # {"chains": int, "residues": int}
    warnings: List[str] 