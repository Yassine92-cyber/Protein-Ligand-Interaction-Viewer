from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import numpy as np


class ContactParams(BaseModel):
    """Parameters for contact detection with validation and clamping"""
    hbond_max_dist: float = Field(default=3.5, ge=0.5, le=10.0, description="H-bond maximum distance in Å")
    hbond_min_angle: float = Field(default=120.0, ge=90.0, le=180.0, description="H-bond minimum angle in degrees")
    hydrophobic_max_dist: float = Field(default=4.0, ge=1.0, le=10.0, description="Hydrophobic maximum distance in Å")
    pi_stack: bool = Field(default=True, description="Enable π-π stacking detection")
    salt_bridge_max_dist: float = Field(default=4.0, ge=1.0, le=10.0, description="Salt bridge maximum distance in Å")
    metal_max_dist: float = Field(default=2.8, ge=1.0, le=5.0, description="Metal coordination maximum distance in Å")
    
    @field_validator('*', mode='before')
    @classmethod
    def clamp_numeric_values(cls, v, info):
        """Clamp numeric values to reasonable ranges"""
        if isinstance(v, (int, float)) and info.field_name != 'pi_stack':
            # Define hardcoded ranges for each field
            ranges = {
                'hbond_max_dist': (0.5, 10.0),
                'hbond_min_angle': (90.0, 180.0),
                'hydrophobic_max_dist': (1.0, 10.0),
                'salt_bridge_max_dist': (1.0, 10.0),
                'metal_max_dist': (1.0, 5.0)
            }
            
            if info.field_name in ranges:
                min_val, max_val = ranges[info.field_name]
                if v < min_val:
                    v = min_val
                if v > max_val:
                    v = max_val
        return v


class VisualizationParams(BaseModel):
    """Parameters for visualization options"""
    color_contact_residues: bool = Field(default=True, description="Color residues involved in contacts")
    highlight_ligand_contacts: bool = Field(default=True, description="Highlight ligand atoms involved in contacts")
    show_contact_labels: bool = Field(default=True, description="Show contact type labels")
    hide_waters_ions: bool = Field(default=True, description="Hide water molecules and ions")


class Contact(BaseModel):
    """A single protein-ligand contact"""
    type: Literal["HBOND", "HYDROPHOBIC", "PI-PI", "SALT_BRIDGE", "METAL"]
    ligand_atom: int
    protein_resi: int
    protein_resn: str
    protein_atom: str
    distance: float = Field(ge=0.0, le=20.0, description="Distance in Å")
    angle: Optional[float] = Field(None, ge=0.0, le=180.0, description="Angle in degrees")


class AnalyzeRequest(BaseModel):
    """Request for protein-ligand interaction analysis"""
    pdb_text: str
    sdf_text: str
    params: ContactParams
    viz_params: Optional[VisualizationParams] = None


class AnalyzeResponse(BaseModel):
    """Response from protein-ligand interaction analysis"""
    contacts: List[Contact]
    ligand_summary: dict[str, int]  # {"atoms": int, "bonds": int}
    protein_summary: dict[str, int]  # {"chains": int, "residues": int}
    warnings: List[str]
    filtered_pdb: Optional[str] = None  # PDB with waters/ions removed if requested 