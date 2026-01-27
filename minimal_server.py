#!/usr/bin/env python3
"""
Minimal FastAPI server for testing basic functionality
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
import sys
import os
sys.path.append('backend')

from backend.app.core.database import get_collection
from backend.app.core.security import hash_password, verify_password, create_access_token, decode_token, get_user_by_email
from typing import Optional

# Create FastAPI app
app = FastAPI(
    title="Skill Gap Analyzer API - Test Mode",
    description="Minimal API for testing authentication and database",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Skill Gap Analyzer API - Test Mode",
        "status": "running",
        "mode": "minimal"
    }

@app.get("/api/info")
async def api_info():
    return {
        "name": "Skill Gap Analyzer - Test Mode",
        "version": "1.0",
        "mode": "minimal",
        "endpoints": {
            "auth": "/api/auth/",
            "docs": "/docs"
        }
    }

@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    users = get_collection('users')
    existing = users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "name": req.name,
        "email": req.email,
        "password_hash": hash_password(req.password),
        "created_at": datetime.utcnow()
    }
    result = users.insert_one(user)
    user_id = str(result.inserted_id)
    token = create_access_token({"user_id": user_id, "email": req.email})
    return {"status": "success", "user_id": user_id, "access_token": token}

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    users = get_collection('users')
    user = users.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, user.get('password_hash', '')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user.get('_id'))
    token = create_access_token({"user_id": user_id, "email": user.get('email')})
    return {"status": "success", "access_token": token, "user_id": user_id}

def _get_token_from_header(authorization: Optional[str]):
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    return None

@app.get("/api/auth/me")
async def me(authorization: Optional[str] = Header(None)):
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(payload.get('email'))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": str(user.get('_id')),
        "name": user.get('name'),
        "email": user.get('email'),
        "created_at": user.get('created_at')
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        print("[*] Initializing database...")
        from backend.app.core.database import get_database
        get_database()
        print("[OK] Database initialized")
        print("[OK] Minimal server startup complete")
    except Exception as e:
        print(f"[ERROR] Startup failed: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Minimal Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")