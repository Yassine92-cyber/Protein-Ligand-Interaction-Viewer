#!/usr/bin/env python3
"""Debug script to test detection functions directly"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.contacts import (
    detect_hbonds, detect_hydrophobic, detect_pi_stacking,
    get_simple_donor_acceptor_types, parse_pdb, parse_sdf
)
from app.schemas import ContactParams
import numpy as np

def debug_hbond_detection():
    """Debug HBOND detection"""
    print("=== Debugging HBOND Detection ===")
    
    # Create synthetic PDB with serine OH pointing to a carbonyl oxygen
    synthetic_pdb = """ATOM      1  N   SER     1       0.000   0.000   0.000  1.00 20.00           N  
ATOM      2  CA  SER     1       1.000   0.000   0.000  1.00 20.00           C  
ATOM      3  C   SER     1       2.000   0.000   0.000  1.00 20.00           C  
ATOM      4  O   SER     1       3.000   0.000   0.000  1.00 20.00           O  
ATOM      5  CB  SER     1       1.000   1.000   0.000  1.00 20.00           C  
ATOM      6  OG  SER     1       1.000   1.000   1.000  1.00 20.00           O  
ATOM      7  HO  SER     1       1.000   1.000   2.000  1.00 20.00           H  
TER
END"""
    
    # Create synthetic SDF with a donor group (e.g., NH2) at 2.8 Å from serine OH
    synthetic_sdf = """donor
     RDKit          3D

  3  2  0  0  0  0  0  0  0  0999 V2000
    1.0000    1.0000    3.8000 N   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000    1.0000    4.8000 H   0  0  0  0  0  0  0  0  0  0  0  0
    2.0000    1.0000    3.8000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END"""
    
    print("Parsing PDB...")
    protein_mol, residue_info = parse_pdb(synthetic_pdb)
    print(f"  Protein: {protein_mol.GetNumAtoms()} atoms, {len(residue_info)} residue info entries")
    
    print("Parsing SDF...")
    ligand_mol = parse_sdf(synthetic_sdf)
    print(f"  Ligand: {ligand_mol.GetNumAtoms()} atoms")
    
    print("Getting coordinates...")
    protein_conf = protein_mol.GetConformer()
    ligand_conf = ligand_mol.GetConformer()
    protein_coords = np.array([protein_conf.GetAtomPosition(i) for i in range(protein_mol.GetNumAtoms())])
    ligand_coords = np.array([ligand_conf.GetAtomPosition(i) for i in range(ligand_mol.GetNumAtoms())])
    print(f"  Protein coords shape: {protein_coords.shape}")
    print(f"  Ligand coords shape: {ligand_coords.shape}")
    
    print("Checking donor/acceptor types...")
    for i, atom in enumerate(protein_mol.GetAtoms()):
        if i in residue_info:
            res_info = residue_info[i]
            is_donor, is_acceptor = get_simple_donor_acceptor_types(
                atom, res_info['res_name'], res_info['atom_name']
            )
            print(f"  {res_info['res_name']}.{res_info['atom_name']} ({atom.GetSymbol()}): donor={is_donor}, acceptor={is_acceptor}")
    
    for i, atom in enumerate(ligand_mol.GetAtoms()):
        is_donor, is_acceptor = get_simple_donor_acceptor_types(atom, "LIG", f"L{i}")
        print(f"  LIG.L{i} ({atom.GetSymbol()}): donor={is_donor}, acceptor={is_acceptor}")
    
    print("\nChecking distances between potential HBOND pairs...")
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
            print(f"  {res_info['res_name']}.{res_info['atom_name']} ({protein_atom.GetSymbol()}) to LIG.L{j} ({ligand_atom.GetSymbol()}): {dist:.3f} Å")
            print(f"    Protein donor: {protein_is_donor}, acceptor: {protein_is_acceptor}")
            print(f"    Ligand donor: {ligand_is_donor}, acceptor: {ligand_is_acceptor}")
            print(f"    Distance threshold: {3.0} Å (max)")
    
    print("\nTesting HBOND detection...")
    params = ContactParams(hbond_max_dist=3.0, hbond_min_angle=160.0)
    contacts = detect_hbonds(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
    print(f"  Found {len(contacts)} HBOND contacts")
    for contact in contacts:
        print(f"    {contact}")

def debug_pi_pi_detection():
    """Debug PI-PI detection"""
    print("\n=== Debugging PI-PI Detection ===")
    
    try:
        # Create synthetic PDB with benzene ring
        synthetic_pdb = """ATOM      1  N   PHE     1       0.000   0.000   0.000  1.00 20.00           N  
ATOM      2  CA  PHE     1       1.000   0.000   0.000  1.00 20.00           C  
ATOM      3  C   PHE     1       2.000   0.000   0.000  1.00 20.00           C  
ATOM      4  O   PHE     1       3.000   0.000   0.000  1.00 20.00           O  
ATOM      5  CB  PHE     1       1.000   1.000   0.000  1.00 20.00           C  
ATOM      6  CG  PHE     1       1.000   1.000   1.000  1.00 20.00           C  
ATOM      7  CD1 PHE     1       0.000   1.000   1.000  1.00 20.00           C  
ATOM      8  CD2 PHE     1       2.000   1.000   1.000  1.00 20.00           C  
ATOM      9  CE1 PHE     1       0.000   2.000   1.000  1.00 20.00           C  
ATOM     10  CE2 PHE     1       2.000   2.000   1.000  1.00 20.00           C  
ATOM     11  CZ  PHE     1       1.000   2.000   1.000  1.00 20.00           C  
TER
END"""
        
        # Create synthetic SDF with benzene ring at 5.0 Å, parallel to protein ring
        synthetic_sdf = """benzene
     RDKit          3D

  6  6  0  0  0  0  0  0  0  0999 V2000
    1.0000    1.0000    6.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.0000    1.0000    6.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.5000    1.8660    6.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.0000    2.7320    6.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000    2.7320    6.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000    1.8660    6.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0  0  0  0
  2  3  2  0  0  0  0
  3  4  2  0  0  0  0
  4  5  2  0  0  0  0
  5  6  2  0  0  0  0
  6  1  2  0  0  0  0
M  END"""
        
        print("Parsing PDB...")
        protein_mol, residue_info = parse_pdb(synthetic_pdb)
        print(f"  Protein: {protein_mol.GetNumAtoms()} atoms, {len(residue_info)} residue info entries")
        
        print("Parsing SDF...")
        ligand_mol = parse_sdf(synthetic_sdf)
        print(f"  Ligand: {ligand_mol.GetNumAtoms()} atoms")
        
        print("Getting coordinates...")
        protein_conf = protein_mol.GetConformer()
        ligand_conf = ligand_mol.GetConformer()
        protein_coords = np.array([protein_conf.GetAtomPosition(i) for i in range(protein_mol.GetNumAtoms())])
        ligand_coords = np.array([ligand_conf.GetAtomPosition(i) for i in range(ligand_mol.GetNumAtoms())])
        print(f"  Protein coords shape: {protein_coords.shape}")
        print(f"  Ligand coords shape: {ligand_coords.shape}")
        
        print("\nChecking ring detection...")
        from app.contacts import get_ring_centroids_and_normals, get_cache_key
        
        protein_cache_key = get_cache_key(protein_mol, "protein")
        ligand_cache_key = get_cache_key(ligand_mol, "ligand")
        
        protein_rings = get_ring_centroids_and_normals(protein_mol, protein_coords, protein_cache_key)
        ligand_rings = get_ring_centroids_and_normals(ligand_mol, ligand_coords, ligand_cache_key)
        
        print(f"  Protein rings found: {len(protein_rings)}")
        for i, ring in enumerate(protein_rings):
            print(f"    Ring {i}: {ring['size']} atoms, centroid: {ring['centroid']}, normal: {ring['normal']}")
        
        print(f"  Ligand rings found: {len(ligand_rings)}")
        for i, ring in enumerate(ligand_rings):
            print(f"    Ring {i}: {ring['size']} atoms, centroid: {ring['centroid']}, normal: {ring['normal']}")
        
        if protein_rings and ligand_rings:
            print("\nChecking ring-ring distances...")
            for i, p_ring in enumerate(protein_rings):
                for j, l_ring in enumerate(ligand_rings):
                    dist = np.linalg.norm(p_ring['centroid'] - l_ring['centroid'])
                    print(f"  Protein ring {i} to ligand ring {j}: {dist:.3f} Å")
                    
                    # Calculate angle between normals
                    normal_angle = np.arccos(np.clip(
                        np.abs(np.dot(p_ring['normal'], l_ring['normal'])), -1, 1
                    )) * 180 / np.pi
                    print(f"    Normal angle: {normal_angle:.1f}°")
        
        print("\nTesting PI-PI detection...")
        params = ContactParams(pi_stack=True)
        contacts = detect_pi_stacking(protein_coords, ligand_coords, protein_mol, ligand_mol, residue_info, params)
        print(f"  Found {len(contacts)} PI-PI contacts")
        for contact in contacts:
            print(f"    {contact}")
            
    except Exception as e:
        print(f"Error in PI-PI detection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_hbond_detection()
    debug_pi_pi_detection() 