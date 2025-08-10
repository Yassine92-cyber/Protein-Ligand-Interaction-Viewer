import numpy as np
from typing import List, Tuple, Dict, Optional
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolDescriptors
from .schemas import Contact, ContactParams, AnalyzeResponse


def parse_pdb(pdb_text: str) -> Tuple[Chem.Mol, Dict[int, Dict]]:
    """Parse PDB text and return RDKit molecule with residue annotations"""
    mol = Chem.MolFromPDBBlock(pdb_text, sanitize=False)
    if mol is None:
        raise ValueError("Failed to parse PDB text")
    
    # Parse PDB lines to get residue information
    residue_info = {}
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            try:
                atom_idx = int(line[6:11]) - 1  # PDB atom numbering starts at 1
                res_name = line[17:20].strip()
                res_id = int(line[22:26])
                atom_name = line[12:16].strip()
                
                if atom_idx < mol.GetNumAtoms():
                    residue_info[atom_idx] = {
                        'res_name': res_name,
                        'res_id': res_id,
                        'atom_name': atom_name
                    }
            except (ValueError, IndexError):
                continue
    
    return mol, residue_info


def parse_sdf(sdf_text: str) -> Chem.Mol:
    """Parse SDF text and return RDKit molecule"""
    mol = Chem.MolFromMolBlock(sdf_text)
    if mol is None:
        raise ValueError("Failed to parse SDF text")
    return mol


def get_coordinates(mol: Chem.Mol) -> np.ndarray:
    """Get 3D coordinates from RDKit molecule"""
    conf = mol.GetConformer()
    coords = []
    for i in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        coords.append([pos.x, pos.y, pos.z])
    return np.array(coords)


def detect_hbonds(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                  protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                  residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect hydrogen bonds between protein and ligand"""
    contacts = []
    
    # Simple donor/acceptor heuristics
    donor_atoms = ['N', 'O', 'S']
    acceptor_atoms = ['N', 'O', 'S']
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if protein_atom.GetSymbol() not in donor_atoms + acceptor_atoms:
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            if ligand_atom.GetSymbol() not in donor_atoms + acceptor_atoms:
                continue
            
            # Calculate distance
            dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
            if dist > params.hbond_max_dist:
                continue
            
            # Check if this is a valid H-bond (simplified)
            # In a real implementation, you'd check for H atoms and proper geometry
            if i in residue_info:
                res_info = residue_info[i]
                contacts.append(Contact(
                    type="HBOND",
                    ligand_atom=j,
                    protein_resi=res_info['res_id'],
                    protein_resn=res_info['res_name'],
                    protein_atom=res_info['atom_name'],
                    distance=dist,
                    angle=None  # Would calculate D-H-A angle in full implementation
                ))
    
    return contacts


def detect_hydrophobic(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                       protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                       residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect hydrophobic contacts between protein and ligand"""
    contacts = []
    
    # Hydrophobic atoms (C, S in sidechains, excluding polar contexts)
    hydrophobic_atoms = ['C', 'S']
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if protein_atom.GetSymbol() not in hydrophobic_atoms:
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            if ligand_atom.GetSymbol() != 'C':
                continue
            
            # Calculate distance
            dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
            if dist <= params.hydrophobic_max_dist:
                if i in residue_info:
                    res_info = residue_info[i]
                    contacts.append(Contact(
                        type="HYDROPHOBIC",
                        ligand_atom=j,
                        protein_resi=res_info['res_id'],
                        protein_resn=res_info['res_name'],
                        protein_atom=res_info['atom_name'],
                        distance=dist,
                        angle=None
                    ))
    
    return contacts


def detect_pi_stacking(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                       protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                       residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect π-π stacking interactions"""
    if not params.pi_stack:
        return []
    
    contacts = []
    
    # Aromatic residues
    aromatic_residues = ['PHE', 'TYR', 'TRP', 'HIS']
    
    # Find aromatic rings in protein and ligand
    protein_rings = []
    ligand_rings = []
    
    # Simplified ring detection - in practice, use RDKit's ring finding
    for i, atom in enumerate(protein_mol.GetAtoms()):
        if atom.GetIsAromatic() and i in residue_info:
            res_info = residue_info[i]
            if res_info['res_name'] in aromatic_residues:
                protein_rings.append((i, protein_coords[i]))
    
    for i, atom in enumerate(ligand_mol.GetAtoms()):
        if atom.GetIsAromatic():
            ligand_rings.append((i, ligand_coords[i]))
    
    # Check ring-ring distances (simplified)
    for p_ring in protein_rings:
        for l_ring in ligand_rings:
            dist = np.linalg.norm(p_ring[1] - l_ring[1])
            if 4.4 <= dist <= 7.0:  # π-π stacking distance range
                res_info = residue_info[p_ring[0]]
                contacts.append(Contact(
                    type="PI-PI",
                    ligand_atom=l_ring[0],
                    protein_resi=res_info['res_id'],
                    protein_resn=res_info['res_name'],
                    protein_atom=res_info['atom_name'],
                    distance=dist,
                    angle=None
                ))
    
    return contacts


def detect_salt_bridges(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                        protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                        residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect salt bridge interactions"""
    contacts = []
    
    # Charged residues
    positive_residues = ['LYS', 'ARG']
    negative_residues = ['ASP', 'GLU']
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if i not in residue_info:
            continue
            
        res_info = residue_info[i]
        res_name = res_info['res_name']
        
        # Check if this is a charged residue
        is_charged = False
        if res_name in positive_residues:
            is_charged = True
        elif res_name in negative_residues:
            is_charged = True
        
        if not is_charged:
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            # Check if ligand atom has opposite charge (simplified)
            # In practice, you'd use formal charges or pKa values
            
            # Calculate distance
            dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
            if dist <= params.salt_bridge_max_dist:
                contacts.append(Contact(
                    type="SALT_BRIDGE",
                    ligand_atom=j,
                    protein_resi=res_info['res_id'],
                    protein_resn=res_info['res_name'],
                    protein_atom=res_info['atom_name'],
                    distance=dist,
                    angle=None
                ))
    
    return contacts


def detect_metal_coordination(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                             protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                             residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect metal coordination interactions"""
    contacts = []
    
    # Metal ions
    metal_atoms = ['MG', 'ZN', 'FE', 'MN', 'CA']
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if protein_atom.GetSymbol() not in metal_atoms:
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            # Check if ligand atom is a heteroatom (not C or H)
            if ligand_atom.GetSymbol() in ['C', 'H']:
                continue
            
            # Calculate distance
            dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
            if dist <= params.metal_max_dist:
                if i in residue_info:
                    res_info = residue_info[i]
                    contacts.append(Contact(
                        type="METAL",
                        ligand_atom=j,
                        protein_resi=res_info['res_id'],
                        protein_resn=res_info['res_name'],
                        protein_atom=res_info['atom_name'],
                        distance=dist,
                        angle=None
                    ))
    
    return contacts


def get_summaries(protein_mol: Chem.Mol, ligand_mol: Chem.Mol, 
                  residue_info: Dict[int, Dict]) -> Tuple[Dict, Dict]:
    """Get ligand and protein summaries"""
    # Ligand summary
    ligand_summary = {
        "atoms": ligand_mol.GetNumAtoms(),
        "bonds": ligand_mol.GetNumBonds()
    }
    
    # Protein summary (simplified)
    unique_residues = set()
    unique_chains = set()
    
    for res_info in residue_info.values():
        unique_residues.add(res_info['res_id'])
        # In a full implementation, you'd extract chain info from PDB
    
    protein_summary = {
        "residues": len(unique_residues),
        "chains": len(unique_chains) if unique_chains else 1
    }
    
    return ligand_summary, protein_summary


def analyze_protein_ligand_interactions(pdb_text: str, sdf_text: str, 
                                      params: ContactParams) -> AnalyzeResponse:
    """Main function to analyze protein-ligand interactions"""
    warnings = []
    
    try:
        # Parse structures
        protein_mol, residue_info = parse_pdb(pdb_text)
        ligand_mol = parse_sdf(sdf_text)
        
        # Get coordinates
        protein_coords = get_coordinates(protein_mol)
        ligand_coords = get_coordinates(ligand_mol)
        
        # Detect different types of contacts
        contacts = []
        contacts.extend(detect_hbonds(protein_coords, ligand_coords, protein_mol, 
                                   ligand_mol, residue_info, params))
        contacts.extend(detect_hydrophobic(protein_coords, ligand_coords, protein_mol, 
                                        ligand_mol, residue_info, params))
        contacts.extend(detect_pi_stacking(protein_coords, ligand_coords, protein_mol, 
                                        ligand_mol, residue_info, params))
        contacts.extend(detect_salt_bridges(protein_coords, ligand_coords, protein_mol, 
                                         ligand_mol, residue_info, params))
        contacts.extend(detect_metal_coordination(protein_coords, ligand_coords, protein_mol, 
                                               ligand_mol, residue_info, params))
        
        # Get summaries
        ligand_summary, protein_summary = get_summaries(protein_mol, ligand_mol, residue_info)
        
        return AnalyzeResponse(
            contacts=contacts,
            ligand_summary=ligand_summary,
            protein_summary=protein_summary,
            warnings=warnings
        )
        
    except Exception as e:
        warnings.append(f"Analysis error: {str(e)}")
        raise 