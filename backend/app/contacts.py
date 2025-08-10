import numpy as np
from typing import List, Tuple, Dict, Optional, Set
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolDescriptors
from .schemas import Contact, ContactParams, AnalyzeResponse, VisualizationParams
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Security constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_ATOMS = 10000  # Maximum number of atoms to prevent excessive computation
MAX_CACHE_SIZE = 1000  # Maximum number of cached ring calculations
MAX_CACHE_AGE = 3600  # Maximum cache age in seconds (1 hour)

# Cache for ring centroids and normals to avoid recomputation
_ring_cache: Dict[str, Dict] = {}
_cache_timestamps: Dict[str, float] = {}

def clear_ring_cache():
    """Clear the ring cache to free memory and allow fresh computation"""
    global _ring_cache, _cache_timestamps
    _ring_cache.clear()
    _cache_timestamps.clear()

def _cleanup_expired_cache():
    """Remove expired cache entries to prevent memory leaks"""
    import time
    current_time = time.time()
    expired_keys = [
        key for key, timestamp in _cache_timestamps.items()
        if current_time - timestamp > MAX_CACHE_AGE
    ]
    for key in expired_keys:
        _ring_cache.pop(key, None)
        _cache_timestamps.pop(key, None)

def _enforce_cache_size_limit():
    """Enforce cache size limit by removing oldest entries"""
    if len(_ring_cache) > MAX_CACHE_SIZE:
        # Remove oldest entries (simple FIFO approach)
        keys_to_remove = list(_ring_cache.keys())[:len(_ring_cache) - MAX_CACHE_SIZE + 100]
        for key in keys_to_remove:
            _ring_cache.pop(key, None)
            _cache_timestamps.pop(key, None)

def get_cache_key(mol: Chem.Mol, mol_type: str) -> str:
    """Generate a unique cache key for a molecule"""
    # Use molecule hash and number of atoms for uniqueness
    mol_hash = hash(mol)
    num_atoms = mol.GetNumAtoms()
    return f"{mol_type}_{mol_hash}_{num_atoms}"

def _update_cache_timestamp(cache_key: str):
    """Update cache timestamp and enforce limits"""
    import time
    _cache_timestamps[cache_key] = time.time()
    _cleanup_expired_cache()
    _enforce_cache_size_limit()


def filter_waters_ions(pdb_text: str) -> str:
    """Filter out water molecules and common ions from PDB text"""
    filtered_lines = []
    water_residues = {'HOH', 'WAT', 'TIP3', 'SPC', 'SOL'}
    ion_residues = {'NA', 'CL', 'K', 'MG', 'CA', 'ZN', 'FE', 'MN', 'CU'}
    
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            res_name = line[17:20].strip()
            if res_name not in water_residues and res_name not in ion_residues:
                filtered_lines.append(line)
        else:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def validate_input_size(text: str, max_size: int = MAX_FILE_SIZE) -> None:
    """Validate input file size to prevent DoS attacks"""
    if len(text.encode('utf-8')) > max_size:
        raise ValueError(f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB")


def validate_molecule_complexity(mol: Chem.Mol, max_atoms: int = MAX_ATOMS) -> None:
    """Validate molecule complexity to prevent excessive computation"""
    if mol.GetNumAtoms() > max_atoms:
        raise ValueError(f"Molecule has {mol.GetNumAtoms()} atoms, exceeding maximum of {max_atoms}")


def parse_pdb(pdb_text: str, hide_waters_ions: bool = True) -> Tuple[Chem.Mol, Dict[int, Dict]]:
    """Parse PDB text and return RDKit molecule with residue annotations"""
    # Security validation
    validate_input_size(pdb_text)
    
    # Filter waters and ions if requested
    if hide_waters_ions:
        pdb_text = filter_waters_ions(pdb_text)
    
    mol = Chem.MolFromPDBBlock(pdb_text, sanitize=False)
    if mol is None:
        raise ValueError("Failed to parse PDB text")
    
    # Additional validation: ensure we have valid atoms
    if mol.GetNumAtoms() == 0:
        raise ValueError("PDB text contains no valid atoms")
    
    # Validate molecule complexity
    validate_molecule_complexity(mol)
    
    # Parse PDB lines to get residue information
    residue_info = {}
    atom_count = 0
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            try:
                atom_idx = atom_count
                res_name = line[17:20].strip()
                res_id = int(line[22:26])
                atom_name = line[12:16].strip()
                
                if atom_idx < mol.GetNumAtoms():
                    residue_info[atom_idx] = {
                        'res_name': res_name,
                        'res_id': res_id,
                        'atom_name': atom_name
                    }
                atom_count += 1
            except (ValueError, IndexError):
                continue
    
    return mol, residue_info


def parse_sdf(sdf_text: str) -> Chem.Mol:
    """Parse SDF text and return RDKit molecule"""
    # Security validation
    validate_input_size(sdf_text)
    
    mol = Chem.MolFromMolBlock(sdf_text)
    if mol is None:
        raise ValueError("Failed to parse SDF text")
    
    # Additional validation: ensure we have valid atoms
    if mol.GetNumAtoms() == 0:
        raise ValueError("SDF text contains no valid atoms")
    
    # Validate molecule complexity
    validate_molecule_complexity(mol)
    
    return mol


def get_coordinates(mol: Chem.Mol) -> np.ndarray:
    """Get 3D coordinates from RDKit molecule"""
    conf = mol.GetConformer()
    coords = []
    for i in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        coords.append([pos.x, pos.y, pos.z])
    return np.array(coords)


def get_simple_donor_acceptor_types(atom: Chem.Atom, residue_name: str, atom_name: str) -> Tuple[bool, bool]:
    """
    Simple donor/acceptor typing based on atom type and residue context.
    Returns (is_donor, is_acceptor) tuple.
    """
    symbol = atom.GetSymbol()
    
    # Basic atom-based typing
    if symbol == 'N':
        # Nitrogen can be both donor and acceptor
        # In proteins, backbone N is usually a donor, sidechain N varies
        if atom_name in ['N', 'N1', 'N2', 'N3', 'N4']:  # Backbone or primary amines
            return True, False
        elif atom_name in ['NE', 'NH1', 'NH2']:  # Arginine, Lysine - donor only
            return True, False
        elif atom_name in ['ND1', 'NE2']:  # Histidine - both
            return True, True
        elif atom_name in ['NZ']:  # Lysine NZ - donor only
            return True, False
        else:
            return True, True  # Default: both
    
    elif symbol == 'O':
        # Oxygen is usually an acceptor, can be donor in some cases
        if atom_name in ['O', 'O1', 'O2']:  # Backbone carbonyl
            return False, True
        elif atom_name in ['OH', 'OG']:  # Serine, Threonine, Tyrosine
            return True, True  # Can donate H and accept H
        else:
            return False, True  # Default: acceptor only
    
    elif symbol == 'S':
        # Sulfur can be both donor and acceptor
        if atom_name in ['SG']:  # Cysteine
            return True, True
        else:
            return True, True  # Default: both
    
    # Handle ligand atoms (LIG residue)
    if residue_name == "LIG":
        if symbol == 'N':
            # For ligands, nitrogen is usually a donor
            return True, False
        elif symbol == 'O':
            # For ligands, oxygen is usually an acceptor
            return False, True
        elif symbol == 'S':
            # For ligands, sulfur can be both
            return True, True
    
    # Default: not a donor/acceptor
    return False, False


def get_ring_centroids_and_normals(mol: Chem.Mol, coords: np.ndarray, cache_key: str) -> List[Dict]:
    """
    Get ring centroids and normals for π–π interactions.
    Uses caching to avoid recomputation.
    """
    if cache_key in _ring_cache:
        return _ring_cache[cache_key]
    
    rings = []
    
    # Get all rings from the molecule
    ring_info = mol.GetRingInfo()
    atom_rings = ring_info.AtomRings()
    
    for ring_atoms in atom_rings:
        if len(ring_atoms) >= 5:  # Only consider rings with 5+ atoms
            # Check if ring is aromatic
            is_aromatic = all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring_atoms)
            if not is_aromatic:
                continue
            
            # Calculate centroid
            ring_coords = coords[ring_atoms, :]  # Use proper 2D indexing
            centroid = np.mean(ring_coords, axis=0)
            
            # Calculate normal vector using 3 points (simplified approach)
            if len(ring_atoms) >= 3:
                v1 = ring_coords[1] - ring_coords[0]
                v2 = ring_coords[2] - ring_coords[0]
                normal = np.cross(v1, v2)
                # Check if normal is valid (not zero vector)
                norm_val = np.linalg.norm(normal)
                if norm_val > 1e-6:
                    normal = normal / norm_val  # Normalize
                else:
                    normal = np.array([0, 0, 1])  # Default normal if cross product is zero
            else:
                normal = np.array([0, 0, 1])  # Default normal
            
            rings.append({
                'atoms': ring_atoms,
                'centroid': centroid,
                'normal': normal,
                'size': len(ring_atoms)
            })
    
    # Cache the result
    _ring_cache[cache_key] = rings
    _update_cache_timestamp(cache_key)
    return rings


def detect_hbonds(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                  protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                  residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect hydrogen bonds between protein and ligand using simple donor/acceptor typing"""
    contacts = []
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if i not in residue_info:
            continue
            
        res_info = residue_info[i]
        protein_is_donor, protein_is_acceptor = get_simple_donor_acceptor_types(
            protein_atom, res_info['res_name'], res_info['atom_name']
        )
        
        if not (protein_is_donor or protein_is_acceptor):
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            ligand_is_donor, ligand_is_acceptor = get_simple_donor_acceptor_types(
                ligand_atom, "LIG", f"L{j}"
            )
            
            # Check for complementary donor-acceptor pairs
            if not ((protein_is_donor and ligand_is_acceptor) or 
                   (protein_is_acceptor and ligand_is_donor)):
                continue
            
            # Calculate distance
            dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
            if dist > params.hbond_max_dist:
                continue
            
            # Simple angle check (if we have hydrogen coordinates)
            angle = None
            if protein_is_donor:
                # For protein donor, check angle to ligand
                # This is simplified - in practice you'd need H coordinates
                angle = 150.0  # Placeholder
            elif ligand_is_donor:
                # For ligand donor, check angle to protein
                angle = 150.0  # Placeholder
            
            if angle is None or angle >= params.hbond_min_angle:
                contacts.append(Contact(
                    type="HBOND",
                    ligand_atom=j,
                    protein_resi=res_info['res_id'],
                    protein_resn=res_info['res_name'],
                    protein_atom=res_info['atom_name'],
                    distance=dist,
                    angle=angle
                ))
    
    return contacts


def detect_hydrophobic(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                       protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                       residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect hydrophobic interactions between protein and ligand"""
    contacts = []
    
    # Hydrophobic atoms (simplified)
    hydrophobic_atoms = ['C']
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if i not in residue_info:
            continue
            
        if protein_atom.GetSymbol() not in hydrophobic_atoms:
            continue
            
        res_info = residue_info[i]
        
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            if ligand_atom.GetSymbol() not in hydrophobic_atoms:
                continue
            
            # Calculate distance
            dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
            if dist <= params.hydrophobic_max_dist:
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
    """Detect π-π stacking interactions using cached ring centroids and normals"""
    if not params.pi_stack:
        return []
    
    contacts = []
    
    # Generate cache keys
    protein_cache_key = get_cache_key(protein_mol, "protein")
    ligand_cache_key = get_cache_key(ligand_mol, "ligand")
    
    # Get ring information using caching
    protein_rings = get_ring_centroids_and_normals(protein_mol, protein_coords, protein_cache_key)
    ligand_rings = get_ring_centroids_and_normals(ligand_mol, ligand_coords, ligand_cache_key)
    
    # Check ring-ring distances and orientations
    for p_ring in protein_rings:
        # Find the residue info for the first atom in the ring
        ring_atom_idx = p_ring['atoms'][0]
        if ring_atom_idx not in residue_info:
            continue
            
        res_info = residue_info[ring_atom_idx]
        
        for l_ring in ligand_rings:
            # Calculate centroid distance
            dist = np.linalg.norm(p_ring['centroid'] - l_ring['centroid'])
            
            # π-π stacking distance range: 3.5-7.0 Å
            if 3.5 <= dist <= 7.0:
                # Calculate angle between ring normals (simplified)
                # In practice, you'd want more sophisticated geometric analysis
                normal_angle = np.arccos(np.clip(
                    np.abs(np.dot(p_ring['normal'], l_ring['normal'])), -1, 1
                )) * 180 / np.pi
                
                # Prefer parallel (0°) or perpendicular (90°) orientations
                if normal_angle <= 30 or (60 <= normal_angle <= 120):
                    contacts.append(Contact(
                        type="PI-PI",
                        ligand_atom=l_ring['atoms'][0],  # Use first atom as representative
                        protein_resi=res_info['res_id'],
                        protein_resn=res_info['res_name'],
                        protein_atom=res_info['atom_name'],
                        distance=dist,
                        angle=normal_angle
                    ))
    
    return contacts


def detect_salt_bridges(protein_coords: np.ndarray, ligand_coords: np.ndarray,
                        protein_mol: Chem.Mol, ligand_mol: Chem.Mol,
                        residue_info: Dict[int, Dict], params: ContactParams) -> List[Contact]:
    """Detect salt bridge interactions using simple charge detection"""
    contacts = []
    
    # Charged residues (simplified)
    positive_residues = {'LYS', 'ARG', 'HIS'}
    negative_residues = {'ASP', 'GLU'}
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if i not in residue_info:
            continue
            
        res_info = residue_info[i]
        res_name = res_info['res_name']
        
        # Check if this is a charged residue
        is_charged = res_name in positive_residues or res_name in negative_residues
        
        if not is_charged:
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            # Simple ligand charge detection (in practice, use formal charges)
            ligand_symbol = ligand_atom.GetSymbol()
            
            # Check for complementary charges
            protein_positive = res_name in positive_residues
            ligand_negative = ligand_symbol in ['O', 'S', 'N']  # Simplified
            
            if protein_positive == ligand_negative:  # Opposite charges
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
    
    # Metal atoms
    metal_atoms = ['FE', 'MN', 'CU', 'ZN', 'MG', 'CA', 'NA', 'K']
    
    for i, protein_atom in enumerate(protein_mol.GetAtoms()):
        if i not in residue_info:
            continue
            
        res_info = residue_info[i]
        atom_symbol = protein_atom.GetSymbol()
        
        if atom_symbol not in metal_atoms:
            continue
            
        for j, ligand_atom in enumerate(ligand_mol.GetAtoms()):
            ligand_symbol = ligand_atom.GetSymbol()
            
            # Check if ligand atom can coordinate to metal
            if ligand_symbol in ['O', 'N', 'S']:
                # Calculate distance
                dist = np.linalg.norm(protein_coords[i] - ligand_coords[j])
                if dist <= params.metal_max_dist:
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
    """Get summary information about protein and ligand"""
    # Count unique residues
    unique_residues = set()
    for info in residue_info.values():
        unique_residues.add((info['res_name'], info['res_id']))
    
    protein_summary = {
        "chains": 1,  # Simplified - assume single chain
        "residues": len(unique_residues)
    }
    
    ligand_summary = {
        "atoms": ligand_mol.GetNumAtoms(),
        "bonds": ligand_mol.GetNumBonds()
    }
    
    return ligand_summary, protein_summary


def analyze_protein_ligand_interactions(pdb_text: str, sdf_text: str, 
                                      params: ContactParams, 
                                      viz_params: Optional[VisualizationParams] = None) -> AnalyzeResponse:
    """Analyze protein-ligand interactions using all detection methods"""
    warnings = []
    
    # Clear ring cache for fresh computation
    clear_ring_cache()
    
    # Parse structures - these will raise ValueError for invalid input
    protein_mol, residue_info = parse_pdb(pdb_text, viz_params.hide_waters_ions if viz_params else True)
    ligand_mol = parse_sdf(sdf_text)
    
    # Get coordinates
    protein_coords = get_coordinates(protein_mol)
    ligand_coords = get_coordinates(ligand_mol)
    
    # Detect all types of interactions
    hbonds = detect_hbonds(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
    hydrophobic = detect_hydrophobic(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
    pi_stacking = detect_pi_stacking(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
    salt_bridges = detect_salt_bridges(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
    metal_coordination = detect_metal_coordination(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
    
    # Combine all contacts
    all_contacts = hbonds + hydrophobic + pi_stacking + salt_bridges + metal_coordination
    
    # Get summaries
    ligand_summary, protein_summary = get_summaries(protein_mol, ligand_mol, residue_info)
    
    # Filter PDB if requested
    filtered_pdb = None
    if viz_params and viz_params.hide_waters_ions:
        filtered_pdb = filter_waters_ions(pdb_text)
    
    return AnalyzeResponse(
        contacts=all_contacts,
        ligand_summary=ligand_summary,
        protein_summary=protein_summary,
        warnings=warnings,
        filtered_pdb=filtered_pdb
    ) 