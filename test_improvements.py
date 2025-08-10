#!/usr/bin/env python3
"""
Test script for the improved protein-ligand interaction analysis
Tests the new donor/acceptor typing and ring caching features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.contacts import (
    get_simple_donor_acceptor_types,
    get_ring_centroids_and_normals,
    clear_ring_cache,
    get_cache_key
)
from backend.app.schemas import ContactParams
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np


def test_donor_acceptor_typing():
    """Test the simple donor/acceptor typing function"""
    print("Testing donor/acceptor typing...")
    
    # Create a simple molecule for testing
    mol = Chem.MolFromSmiles("CCO")  # Ethanol
    atom = mol.GetAtomWithIdx(1)  # Oxygen atom
    
    # Test different atom types
    test_cases = [
        ("N", "LYS", "NZ", (True, False)),  # Lysine nitrogen - donor only
        ("O", "SER", "OG", (True, True)),   # Serine oxygen - both
        ("S", "CYS", "SG", (True, True)),   # Cysteine sulfur - both
        ("C", "ALA", "CA", (False, False)), # Carbon - neither
    ]
    
    for symbol, res_name, atom_name, expected in test_cases:
        # Create a mock atom
        mock_atom = Chem.Atom(symbol)
        result = get_simple_donor_acceptor_types(mock_atom, res_name, atom_name)
        print(f"  {symbol} in {res_name}.{atom_name}: {result} (expected: {expected})")
        assert result == expected, f"Failed for {symbol} in {res_name}.{atom_name}"
    
    print("✅ Donor/acceptor typing tests passed!")


def test_ring_caching():
    """Test the ring centroid and normal caching"""
    print("\nTesting ring caching...")
    
    # Create a simple aromatic molecule
    mol = Chem.MolFromSmiles("c1ccccc1")  # Benzene
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)
    
    # Get coordinates - ensure proper 2D array shape
    conf = mol.GetConformer()
    coords = []
    for i in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        coords.append([pos.x, pos.y, pos.z])
    coords = np.array(coords, dtype=np.float64)
    
    print(f"  Molecule has {mol.GetNumAtoms()} atoms")
    print(f"  Coordinates shape: {coords.shape}")
    
    # Test cache key generation
    cache_key = get_cache_key(mol, "test")
    print(f"  Generated cache key: {cache_key}")
    
    # Test first call (should compute)
    rings1 = get_ring_centroids_and_normals(mol, coords, cache_key)
    print(f"  First call - found {len(rings1)} rings")
    
    # Test second call (should use cache)
    rings2 = get_ring_centroids_and_normals(mol, coords, cache_key)
    print(f"  Second call - found {len(rings2)} rings (cached)")
    
    # Verify cache hit
    assert len(rings1) == len(rings2), "Cache not working properly"
    assert rings1 == rings2, "Cached results don't match"
    
    # Test cache clearing
    clear_ring_cache()
    rings3 = get_ring_centroids_and_normals(mol, coords, cache_key)
    print(f"  After cache clear - found {len(rings3)} rings (recomputed)")
    
    print("✅ Ring caching tests passed!")


def test_parameter_validation():
    """Test the parameter validation and clamping"""
    print("\nTesting parameter validation...")
    
    # Test valid parameters
    valid_params = ContactParams(
        hbond_max_dist=5.0,
        hbond_min_angle=150.0,
        hydrophobic_max_dist=6.0,
        pi_stack=True,
        salt_bridge_max_dist=5.0,
        metal_max_dist=3.0
    )
    print(f"  Valid parameters: {valid_params}")
    
    # Test parameter clamping
    clamped_params = ContactParams(
        hbond_max_dist=15.0,  # Should be clamped to 10.0
        hbond_min_angle=50.0,  # Should be clamped to 90.0
        hydrophobic_max_dist=0.5,  # Should be clamped to 1.0
        pi_stack=False,
        salt_bridge_max_dist=20.0,  # Should be clamped to 10.0
        metal_max_dist=0.1  # Should be clamped to 1.0
    )
    print(f"  Clamped parameters: {clamped_params}")
    
    # Verify clamping worked
    assert clamped_params.hbond_max_dist == 10.0, "H-bond distance not clamped"
    assert clamped_params.hbond_min_angle == 90.0, "H-bond angle not clamped"
    assert clamped_params.hydrophobic_max_dist == 1.0, "Hydrophobic distance not clamped"
    assert clamped_params.salt_bridge_max_dist == 10.0, "Salt bridge distance not clamped"
    assert clamped_params.metal_max_dist == 1.0, "Metal distance not clamped"
    
    print("✅ Parameter validation tests passed!")


def main():
    """Run all tests"""
    print("🧪 Testing Protein-Ligand Interaction Analysis Improvements\n")
    
    try:
        test_donor_acceptor_typing()
        test_ring_caching()
        test_parameter_validation()
        
        print("\n🎉 All tests passed! The improvements are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 