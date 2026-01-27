#!/usr/bin/env python3
"""
Start the Skill Gap Analyzer Backend Server
"""

import sys
import os
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Now import and run the app
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🚀 Starting Skill Gap Analyzer Backend Server...")
    print("📊 Features: AI-Powered Role Matching, Deep Learning Analysis")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("-" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )