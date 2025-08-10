import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AnalyzeRequest, AnalyzeResponse
from .contacts import analyze_protein_ligand_interactions, clear_ring_cache, _ring_cache
import os
import time
from collections import defaultdict
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting storage
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# CSRF protection
CSRF_TOKEN_HEADER = "X-CSRF-Token"
csrf_tokens = set()

def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    token = secrets.token_urlsafe(32)
    csrf_tokens.add(token)
    return token

def validate_csrf_token(token: str) -> bool:
    """Validate a CSRF token"""
    if token in csrf_tokens:
        csrf_tokens.remove(token)  # Use once
        return True
    return False

def rate_limit_middleware(request: Request):
    """Simple rate limiting middleware"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)

app = FastAPI(
    title="Protein-Ligand Interaction Viewer API",
    description="API for analyzing protein-ligand interactions using RDKit",
    version="1.0.0"
)

# Configure CORS with security restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:3000",  # Alternative dev port
        "http://localhost:80"     # Docker production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to needed methods only
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
    max_age=3600,  # Cache preflight requests
)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Apply rate limiting to all requests"""
    try:
        rate_limit_middleware(request)
        response = await call_next(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limiting error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint with system information"""
    return {
        "ok": True,
        "version": "1.0.0",
        "service": "Protein-Ligand Interaction Viewer API",
        "cache_status": {
            "ring_cache_size": len(_ring_cache),
            "ring_cache_keys": list(_ring_cache.keys())[:5] if _ring_cache else []
        }
    }

@app.get("/csrf-token")
async def get_csrf_token():
    """Get a CSRF token for form submission"""
    token = generate_csrf_token()
    return {"csrf_token": token}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_interactions(request: Request):
    """Analyze protein-ligand interactions"""
    # Get CSRF token from header
    csrf_token = request.headers.get("X-CSRF-Token")
    
    # Validate CSRF token for state-changing operations
    if not csrf_token or not validate_csrf_token(csrf_token):
        logger.warning("Invalid or missing CSRF token")
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing CSRF token"
        )
    
    # Parse the request body
    try:
        body = await request.json()
        analyze_request = AnalyzeRequest(**body)
    except Exception as e:
        logger.error(f"Invalid request body: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid request body"
        )
    
    try:
        result = analyze_protein_ligand_interactions(
            pdb_text=analyze_request.pdb_text,
            sdf_text=analyze_request.sdf_text,
            params=analyze_request.params,
            viz_params=analyze_request.viz_params
        )
        return result
    except ValueError as e:
        logger.error(f"Validation error in analysis: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid input data provided"
        )
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred"
        )


@app.post("/cache/clear")
async def clear_cache():
    """Clear the ring cache"""
    try:
        clear_ring_cache()
        return {"message": "Ring cache cleared successfully", "cache_size": 0}
    except Exception as e:
        # Log the actual error for debugging
        logger.error(f"Failed to clear cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )


@app.get("/cache/status")
async def get_cache_status():
    """Get current cache status"""
    return {
        "ring_cache_size": len(_ring_cache),
        "ring_cache_keys": list(_ring_cache.keys()),
        "memory_usage_mb": len(_ring_cache) * 0.001  # Rough estimate
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 