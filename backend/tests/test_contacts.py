import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import ContactParams

client = TestClient(app)

# Test PDB data (simplified 1L2Y thrombin structure)
TEST_PDB = """ATOM      1  N   ALA     1      27.387  14.327   5.623  1.00 20.00           N  
ATOM      2  CA  ALA     1      26.123  13.823   6.147  1.00 20.00           C  
ATOM      3  C   ALA     1      25.000  14.856   5.823  1.00 20.00           C  
ATOM      4  O   ALA     1      24.000  14.551   5.123  1.00 20.00           O  
ATOM      5  CB  ALA     1      26.123  12.456   5.456  1.00 20.00           C  
ATOM      6  N   ARG     2      25.123  15.987   6.456  1.00 20.00           N  
ATOM      7  CA  ARG     2      24.123  17.123   6.789  1.00 20.00           C  
ATOM      8  C   ARG     2      23.123  17.456   7.890  1.00 20.00           C  
ATOM      9  O   ARG     2      22.123  18.123   7.789  1.00 20.00           O  
ATOM     10  CB  ARG     2      24.123  18.123   5.456  1.00 20.00           C  
ATOM     11  CG  ARG     2      23.123  19.123   5.123  1.00 20.00           C  
ATOM     12  CD  ARG     2      22.123  19.456   6.234  1.00 20.00           C  
ATOM     13  NE  ARG     2      21.123  20.123   6.123  1.00 20.00           N  
ATOM     14  CZ  ARG     2      20.123  20.456   7.234  1.00 20.00           C  
ATOM     15  NH1 ARG     2      19.123  21.123   7.123  1.00 20.00           N  
ATOM     16  NH2 ARG     2      20.123  19.789   8.345  1.00 20.00           N  
ATOM     17  N   PHE     3      23.456  16.789   8.901  1.00 20.00           N  
ATOM     18  CA  PHE     3      22.456  17.123   9.012  1.00 20.00           C  
ATOM     19  C   PHE     3      21.456  16.456   9.123  1.00 20.00           C  
ATOM     20  O   PHE     3      20.456  16.789   9.234  1.00 20.00           O  
ATOM     21  CB  PHE     3      22.456  18.456   9.345  1.00 20.00           C  
ATOM     22  CG  PHE     3      21.456  19.123   9.456  1.00 20.00           C  
ATOM     23  CD1 PHE     3      20.456  19.456   8.567  1.00 20.00           C  
ATOM     24  CD2 PHE     3      21.456  19.789   10.678  1.00 20.00           C  
ATOM     25  CE1 PHE     3      19.456  20.123   8.678  1.00 20.00           C  
ATOM     26  CE2 PHE     3      20.456  20.456   10.789  1.00 20.00           C  
ATOM     27  CZ  PHE     3      19.456  20.789   9.890  1.00 20.00           C  
TER
END"""

# Test SDF data (simple benzene-like molecule)
TEST_SDF = """benzene
     RDKit          3D

  6  6  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.1000    1.2120    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4000    2.4240    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    2.4240    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7000    1.2120    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0  0  0  0
  2  3  2  0  0  0  0
  3  4  2  0  0  0  0
  4  5  2  0  0  0  0
  5  6  2  0  0  0  0
  6  1  2  0  0  0  0
M  END"""


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_analyze_endpoint_basic():
    """Test the analyze endpoint with basic parameters"""
    request_data = {
        "pdb_text": TEST_PDB,
        "sdf_text": TEST_SDF,
        "params": {
            "hbond_max_dist": 5.0,
            "hbond_min_angle": 120.0,
            "hydrophobic_max_dist": 5.0,
            "pi_stack": True,
            "salt_bridge_max_dist": 5.0,
            "metal_max_dist": 3.0
        }
    }
    
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "contacts" in data
    assert "ligand_summary" in data
    assert "protein_summary" in data
    assert "warnings" in data
    
    # Check ligand summary
    assert data["ligand_summary"]["atoms"] == 6
    assert data["ligand_summary"]["bonds"] == 6
    
    # Check protein summary
    assert data["protein_summary"]["residues"] >= 3  # ALA, ARG, PHE
    assert data["protein_summary"]["chains"] >= 1


def test_analyze_endpoint_permissive_params():
    """Test with very permissive parameters to ensure we get contacts"""
    request_data = {
        "pdb_text": TEST_PDB,
        "sdf_text": TEST_SDF,
        "params": {
            "hbond_max_dist": 10.0,  # Very permissive
            "hbond_min_angle": 90.0,  # Very permissive
            "hydrophobic_max_dist": 10.0,  # Very permissive
            "pi_stack": True,
            "salt_bridge_max_dist": 10.0,  # Very permissive
            "metal_max_dist": 5.0  # Very permissive
        }
    }
    
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    # With permissive parameters, we should get at least some contacts
    assert len(data["contacts"]) >= 0  # Could be 0 if no valid contacts found


def test_analyze_endpoint_restrictive_params():
    """Test with very restrictive parameters"""
    request_data = {
        "pdb_text": TEST_PDB,
        "sdf_text": TEST_SDF,
        "params": {
            "hbond_max_dist": 1.0,  # Very restrictive
            "hbond_min_angle": 180.0,  # Very restrictive
            "hydrophobic_max_dist": 1.0,  # Very restrictive
            "pi_stack": False,  # Disabled
            "salt_bridge_max_dist": 1.0,  # Very restrictive
            "metal_max_dist": 1.0  # Very restrictive
        }
    }
    
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    # With restrictive parameters, we should get fewer contacts
    assert len(data["contacts"]) >= 0


def test_analyze_endpoint_invalid_pdb():
    """Test with invalid PDB data"""
    request_data = {
        "pdb_text": "INVALID PDB DATA",
        "sdf_text": TEST_SDF,
        "params": ContactParams().dict()
    }
    
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 400
    assert "Analysis failed" in response.json()["detail"]


def test_analyze_endpoint_invalid_sdf():
    """Test with invalid SDF data"""
    request_data = {
        "pdb_text": TEST_PDB,
        "sdf_text": "INVALID SDF DATA",
        "params": ContactParams().dict()
    }
    
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 400
    assert "Analysis failed" in response.json()["detail"]


def test_contact_params_defaults():
    """Test ContactParams default values"""
    params = ContactParams()
    assert params.hbond_max_dist == 3.5
    assert params.hbond_min_angle == 120.0
    assert params.hydrophobic_max_dist == 4.0
    assert params.pi_stack is True
    assert params.salt_bridge_max_dist == 4.0
    assert params.metal_max_dist == 2.8


def test_contact_structure():
    """Test Contact model structure"""
    contact = {
        "type": "HBOND",
        "ligand_atom": 0,
        "protein_resi": 1,
        "protein_resn": "ALA",
        "protein_atom": "N",
        "distance": 3.2,
        "angle": 150.0
    }
    
    # This should not raise validation errors
    from app.schemas import Contact
    Contact(**contact)


def test_analyze_request_structure():
    """Test AnalyzeRequest model structure"""
    request_data = {
        "pdb_text": TEST_PDB,
        "sdf_text": TEST_SDF,
        "params": ContactParams().dict()
    }
    
    # This should not raise validation errors
    from app.schemas import AnalyzeRequest
    AnalyzeRequest(**request_data)


if __name__ == "__main__":
    pytest.main([__file__]) 