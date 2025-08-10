from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AnalyzeRequest, AnalyzeResponse
from .contacts import analyze_protein_ligand_interactions

app = FastAPI(
    title="Protein-Ligand Interaction Viewer API",
    description="API for analyzing protein-ligand interactions using RDKit",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_interactions(request: AnalyzeRequest):
    """Analyze protein-ligand interactions"""
    try:
        result = analyze_protein_ligand_interactions(
            pdb_text=request.pdb_text,
            sdf_text=request.sdf_text,
            params=request.params
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 