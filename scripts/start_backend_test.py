#!/usr/bin/env python3
"""
Simple backend startup test - runs server for testing
"""
import uvicorn
import time
import sys

if __name__ == "__main__":
    print("="*70)
    print("BACKEND SERVER STARTUP TEST")
    print("="*70)
    
    config = uvicorn.Config(
        app="backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
    
    server = uvicorn.Server(config)
    
    print("\n[*] Starting Uvicorn server...")
    print(f"[*] Listening on http://0.0.0.0:8000")
    print("[*] Press Ctrl+C to stop")
    print("\nServer logs:")
    print("-" * 70)
    
    try:
        # This should keep running until Ctrl+C
        import asyncio
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Server failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
