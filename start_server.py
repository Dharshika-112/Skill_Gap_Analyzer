#!/usr/bin/env python3
"""
Start the FastAPI server directly
"""

import sys
import os
sys.path.append('backend')

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Skill Gap Analyzer API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    try:
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)