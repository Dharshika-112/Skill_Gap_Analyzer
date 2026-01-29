#!/usr/bin/env python3
"""
Simple Authentication Server for CareerBoost AI
Handles user signup and login with MongoDB integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

# Create FastAPI app
app = FastAPI(
    title="CareerBoost AI - Authentication API",
    description="User authentication system",
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

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "careerboost"
JWT_SECRET = "careerboost_secret_key_2026"

def get_db():
    """Get database connection"""
    client = MongoClient(MONGODB_URL)
    return client[DATABASE_NAME]

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for user"""
    payload = {
        "user_id": str(user_data["_id"]),
        "email": user_data["email"],
        "name": user_data["name"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def calculate_profile_completion(user_data: dict) -> int:
    """Calculate profile completion percentage"""
    completion = 25  # Base for name, email, password
    
    if user_data.get('phone'):
        completion += 15
    if user_data.get('specialization'):
        completion += 20
    if user_data.get('experience'):
        completion += 20
    if user_data.get('degree'):
        completion += 20
    
    return completion

# Health check
@app.get("/")
async def root():
    return {
        "message": "CareerBoost AI - Authentication API v1.0",
        "status": "running",
        "features": ["User Signup", "User Login", "Profile Management"]
    }

# User Signup
@app.post("/auth/signup")
async def signup(request: dict):
    """User signup endpoint"""
    try:
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not request.get(field):
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        db = get_db()
        users_collection = db['users']
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": request['email']})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Calculate profile completion
        completion = calculate_profile_completion(request)
        
        # Prepare user document
        user_doc = {
            "name": request['name'],
            "email": request['email'],
            "password_hash": hash_password(request['password']),
            "phone": request.get('phone', ''),
            "specialization": request.get('specialization', ''),
            "experience": request.get('experience', ''),
            "degree": request.get('degree', ''),
            "profile_completion": completion,
            "needs_profile_completion": completion < 100,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insert user
        result = users_collection.insert_one(user_doc)
        
        # Get created user
        created_user = users_collection.find_one({"_id": result.inserted_id})
        
        # Create JWT token
        token = create_jwt_token(created_user)
        
        return JSONResponse({
            "success": True,
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": str(created_user["_id"]),
                "name": created_user["name"],
                "email": created_user["email"],
                "phone": created_user.get("phone", ""),
                "specialization": created_user.get("specialization", ""),
                "experience": created_user.get("experience", ""),
                "degree": created_user.get("degree", ""),
                "profile_completion": created_user["profile_completion"],
                "needs_profile_completion": created_user["needs_profile_completion"]
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

# User Login
@app.post("/auth/login")
async def login(request: dict):
    """User login endpoint"""
    try:
        email = request.get('email')
        password = request.get('password')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        db = get_db()
        users_collection = db['users']
        
        # Find user
        user_doc = users_collection.find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        password_hash = hash_password(password)
        if user_doc['password_hash'] != password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user_doc.get('is_active', False):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Create JWT token
        token = create_jwt_token(user_doc)
        
        return JSONResponse({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user_doc["_id"]),
                "name": user_doc["name"],
                "email": user_doc["email"],
                "phone": user_doc.get("phone", ""),
                "specialization": user_doc.get("specialization", ""),
                "experience": user_doc.get("experience", ""),
                "degree": user_doc.get("degree", ""),
                "profile_completion": user_doc.get("profile_completion", 25),
                "needs_profile_completion": user_doc.get("needs_profile_completion", True)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# Update Profile
@app.put("/auth/profile")
async def update_profile(request: dict):
    """Update user profile"""
    try:
        user_id = request.get('user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        db = get_db()
        users_collection = db['users']
        
        # Find user
        from bson import ObjectId
        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        allowed_fields = ['phone', 'specialization', 'experience', 'degree']
        for field in allowed_fields:
            if field in request:
                update_data[field] = request[field]
        
        # Calculate new completion percentage
        updated_user_data = {**user_doc, **update_data}
        completion = calculate_profile_completion(updated_user_data)
        update_data['profile_completion'] = completion
        update_data['needs_profile_completion'] = completion < 100
        
        # Update user
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Get updated user
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        return JSONResponse({
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": str(updated_user["_id"]),
                "name": updated_user["name"],
                "email": updated_user["email"],
                "phone": updated_user.get("phone", ""),
                "specialization": updated_user.get("specialization", ""),
                "experience": updated_user.get("experience", ""),
                "degree": updated_user.get("degree", ""),
                "profile_completion": updated_user["profile_completion"],
                "needs_profile_completion": updated_user["needs_profile_completion"]
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

# Database info
@app.get("/auth/database/info")
async def get_database_info():
    """Get database information"""
    try:
        db = get_db()
        users_count = db['users'].count_documents({})
        active_users = db['users'].count_documents({"is_active": True})
        
        return {
            "database": DATABASE_NAME,
            "collections": {
                "users": {
                    "total": users_count,
                    "active": active_users,
                    "inactive": users_count - active_users
                }
            },
            "status": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CareerBoost AI Authentication Server")
    print("=" * 50)
    print("📊 Database: careerboost")
    print("🌐 Server: http://localhost:8003")
    print("📖 API Docs: http://localhost:8003/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )