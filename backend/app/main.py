"""
Skill Gap Analyzer - FastAPI Backend
Enhanced with Deep Learning and ML algorithms
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import routes
from api.routes import auth, skills, data

# Import database and ML services
from core.database import get_database
from services.advanced_ml import analyzer, get_skill_gap_analysis, get_learning_path
from services.extended_dataset import get_dataset_summary

# Create FastAPI app
app = FastAPI(
    title="Skill Gap Analyzer API",
    description="Advanced skill gap analyzer with Deep Learning and ML algorithms",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Skill Gap Analyzer API v2.0",
        "status": "running",
        "features": [
            "Deep Learning Predictions",
            "ML-Based Analysis",
            "Extended Skill Dataset",
            "Learning Path Generation",
            "Real-time Recommendations"
        ]
    }

# API Documentation
@app.get("/api/info")
async def api_info():
    return {
        "name": "Skill Gap Analyzer",
        "version": "2.0",
        "features": get_dataset_summary(),
        "endpoints": {
            "auth": "/api/auth/",
            "skills": "/api/skills/",
            "data": "/api/data/",
            "docs": "/docs"
        }
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and ML models on startup"""
    try:
        print("[*] Initializing database...")
        get_database()
        print("[OK] Database initialized")
        
        print("[*] ML Models ready")
        print("[OK] Application startup complete")
    except Exception as e:
        print(f"[ERROR] Startup failed: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
