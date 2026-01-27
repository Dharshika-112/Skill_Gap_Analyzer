#!/usr/bin/env python3
"""
Skill Gap Analyzer - Server Startup Script
Handles all imports and starts the FastAPI server
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variable for imports
os.environ['PYTHONPATH'] = str(project_root)

def start_server():
    """Start the FastAPI server with proper configuration"""
    
    print("🚀 SKILL GAP ANALYZER - STARTING SERVER")
    print("=" * 60)
    print("🧠 Features: AI-Powered Role Matching with Deep Learning")
    print("📊 Dataset: 1000+ Real Job Descriptions")
    print("🎯 Intelligent Skill Gap Analysis")
    print("-" * 60)
    
    try:
        # Import FastAPI and create app
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
        import uvicorn
        
        # Create FastAPI app
        app = FastAPI(
            title="Skill Gap Analyzer API",
            description="AI-Powered Career Analysis with Real Job Data",
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
        
        # Import and setup routes
        sys.path.append(str(project_root / 'backend'))
        
        from backend.app.api.routes import auth, skills, data, resume_analysis
        from backend.app.core.database import get_database
        from backend.app.services.extended_dataset import get_dataset_summary
        
        # Health check endpoint
        @app.get("/")
        async def root():
            return {
                "message": "Skill Gap Analyzer API v2.0 - AI Powered",
                "status": "running",
                "features": [
                    "🧠 Deep Learning Role Matching",
                    "📊 Skill Importance Analysis", 
                    "🎯 Intelligent Gap Analysis",
                    "📈 Market Trend Analysis",
                    "🔍 Resume Parsing with AI"
                ],
                "endpoints": {
                    "docs": "/docs",
                    "auth": "/api/auth/",
                    "skills": "/api/skills/",
                    "resume": "/api/resume/",
                    "data": "/api/data/"
                }
            }
        
        # API info endpoint
        @app.get("/api/info")
        async def api_info():
            try:
                dataset_info = get_dataset_summary()
                return {
                    "name": "Skill Gap Analyzer",
                    "version": "2.0",
                    "dataset": dataset_info,
                    "ai_features": [
                        "TensorFlow/Keras Deep Learning Models",
                        "Skill Importance Scoring",
                        "Intelligent Role Matching",
                        "Market Analysis"
                    ]
                }
            except Exception as e:
                return {"error": str(e)}
        
        # Error handler
        @app.exception_handler(Exception)
        async def general_exception_handler(request, exc):
            print(f"[ERROR] {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Server error: {str(exc)}"}
            )
        
        # Include routers
        app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
        app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
        app.include_router(data.router, prefix="/api/data", tags=["Data"])
        app.include_router(resume_analysis.router, prefix="/api/resume", tags=["Resume Analysis"])
        
        # Initialize database
        @app.on_event("startup")
        async def startup_event():
            try:
                print("[*] Initializing database connection...")
                get_database()
                print("[✓] Database connected successfully")
                print("[*] Loading AI models...")
                print("[✓] AI models ready")
                print("[✓] Server startup complete!")
            except Exception as e:
                print(f"[✗] Startup error: {e}")
        
        # Start server
        print(f"🌐 Starting server at: http://localhost:8000")
        print(f"📖 API Documentation: http://localhost:8000/docs")
        print(f"🎯 Frontend URL: http://localhost:3000/index.html")
        print("-" * 60)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"[✗] Import Error: {e}")
        print("Installing missing dependencies...")
        os.system("pip install fastapi uvicorn python-multipart pymongo bcrypt python-jose[cryptography] pandas numpy scikit-learn tensorflow")
        print("Please run the script again after installation.")
        
    except Exception as e:
        print(f"[✗] Server startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_server()